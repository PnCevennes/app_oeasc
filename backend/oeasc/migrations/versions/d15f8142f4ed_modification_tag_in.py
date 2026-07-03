"""modification tag IN

Revision ID: d15f8142f4ed
Revises: 41042f593f9f
Create Date: 2026-05-12 15:53:40.614845

"""

from alembic import op
import sqlalchemy as sa

revision = "d15f8142f4ed"
down_revision = "41042f593f9f"
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        "ALTER TABLE oeasc_in.t_circuits ADD COLUMN IF NOT EXISTS in_coeur BOOLEAN DEFAULT TRUE"
    )
    op.execute("UPDATE oeasc_in.t_circuits SET in_coeur = True")
    op.execute(
        "UPDATE oeasc_in.t_circuits SET in_coeur = False"
        " WHERE nom_circuit IN ('St-Pierre-des-Trippiers', 'Hures-la-Parade', 'Mas-St-Chély')"
    )

    op.execute(
        'ALTER TABLE oeasc_in.t_realisations ADD COLUMN IF NOT EXISTS "valide_ZC" BOOLEAN DEFAULT FALSE'
    )
    op.execute('UPDATE oeasc_in.t_realisations SET "valide_ZC" = False')
    op.execute("""
        DO $$ BEGIN
            IF EXISTS (
                SELECT 1 FROM information_schema.tables
                WHERE table_schema = 'oeasc_in' AND table_name = 'cor_realisation_tag'
            ) THEN
                UPDATE oeasc_in.t_realisations SET "valide_ZC" = True
                WHERE id_realisation IN (
                    SELECT id_realisation FROM oeasc_in.cor_realisation_tag
                    WHERE valid = True AND id_tag = 2
                );
            END IF;
        END $$;
    """)

    op.execute(
        'ALTER TABLE oeasc_in.t_realisations ADD COLUMN IF NOT EXISTS "valide_PNC" BOOLEAN DEFAULT FALSE'
    )
    op.execute('UPDATE oeasc_in.t_realisations SET "valide_PNC" = False')
    op.execute("""
        DO $$ BEGIN
            IF EXISTS (
                SELECT 1 FROM information_schema.tables
                WHERE table_schema = 'oeasc_in' AND table_name = 'cor_realisation_tag'
            ) THEN
                UPDATE oeasc_in.t_realisations SET "valide_PNC" = True
                WHERE id_realisation IN (
                    SELECT id_realisation FROM oeasc_in.cor_realisation_tag
                    WHERE valid = True AND id_tag = 1
                );
            END IF;
        END $$;
    """)

    op.execute("DROP VIEW IF EXISTS oeasc_in.v_result")
    op.drop_table("cor_realisation_tag", schema="oeasc_in", if_exists=True)
    op.drop_table("t_tags", schema="oeasc_in", if_exists=True)


def downgrade():
    op.execute("ALTER TABLE oeasc_in.t_circuits DROP COLUMN IF EXISTS in_coeur")
    op.execute('ALTER TABLE oeasc_in.t_realisations DROP COLUMN IF EXISTS "valide_ZC"')
    op.execute('ALTER TABLE oeasc_in.t_realisations DROP COLUMN IF EXISTS "valide_PNC"')

    op.execute("""CREATE OR REPLACE VIEW oeasc_in.v_result AS
        SELECT r.id_realisation,
            r.id_circuit,
            r.serie,
            r.groupes,
            r.vent,
            r.temps,
            r.temperature,
            r.date_realisation,
            c.nom_circuit,
            s.nom_secteur,
            array_agg(DISTINCT o.id_observation) AS observations,
            array_agg(DISTINCT ob.id_observer) AS observers,
            array_agg(DISTINCT t.id_tag) AS tags
        FROM oeasc_in.t_realisations r
                JOIN oeasc_in.t_circuits c ON r.id_circuit = c.id_circuit
                JOIN oeasc_in.t_secteurs s ON c.id_secteur = s.id_secteur
                LEFT JOIN oeasc_in.cor_realisation_observer ro ON r.id_realisation = ro.id_realisation
                LEFT JOIN oeasc_in.t_observers ob ON ro.id_observer = ob.id_observer
                LEFT JOIN oeasc_in.t_observations o ON r.id_realisation = o.id_realisation
                LEFT JOIN oeasc_in.cor_realisation_tag rt ON r.id_realisation = rt.id_realisation
                LEFT JOIN oeasc_in.t_tags t ON rt.id_tag = t.id_tag
        GROUP BY r.id_realisation, c.nom_circuit, s.nom_secteur;""")

    op.execute("""
        CREATE TABLE IF NOT EXISTS oeasc_in.t_tags (
            id_tag SERIAL PRIMARY KEY,
            nom_tag VARCHAR(255)
        )
    """)
    op.execute("""
        CREATE TABLE IF NOT EXISTS oeasc_in.cor_realisation_tag (
            id_realisation INTEGER NOT NULL,
            id_tag INTEGER NOT NULL,
            valid BOOLEAN DEFAULT FALSE,
            PRIMARY KEY (id_realisation, id_tag),
            FOREIGN KEY (id_realisation) REFERENCES oeasc_in.t_realisations(id_realisation) ON DELETE CASCADE,
            FOREIGN KEY (id_tag) REFERENCES oeasc_in.t_tags(id_tag) ON DELETE CASCADE
        )
    """)
