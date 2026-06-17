"""modification table foret

Revision ID: 3e5c666af390
Revises: 8bf1a1d4e2c7
Create Date: 2026-06-08 14:06:56.041320

"""
from alembic import op
import sqlalchemy as sa


revision = '3e5c666af390'
down_revision = '8bf1a1d4e2c7'
branch_labels = None
depends_on = None


def upgrade():
    for col, col_type in [
        ('id_area', 'INTEGER'),
        ('nom_proprietaire', 'VARCHAR(255)'),
        ('adresse_proprietaire', 'VARCHAR(255)'),
        ('cp_proprietaire', 'VARCHAR(5)'),
        ('commune_proprietaire', 'VARCHAR(255)'),
        ('email_proprietaire', 'VARCHAR(255)'),
        ('tel_proprietaire', 'VARCHAR(255)'),
        ('id_nomenclature_proprietaire_type', 'INTEGER'),
        ('id_declarant', 'INTEGER'),
    ]:
        op.execute(f"ALTER TABLE oeasc_forets.t_forets ADD COLUMN IF NOT EXISTS {col} {col_type}")

    op.execute("""
        DO $$ BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.table_constraints
                WHERE constraint_schema = 'oeasc_forets'
                  AND constraint_name = 'fk_foret_id_nomenclature_proprietaire_type'
            ) THEN
                ALTER TABLE oeasc_forets.t_forets
                ADD CONSTRAINT fk_foret_id_nomenclature_proprietaire_type
                FOREIGN KEY (id_nomenclature_proprietaire_type)
                REFERENCES ref_nomenclatures.t_nomenclatures(id_nomenclature);
            END IF;
        END $$;
    """)
    op.execute("""
        DO $$ BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.table_constraints
                WHERE constraint_schema = 'oeasc_forets'
                  AND constraint_name = 'fk_foret_id_declarant'
            ) THEN
                ALTER TABLE oeasc_forets.t_forets
                ADD CONSTRAINT fk_foret_id_declarant
                FOREIGN KEY (id_declarant)
                REFERENCES utilisateurs.t_roles(id_role);
            END IF;
        END $$;
    """)

    op.execute("""
        UPDATE oeasc_forets.t_forets f
        SET nom_proprietaire = p.nom_proprietaire,
            adresse_proprietaire = p.adresse,
            cp_proprietaire = p.s_code_postal,
            commune_proprietaire = p.s_commune_proprietaire,
            email_proprietaire = p.email,
            tel_proprietaire = p.telephone,
            id_nomenclature_proprietaire_type = p.id_nomenclature_proprietaire_type,
            id_declarant = p.id_declarant
        FROM oeasc_forets.t_proprietaires p
        WHERE f.id_proprietaire = p.id_proprietaire
    """)

    op.execute("""
        INSERT INTO ref_geo.bib_areas_types (type_name, type_code, ref_name, type_desc, ref_version)
        SELECT 'Forêt non documentée', 'OEASC_FORET_PRIVE', 'OEASC', 'Forets privées non documentées', '2026'
        WHERE NOT EXISTS (
            SELECT 1 FROM ref_geo.bib_areas_types WHERE type_code = 'OEASC_FORET_PRIVE'
        )
    """)


def downgrade():
    op.execute("""
        DO $$ BEGIN
            IF EXISTS (
                SELECT 1 FROM information_schema.table_constraints
                WHERE constraint_schema = 'oeasc_forets'
                  AND constraint_name = 'fk_foret_id_nomenclature_proprietaire_type'
            ) THEN
                ALTER TABLE oeasc_forets.t_forets
                DROP CONSTRAINT fk_foret_id_nomenclature_proprietaire_type;
            END IF;
        END $$;
    """)
    op.execute("""
        DO $$ BEGIN
            IF EXISTS (
                SELECT 1 FROM information_schema.table_constraints
                WHERE constraint_schema = 'oeasc_forets'
                  AND constraint_name = 'fk_foret_id_declarant'
            ) THEN
                ALTER TABLE oeasc_forets.t_forets DROP CONSTRAINT fk_foret_id_declarant;
            END IF;
        END $$;
    """)

    for col in [
        'id_area', 'nom_proprietaire', 'adresse_proprietaire', 'cp_proprietaire',
        'commune_proprietaire', 'email_proprietaire', 'tel_proprietaire',
        'id_nomenclature_proprietaire_type', 'id_declarant',
    ]:
        op.execute(f"ALTER TABLE oeasc_forets.t_forets DROP COLUMN IF EXISTS {col}")

    op.execute("""
        DELETE FROM ref_geo.bib_areas_types WHERE type_code = 'OEASC_FORET_PRIVE'
    """)
