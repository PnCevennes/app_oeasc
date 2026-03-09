"""creation champs lieu_dit_txt, latitude, longitude dans t_realisation

Revision ID: 42abbaaa4dbb
Revises: e70bfbc2094b
Create Date: 2026-02-13 17:01:31.369981

"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "42abbaaa4dbb"
down_revision = "e70bfbc2094b"
branch_labels = None
depends_on = None


def upgrade():

    # ajout du champ lieu_tir_txt dans la table oeasc_chasse.t_realisations
    sql = """ALTER TABLE oeasc_chasse.t_realisations
        ADD COLUMN IF NOT EXISTS lieu_tir_txt VARCHAR(255);"""
    op.execute(sql)

    # remplissage du champ lieu_tir_txt avec les données de la table oeasc_chasse.t_lieux_tirs qui correspond à l'id_lieu_tir_synonyme de la table oeasc_chasse.t_realisations
    sql = """UPDATE oeasc_chasse.t_realisations r
        SET lieu_tir_txt = lt.nom_lieu_tir
        FROM oeasc_chasse.t_lieu_tirs lt, oeasc_chasse.t_lieu_tir_synonymes lts
        WHERE r.id_lieu_tir_synonyme = lts.id_lieu_tir_synonyme
        AND lts.id_lieu_tir = lt.id_lieu_tir;"""
    op.execute(sql)

    # ajout du champ latitude dans la table oeasc_chasse.t_realisations
    sql = """ALTER TABLE oeasc_chasse.t_realisations
        ADD COLUMN IF NOT EXISTS latitude DOUBLE PRECISION;"""
    op.execute(sql)

    # ajout du champ longitude dans la table oeasc_chasse.t_realisations
    sql = """ALTER TABLE oeasc_chasse.t_realisations
        ADD COLUMN IF NOT EXISTS longitude DOUBLE PRECISION;"""
    op.execute(sql)


def downgrade():
    # suppression du champ lieu_tir_txt dans la table oeasc_chasse.t_realisations
    sql = """ALTER TABLE oeasc_chasse.t_realisations
        DROP COLUMN IF EXISTS lieu_tir_txt;"""
    op.execute(sql)

    # suppression du champ latitude dans la table oeasc_chasse.t_realisations
    sql = """ALTER TABLE oeasc_chasse.t_realisations
        DROP COLUMN IF EXISTS latitude;"""
    op.execute(sql)

    # suppression du champ longitude dans la table oeasc_chasse.t_realisations
    sql = """ALTER TABLE oeasc_chasse.t_realisations
        DROP COLUMN IF EXISTS longitude;"""
    op.execute(sql)
