"""creation table hierarchie area

Cette table permet de connaitre quelles areas sont enfants d'une autre area. Par exemple quelles areas 
sont contenues dans telle commune ou dans tel foret. Elle permet donc de retrouver le parents d'une area
Utilisés pour naviguer dans les cartes de creations et modifications de declarations

Revision ID: 96ebff8bac23
Revises: 0a44db773490
Create Date: 2025-06-13 14:50:07.758374

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '96ebff8bac23'
down_revision = '0a44db773490'
branch_labels = None
depends_on = None


def upgrade():

    sql_creation_table = """
        
        CREATE TABLE ref_geo.cor_hierarchie_area (
                id_area_enfant INTEGER NOT NULL,
                id_type_enfant INTEGER NOT NULL,
                id_area_parent INTEGER NOT NULL,
                id_type_parent INTEGER NOT NULL,
                PRIMARY KEY (id_area_enfant, id_type_enfant, id_area_parent, id_type_parent),
                FOREIGN KEY (id_area_enfant) REFERENCES ref_geo.l_areas(id_area), 
                FOREIGN KEY (id_area_enfant) REFERENCES ref_geo.l_areas(id_area) 
        );
        CREATE INDEX cor_hierarchie_area_id_type_enfant_idx ON ref_geo.cor_hierarchie_area (id_type_enfant,id_type_parent);
        
        """
    op.execute(sql_creation_table)

    sql_insertions_communes = """
        with c as (
            select substring(la.area_code, 1, 5) as c, la.*
            from ref_geo.l_areas la 
            where la.id_type = 333
        ), com as (
            select unnest(coc.old_area_codes) as old_area_codes, coc.area_code
            from ref_geo.cor_old_communes coc 
            union
            select la.area_code, la.area_code
            from ref_geo.l_areas la 
            where la.id_type = 327
        )
        INSERT INTO ref_geo.cor_hierarchie_area (id_area_enfant, id_type_enfant, id_area_parent, id_type_parent)
        select c.id_area as id_area_enfant, c.id_type as id_type_enfant, la.id_area as id_area_parent, la.id_type as id_type_parent
        from c 
        left join com 
        on com.old_area_codes = c.c
        join ref_geo.l_areas la 
        on (la.area_code = com.area_code and la.id_type = 327);
    """
    op.execute(sql_insertions_communes)



    sql_insertion_sections_cadastre = """
    with
        section as (
            select id_area, id_type, area_code
            from ref_geo.l_areas la
            join ref_geo.cor_hierarchie_area cha
            on la.id_area = cha.id_area_enfant
            where la.id_type = 333
        ),
        cadastre as (
            select id_area, area_code, id_type, split_part(la.area_code, '-', 1) || '-' ||  split_part(la.area_code, '-', 2) as code_section
            from ref_geo.l_areas la
            where la.id_type = 332
        )
    INSERT INTO ref_geo.cor_hierarchie_area (id_area_enfant, id_type_enfant, id_area_parent, id_type_parent)
    select cadastre.id_area as id_area_enfant, cadastre.id_type as id_type_enfant, section.id_area as id_area_parent, section.id_type as id_type_parent
    from cadastre
    join section
    on (cadastre.code_section = section.area_code );
    """

    op.execute(sql_insertion_sections_cadastre)

    sql_insertion_dgd = """
    INSERT INTO ref_geo.cor_hierarchie_area (id_area_enfant, id_type_enfant, id_area_parent, id_type_parent)
    select distinct lac.id_area as id_area_enfant ,lac.id_type as id_type_enfant, lad.id_area as id_area_parent, lad.id_type as id_type_parent
    from oeasc_forets.cor_dgd_cadastre cdc 
    join ref_geo.l_areas lad 
    on lad.area_code  = cdc.area_code_dgd
    join ref_geo.l_areas lac 
    on lac.area_code  = cdc.area_code_cadastre """
    op.execute(sql_insertion_dgd)


    sql_insertion_onf = """
    INSERT INTO ref_geo.cor_hierarchie_area (id_area_enfant, id_type_enfant, id_area_parent, id_type_parent)
    with foret_onf as (
        select *
            from ref_geo.l_areas la 
            where la.id_type =328
        )
    select la.id_area as id_area_enfant, la.id_type as id_type_enfant, f.id_area as id_area_parent, f.id_type  as id_type_parent
    from ref_geo.l_areas la 
    join foret_onf f
    on la.area_code ilike f.area_code || '-%'
    and la.id_type = 329"""
    op.execute(sql_insertion_onf)


    sql_insertion_unite_gestion_onf = """
    INSERT INTO ref_geo.cor_hierarchie_area (id_area_enfant, id_type_enfant, id_area_parent, id_type_parent)
    with parcelle_onf as (
        select *
            from ref_geo.l_areas la 
            where la.id_type =329
        )    
    select la.id_area as id_area_enfant, la.id_type as id_type_enfant, f.id_area as id_area_parent, f.id_type  as id_type_parent
        from ref_geo.l_areas la 
        join parcelle_onf f
        on la.area_code ilike f.area_code || '-%'
        and la.id_type = 330"""
    op.execute(sql_insertion_unite_gestion_onf)



def downgrade():
    op.execute("DROP TABLE IF EXISTS ref_geo.cor_hierarchie_area CASCADE;")

    pass
