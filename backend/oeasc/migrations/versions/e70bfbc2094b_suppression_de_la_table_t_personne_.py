"""suppression de la table t_personne: attention après git auteur_tir en str

Revision ID: e70bfbc2094b
Revises: 136abe8be18e
Create Date: 2026-02-11 16:20:39.926129

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e70bfbc2094b'
down_revision = '136abe8be18e'
branch_labels = None
depends_on = None


def upgrade():
    
    # suppression de la clé étrangère id_auteur_tir dans la table oeasc_chasse.t_realisations
    sql = """ALTER TABLE oeasc_chasse.t_realisations
        DROP CONSTRAINT IF EXISTS fk_t_realisations_t_personne_tirs CASCADE;"""
    op.execute(sql)

    # suppression de la clé étrangère id_auteur_constat dans la table oeasc_chasse.t_realisations
    sql = """ALTER TABLE oeasc_chasse.t_realisations
        DROP CONSTRAINT IF EXISTS fk_t_realisations_t_personne_constats;"""
    op.execute(sql)

    # suppression de la clé étrangère id_auteur_constat dans la table oeasc_chasse.t_realisations
    sql = """ALTER TABLE oeasc_chasse.t_realisations
        DROP CONSTRAINT IF EXISTS fk_t_realisations_t_personne_constats CASCADE;"""
    op.execute(sql)

    # suppression de la clé étrangère id_auteur_constat dans la table oeasc_chasse.t_realisations
    sql = """ALTER TABLE oeasc_chasse.t_realisations
        DROP CONSTRAINT IF EXISTS fk_t_realisations_t_personne_constats;"""
    op.execute(sql)

    # suppression de la table oeasc_chasse.t_personnes
    sql = """DROP TABLE IF EXISTS oeasc_chasse.t_personnes CASCADE;"""
    op.execute(sql)


def downgrade():

    # creation de la table oeasc_chasse.t_personnes
    sql = """CREATE TABLE IF NOT EXISTS oeasc_chasse.t_personnes (
        id_personne SERIAL PRIMARY KEY,
        nom_personne VARCHAR(255) NOT NULL
    );"""
    op.execute(sql)

    # création de la clé étrangère id_auteur_tir dans la table oeasc_chasse.t_realisations
    sql = """ALTER TABLE oeasc_chasse.t_realisations
        ADD CONSTRAINT fk_t_realisations_t_personne_tirs
        FOREIGN KEY (id_auteur_tir) REFERENCES oeasc_chasse.t_personnes (id_personne) ON DELETE SET NULL;"""
    op.execute(sql)

    # création de la clé étrangère id_auteur_constat dans la table oeasc_chasse.t_realisations
    sql = """ALTER TABLE oeasc_chasse.t_realisations
        ADD CONSTRAINT fk_t_realisations_t_personne_constats
        FOREIGN KEY (id_auteur_constat) REFERENCES oeasc_chasse.t_personnes (id_personne) ON DELETE SET NULL;"""
    op.execute(sql)

    pass
