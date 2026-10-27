"""fix_unite_dagues_cm_vers_mm

Les longueurs de dagues des cerfs subadultes des saisons 2024-2025 et 2025-2026
avaient été saisies en cm au lieu de mm (moyenne ICE à ~22 au lieu de ~230).
Les valeurs <= 48 sont multipliées par 10 (aucune dague de cerf subadulte ne
mesure moins de 5 cm : une valeur aussi faible est une saisie en cm).

Attention : la règle n'est pas idempotente (une valeur corrigée de 2 à 4 cm
redeviendrait <= 48). Elle ne doit donc être jouée qu'une fois par base ; sur
une base où la correction a déjà été faite à la main, utiliser
`flask db stamp f3a9c5e7b1d4` au lieu de `upgrade`.

Revision ID: f3a9c5e7b1d4
Revises: e8b2d4f6a1c3
Create Date: 2026-10-27 10:00:00.000000

"""

from alembic import op

# revision identifiers, used by Alembic.
revision = "f3a9c5e7b1d4"
down_revision = "e8b2d4f6a1c3"
branch_labels = None
depends_on = None

SEUIL_CM_MM = 48
SAISONS = ("2024-2025", "2025-2026")



def upgrade():
    op.execute(
        f"""
        UPDATE oeasc_chasse.t_realisations tr
        SET long_dagues_droite = tr.long_dagues_droite * 10,
            long_dagues_gauche = tr.long_dagues_gauche * 10
        FROM (
            SELECT tr2.id_realisation
            FROM oeasc_chasse.t_realisations tr2
            JOIN oeasc_chasse.t_attributions ta ON ta.id_attribution = tr2.id_attribution
            JOIN oeasc_chasse.t_saisons ts ON ts.id_saison = ta.id_saison
            JOIN oeasc_chasse.t_type_bracelets ttb ON ttb.id_type_bracelet = ta.id_type_bracelet
            JOIN oeasc_commons.t_especes te ON te.id_espece = ttb.id_espece
            JOIN ref_nomenclatures.t_nomenclatures tn ON tn.id_nomenclature = tr2.id_nomenclature_classe_age
            WHERE ts.nom_saison IN {SAISONS}
                AND te.code_espece = 'CF'
                AND tn.cd_nomenclature = '5'
                AND GREATEST(tr2.long_dagues_droite, tr2.long_dagues_gauche) <= {SEUIL_CM_MM}
        ) cible
        WHERE tr.id_realisation = cible.id_realisation
        """
    )


def downgrade():
    # irréversible sans ambiguïté (la règle ne permet pas de retrouver les lignes d'origine)
    pass
