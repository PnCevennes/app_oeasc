"""type_page dans t_contents, suppression de t_tags et cor_content_tag

Le type d'un contenu (actualité ou page) était porté par les tags « actualité » / « page ».
Il devient une colonne `type_page` ('actualite' | 'page') de oeasc_commons.t_contents ; les tables
oeasc_commons.t_tags et oeasc_commons.cor_content_tag sont supprimées.

Revision ID: a4c8e2f61b37
Revises: 7d3f9a1c5e82
Create Date: 2026-11-10

"""

from alembic import op

revision = "a4c8e2f61b37"
down_revision = "7d3f9a1c5e82"
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        "ALTER TABLE oeasc_commons.t_contents "
        "ADD COLUMN IF NOT EXISTS type_page VARCHAR(20) NOT NULL DEFAULT 'page'"
    )
    op.execute("""
        DO $$ BEGIN
            IF EXISTS (
                SELECT 1 FROM information_schema.tables
                WHERE table_schema = 'oeasc_commons' AND table_name = 'cor_content_tag'
            ) THEN
                UPDATE oeasc_commons.t_contents
                SET type_page = 'actualite'
                WHERE id_content IN (
                    SELECT cct.id_content
                    FROM oeasc_commons.cor_content_tag cct
                    JOIN oeasc_commons.t_tags t ON t.id_tag = cct.id_tag
                    WHERE t.nom_tag = 'actualité'
                );
            END IF;
        END $$;
    """)
    op.execute("DROP TABLE IF EXISTS oeasc_commons.cor_content_tag")
    op.execute("DROP TABLE IF EXISTS oeasc_commons.t_tags")


def downgrade():
    op.execute("""
        CREATE TABLE IF NOT EXISTS oeasc_commons.t_tags (
            id_tag SERIAL PRIMARY KEY,
            nom_tag VARCHAR(30),
            code_tag VARCHAR(10)
        )
    """)
    op.execute("""
        CREATE TABLE IF NOT EXISTS oeasc_commons.cor_content_tag (
            id_content INTEGER NOT NULL REFERENCES oeasc_commons.t_contents(id_content),
            id_tag INTEGER NOT NULL REFERENCES oeasc_commons.t_tags(id_tag),
            PRIMARY KEY (id_content, id_tag)
        )
    """)
    op.execute(
        "INSERT INTO oeasc_commons.t_tags (nom_tag, code_tag) "
        "VALUES ('actualité', 'actu'), ('page', 'page')"
    )
    op.execute("""
        INSERT INTO oeasc_commons.cor_content_tag (id_content, id_tag)
        SELECT c.id_content, t.id_tag
        FROM oeasc_commons.t_contents c
        JOIN oeasc_commons.t_tags t
          ON t.nom_tag = CASE c.type_page WHEN 'actualite' THEN 'actualité' ELSE 'page' END
    """)
    op.execute("ALTER TABLE oeasc_commons.t_contents DROP COLUMN IF EXISTS type_page")
