"""add_t_cultures_and_t_ug_agricole

Dégâts agricoles :

- l'actuelle `t_type_culture` contenait en réalité les cultures : elle est
  renommée `t_cultures` (les id, donc `t_declaration_agricole.id_culture`, sont
  conservés). Une nouvelle `t_type_culture` porte les catégories de cultures
  (CEREALES, PRAIRIES...) et `t_cultures.id_type_culture` y fait référence.
  Correspondance culture -> type : `data/degat_agricoles/table_cultures.xlsx`.
- `t_ug_agricole` : unités de gestion (colonne « Secteur » du fichier importé),
  référencées par le nouveau champ `t_declaration_agricole.id_ug_agricole`.

Revision ID: e8b2d4f6a1c3
Revises: d7a1c3e5f9b2
Create Date: 2026-10-13 10:00:00.000000

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "e8b2d4f6a1c3"
down_revision = "d7a1c3e5f9b2"
branch_labels = None
depends_on = None


# contenu de data/degat_agricoles/table_cultures.xlsx : {type de culture: [cultures]}
# + BLE BARBUT DU ROUSSILLON, présente dans degats_lozere.xls mais absente du xlsx
CULTURES_PAR_TYPE = {
    "CEREALES": [
        "AUTRES CEREALES",
        "AVOINE",
        "AVOINE BIOLOGIQUE",
        "BLE",
        "BLE BARBUT DU ROUSSILLON",
        "BLE BIOLOGIQUE",
        "EPEAUTRE",
        "GRAND EPEAUTRE",
        "GRAND EPEAUTRE BIOLOGIQUE",
        "MAIS ENSILAGE",
        "MAIS ENSILAGE BIOLOGIQUE",
        "ORGE",
        "ORGE BIOLOGIQUE",
        "PAILLE",
        "SARRASIN BIOLOGIQUE",
        "SARRAZIN",
        "SEIGLE",
        "SEIGLE BIOLOGIQUE",
        "TRITICALE",
        "TRITICALE BIOLOGIQUE",
    ],
    "FRUITS ET LEGUMES": [
        "ABRICOTIERS",
        "BETTERAVES",
        "CERISIERS",
        "COTES DE BLETTES",
        "COURGETTES",
        "EPINARDS",
        "FRAISIERS",
        "FRAISIERS BIOLOGIQUES",
        "FRAMBOISIERS",
        "LEGUMES PLEIN CHAMP",
        "LENTILLES",
        "MARAICHAGE BIOLOGIQUE",
        "MARRONS BETIZAC et DAUPHINE",
        "MARRONS COMBALLE",
        "PLANTS DE MELONS",
        "PLANTS DE POTIRONS BIOLOGIQUES",
        "POMMES DE TERRE",
        "POMMES DE TERRE BIOLOGIQUES",
        "POMMIERS",
        "POMMIERS BIOLOGIQUES",
        "RAISIN CUVE IGP PAYS D'OC",
        "VERGER",
    ],
    "PRAIRIES": [
        "BON ALPAGE",
        "METEIL",
        "METEIL BIOLOGIQUE",
        "PRAIRIES PERMANENTES",
        "PRAIRIES PERMANENTES BIOLOGIQUES",
        "PRAIRIES TEMPORAIRES",
        "PRAIRIES TEMPORAIRES BIOLOGIQUES",
    ],
    "MÉLANGE": [
        "COMPEMENT BIO",
        "MELANGE",
        "MELANGE BIOLOGIQUE",
    ],
}

# valeurs de la colonne « Secteur » de data/degat_agricoles/degats_lozere.xls
UG_AGRICOLES = [
    "06 / GARDILLE/CHASSEZAC",
    "07 / SAUVETERRE",
    "08 / MEJEAN",
    "09 / MONT LOZERE",
    "10 / AIGOUAL",
    "11 / CEVENNES",
]


def upgrade():
    conn = op.get_bind()

    # --- t_type_culture (cultures) -> t_cultures -----------------------------
    # contraintes et séquence renommées aussi : leurs noms seraient sinon en
    # conflit avec ceux de la nouvelle t_type_culture
    op.execute("ALTER TABLE oeasc_agricole.t_type_culture RENAME TO t_cultures")
    op.execute("""
        ALTER TABLE oeasc_agricole.t_cultures
        RENAME CONSTRAINT t_type_culture_pkey TO t_cultures_pkey
        """)
    op.execute("""
        ALTER TABLE oeasc_agricole.t_cultures
        RENAME CONSTRAINT t_type_culture_nom_culture_key
        TO t_cultures_nom_culture_key
        """)
    op.execute("""
        ALTER SEQUENCE oeasc_agricole.t_type_culture_id_culture_seq
        RENAME TO t_cultures_id_culture_seq
        """)

    # --- nouvelle t_type_culture (catégories de cultures) -------------------
    op.execute("""
        CREATE TABLE oeasc_agricole.t_type_culture (
            id_type_culture SERIAL PRIMARY KEY,
            nom_type_culture VARCHAR(250) NOT NULL UNIQUE
        )
        """)
    op.execute("""
        ALTER TABLE oeasc_agricole.t_cultures
        ADD COLUMN id_type_culture INTEGER
            REFERENCES oeasc_agricole.t_type_culture (id_type_culture)
        """)
    op.execute("""
        CREATE INDEX idx_t_cultures_type_culture
        ON oeasc_agricole.t_cultures (id_type_culture)
        """)

    for nom_type, cultures in CULTURES_PAR_TYPE.items():
        id_type = conn.execute(
            sa.text("""
                INSERT INTO oeasc_agricole.t_type_culture (nom_type_culture)
                VALUES (:nom) RETURNING id_type_culture
                """),
            {"nom": nom_type},
        ).scalar()
        for nom_culture in cultures:
            params = {"nom": nom_culture, "id_type": id_type}
            maj = conn.execute(
                sa.text("""
                    UPDATE oeasc_agricole.t_cultures
                    SET id_type_culture = :id_type
                    WHERE nom_culture = :nom
                    """),
                params,
            )
            if maj.rowcount == 0:
                # culture absente de la base (pas encore rencontrée à l'import)
                conn.execute(
                    sa.text("""
                        INSERT INTO oeasc_agricole.t_cultures
                            (nom_culture, id_type_culture)
                        VALUES (:nom, :id_type)
                        """),
                    params,
                )

    # --- t_ug_agricole -------------------------------------------------------
    op.execute("""
        CREATE TABLE oeasc_agricole.t_ug_agricole (
            id_ug_agricole SERIAL PRIMARY KEY,
            nom_ug_agricole VARCHAR(250) NOT NULL UNIQUE,
            in_oeasc BOOLEAN NOT NULL DEFAULT FALSE
        )
        """)
    for nom_ug in UG_AGRICOLES:
        # in_oeasc à vrai : le fichier ne contient que des communes de l'OEASC
        conn.execute(
            sa.text("""
                INSERT INTO oeasc_agricole.t_ug_agricole (nom_ug_agricole, in_oeasc)
                VALUES (:nom, TRUE)
                """),
            {"nom": nom_ug},
        )

    op.execute("""
        ALTER TABLE oeasc_agricole.t_declaration_agricole
        ADD COLUMN id_ug_agricole INTEGER
            REFERENCES oeasc_agricole.t_ug_agricole (id_ug_agricole)
        """)
    op.execute("""
        CREATE INDEX idx_t_declaration_agricole_ug_agricole
        ON oeasc_agricole.t_declaration_agricole (id_ug_agricole)
        """)


def downgrade():
    op.execute("""
        ALTER TABLE oeasc_agricole.t_declaration_agricole
        DROP COLUMN id_ug_agricole
        """)
    op.execute("DROP TABLE oeasc_agricole.t_ug_agricole")

    # les cultures ajoutées par l'upgrade sont conservées (elles peuvent être
    # référencées par des déclarations)
    op.execute("ALTER TABLE oeasc_agricole.t_cultures DROP COLUMN id_type_culture")
    op.execute("DROP TABLE oeasc_agricole.t_type_culture")

    op.execute("ALTER TABLE oeasc_agricole.t_cultures RENAME TO t_type_culture")
    op.execute("""
        ALTER TABLE oeasc_agricole.t_type_culture
        RENAME CONSTRAINT t_cultures_pkey TO t_type_culture_pkey
        """)
    op.execute("""
        ALTER TABLE oeasc_agricole.t_type_culture
        RENAME CONSTRAINT t_cultures_nom_culture_key
        TO t_type_culture_nom_culture_key
        """)
    op.execute("""
        ALTER SEQUENCE oeasc_agricole.t_cultures_id_culture_seq
        RENAME TO t_type_culture_id_culture_seq
        """)
