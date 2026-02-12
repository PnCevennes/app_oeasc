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
VIEW_FILE_PATH2 = f"./data/oeasc_views/oeasc_declarations_views.sql"
VIEW_FILE_PATH3 = f"./data/oeasc_views/oeasc_resultats_views.sql"


def upgrade():
    # Récupère les fichiers contenant les views et les réintègre dans la base
    with open(VIEW_FILE_PATH1, "r", encoding="utf-8") as file:
        views_sql = file.read()
        op.execute(views_sql)

    with open(VIEW_FILE_PATH2, "r", encoding="utf-8") as file:
        views_sql = file.read()
        op.execute(views_sql)

    with open(VIEW_FILE_PATH3, "r", encoding="utf-8") as file:
        views_sql = file.read()
        op.execute(views_sql)


def downgrade():
    # Supprimer les views avant la migration
    op.execute("DROP VIEW IF EXISTS oeasc_commons.v_users CASCADE;")
