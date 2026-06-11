"""modification table foret

Revision ID: 3e5c666af390
Revises: 8bf1a1d4e2c7
Create Date: 2026-06-08 14:06:56.041320

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3e5c666af390'
down_revision = '8bf1a1d4e2c7'
branch_labels = None
depends_on = None


def upgrade():
    # ajout de la colonne id_area dans la table foret
    op.add_column('t_forets', sa.Column('id_area', sa.Integer(), nullable=True), schema='oeasc_forets')
    # ajout des colonnes d'informations sur le propriétaire de la forêt
    op.add_column('t_forets', sa.Column('nom_proprietaire', sa.String(length=255), nullable=True), schema='oeasc_forets')
    op.add_column('t_forets', sa.Column('adresse_proprietaire', sa.String(length=255), nullable=True), schema='oeasc_forets')
    op.add_column('t_forets', sa.Column('cp_proprietaire', sa.String(length=5), nullable=True), schema='oeasc_forets')
    op.add_column('t_forets', sa.Column('commune_proprietaire', sa.String(length=255), nullable=True), schema='oeasc_forets')
    op.add_column('t_forets', sa.Column('email_proprietaire', sa.String(length=255), nullable=True), schema='oeasc_forets')
    op.add_column('t_forets', sa.Column('tel_proprietaire', sa.String(length=255), nullable=True), schema='oeasc_forets')
    op.add_column('t_forets', sa.Column('id_nomenclature_proprietaire_type', sa.Integer(), nullable=True), schema='oeasc_forets')
    # ajout clé étrangère vers la table ref_nomenclatures.t_nomenclatures pour le type de propriétaire
    op.create_foreign_key(
        'fk_foret_id_nomenclature_proprietaire_type',
        't_forets', 't_nomenclatures',
        ['id_nomenclature_proprietaire_type'], ['id_nomenclature'],
        source_schema='oeasc_forets', referent_schema='ref_nomenclatures'
    )

    op.add_column('t_forets', sa.Column('id_declarant', sa.Integer(), nullable=True), schema='oeasc_forets')
    # ajout clé étrangère vers la table utilisateurs.t_roles(id_role) pour le déclarant
    op.create_foreign_key(
        'fk_foret_id_declarant',
        't_forets', 't_roles',
        ['id_declarant'], ['id_role'],
        source_schema='oeasc_forets', referent_schema='utilisateurs'
    )
    
    # on remplit les colonnes d'informations sur les propriétaires à partir de la table t_proprietaires et en fonction du id_proprietaire dans t_forets qui correspond au id_proprietaire dans t_proprietaires
    op.execute("""
        UPDATE oeasc_forets.t_forets f
        SET nom_proprietaire = p.nom_proprietaire,
            adresse_proprietaire = p.adresse,
            cp_proprietaire = p.s_code_postal,
            commune_proprietaire = p.s_commune_proprietaire,
            email_proprietaire = p.email,
            tel_proprietaire = p.telephone,
            id_nomenclature_proprietaire_type = p.id_nomenclature_proprietaire_type,
            id_declarant = p.id_declarant
               
        FROM oeasc_forets.t_proprietaires p
        WHERE f.id_proprietaire = p.id_proprietaire
    """)
    


    # pour les foret où b_document = false:
    # tout d'abord on créé un nouveau type d'area dans ref_geo.bib_areas_types avec type_name = "Forêt non documentée", type_code = "OEASC_FORET_PRIVE", ref_name = "OEASC"
    # type_desc = "Forets privées non documentées", ref_version = "2026"
    op.execute("""
        INSERT INTO ref_geo.bib_areas_types (type_name, type_code, ref_name, type_desc, ref_version)
        VALUES ('Forêt non documentée', 'OEASC_FORET_PRIVE', 'OEASC', 'Forets privées non documentées', '2026')
    """)

    # pour créer les foret le fera en python dans un script à part qui fera le lien entre les données de la table foret et les données de la table oeasc_foret.cor_areas_foret pour récupérer les id_area correspondants et remplir les autres champs d'informations sur le propriétaire de la forêt
    # trop de complexité pour le faire en SQL directement dans cette migration



def downgrade():

    # suppression des clés étrangères
    op.drop_constraint('fk_foret_id_nomenclature_proprietaire_type', 't_forets', type_='foreignkey', schema='oeasc_forets')
    op.drop_constraint('fk_foret_id_declarant', 't_forets', type_='foreignkey', schema='oeasc_forets')

    op.drop_column('t_forets', 'id_area', schema='oeasc_forets')
    op.drop_column('t_forets', 'nom_proprietaire', schema='oeasc_forets')
    op.drop_column('t_forets', 'adresse_proprietaire', schema='oeasc_forets')
    op.drop_column('t_forets', 'cp_proprietaire', schema='oeasc_forets')
    op.drop_column('t_forets', 'commune_proprietaire', schema='oeasc_forets')
    op.drop_column('t_forets', 'email_proprietaire', schema='oeasc_forets')
    op.drop_column('t_forets', 'tel_proprietaire', schema='oeasc_forets')
    op.drop_column('t_forets', 'id_nomenclature_proprietaire_type', schema='oeasc_forets')
    op.drop_column('t_forets', 'id_declarant', schema='oeasc_forets')


    # on supprimera le type d'area "Forêt non documentée" dans ref_geo.bib_areas_types manuellement après la migration de downgrade
    op.execute("""
        DELETE FROM ref_geo.bib_areas_types
        WHERE type_code = 'OEASC_FORET_PRIVE'
    """) 