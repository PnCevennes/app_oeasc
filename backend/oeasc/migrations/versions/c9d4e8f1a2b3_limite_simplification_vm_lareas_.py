"""limite la simplification de vm_lareas_simples (cadastres 5m, autres 2m)

Revision ID: c9d4e8f1a2b3
Revises: 71ace03ca6a3
Create Date: 2026-09-16 00:00:00.000000

"""

from alembic import op

# revision identifiers, used by Alembic.
revision = "c9d4e8f1a2b3"
down_revision = "71ace03ca6a3"
branch_labels = None
depends_on = None

# id_type du cadastre (ref_geo.bib_areas_types), seul type dont la géométrie
# doit être simplifiée dans vm_lareas_simples.geom_4326.
ID_TYPE_CADASTRE = 332

# Tolérances ST_SimplifyPreserveTopology (en mètres, Lambert-93), validées
# visuellement via `flask fix-vm-lareas-simples-simplification --tolerance ... --other-tolerance ...`
CADASTRE_TOLERANCE = 5
OTHER_TOLERANCE = 2


def upgrade():
    op.execute("DROP MATERIALIZED VIEW IF EXISTS ref_geo.vm_lareas_simples")

    op.execute(f"""
        CREATE MATERIALIZED VIEW ref_geo.vm_lareas_simples AS
        SELECT
            l.id_area, l.id_type,
            CASE
                WHEN l.id_type = {ID_TYPE_CADASTRE}
                    THEN ST_Transform(ST_SimplifyPreserveTopology(l.geom, {CADASTRE_TOLERANCE}), 4326)
                ELSE ST_Transform(ST_SimplifyPreserveTopology(l.geom, {OTHER_TOLERANCE}), 4326)
            END AS geom_4326,
            l.area_code, l.area_name, l.area_name AS label,
            ROUND((ST_Area(l.geom) / 10000)::numeric, 3) AS surface_calculee,
            ROUND((ST_Area(l.geom) / 10000)::numeric, 3) AS surface_renseignee,
            COALESCE(l.source, 'OEASC') AS source,
            COALESCE(l.enable, TRUE) AS enable
        FROM ref_geo.l_areas l
        WITH NO DATA
    """)

    op.execute(
        "CREATE UNIQUE INDEX ux_vm_lareas_simples_id_area ON ref_geo.vm_lareas_simples (id_area)"
    )
    op.execute(
        "CREATE INDEX ix_vm_lareas_simples_geom_4326 ON ref_geo.vm_lareas_simples USING GIST (geom_4326)"
    )
    op.execute(
        "CREATE INDEX ix_vm_lareas_simples_id_type ON ref_geo.vm_lareas_simples (id_type)"
    )
    op.execute(
        "CREATE INDEX ix_vm_lareas_simples_area_code ON ref_geo.vm_lareas_simples (area_code)"
    )
    op.execute(
        "CREATE INDEX ix_vm_lareas_simples_source ON ref_geo.vm_lareas_simples (source)"
    )

    op.execute("REFRESH MATERIALIZED VIEW ref_geo.vm_lareas_simples")


def downgrade():
    op.execute("DROP MATERIALIZED VIEW IF EXISTS ref_geo.vm_lareas_simples")

    op.execute("""
        CREATE MATERIALIZED VIEW ref_geo.vm_lareas_simples AS
        SELECT
            l.id_area, l.id_type,
            ST_Transform(ST_SimplifyPreserveTopology(l.geom, 50), 4326) AS geom_4326,
            l.area_code, l.area_name, l.area_name AS label,
            ROUND((ST_Area(l.geom) / 10000)::numeric, 3) AS surface_calculee,
            ROUND((ST_Area(l.geom) / 10000)::numeric, 3) AS surface_renseignee,
            COALESCE(l.source, 'OEASC') AS source,
            COALESCE(l.enable, TRUE) AS enable
        FROM ref_geo.l_areas l
        WITH NO DATA
    """)

    op.execute(
        "CREATE UNIQUE INDEX ux_vm_lareas_simples_id_area ON ref_geo.vm_lareas_simples (id_area)"
    )
    op.execute(
        "CREATE INDEX ix_vm_lareas_simples_geom_4326 ON ref_geo.vm_lareas_simples USING GIST (geom_4326)"
    )
    op.execute(
        "CREATE INDEX ix_vm_lareas_simples_id_type ON ref_geo.vm_lareas_simples (id_type)"
    )
    op.execute(
        "CREATE INDEX ix_vm_lareas_simples_area_code ON ref_geo.vm_lareas_simples (area_code)"
    )
    op.execute(
        "CREATE INDEX ix_vm_lareas_simples_source ON ref_geo.vm_lareas_simples (source)"
    )

    op.execute("REFRESH MATERIALIZED VIEW ref_geo.vm_lareas_simples")
