SELECT id_nomenclature, id_type, cd_nomenclature, mnemonique, label_default, 
       definition_default, label_fr, definition_fr, label_en, definition_en, 
       label_es, definition_es, label_de, definition_de, label_it, definition_it, 
       source, statut, id_broader, hierarchy, meta_create_date, meta_update_date, 
       active
  FROM ref_nomenclatures.t_nomenclatures
  WHERE id_type=9

  SELECT * FROM ref_nomenclatures.bib_nomenclatures_types 
  WHERE id_type = 9