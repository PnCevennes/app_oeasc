"""modification tag IN

Revision ID: d15f8142f4ed
Revises: 41042f593f9f
Create Date: 2026-05-12 15:53:40.614845

"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "d15f8142f4ed"
down_revision = "41042f593f9f"
branch_labels = None
depends_on = None


def upgrade():
    # création du champ "in_coeur" dans la table t_ciruits
    op.add_column(
        "t_circuits",
        sa.Column("in_coeur", sa.Boolean(), nullable=True, default=True),
        schema="oeasc_in",
    )
    # les circuits dont le nom est "Fretma" et "Le Pradal" ont in_coeur à False
    op.execute("UPDATE oeasc_in.t_circuits SET in_coeur = True")
    op.execute(
        "UPDATE oeasc_in.t_circuits SET in_coeur = False WHERE nom_circuit IN ('St-Pierre-des-Trippiers', 'Hures-la-Parade', 'Mas-St-Chély')"
    )

    # ajout du champ valide_ZC dans la table t_realisations
    op.add_column(
        "t_realisations",
        sa.Column("valide_ZC", sa.Boolean(), nullable=True, default=False),
        schema="oeasc_in",
    )

    # on met valide_ZC à True pour toutes les réalisations où il existe au moins une valeur valid==True dans cor_realisation_tag
    op.execute('UPDATE oeasc_in.t_realisations SET "valide_ZC" = False')
    op.execute(
        'UPDATE oeasc_in.t_realisations SET "valide_ZC" = True WHERE id_realisation IN (SELECT id_realisation FROM oeasc_in.cor_realisation_tag WHERE valid = True AND id_tag = 2)'
    )

    # ajout du champ valide_hors_coeur dans la table t_realisations
    op.add_column(
        "t_realisations",
        sa.Column("valide_PNC", sa.Boolean(), nullable=True, default=False),
        schema="oeasc_in",
    )

    # on met valide_PNC à True pour toutes les réalisations où il existe au moins une valeur valid==True dans cor_realisation_tag
    op.execute('UPDATE oeasc_in.t_realisations SET "valide_PNC" = False')
    op.execute(
        'UPDATE oeasc_in.t_realisations SET "valide_PNC" = True WHERE id_realisation IN (SELECT id_realisation FROM oeasc_in.cor_realisation_tag WHERE valid = True AND id_tag = 1)'
    )

    # suppression des objets dépendants avant la suppression des tables tags
    op.execute("DROP VIEW IF EXISTS oeasc_in.v_result")
    op.drop_table("cor_realisation_tag", schema="oeasc_in")
    op.drop_table("t_tags", schema="oeasc_in")


def downgrade():

    # suppression du champ "in_coeur" dans la table t_ciruits
    op.drop_column("t_circuits", "in_coeur", schema="oeasc_in")
    # suppression du champ "valide_ZC" dans la table t_realisations
    op.drop_column("t_realisations", "valide_ZC", schema="oeasc_in")
    # suppression du champ "valide_PNC" dans la table t_realisations
    op.drop_column("t_realisations", "valide_PNC", schema="oeasc_in")

    # recréation de la vue v_result
    op.execute("""CREATE OR REPLACE VIEW oeasc_in.v_result AS
        SELECT r.id_realisation,
            r.id_circuit,
            r.valide_ZC,
            r.valide_PNC,
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

    # recréation de la table t_tags
    op.create_table(
        "t_tags",
        sa.Column("id_tag", sa.Integer(), nullable=False),
        sa.Column("nom_tag", sa.String(length=255), nullable=True),
        sa.PrimaryKeyConstraint("id_tag"),
        schema="oeasc_in",
    )
    # recréation de la table cor_realisation_tag
    op.create_table(
        "cor_realisation_tag",
        sa.Column("id_realisation", sa.Integer(), nullable=False),
        sa.Column("id_tag", sa.Integer(), nullable=False),
        sa.Column("valid", sa.Boolean(), nullable=True, default=False),
        sa.ForeignKeyConstraint(
            ["id_realisation"],
            ["oeasc_in.t_realisations.id_realisation"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["id_tag"], ["oeasc_in.t_tags.id_tag"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id_realisation", "id_tag"),
        schema="oeasc_in",
    )
