"""creation table area_intersect

Revision ID: 117bec8ed8d2
Revises: d15f8142f4ed
Create Date: 2026-05-22 09:25:34.519550

"""
from alembic import op
import sqlalchemy as sa
import geoalchemy2


# revision identifiers, used by Alembic.
revision = '117bec8ed8d2'
down_revision = 'd15f8142f4ed'
branch_labels = None
depends_on = None


def upgrade():
    

    #suppression de la table li_grids si elle existe
    op.drop_table('li_grids', schema='ref_geo', if_exists=True)
    # suppression de la table dem si elle existe
    op.drop_table('dem', schema='ref_geo', if_exists=True)
    # suppression de la table dem_vector si elle existe
    op.drop_table('dem_vector', schema='ref_geo', if_exists=True)
    # suppression de la table li_municipalities si elle existe
    op.drop_table('li_municipalities', schema='ref_geo', if_exists=True)
    # suppression de la vue vl_areas si elle existe
    op.execute("DROP VIEW IF EXISTS ref_geo.vl_areas")
    # suppression de vl_areas_simples (vue simple ou matérialisée selon ce qui existe)
    op.execute("""
        DO $$ BEGIN
            IF EXISTS (SELECT 1 FROM pg_matviews WHERE schemaname = 'ref_geo' AND matviewname = 'vl_areas_simples') THEN
                DROP MATERIALIZED VIEW ref_geo.vl_areas_simples;
            ELSIF EXISTS (SELECT 1 FROM pg_views WHERE schemaname = 'ref_geo' AND viewname = 'vl_areas_simples') THEN
                DROP VIEW ref_geo.vl_areas_simples;
            END IF;
        END $$;
    """)
    # suppression de la table l_areas_simples si elle existe
    op.drop_table('l_areas_simples', schema='ref_geo', if_exists=True)

    # suppression de la table li_areas si elle existe
    op.drop_table('li_areas', schema='ref_geo', if_exists=True)


    # creation de la table cor_area_intersect dans le shema ref_geo
    op.create_table(
        'cor_area_intersect',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('id_parcelle', sa.Integer, nullable=False, index=True, comment="id de la parcelle cadastrale ou de l'unité de gestion ONF"), # FK vers l_areas
        sa.Column('id_type_parcelle', sa.Integer, nullable=True, comment="332 pour parcelle cadastrale, 329 pour parcelle onf"), # 332 pour parcelle cadastrale, 329 pour parcelle onf
        sa.Column('id_section_cadastrale', sa.Integer, nullable=True),
        sa.Column('id_commune', sa.Integer, nullable=True),
        sa.Column('id_foret_dgd', sa.Integer, nullable=True),
        sa.Column('id_foret_onf', sa.Integer, nullable=True),
        sa.Column('id_parcelle_onf', sa.Integer, nullable=True),
        sa.Column('id_secteur', sa.Integer, nullable=True),
        sa.Column('in_coeur', sa.Boolean, nullable=False, default=True),
        sa.Column('in_aire_adhesion_pnc', sa.Boolean, nullable=False, default=True),
        sa.Column('in_oeasc', sa.Boolean, nullable=False, default=True),
        schema='ref_geo'
    )
    # création des clé étrangères
    op.create_foreign_key(
        'fk_cor_area_intersect_id_parcelle',
        'cor_area_intersect', 'l_areas',
        ['id_parcelle'], ['id_area'],
        source_schema='ref_geo', referent_schema='ref_geo',
        ondelete='CASCADE'
    )
    op.create_foreign_key(
        'fk_cor_area_intersect_id_section_cadastrale',
        'cor_area_intersect', 'l_areas',
        ['id_section_cadastrale'], ['id_area'],
        source_schema='ref_geo', referent_schema='ref_geo',
        ondelete='CASCADE'
    )
    op.create_foreign_key(
        'fk_cor_area_intersect_id_commune',
        'cor_area_intersect', 'l_areas',
        ['id_commune'], ['id_area'],
        source_schema='ref_geo', referent_schema='ref_geo',
        ondelete='CASCADE'
    )
    op.create_foreign_key(
        'fk_cor_area_intersect_id_foret_dgd',
        'cor_area_intersect', 'l_areas',
        ['id_foret_dgd'], ['id_area'],
        source_schema='ref_geo', referent_schema='ref_geo',
        ondelete='CASCADE'
    )
    op.create_foreign_key(
        'fk_cor_area_intersect_id_foret_onf',
        'cor_area_intersect', 'l_areas',
        ['id_foret_onf'], ['id_area'],
        source_schema='ref_geo', referent_schema='ref_geo',
        ondelete='CASCADE'
    )
    op.create_foreign_key(
        'fk_cor_area_intersect_id_parcelle_onf',
        'cor_area_intersect', 'l_areas',
        ['id_parcelle_onf'], ['id_area'],
        source_schema='ref_geo', referent_schema='ref_geo',
        ondelete='CASCADE'
    )
    op.create_foreign_key(
        'fk_cor_area_intersect_id_secteur',
        'cor_area_intersect', 'l_areas',
        ['id_secteur'], ['id_area'],
        source_schema='ref_geo', referent_schema='ref_geo',
        ondelete='CASCADE'
    )


    # création d'une vue matérialisée de l_areas avec les géométries simplifiées (colonne geom_4326)
    op.execute("""CREATE MATERIALIZED VIEW ref_geo.vm_lareas_simples
        AS SELECT 
            l.id_area AS id_area,
            l.id_type AS id_type,
            ST_Transform(ST_SimplifyPreserveTopology(l.geom, 50), 4326) AS geom_4326,
            l.area_code AS area_code,
            l.area_name AS area_name,
            l.area_name AS label,
            ROUND((ST_Area(l.geom)/10000)::numeric, 3) AS surface_calculee,
            ROUND((ST_Area(l.geom)/10000)::numeric, 3) AS surface_renseignee,
            COALESCE(l.source, 'OEASC') AS source,
            COALESCE(l.enable, TRUE) AS enable
        FROM ref_geo.l_areas l
        WITH NO DATA;""")
    op.execute("REFRESH MATERIALIZED VIEW ref_geo.vm_lareas_simples;")

    # id_area est une clé étrangère vers l_areas, on ajoute un index pour optimiser les jointures
    op.execute("CREATE INDEX IF NOT EXISTS ix_vm_lareas_simples_id_area ON ref_geo.vm_lareas_simples (id_area);")
    

    # création d'un index sur la colonne de géométrie geom_4326
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_vm_lareas_simples_geom_4326 ON ref_geo.vm_lareas_simples USING GIST (geom_4326);"
    )
    
    # création d'un index sur la colonne area_code
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_vm_lareas_simples_area_code ON ref_geo.vm_lareas_simples (area_code);"

    )
    # création d'un index sur la colonne id_type
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_vm_lareas_simples_id_type ON ref_geo.vm_lareas_simples (id_type);"
    )

    # creation d'un index sur la colonne source
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_vm_lareas_simples_source ON ref_geo.vm_lareas_simples (source);"
    )





def downgrade():

    op.drop_table('cor_area_intersect', schema='ref_geo')

    # suppression de vl_areas_simples (vue simple ou matérialisée selon ce qui existe)
    op.execute("""
        DO $$ BEGIN
            IF EXISTS (SELECT 1 FROM pg_matviews WHERE schemaname = 'ref_geo' AND matviewname = 'vm_lareas_simples') THEN
                DROP MATERIALIZED VIEW ref_geo.vm_lareas_simples;
            ELSIF EXISTS (SELECT 1 FROM pg_views WHERE schemaname = 'ref_geo' AND viewname = 'vm_lareas_simples') THEN
                DROP VIEW ref_geo.vm_lareas_simples;
            END IF;
        END $$;
    """)
    # suppression de vl_areas_simples (vue simple ou matérialisée selon ce qui existe)
    op.execute("""
        DO $$ BEGIN
            IF EXISTS (SELECT 1 FROM pg_matviews WHERE schemaname = 'ref_geo' AND matviewname = 'vl_areas_simples') THEN
                DROP MATERIALIZED VIEW ref_geo.vl_areas_simples;
            ELSIF EXISTS (SELECT 1 FROM pg_views WHERE schemaname = 'ref_geo' AND viewname = 'vl_areas_simples') THEN
                DROP VIEW ref_geo.vl_areas_simples;
            END IF;
        END $$;
    """)
    # suppression de la vue vl_areas
    op.execute("DROP VIEW IF EXISTS ref_geo.vl_areas")

    # Recréer les tables dans l'ordre inverse des dépendances FK
    # création de la table li_areas dans le schema ref_geo (AVANT l_areas_simples et li_municipalities)
    op.create_table(
        'li_areas',
        sa.Column('id_area', sa.Integer, primary_key=True),
        sa.Column('id_type', sa.Integer, nullable=False),
        sa.Column('area_code', sa.VARCHAR(25), nullable=True),
        sa.Column('label', sa.VARCHAR(250), nullable=True),
        sa.Column('area_name', sa.VARCHAR(250), nullable=True),
        sa.Column('surface_calculee', sa.Float, nullable=True),
        sa.Column('surface_renseignee', sa.Float, nullable=True),
        sa.Column('source', sa.VARCHAR(250), nullable=True),
        sa.Column('enable', sa.Boolean, nullable=False, default=True),
        sa.Column('geom', geoalchemy2.Geometry(geometry_type='MULTIPOLYGON', srid=4326), nullable=True),
        schema='ref_geo'
    )

    # creation de la table l_areas_simples dans le schema ref_geo
    op.create_table(
        'l_areas_simples',
        sa.Column('id_area', sa.Integer, primary_key=True),
        sa.Column('id_type', sa.Integer, nullable=False),
        sa.Column('area_name', sa.VARCHAR(250), nullable=True),
        sa.Column('area_code', sa.VARCHAR(25), nullable=True),
        sa.Column('source', sa.VARCHAR(250), nullable=True),
        sa.Column('tolerance', sa.Float, nullable=True),
        sa.Column('geom_4326', geoalchemy2.Geometry(geometry_type='MULTIPOLYGON', srid=4326), nullable=True),
        schema='ref_geo'
    )

    # creation de la table li_municipalities dans le schema ref_geo
    op.create_table(
        'li_municipalities',
        sa.Column('id_municipality', sa.Integer, primary_key=True),
        sa.Column('id_area', sa.Integer, nullable=False),
        sa.Column('status', sa.VARCHAR(50), nullable=True),
        sa.Column('insee_com', sa.VARCHAR(5), nullable=True),
        sa.Column('nom_com', sa.VARCHAR(50), nullable=True),
        sa.Column('insee_arr', sa.VARCHAR(2), nullable=True),
        sa.Column('nom_dep', sa.VARCHAR(30), nullable=True),
        sa.Column('insee_dep', sa.VARCHAR(3), nullable=True),
        sa.Column('nom_reg', sa.VARCHAR(35), nullable=True),
        sa.Column('insee_reg', sa.VARCHAR(2), nullable=True),
        sa.Column('code_epci', sa.VARCHAR(9), nullable=True),
        sa.Column('plani_precision', sa.Float, nullable=True),
        sa.Column('siren_code', sa.VARCHAR(10), nullable=True),
        sa.Column('canton', sa.VARCHAR(200), nullable=True),
        sa.Column('population', sa.Integer, nullable=True),
        sa.Column('multican', sa.VARCHAR(3), nullable=True),
        sa.Column('cc_nom', sa.VARCHAR(250), nullable=True),
        sa.Column('cc_siren', sa.Integer, nullable=True),
        sa.Column('cc_nature', sa.VARCHAR(5), nullable=True),
        sa.Column('cc_date_creation', sa.Date, nullable=True),
        sa.Column('cc_date_effet', sa.Date, nullable=True),
        sa.Column('insee_commune_nouvelle', sa.VARCHAR(50), nullable=True),
        sa.Column('meta_create_date', sa.DateTime, nullable=True),
        sa.Column('meta_update_date', sa.DateTime, nullable=True),
        schema='ref_geo'
    )

    # creation de la table li_grids dans le schema ref_geo
    op.create_table(
        'li_grids',
        sa.Column('id_grid', sa.Integer, primary_key=True),
        sa.Column('id_area', sa.Integer, nullable=False),
        sa.Column('cymin', sa.Integer, nullable=True),
        sa.Column('cymax', sa.String, nullable=True),
        sa.Column('cxmin', sa.Integer, nullable=True),
        sa.Column('cxmax', sa.Integer, nullable=True), 
        schema='ref_geo'
    )

    # creation de la table dem dans le schema ref_geo
    op.create_table(
        'dem',
        sa.Column('rid', sa.Integer, primary_key=True),
        sa.Column('rast', geoalchemy2.Raster, nullable=False),
        schema='ref_geo'
    )

    # creation de la table dem_vector dans le schema ref_geo
    op.create_table(
        'dem_vector',
        sa.Column('gid', sa.Integer, primary_key=True),
        sa.Column('geom', geoalchemy2.Geometry(geometry_type='POLYGON', srid=4326), nullable=True),
        sa.Column('val', sa.Float, nullable=True),
        schema='ref_geo'
    )




    # création de la vue vl_areas_simples dans le schema ref_geo
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
    
    # création de la vue vl_areas dans le schema ref_geo
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
    

    # suppression de vl_areas_simples (vue simple ou matérialisée selon ce qui existe)
    op.execute("""
        DO $$ BEGIN
            IF EXISTS (SELECT 1 FROM pg_matviews WHERE schemaname = 'ref_geo' AND matviewname = 'vl_areas_simples') THEN
                DROP MATERIALIZED VIEW ref_geo.vl_areas_simples;
            ELSIF EXISTS (SELECT 1 FROM pg_views WHERE schemaname = 'ref_geo' AND viewname = 'vl_areas_simples') THEN
                DROP VIEW ref_geo.vl_areas_simples;
            END IF;
        END $$;
    """)
