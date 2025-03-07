"""migration utilisateurs f9d3b95946cd. Supprime les view en conflit

Revision ID: 3fc01cbe83a2
Revises: 8857f2169f96
Create Date: 2025-03-10 11:22:11.138327

"""
from alembic import op
import sqlalchemy as sa
import subprocess


# revision identifiers, used by Alembic.
revision = '3fc01cbe83a2'
down_revision = '8857f2169f96'
branch_labels = None
depends_on = None


VIEW_FILE_PATH1 = f"data/oeasc_views/oeasc_commons_views.sql"
VIEW_FILE_PATH2 = f"data/oeasc_views/oeasc_declarations_views.sql"
VIEW_FILE_PATH3 = f"data/oeasc_views/oeasc_resultats_views.sql"



def upgrade():
    # Supprimer les views avant la migration
    op.execute("DROP VIEW IF EXISTS oeasc_commons.v_users CASCADE;")


def downgrade():

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