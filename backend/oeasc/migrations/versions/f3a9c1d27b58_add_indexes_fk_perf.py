"""add indexes on foreign keys and join columns (perf)

Revision ID: f3a9c1d27b58
Revises: d8e3a5b71c42
Create Date: 2026-11-25

"""

from alembic import op

revision = "f3a9c1d27b58"
down_revision = "d8e3a5b71c42"
branch_labels = None
depends_on = None

# (nom_index, schema.table, colonne)
INDEXES = [
    # ref_geo.cor_area_intersect : jointures des déclarations (reconstruite par refresh-ref-geo,
    # les mêmes index y sont recréés)
    ("ix_cor_area_intersect_id_parcelle", "ref_geo.cor_area_intersect", "id_parcelle"),
    ("ix_cor_area_intersect_id_commune", "ref_geo.cor_area_intersect", "id_commune"),
    ("ix_cor_area_intersect_id_secteur", "ref_geo.cor_area_intersect", "id_secteur"),
    ("ix_cor_area_intersect_id_foret_onf", "ref_geo.cor_area_intersect", "id_foret_onf"),
    ("ix_cor_area_intersect_id_foret_dgd", "ref_geo.cor_area_intersect", "id_foret_dgd"),
    ("ix_cor_area_intersect_id_foret_prive", "ref_geo.cor_area_intersect", "id_foret_prive"),
    ("ix_cor_area_intersect_id_section_cadastrale", "ref_geo.cor_area_intersect", "id_section_cadastrale"),
    ("ix_cor_area_intersect_id_parcelle_onf", "ref_geo.cor_area_intersect", "id_parcelle_onf"),
    ("ix_cor_hierarchie_area_id_area_parent", "ref_geo.cor_hierarchie_area", "id_area_parent"),
    # chasse
    ("ix_t_attributions_id_saison", "oeasc_chasse.t_attributions", "id_saison"),
    ("ix_t_attributions_id_zone_cynegetique_affectee", "oeasc_chasse.t_attributions", "id_zone_cynegetique_affectee"),
    ("ix_t_attributions_id_zone_indicative_affectee", "oeasc_chasse.t_attributions", "id_zone_indicative_affectee"),
    ("ix_t_attributions_id_type_bracelet", "oeasc_chasse.t_attributions", "id_type_bracelet"),
    ("ix_t_realisations_id_zone_cynegetique_realisee", "oeasc_chasse.t_realisations", "id_zone_cynegetique_realisee"),
    ("ix_t_realisations_id_numerisateur", "oeasc_chasse.t_realisations", "id_numerisateur"),
    # déclarations
    ("ix_t_declarations_id_declarant", "oeasc_declarations.t_declarations", "id_declarant"),
    ("ix_t_declarations_id_foret", "oeasc_declarations.t_declarations", "id_foret"),
    ("ix_t_declarations_id_declaration_originale", "oeasc_declarations.t_declarations", "id_declaration_originale"),
    ("ix_cor_areas_forets_id_area", "oeasc_forets.cor_areas_forets", "id_area"),
]


def upgrade():
    for name, table, col in INDEXES:
        op.execute(f"CREATE INDEX IF NOT EXISTS {name} ON {table} ({col})")
    for table in sorted({t for _, t, _ in INDEXES}):
        op.execute(f"ANALYZE {table}")


def downgrade():
    for name, table, _ in INDEXES:
        schema = table.split(".")[0]
        op.execute(f"DROP INDEX IF EXISTS {schema}.{name}")
