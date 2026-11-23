"""historique des relances automatiques et table de paramètres des déclarations

Crée oeasc_declarations.t_relances_declaration (une ligne par relance automatique envoyée)
et oeasc_declarations.t_parametres (clé / valeur, pour activer/désactiver les relances
automatiques depuis l'interface d'administration).

Revision ID: c7d2f4a9e613
Revises: a4c8e2f61b37
Create Date: 2026-11-23

"""

from alembic import op

revision = "c7d2f4a9e613"
down_revision = "a4c8e2f61b37"
branch_labels = None
depends_on = None


def upgrade():
    op.execute("""
        CREATE TABLE IF NOT EXISTS oeasc_declarations.t_relances_declaration (
            id_relance SERIAL PRIMARY KEY,
            id_declaration INTEGER NOT NULL
                REFERENCES oeasc_declarations.t_declarations (id_declaration) ON DELETE CASCADE,
            numero_relance INTEGER NOT NULL,
            date_relance TIMESTAMP NOT NULL DEFAULT now()
        )
    """)
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_t_relances_declaration_id_declaration "
        "ON oeasc_declarations.t_relances_declaration (id_declaration)"
    )
    op.execute("""
        CREATE TABLE IF NOT EXISTS oeasc_declarations.t_parametres (
            cle VARCHAR(100) PRIMARY KEY,
            valeur TEXT
        )
    """)


def downgrade():
    op.execute("DROP TABLE IF EXISTS oeasc_declarations.t_parametres")
    op.execute("DROP TABLE IF EXISTS oeasc_declarations.t_relances_declaration")
