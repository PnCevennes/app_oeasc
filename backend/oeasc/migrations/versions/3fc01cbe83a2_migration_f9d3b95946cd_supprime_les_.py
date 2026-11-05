"""migration utilisateurs f9d3b95946cd. Supprime les view en conflit

Revision ID: 3fc01cbe83a2
Revises: 8857f2169f96
Create Date: 2025-03-10 11:22:11.138327

"""

from alembic import op
import sqlalchemy as sa
import subprocess

# revision identifiers, used by Alembic.
revision = "3fc01cbe83a2"
down_revision = "8857f2169f96"
branch_labels = None
depends_on = None

# récupère le chemin du actuel courant
# ROOT_PATH = subprocess.check_output(['pwd']).decode('utf-8').strip()


VIEW_FILE_PATH1 = f"../data/oeasc_views/oeasc_commons_views.sql"
# Les vues oeasc_declarations_views.sql / oeasc_resultats_views.sql ont été supprimées du dépôt
# (vues devenues inutiles, cf. migration e5b7d3a91c24) : seule v_users est recréée ici.


def upgrade():
    # Supprimer les views avant la migration
    op.execute("DROP VIEW IF EXISTS oeasc_commons.v_users CASCADE;")


def downgrade():

    # Récupère le fichier contenant la vue v_users et la réintègre dans la base
    with open(VIEW_FILE_PATH1, "r", encoding="utf-8") as file:
        views_sql = file.read()
    op.execute(views_sql)
