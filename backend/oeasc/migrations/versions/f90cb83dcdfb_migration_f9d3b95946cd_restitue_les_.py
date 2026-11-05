"""migration f9d3b95946cd. restitue les vues en conflits après la migration utilisateur

Revision ID: f90cb83dcdfb
Revises: 3fc01cbe83a2
Create Date: 2025-03-10 12:11:10.600209

"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "f90cb83dcdfb"
down_revision = "3fc01cbe83a2"
branch_labels = None
depends_on = None

# Chemin du fichier contenant les views SQL

VIEW_FILE_PATH1 = f"./data/oeasc_views/oeasc_commons_views.sql"
# Les vues oeasc_declarations_views.sql / oeasc_resultats_views.sql ont été supprimées du dépôt
# (vues devenues inutiles, cf. migration e5b7d3a91c24) : seule v_users est recréée ici.


def upgrade():
    # Récupère le fichier contenant la vue v_users et la réintègre dans la base
    with open(VIEW_FILE_PATH1, "r", encoding="utf-8") as file:
        views_sql = file.read()
        op.execute(views_sql)


def downgrade():
    # Supprimer les views avant la migration
    op.execute("DROP VIEW IF EXISTS oeasc_commons.v_users CASCADE;")
