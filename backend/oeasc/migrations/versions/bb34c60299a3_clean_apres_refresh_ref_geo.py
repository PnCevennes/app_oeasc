"""clean_apres_refresh_ref_geo

Revision ID: bb34c60299a3
Revises: a1b2c3d4e5f6
Create Date: 2026-06-19 15:16:48.094517

"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "bb34c60299a3"
down_revision = "a1b2c3d4e5f6"
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    has_forets_ancien = inspector.has_table("t_forets_ancien", schema="oeasc_forets")
    has_l_areas_ancien = inspector.has_table("l_areas_ancien", schema="ref_geo")

    if not has_forets_ancien or not has_l_areas_ancien:
        raise Exception(
            "La commande 'flask refresh-ref-geo' doit être exécutée avant d'appliquer cette migration. "
            "Les tables oeasc_forets.t_forets_ancien et ref_geo.l_areas_ancien doivent exister."
        )

    op.execute(sa.text("DROP TABLE IF EXISTS oeasc_forets.t_forets_ancien CASCADE"))
    op.execute(sa.text("DROP TABLE IF EXISTS oeasc_forets.t_proprietaires CASCADE"))
    op.execute(sa.text("DROP TABLE IF EXISTS ref_geo.l_areas_ancien CASCADE"))
    op.execute(sa.text("DROP TABLE IF EXISTS oeasc_forets.cor_dgd_cadastre"))
    op.execute(
        sa.text("DROP TABLE IF EXISTS oeasc_declarations.cor_areas_declarations_ancien")
    )


def downgrade():
    raise NotImplementedError(
        "Cette migration est irréversible : les tables supprimées ne peuvent pas être recréées automatiquement."
    )
