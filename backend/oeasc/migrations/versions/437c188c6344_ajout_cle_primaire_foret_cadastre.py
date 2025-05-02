"""ajout_cle_primaire_foret_cadastre

Revision ID: 437c188c6344
Revises: f90cb83dcdfb
Create Date: 2025-05-02 11:54:18.758799

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '437c188c6344'
down_revision = 'f90cb83dcdfb'
branch_labels = None
depends_on = None


def upgrade():
    op.execute("ALTER TABLE oeasc_forets.cor_dgd_cadastre ADD CONSTRAINT cor_dgd_cadastre_pkey PRIMARY KEY (area_code_cadastre, area_code_dgd);")


def downgrade():
    op.execute("ALTER TABLE oeasc_forets.cor_dgd_cadastre DROP CONSTRAINT cor_dgd_cadastre_pkey;")
