"""add_t_standards_mesures

Fourchettes « standard » (poids et longueur de dagues) par espèce, classe d'âge
et sexe, utilisées par la page chasse « Données aberrantes » pour repérer les
réalisations dont une mesure sort de la fourchette.

Pré-remplissage : bornes déjà utilisées à l'import CSV (`importation_csv.py` :
TAILLE_MINIMUM/MAXIMUM_DAGUES, POIDS_VIDE_MINIMUM/MAXIMUM), sexe = NULL (tous).
Les bornes de poids entier et de poids c_f_p sont
déduites des bornes de poids vide en inversant les formules de `fct_poid_vide`
(cerf et chevreuil uniquement). Toutes les bornes sont modifiables ensuite
(Données chasse -> onglet « Standards de mesures »).

Revision ID: a7c2e91b4d30
Revises: f3a9c5e7b1d4
Create Date: 2026-10-27 14:00:00.000000

"""

import math

from alembic import op

# revision identifiers, used by Alembic.
revision = "a7c2e91b4d30"
down_revision = "f3a9c5e7b1d4"
branch_labels = None
depends_on = None

# classe d'âge de l'import -> cd_nomenclature (type STADE_VIE) ; FAON et JEUNE partagent le code 3
CD_AGE = {"ADULTE": "2", "SUBADULTE": "5", "INDÉTERMINÉ": "1", "JEUNE": "3", "FAON": "3"}
CODE_ESPECE = {"CERF": "CF", "CHEVREUIL": "CH", "MOUFLON": "MF"}

DAGUES_MIN = {
    "CERF": {"ADULTE": 50, "SUBADULTE": 50, "INDÉTERMINÉ": 5, "JEUNE": 2},
    "CHEVREUIL": {"ADULTE": 10, "SUBADULTE": 1, "INDÉTERMINÉ": 1, "JEUNE": 1},
}
DAGUES_MAX = {
    "CERF": {"ADULTE": 650, "SUBADULTE": 500, "INDÉTERMINÉ": 600, "JEUNE": 200},
    "CHEVREUIL": {"ADULTE": 200, "SUBADULTE": 150, "INDÉTERMINÉ": 200, "JEUNE": 100},
}
POIDS_VIDE_MIN = {
    "CERF": {"ADULTE": 40, "SUBADULTE": 20, "INDÉTERMINÉ": 18, "JEUNE": 18},
    "CHEVREUIL": {"ADULTE": 7, "SUBADULTE": 7, "INDÉTERMINÉ": 7, "JEUNE": 7},
    "MOUFLON": {"ADULTE": 18, "SUBADULTE": 10, "INDÉTERMINÉ": 5, "JEUNE": 5},
}
POIDS_VIDE_MAX = {
    "CERF": {"ADULTE": 250, "SUBADULTE": 150, "INDÉTERMINÉ": 300, "JEUNE": 120},
    "CHEVREUIL": {"ADULTE": 70, "SUBADULTE": 50, "INDÉTERMINÉ": 50, "JEUNE": 26},
    "MOUFLON": {"ADULTE": 55, "SUBADULTE": 30, "INDÉTERMINÉ": 35, "JEUNE": 35},
}
# coefficients de fct_poid_vide : poids_vide = exp(exp_) * poids ** puissance
COEF_PE = {"CERF": (-0.3948, 1.0247), "CHEVREUIL": (-0.3572, 1.023)}
COEF_PCFP = {"CERF": (-0.1128, 1.0041), "CHEVREUIL": (-0.2868, 1.0614)}


def _inverse(poids_vide, coef):
    exp_, puissance = coef
    return (poids_vide / math.exp(exp_)) ** (1 / puissance)


def _lignes():
    """[(code_espece, cd_age, mesure, min, max)]"""
    lignes = []
    for espece, par_age in DAGUES_MIN.items():
        for age, mini in par_age.items():
            lignes.append(
                (CODE_ESPECE[espece], CD_AGE[age], "long_dagues", mini, DAGUES_MAX[espece][age])
            )
    for espece, par_age in POIDS_VIDE_MIN.items():
        for age, mini in par_age.items():
            maxi = POIDS_VIDE_MAX[espece][age]
            code, cd_age = CODE_ESPECE[espece], CD_AGE[age]
            lignes.append((code, cd_age, "poid_vide", mini, maxi))
            for mesure, coefs in (("poid_entier", COEF_PE), ("poid_c_f_p", COEF_PCFP)):
                if espece in coefs:
                    lignes.append(
                        (
                            code,
                            cd_age,
                            mesure,
                            math.floor(_inverse(mini, coefs[espece])),
                            math.ceil(_inverse(maxi, coefs[espece])),
                        )
                    )
    return lignes


def upgrade():
    op.execute("""
        CREATE TABLE oeasc_chasse.t_standards_mesures (
            id_standard SERIAL PRIMARY KEY,
            id_espece INTEGER NOT NULL REFERENCES oeasc_commons.t_especes (id_espece),
            id_nomenclature_classe_age INTEGER NOT NULL
                REFERENCES ref_nomenclatures.t_nomenclatures (id_nomenclature),
            id_nomenclature_sexe INTEGER
                REFERENCES ref_nomenclatures.t_nomenclatures (id_nomenclature),
            mesure VARCHAR(20) NOT NULL
                CHECK (mesure IN ('poid_entier', 'poid_vide', 'poid_c_f_p', 'long_dagues')),
            valeur_min FLOAT,
            valeur_max FLOAT,
            CHECK (valeur_min IS NULL OR valeur_max IS NULL OR valeur_min <= valeur_max)
        )
        """)
    # sexe NULL = « tous les sexes » : COALESCE pour que l'unicité couvre aussi ce cas
    op.execute("""
        CREATE UNIQUE INDEX uq_standards_mesures
        ON oeasc_chasse.t_standards_mesures
            (id_espece, id_nomenclature_classe_age, COALESCE(id_nomenclature_sexe, 0), mesure)
        """)

    for code_espece, cd_age, mesure, mini, maxi in _lignes():
        op.execute(f"""
            INSERT INTO oeasc_chasse.t_standards_mesures
                (id_espece, id_nomenclature_classe_age, mesure, valeur_min, valeur_max)
            SELECT te.id_espece, tn.id_nomenclature, '{mesure}', {mini}, {maxi}
            FROM oeasc_commons.t_especes te,
                ref_nomenclatures.t_nomenclatures tn
                JOIN ref_nomenclatures.bib_nomenclatures_types bt ON bt.id_type = tn.id_type
            WHERE te.code_espece = '{code_espece}'
                AND bt.mnemonique = 'STADE_VIE'
                AND tn.cd_nomenclature = '{cd_age}'
            """)


def downgrade():
    op.execute("DROP TABLE IF EXISTS oeasc_chasse.t_standards_mesures")
