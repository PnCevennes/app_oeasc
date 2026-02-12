"""ajout de clé primaire sur commons.t_communes

Revision ID: 0a44db773490
Revises: 437c188c6344
Create Date: 2025-05-05 10:21:46.511240

"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "0a44db773490"
down_revision = "437c188c6344"
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        "ALTER TABLE oeasc_commons.t_communes ADD CONSTRAINT code_pkey PRIMARY KEY (code, cp);"
    )


def downgrade():
    op.execute("ALTER TABLE oeasc_commons.t_communes DROP CONSTRAINT code_pkey;")
