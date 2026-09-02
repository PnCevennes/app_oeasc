"""add_superficie_to_t_zone_indicatives

Revision ID: 71ace03ca6a3
Revises: bb34c60299a3
Create Date: 2026-09-02 14:39:16.328394

"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "71ace03ca6a3"
down_revision = "bb34c60299a3"
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        "ALTER TABLE oeasc_chasse.t_zone_indicatives "
        "ADD COLUMN IF NOT EXISTS superficie DOUBLE PRECISION"
    )

    # Bien que la colonne geom soit typée SRID 4326 au niveau du modèle, les
    # géométries sont en réalité stockées projetées en Lambert-93 (EPSG:2154,
    # mètres) comme le reste des géométries oeasc_* de la base. ST_Area(geom)
    # renvoie donc directement une surface en m2, sans transformation.
    op.execute("""
        UPDATE oeasc_chasse.t_zone_indicatives
        SET superficie = ROUND((ST_Area(geom) / 10000)::numeric, 4)
        WHERE geom IS NOT NULL
        """)


def downgrade():
    op.execute("""
        DO $$ BEGIN
            IF EXISTS (
                SELECT 1 FROM information_schema.tables
                WHERE table_schema = 'oeasc_chasse' AND table_name = 't_zone_indicatives'
            ) THEN
                ALTER TABLE oeasc_chasse.t_zone_indicatives DROP COLUMN IF EXISTS superficie;
            END IF;
        END $$;
        """)
