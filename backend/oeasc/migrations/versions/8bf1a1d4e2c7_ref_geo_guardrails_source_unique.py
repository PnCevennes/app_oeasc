"""ref_geo guardrails source unique

Revision ID: 8bf1a1d4e2c7
Revises: 117bec8ed8d2
Create Date: 2026-06-01 12:00:00.000000

"""

from alembic import op

# revision identifiers, used by Alembic.
revision = "8bf1a1d4e2c7"
down_revision = "117bec8ed8d2"
branch_labels = None
depends_on = None


def upgrade():
    # Validate mandatory source tables.
    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1
                FROM information_schema.tables
                WHERE table_schema = 'ref_geo' AND table_name = 'l_areas'
            ) THEN
                RAISE EXCEPTION 'Table ref_geo.l_areas is required before applying this migration';
            END IF;

            IF NOT EXISTS (
                SELECT 1
                FROM information_schema.tables
                WHERE table_schema = 'ref_geo' AND table_name = 'bib_areas_types'
            ) THEN
                RAISE EXCEPTION 'Table ref_geo.bib_areas_types is required before applying this migration';
            END IF;
        END
        $$;
        """)

    # Ensure hierarchy table exists (non destructive).
    op.execute("""
        CREATE TABLE IF NOT EXISTS ref_geo.cor_hierarchie_area (
            id_area_enfant INTEGER NOT NULL,
            id_type_enfant INTEGER NOT NULL,
            id_area_parent INTEGER NOT NULL,
            id_type_parent INTEGER NOT NULL,
            PRIMARY KEY (id_area_enfant, id_type_enfant, id_area_parent, id_type_parent),
            FOREIGN KEY (id_area_enfant) REFERENCES ref_geo.l_areas(id_area),
            FOREIGN KEY (id_area_parent) REFERENCES ref_geo.l_areas(id_area)
        );
        """)

    # Ensure simplified materialized view exists.
    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1
                FROM pg_matviews
                WHERE schemaname = 'ref_geo' AND matviewname = 'vm_lareas_simples'
            ) THEN
                CREATE MATERIALIZED VIEW ref_geo.vm_lareas_simples AS
                SELECT
                    l.id_area AS id_area,
                    l.id_type AS id_type,
                    ST_Transform(ST_SimplifyPreserveTopology(l.geom, 50), 4326) AS geom_4326,
                    l.area_code AS area_code,
                    l.area_name AS area_name,
                    l.area_name AS label,
                    ROUND((ST_Area(l.geom) / 10000)::numeric, 3) AS surface_calculee,
                    ROUND((ST_Area(l.geom) / 10000)::numeric, 3) AS surface_renseignee,
                    COALESCE(l.source, 'OEASC') AS source,
                    COALESCE(l.enable, TRUE) AS enable
                FROM ref_geo.l_areas l
                WITH NO DATA;
            END IF;
        END
        $$;
        """)

    # Ensure indexes for runtime and future concurrent refresh.
    op.execute(
        "CREATE UNIQUE INDEX IF NOT EXISTS ux_vm_lareas_simples_id_area ON ref_geo.vm_lareas_simples (id_area);"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_vm_lareas_simples_geom_4326 ON ref_geo.vm_lareas_simples USING GIST (geom_4326);"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_vm_lareas_simples_id_type ON ref_geo.vm_lareas_simples (id_type);"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_vm_lareas_simples_area_code ON ref_geo.vm_lareas_simples (area_code);"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_vm_lareas_simples_source ON ref_geo.vm_lareas_simples (source);"
    )

    # Refresh view content to keep l_areas and vm_lareas_simples aligned.
    op.execute("REFRESH MATERIALIZED VIEW ref_geo.vm_lareas_simples;")

    # Non-blocking legacy object visibility for operators.
    op.execute("""
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1 FROM information_schema.tables
                WHERE table_schema = 'ref_geo' AND table_name IN ('li_areas', 'l_areas_simples')
            ) THEN
                RAISE NOTICE 'Legacy ref_geo tables detected (li_areas/l_areas_simples). Keep only for temporary compatibility.';
            END IF;

            IF EXISTS (
                SELECT 1 FROM pg_views
                WHERE schemaname = 'ref_geo' AND viewname IN ('vl_areas', 'vl_areas_simples')
            ) THEN
                RAISE NOTICE 'Legacy ref_geo views detected (vl_areas/vl_areas_simples). Keep only for temporary compatibility.';
            END IF;
        END
        $$;
        """)


def downgrade():
    # Intentionally non destructive: guardrail migration should not drop runtime objects.
    pass
