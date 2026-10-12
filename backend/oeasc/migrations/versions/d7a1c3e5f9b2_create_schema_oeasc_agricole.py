"""create_schema_oeasc_agricole

Schéma des dégâts agricoles (indemnisations FDC) : saisons, types de culture
et déclarations de dégâts.

Revision ID: d7a1c3e5f9b2
Revises: c9d4e8f1a2b3
Create Date: 2026-10-12 15:30:00.000000

"""

from alembic import op

# revision identifiers, used by Alembic.
revision = "d7a1c3e5f9b2"
down_revision = "c9d4e8f1a2b3"
branch_labels = None
depends_on = None


def upgrade():
    op.execute("CREATE SCHEMA IF NOT EXISTS oeasc_agricole")

    op.execute("""
        CREATE TABLE oeasc_agricole.t_saison_agricole (
            id_saison SERIAL PRIMARY KEY,
            nom_saison VARCHAR(20) NOT NULL UNIQUE,
            date_debut DATE,
            date_fin DATE,
            current BOOLEAN NOT NULL DEFAULT FALSE
        )
        """)

    op.execute("""
        CREATE TABLE oeasc_agricole.t_type_culture (
            id_culture SERIAL PRIMARY KEY,
            nom_culture VARCHAR(250) NOT NULL UNIQUE
        )
        """)

    # id_commune référence ref_geo.communes_aoa.id SANS contrainte de clé
    # étrangère : `flask refresh-ref-geo` fait un TRUNCATE de communes_aoa, qu'une
    # FK bloquerait (ou qui viderait les déclarations en CASCADE). Les id de
    # communes_aoa sont stables d'un rafraîchissement à l'autre.
    op.execute("""
        CREATE TABLE oeasc_agricole.t_declaration_agricole (
            id_declaration SERIAL PRIMARY KEY,
            id_saison INTEGER NOT NULL
                REFERENCES oeasc_agricole.t_saison_agricole (id_saison),
            date_creation DATE,
            numero_dossier VARCHAR(50),
            date_document DATE,
            id_commune VARCHAR(25),
            id_culture INTEGER
                REFERENCES oeasc_agricole.t_type_culture (id_culture),
            surface_detruite NUMERIC(12, 4),
            volume_detruit NUMERIC(12, 4),
            unit_quantite_detruite VARCHAR(50),
            pourcentage NUMERIC(6, 2),
            id_espece INTEGER
                REFERENCES oeasc_commons.t_especes (id_espece),
            montant_paye NUMERIC(12, 2),
            surface_ressemis NUMERIC(12, 4),
            montant_paye_ressemis NUMERIC(12, 2),
            montant_total_paye NUMERIC(12, 2)
        )
        """)

    op.execute("""
        CREATE INDEX idx_t_declaration_agricole_saison_dossier
        ON oeasc_agricole.t_declaration_agricole (id_saison, numero_dossier)
        """)
    op.execute("""
        CREATE INDEX idx_t_declaration_agricole_commune
        ON oeasc_agricole.t_declaration_agricole (id_commune)
        """)


def downgrade():
    op.execute("DROP SCHEMA IF EXISTS oeasc_agricole CASCADE")
