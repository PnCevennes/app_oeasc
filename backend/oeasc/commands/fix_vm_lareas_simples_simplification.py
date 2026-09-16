"""
Commande Flask CLI : flask fix-vm-lareas-simples-simplification

Recrée la vue matérialisée ref_geo.vm_lareas_simples en limitant la
simplification de géométrie (ST_SimplifyPreserveTopology) aux seuls
cadastres (id_type = 332).

Les autres types d'aires (parcelles de forêts ONF, parcelles ONF, UG ONF,
forêts DGD, forêts privées, communes, sections, zones cœur/adhésion/OEASC/
secteur) conservent leur géométrie d'origine (ref_geo.l_areas.geom, en
Lambert-93), simplement reprojetée en 4326 sans simplification.

Usage :
    flask fix-vm-lareas-simples-simplification [--force]
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
@with_appcontext
def fix_vm_lareas_simples_simplification_cmd(force):
    """Recrée ref_geo.vm_lareas_simples en limitant la simplification aux cadastres (id_type=332)."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )

    if not force:
        click.confirm(
            "Cette opération va recréer ref_geo.vm_lareas_simples "
            "(seules les géométries cadastre id_type=332 resteront simplifiées). "
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
        f"(simplification limitée aux cadastres, id_type={ID_TYPE_CADASTRE})"
    )
    db.session.execute(
        text(f"""
        CREATE MATERIALIZED VIEW ref_geo.vm_lareas_simples AS
        SELECT
            l.id_area, l.id_type,
            CASE
                WHEN l.id_type = {ID_TYPE_CADASTRE}
                    THEN ST_Transform(ST_SimplifyPreserveTopology(l.geom, 50), 4326)
                ELSE ST_Transform(l.geom, 4326)
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
