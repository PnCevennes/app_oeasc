"""add id_foret_prive to cor_area_intersect

Revision ID: a1b2c3d4e5f6
Revises: 41042f593f9f
Branch Labels: None
Depends On: None

"""

from alembic import op
import sqlalchemy as sa

revision = "a1b2c3d4e5f6"
down_revision = "41042f593f9f"
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        "ALTER TABLE ref_geo.cor_area_intersect "
        "ADD COLUMN IF NOT EXISTS id_foret_prive INTEGER "
        "REFERENCES ref_geo.l_areas(id_area) ON DELETE CASCADE"
    )


def downgrade():
    op.execute(
        "ALTER TABLE ref_geo.cor_area_intersect "
        "DROP COLUMN IF EXISTS id_foret_prive"
    )
