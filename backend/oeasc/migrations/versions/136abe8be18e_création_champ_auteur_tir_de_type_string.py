"""création champ auteur tir de type string

Revision ID: 136abe8be18e
Revises: 96ebff8bac23
Create Date: 2026-02-11 16:05:15.991220

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '136abe8be18e'
down_revision = '96ebff8bac23'
branch_labels = None
depends_on = None


def upgrade():
    # creation du champ "auteur_tir_str" si il n'existe pas dans la table oeasc_chasse.t_realisations
    sql = """ALTER TABLE oeasc_chasse.t_realisations
        ADD COLUMN IF NOT EXISTS auteur_tir_str VARCHAR(255);"""
    op.execute(sql)

    # remplissage du champ "auteur_tir_str" avec les données de la table oeasc_chasse.t_personnes
    sql = """UPDATE oeasc_chasse.t_realisations r
        SET auteur_tir_str = p.nom_personne
        FROM oeasc_chasse.t_personnes p
        WHERE r.id_auteur_tir = p.id_personne;"""
    op.execute(sql)

    # creation du champ "auteur_constat_str" si il n'existe pas dans la table oeasc_chasse.t_realisations
    sql = """ALTER TABLE oeasc_chasse.t_realisations
        ADD COLUMN IF NOT EXISTS auteur_constat_str VARCHAR(255);"""
    op.execute(sql)

    # remplissage du champ "auteur_constat_str" avec les données de la table oeasc_chasse.t_personnes
    sql = """UPDATE oeasc_chasse.t_realisations r
        SET auteur_constat_str = p.nom_personne
        FROM oeasc_chasse.t_personnes p
        WHERE r.id_auteur_constat = p.id_personne;"""
    op.execute(sql)

def downgrade():

    # suppression du champ "auteur_tir_str" si il existe dans la table oeasc_chasse.t_realisations
    sql = """ALTER TABLE oeasc_chasse.t_realisations
        DROP COLUMN IF EXISTS auteur_tir_str;"""
    op.execute(sql)

    # suppression du champ "auteur_constat_str" si il existe dans la table oeasc_chasse.t_realisations
    sql = """ALTER TABLE oeasc_chasse.t_realisations
        DROP COLUMN IF EXISTS auteur_constat_str;"""
    op.execute(sql)
