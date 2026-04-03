"""modif declaration pour archivage

Revision ID: 41042f593f9f
Revises: 42abbaaa4dbb
Create Date: 2026-03-24 16:35:27.672176

"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "41042f593f9f"
down_revision = "42abbaaa4dbb"
branch_labels = None
depends_on = None


def upgrade():
    # creation du champ date_fin, statut, token_renouvellement et id_declaration_duplique
    # création des champs (table `t_declarations` dans le schema `oeasc_declarations`)
    op.add_column(
        "t_declarations",
        sa.Column("date_fin", sa.DateTime(), nullable=True),
        schema="oeasc_declarations",
    )
    op.add_column(
        "t_declarations",
        sa.Column("status", sa.Integer(), nullable=True),
        schema="oeasc_declarations",
    )
    op.add_column(
        "t_declarations",
        sa.Column("token_renouvellement", sa.String(length=255), nullable=True),
        schema="oeasc_declarations",
    )
    op.add_column(
        "t_declarations",
        sa.Column("date_fin_token", sa.DateTime(), nullable=True),
        schema="oeasc_declarations",
    )
    op.add_column(
        "t_declarations",
        sa.Column("id_declaration_duplique", sa.Integer(), nullable=True),
        schema="oeasc_declarations",
    )

    # ajout d'une contrainte de clé étrangère pour id_declaration_duplique
    op.create_foreign_key(
        "fk_declaration_id_declaration_duplique",
        "t_declarations",
        "t_declarations",
        ["id_declaration_duplique"],
        ["id_declaration"],
        source_schema="oeasc_declarations",
        referent_schema="oeasc_declarations",
        ondelete="SET NULL",
    )

    # pour toutes les déclarations qui ont plus de 3 ans par rapport à meta_create_date, on met la valeur de date_fin à meta_create_date+3ans
    op.execute("""
        UPDATE oeasc_declarations.t_declarations
        SET date_fin = meta_create_date + INTERVAL '3 years'
    """)

    # On met tous les status à 1 (code: Active) pour les déclarations. Le premier changement de status se fera au premier mail de relance.
    op.execute(f"""
        UPDATE oeasc_declarations.t_declarations
        SET status = 1
        WHERE b_valid = true
    """)
    # les déclarations non valides sont considérées comme non validées (code: 0)
    op.execute(f"""
        UPDATE oeasc_declarations.t_declarations
        SET status = 0
        WHERE b_valid = false
    """)
    
    # # pour toutes les déclarations qui ont une date_fin et b_valid == true, on met le status à "A renouveler 1" (code: 10)
    # op.execute(f"""
    #     UPDATE oeasc_declarations.t_declarations
    #     SET status = 10
    #     WHERE date_fin <= NOW() AND b_valid = true
    # """)

    # op.execute(f"""
    #     UPDATE oeasc_declarations.t_declarations
    #     SET status = 1
    #     WHERE date_fin > NOW() AND b_valid = true
    # """)


def downgrade():

    # suppression de la contrainte de clé étrangère pour id_declaration_duplique
    op.drop_constraint(
        "fk_declaration_id_declaration_duplique",
        "t_declarations",
        type_="foreignkey",
        schema="oeasc_declarations",
    )

    # suppression des champs date_fin, statut, token_renouvellement et id_declaration_duplique
    op.drop_column(
        "t_declarations", "id_declaration_duplique", schema="oeasc_declarations"
    )
    op.drop_column(
        "t_declarations", "token_renouvellement", schema="oeasc_declarations"
    )
    op.drop_column("t_declarations", "date_fin_token", schema="oeasc_declarations")
    op.drop_column("t_declarations", "status", schema="oeasc_declarations")
    op.drop_column("t_declarations", "date_fin", schema="oeasc_declarations")
