"""
Commande Flask CLI : flask fix-vm-lareas-simples-simplification

Recrée la vue matérialisée ref_geo.vm_lareas_simples avec une tolérance de
simplification (ST_SimplifyPreserveTopology) distincte pour les cadastres
(id_type = 332) et pour les autres types d'aires (parcelles de forêts ONF,
parcelles ONF, UG ONF, forêts DGD, forêts privées, communes, sections,
zones cœur/adhésion/OEASC/secteur).

Valeurs par défaut retenues après comparaison visuelle : 5m pour les
cadastres, 2m pour les autres id_type (cf. migration c9d4e8f1a2b3).

Usage :
    flask fix-vm-lareas-simples-simplification [--force] [--tolerance N] [--other-tolerance N]

Les options --tolerance et --other-tolerance permettent de tester d'autres
valeurs sans passer par une migration Alembic.
- --tolerance : tolérance appliquée aux cadastres (id_type=332). Défaut : 5.
- --other-tolerance : tolérance appliquée aux autres id_type. Défaut : 2.
  Passer --other-tolerance=0 pour désactiver leur simplification.
"""

import logging

import click
from flask.cli import with_appcontext
from sqlalchemy import text

from oeasc.commands.refresh_ref_geo import ID_TYPE_CADASTRE, _get_db

LOG = logging.getLogger(__name__)


@click.command("fix-vm-lareas-simples-simplification")
@click.option(
    "--force", is_flag=True, default=False, help="Pas de confirmation interactive"
)
@click.option(
    "--tolerance",
    type=float,
    default=5,
    help="Tolérance de simplification (ST_SimplifyPreserveTopology) appliquée aux cadastres, en mètres. Défaut : 5",
)
@click.option(
    "--other-tolerance",
    type=float,
    default=2,
    help="Tolérance de simplification appliquée aux autres id_type, en mètres. Défaut : 2. Passer 0 pour ne quasiment pas simplifier.",
)
@with_appcontext
def fix_vm_lareas_simples_simplification_cmd(force, tolerance, other_tolerance):
    """Recrée ref_geo.vm_lareas_simples avec des tolérances de simplification distinctes cadastres / autres id_type."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )

    if not force:
        click.confirm(
            "Cette opération va recréer ref_geo.vm_lareas_simples "
            f"(cadastres id_type=332 : tolérance={tolerance} ; autres id_type : tolérance={other_tolerance}). "
            "Continuer ?",
            abort=True,
        )

    db = _get_db()

    LOG.info("Suppression de la vue matérialisée ref_geo.vm_lareas_simples")
    db.session.execute(
        text("DROP MATERIALIZED VIEW IF EXISTS ref_geo.vm_lareas_simples")
    )
    db.session.commit()

    LOG.info(
        f"Recréation de ref_geo.vm_lareas_simples "
        f"(cadastres id_type={ID_TYPE_CADASTRE} : tolérance={tolerance} ; autres id_type : tolérance={other_tolerance})"
    )
    db.session.execute(
        text(f"""
        CREATE MATERIALIZED VIEW ref_geo.vm_lareas_simples AS
        SELECT
            l.id_area, l.id_type,
            CASE
                WHEN l.id_type = {ID_TYPE_CADASTRE}
                    THEN ST_Transform(ST_SimplifyPreserveTopology(l.geom, {tolerance}), 4326)
                ELSE ST_Transform(ST_SimplifyPreserveTopology(l.geom, {other_tolerance}), 4326)
            END AS geom_4326,
            l.area_code, l.area_name, l.area_name AS label,
            ROUND((ST_Area(l.geom) / 10000)::numeric, 3) AS surface_calculee,
            ROUND((ST_Area(l.geom) / 10000)::numeric, 3) AS surface_renseignee,
            COALESCE(l.source, 'OEASC') AS source,
            COALESCE(l.enable, TRUE) AS enable
        FROM ref_geo.l_areas l
        WITH NO DATA
    """)
    )

    for stmt in [
        "CREATE UNIQUE INDEX ux_vm_lareas_simples_id_area ON ref_geo.vm_lareas_simples (id_area)",
        "CREATE INDEX ix_vm_lareas_simples_geom_4326 ON ref_geo.vm_lareas_simples USING GIST (geom_4326)",
        "CREATE INDEX ix_vm_lareas_simples_id_type ON ref_geo.vm_lareas_simples (id_type)",
        "CREATE INDEX ix_vm_lareas_simples_area_code ON ref_geo.vm_lareas_simples (area_code)",
        "CREATE INDEX ix_vm_lareas_simples_source ON ref_geo.vm_lareas_simples (source)",
        "REFRESH MATERIALIZED VIEW ref_geo.vm_lareas_simples",
    ]:
        db.session.execute(text(stmt))
    db.session.commit()

    LOG.info("ref_geo.vm_lareas_simples recréée avec succès.")
