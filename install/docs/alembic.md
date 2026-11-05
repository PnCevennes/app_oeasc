[habitats]
  [ ] ─ 62e63cd6135d create ref_habitats schema
[habitats_inpn_data]
  [ ] ┰ 46e91e738845 insert inpn data in ref_habitats schema
  [ ] ┸ 805442837a68 correction on habref data
[nomenclatures ✓]
  [x] ┰ 6015397d686a create ref_nomenclature schema 1.3.9
  [x] ┃ 11e7741319fd fix ref_nomenclatures.get_default_nomenclature_value
  [x] ┃ f8c2c8482419 fix ref_nomenclatures.get_default_nomenclature_value
  [x] ┸ b820c66d8daa fix ref_nomenclatures.get_nomenclature_label
[nomenclatures_inpn_data]
  [ ] ┰ 96a713739fdd insert inpn data in ref_nomenclatures
  [ ] ┃ 618542880d1f fix typo in nomenclature type definition
  [ ] ┃ ee1146f6c0f4 Add UICN Red List
  [ ] ┸ 5e882af04ff6 add_nomenclatures_for_occhab
[nomenclatures_taxonomie]
  [ ] ┰ f5436084bf17 add support for taxonomy into ref_nomenclatures
  [ ] ┸ 803524258bd3 add group3_inpn cor_taxref_nomenclature
[nomenclatures_taxonomie_data]
  [ ] ─ a763fb554ff2 insert taxonomic filtering data in ref_nomenclatures.cor_taxref_nomenclatures
[oeasc ✓]
  [x] ┰ 8857f2169f96 Install oeasc
  [x] ┃ 3fc01cbe83a2 migration utilisateurs f9d3b95946cd. Supprime les view en conflit
  [x] ┸ f90cb83dcdfb migration f9d3b95946cd. restitue les vues en conflits après la migration utilisateur
[ref_geo]
  [ ] ┰ 6afe74833ed0 ref_geo schema
  [ ] ┃ e0ac4c9f5c0a add indexes on FK referencing l_areas.id_area
  [ ] ┃ 4882d6141a41 add regions in area types
  [ ] ┃ 681306b27407 fix altitude trigger
  [ ] ┃ cb038e76d59c fix functions local srid
  [ ] ┃ f7374cd6e38d add linears
  [ ] ┃ dea1645de8c0 Référentiel point, cor (area, linear, point)
  [ ] ┃ 795f6ea8ec45 cor_areas & cor_linear_areas
  [ ] ┃ bc2fcc772b46 Add column LAreas.geom_4326
  [ ] ┃ f22d70b8fcfa add areas types size hierarchy
  [ ] ┸ 1fdac7036dd9 Rewrite function ref_geo.fct_get_altitude_intersection
[ref_geo_fr_departments]
  [ ] ─ 3fdaa1805575 Insert French departments in ref_geo
[ref_geo_fr_municipalities]
  [ ] ┰ 0dfdbfbccd63 Insert French municipalities in ref_geo
  [ ] ┸ fda887e7b578 empty message
[ref_geo_fr_regions]
  [ ] ─ d02f4563bebe Insert French regions in ref_geo
[ref_geo_fr_regions_1970]
  [ ] ─ 05a0ae652c13 Insert French regions 1970-2016 in ref_geo
[ref_geo_inpn_grids_1]
  [ ] ─ 586613e2faeb Insert INPN 1×1 grids in ref_geo
[ref_geo_inpn_grids_10]
  [ ] ─ ede150d9afd9 Insert INPN 10×10 grids in ref_geo
[ref_geo_inpn_grids_2]
  [ ] ─ 175cdb17343f Insert INPN 2x2 grids in ref_geo
[ref_geo_inpn_grids_20]
  [ ] ─ 10a587fb63d1 Insert INPN 20×20 grids in ref_geo
[ref_geo_inpn_grids_5]
  [ ] ─ 7d6e98441e4c Insert INPN 5×5 grids in ref_geo
[ref_geo_inpn_grids_50]
  [ ] ─ 4d0c35ea0cfe Insert INPN 50×50 grids in ref_geo
[sql_utils ×]
  [x] ┰ 3842a6d800a0 Add public shared functions
  [ ] ┸ ba207b468e31 create fr_numeric collation
[taxhub-standalone]
  [ ] ┰ fa5a90853c45 Taxhub standalone samples: add Taxhub to utilisateurs schema
  [ ] ┃ 64d38dbe7739 taxonomie
  [ ] ┸ 1f7b958108ed Remove code_profil 3, 4
[taxhub-standalone-sample]
  [ ] ─ 3fe8c07741be Taxhub standalone samples: add profile to Grp_admin
[taxonomie]
  [ ] ┰ 9c2c0254aadc create taxonomie schema version 1.8.1
  [ ] ┃ 7540702c6407 cd_ref utility functions
  [ ] ┃ 98035939bc0d find_all_taxons_parents
  [ ] ┃ c93cbb35cfe4 set default value for id_liste
  [ ] ┃ 4fb7e197d241 create taxonomie.v_bdc_status view
  [ ] ┃ d768a5da908c add bdc_status indexes
  [ ] ┃ 4a549132d156 Add unique constraints
  [ ] ┃ c4415009f164 Taxref v15 db structure
  [ ] ┃ 1b1a3f5cd107 Add table to link bdc_status and ref_geo
  [ ] ┃ f2c36312b3de fix vm_taxref_for_autocomplete
  [ ] ┃ 27fd7e2b4b79 Add vm_taxref_list_forautocomplete index
  [ ] ┃ 188bc535258a Drop old status table
  [ ] ┃ 23c25552d707 Create bdc_status_table if not exists
  [ ] ┃ 6607b25b2d66 Taxref : set null to empty string
  [ ] ┃ 3bd542b72955 optimize_vm_taxref_for_autocomplete
  [ ] ┃ 32c5ed42bdbd Add table: t_meta_taxref
  [ ] ┃ 33e20a7682b4 check_group3_inpn_vm_and_function
  [ ] ┃ 8f3256f60915 group3_inpn_autocomplete
  [ ] ┃ b7d734f490ff delete bib_noms dependancies (cor_nom_liste)
  [ ] ┃ b9e157ffd8be Change tmedia before insert trigger
  [ ] ┃ 633e0ad4c4e3 Save bib_noms data
  [ ] ┃ f6abb7857493 delete bib_noms
  [ ] ┃ 1cf2cdc94f9b Delete attributesviews_per_kingdom
  [ ] ┃ 5cef20a05a20 remove picto
  [ ] ┃ a982df406ae8 remove t admin log
  [ ] ┃ 52d1b5dd965e strip static/media from path
  [ ] ┃ 0db13d65cb27 fix nom_vern in vm_taxref_list_forautocomplete
  [ ] ┃ b250cfcaab64 set field liste_valeur_attribut nullable
  [ ] ┃ 44447746cacc drop t_medias.supprime column
  [ ] ┃ 6a20cd1055ec Drop bib_themes.id_droit column
  [ ] ┃ 83d7105edb76 create vm_taxref_tree v1
  [ ] ┃ 3c4762751898 create vm_taxref_tree v2
  [ ] ┸ 2c68a907f74c increase t_medias.source size
[utilisateurs ✓]
  [x] ┰ fa35dfe5ff27 utilisateurs schema 1.4.7 (usershub 2.1.3)
  [x] ┃ 830cc8f4daef add additional_data field to bib_organismes
  [x] ┃ 5b334b77f5f5 fix v_roleslist_forall_applications
  [x] ┃ 951b8270a1cf add unique constraint on bib_organismes.uuid_organisme
  [x] ┃ 10e87bc144cd get_id_role_by_name()
  [x] ┃ 112ccf1024ce add unique constraint on t_roles UUID
  [x] ┃ f4bf21ac6238 fix temp user organism size
  [x] ┃ f9d3b95946cd set code_profil in integer
  [x] ┃ b7c98935d9e8 add provider table and correspondances table with t_roles
  [x] ┃ cf38131bc247 Add meta create/insert date to biborganismes
  [x] ┸ b3dec57f13d8 add drop on cascade on cor_role_provider.id_role
[utilisateurs-samples]
  [ ] ─ 72f227e37bdf utilisateurs sample data