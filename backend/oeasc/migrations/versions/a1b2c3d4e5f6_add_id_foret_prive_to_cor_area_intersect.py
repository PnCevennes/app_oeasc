"""add id_foret_prive to cor_area_intersect

Revision ID: a1b2c3d4e5f6
Revises: 41042f593f9f
Branch Labels: None
Depends On: None

"""

from alembic import op
import sqlalchemy as sa

revision = "a1b2c3d4e5f6"
down_revision = "3e5c666af390"
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
        """
        DO $$ BEGIN
            IF EXISTS (
                SELECT 1 FROM information_schema.tables
                WHERE table_schema = 'ref_geo' AND table_name = 'cor_area_intersect'
            ) THEN
                ALTER TABLE ref_geo.cor_area_intersect DROP COLUMN IF EXISTS id_foret_prive;
            END IF;
        END $$;
        """
    )
