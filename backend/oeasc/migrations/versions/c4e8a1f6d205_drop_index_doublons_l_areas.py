"""drop_index_doublons_l_areas

Le refresh (`flask refresh-ref-geo`) créait des index en plus de ceux copiés par
`CREATE TABLE ... (LIKE ... INCLUDING ALL)` : sur ref_geo.l_areas on se
retrouvait avec 3 index GIST identiques sur geom et 2 index btree sur id_type.
On ne garde que les index issus du LIKE (`l_areas_new_geom_idx`,
`l_areas_new_id_type_idx`).

Revision ID: c4e8a1f6d205
Revises: a7c2e91b4d30
Create Date: 2026-10-29 10:00:00.000000

"""

from alembic import op

# revision identifiers, used by Alembic.
revision = "c4e8a1f6d205"
down_revision = "a7c2e91b4d30"
branch_labels = None
depends_on = None


def upgrade():
    op.execute("DROP INDEX IF EXISTS ref_geo.ix_l_areas_new_geom_build")
    op.execute("DROP INDEX IF EXISTS ref_geo.ix_l_areas_new_geom_tmp")
    op.execute("DROP INDEX IF EXISTS ref_geo.ix_l_areas_new_id_type")


def downgrade():
    # Les index supprimés étaient des doublons : rien à recréer.
    pass
