"""add_manuelle_to_relances_declaration

Les relances envoyées manuellement par un administrateur (bouton « envoyer une relance »)
sont désormais enregistrées dans l'historique : colonne `manuelle`, et `numero_relance`
devient facultatif (une relance manuelle ne change pas le statut de la déclaration).

Revision ID: d8e3a5b71c42
Revises: c7d2f4a9e613
Create Date: 2026-11-25

"""

from alembic import op

revision = "d8e3a5b71c42"
down_revision = "c7d2f4a9e613"
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        "ALTER TABLE oeasc_declarations.t_relances_declaration "
        "ADD COLUMN IF NOT EXISTS manuelle BOOLEAN NOT NULL DEFAULT false"
    )
    op.execute(
        "ALTER TABLE oeasc_declarations.t_relances_declaration "
        "ALTER COLUMN numero_relance DROP NOT NULL"
    )


def downgrade():
    op.execute(
        "DELETE FROM oeasc_declarations.t_relances_declaration WHERE manuelle"
    )
    op.execute(
        "ALTER TABLE oeasc_declarations.t_relances_declaration "
        "ALTER COLUMN numero_relance SET NOT NULL"
    )
    op.execute(
        "ALTER TABLE oeasc_declarations.t_relances_declaration "
        "DROP COLUMN IF EXISTS manuelle"
    )
