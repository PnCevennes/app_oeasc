"""creation table area_intersect

Revision ID: 117bec8ed8d2
Revises: d15f8142f4ed
Create Date: 2026-05-22 09:25:34.519550

"""
from alembic import op
import sqlalchemy as sa
import geoalchemy2


revision = '117bec8ed8d2'
down_revision = 'd15f8142f4ed'
branch_labels = None
depends_on = None


def upgrade():
    op.drop_table('li_grids', schema='ref_geo', if_exists=True)
    op.drop_table('dem', schema='ref_geo', if_exists=True)
    op.drop_table('dem_vector', schema='ref_geo', if_exists=True)
    op.drop_table('li_municipalities', schema='ref_geo', if_exists=True)
    op.execute("DROP VIEW IF EXISTS ref_geo.vl_areas")
    op.execute("""
        DO $$ BEGIN
            IF EXISTS (SELECT 1 FROM pg_matviews WHERE schemaname = 'ref_geo' AND matviewname = 'vl_areas_simples') THEN
                DROP MATERIALIZED VIEW ref_geo.vl_areas_simples;
            ELSIF EXISTS (SELECT 1 FROM pg_views WHERE schemaname = 'ref_geo' AND viewname = 'vl_areas_simples') THEN
                DROP VIEW ref_geo.vl_areas_simples;
            END IF;
        END $$;
    """)
    op.drop_table('l_areas_simples', schema='ref_geo', if_exists=True)
    op.drop_table('li_areas', schema='ref_geo', if_exists=True)

    op.execute("""
        CREATE TABLE IF NOT EXISTS ref_geo.cor_area_intersect (
            id SERIAL PRIMARY KEY,
            id_parcelle INTEGER NOT NULL,
            id_type_parcelle INTEGER,
            id_section_cadastrale INTEGER,
            id_commune INTEGER,
            id_foret_dgd INTEGER,
            id_foret_onf INTEGER,
            id_parcelle_onf INTEGER,
            id_secteur INTEGER,
            in_coeur BOOLEAN NOT NULL DEFAULT TRUE,
            in_aire_adhesion_pnc BOOLEAN NOT NULL DEFAULT TRUE,
            in_oeasc BOOLEAN NOT NULL DEFAULT TRUE
        )
    """)
    op.execute("CREATE INDEX IF NOT EXISTS ix_cor_area_intersect_id_parcelle ON ref_geo.cor_area_intersect (id_parcelle)")

    for constraint, column in [
        ('fk_cor_area_intersect_id_parcelle', 'id_parcelle'),
        ('fk_cor_area_intersect_id_section_cadastrale', 'id_section_cadastrale'),
        ('fk_cor_area_intersect_id_commune', 'id_commune'),
        ('fk_cor_area_intersect_id_foret_dgd', 'id_foret_dgd'),
        ('fk_cor_area_intersect_id_foret_onf', 'id_foret_onf'),
        ('fk_cor_area_intersect_id_parcelle_onf', 'id_parcelle_onf'),
        ('fk_cor_area_intersect_id_secteur', 'id_secteur'),
    ]:
        op.execute(f"""
            DO $$ BEGIN
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.table_constraints
                    WHERE constraint_schema = 'ref_geo' AND constraint_name = '{constraint}'
                ) THEN
                    ALTER TABLE ref_geo.cor_area_intersect
                    ADD CONSTRAINT {constraint}
                    FOREIGN KEY ({column}) REFERENCES ref_geo.l_areas(id_area) ON DELETE CASCADE;
                END IF;
            END $$;
        """)

    op.execute("""
        DO $$ BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM pg_matviews
                WHERE schemaname = 'ref_geo' AND matviewname = 'vm_lareas_simples'
            ) THEN
                CREATE MATERIALIZED VIEW ref_geo.vm_lareas_simples AS
                SELECT
                    l.id_area,
                    l.id_type,
                    ST_Transform(ST_SimplifyPreserveTopology(l.geom, 50), 4326) AS geom_4326,
                    l.area_code,
                    l.area_name,
                    l.area_name AS label,
                    ROUND((ST_Area(l.geom)/10000)::numeric, 3) AS surface_calculee,
                    ROUND((ST_Area(l.geom)/10000)::numeric, 3) AS surface_renseignee,
                    COALESCE(l.source, 'OEASC') AS source,
                    COALESCE(l.enable, TRUE) AS enable
                FROM ref_geo.l_areas l
                WITH NO DATA;
            END IF;
        END $$;
    """)
    op.execute("REFRESH MATERIALIZED VIEW ref_geo.vm_lareas_simples")
    op.execute("CREATE INDEX IF NOT EXISTS ix_vm_lareas_simples_id_area ON ref_geo.vm_lareas_simples (id_area)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_vm_lareas_simples_geom_4326 ON ref_geo.vm_lareas_simples USING GIST (geom_4326)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_vm_lareas_simples_area_code ON ref_geo.vm_lareas_simples (area_code)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_vm_lareas_simples_id_type ON ref_geo.vm_lareas_simples (id_type)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_vm_lareas_simples_source ON ref_geo.vm_lareas_simples (source)")


def downgrade():
    op.execute("DROP TABLE IF EXISTS ref_geo.cor_area_intersect CASCADE")

    op.execute("""
        DO $$ BEGIN
            IF EXISTS (SELECT 1 FROM pg_matviews WHERE schemaname = 'ref_geo' AND matviewname = 'vm_lareas_simples') THEN
                DROP MATERIALIZED VIEW ref_geo.vm_lareas_simples;
            ELSIF EXISTS (SELECT 1 FROM pg_views WHERE schemaname = 'ref_geo' AND viewname = 'vm_lareas_simples') THEN
                DROP VIEW ref_geo.vm_lareas_simples;
            END IF;
        END $$;
    """)
    op.execute("""
        DO $$ BEGIN
            IF EXISTS (SELECT 1 FROM pg_matviews WHERE schemaname = 'ref_geo' AND matviewname = 'vl_areas_simples') THEN
                DROP MATERIALIZED VIEW ref_geo.vl_areas_simples;
            ELSIF EXISTS (SELECT 1 FROM pg_views WHERE schemaname = 'ref_geo' AND viewname = 'vl_areas_simples') THEN
                DROP VIEW ref_geo.vl_areas_simples;
            END IF;
        END $$;
    """)
    op.execute("DROP VIEW IF EXISTS ref_geo.vl_areas")

    op.execute("""
        CREATE TABLE IF NOT EXISTS ref_geo.li_areas (
            id_area INTEGER PRIMARY KEY,
            id_type INTEGER NOT NULL,
            area_code VARCHAR(25),
            label VARCHAR(250),
            area_name VARCHAR(250),
            surface_calculee FLOAT,
            surface_renseignee FLOAT,
            source VARCHAR(250),
            enable BOOLEAN NOT NULL DEFAULT TRUE,
            geom geometry(MULTIPOLYGON, 4326)
        )
    """)
    op.execute("""
        CREATE TABLE IF NOT EXISTS ref_geo.l_areas_simples (
            id_area INTEGER PRIMARY KEY,
            id_type INTEGER NOT NULL,
            area_name VARCHAR(250),
            area_code VARCHAR(25),
            source VARCHAR(250),
            tolerance FLOAT,
            geom_4326 geometry(MULTIPOLYGON, 4326)
        )
    """)
    op.execute("""
        CREATE TABLE IF NOT EXISTS ref_geo.li_municipalities (
            id_municipality INTEGER PRIMARY KEY,
            id_area INTEGER NOT NULL,
            status VARCHAR(50),
            insee_com VARCHAR(5),
            nom_com VARCHAR(50),
            insee_arr VARCHAR(2),
            nom_dep VARCHAR(30),
            insee_dep VARCHAR(3),
            nom_reg VARCHAR(35),
            insee_reg VARCHAR(2),
            code_epci VARCHAR(9),
            plani_precision FLOAT,
            siren_code VARCHAR(10),
            canton VARCHAR(200),
            population INTEGER,
            multican VARCHAR(3),
            cc_nom VARCHAR(250),
            cc_siren INTEGER,
            cc_nature VARCHAR(5),
            cc_date_creation DATE,
            cc_date_effet DATE,
            insee_commune_nouvelle VARCHAR(50),
            meta_create_date TIMESTAMP,
            meta_update_date TIMESTAMP
        )
    """)
    op.execute("""
        CREATE TABLE IF NOT EXISTS ref_geo.li_grids (
            id_grid INTEGER PRIMARY KEY,
            id_area INTEGER NOT NULL,
            cymin INTEGER,
            cymax VARCHAR,
            cxmin INTEGER,
            cxmax INTEGER
        )
    """)
    op.execute("""
        CREATE TABLE IF NOT EXISTS ref_geo.dem (
            rid INTEGER PRIMARY KEY,
            rast raster NOT NULL
        )
    """)
    op.execute("""
        CREATE TABLE IF NOT EXISTS ref_geo.dem_vector (
            gid INTEGER PRIMARY KEY,
            geom geometry(POLYGON, 4326),
            val FLOAT
        )
    """)

    op.execute("""CREATE OR REPLACE VIEW ref_geo.vl_areas_simples
        AS SELECT li.id_area,
            li.id_type,
            ls.geom_4326,
            li.area_code,
            li.label,
            li.area_name,
            ST_Area(l.geom) AS surface_calculee,
            li.surface_renseignee,
            li.source,
            li.enable
        FROM ref_geo.l_areas_simples ls,
            ref_geo.li_areas li,
            ref_geo.l_areas l
        WHERE ls.id_area = li.id_area
            AND l.id_area = li.id_area;""")

    op.execute("""CREATE OR REPLACE VIEW ref_geo.vl_areas
        AS SELECT li.id_area,
            li.id_type,
            l.geom_4326,
            l.geom,
            li.area_code,
            li.label,
            li.area_name,
            li.surface_calculee,
            li.surface_renseignee,
            li.source,
            li.enable
        FROM ref_geo.l_areas l,
            ref_geo.li_areas li
        WHERE l.id_area = li.id_area;""")
