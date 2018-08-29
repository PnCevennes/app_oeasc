SELECT ref_nomenclatures.get_id_nomenclature_type('OASC_TYPE_DEGAT');


--Exemple création table avec champ nomenclature

 CREATE TABLE oeasc.t_alertes (
  id_alerte SERIAL PRIMARY KEY, 
  
  id_nomenclature_type_degat integer NOT NULL, -- lien 1-1
  
  uuid_alerte uuid DEFAULT uuid_generate_v4(),
  
  CONSTRAINT fk_t_alertes_type_degat FOREIGN KEY (id_nomenclature_type_degat)
      REFERENCES ref_nomenclatures.t_nomenclatures (id_nomenclature) MATCH SIMPLE
      ON UPDATE CASCADE ON DELETE NO ACTION,
  CONSTRAINT check_t_alertes_type_degat CHECK (ref_nomenclatures.check_nomenclature_type_by_mnemonique(id_nomenclature_type_degat, 'OASC_TYPE_DEGAT')) NOT VALID
);

--Exemple table correspondance n-m alerte nomenclature

CREATE TABLE oeasc.cor_alerte_degats
(
  id_alerte integer NOT NULL,
  id_nomenclature_type_degat integer NOT NULL,
  CONSTRAINT pk_cor_alerte_degats PRIMARY KEY (id_alerte, id_nomenclature_type_degat),
  CONSTRAINT fk_cor_alerte_degats_id_alerte FOREIGN KEY (id_alerte)
      REFERENCES oeasc.t_alertes (id_alerte) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE CASCADE,
  CONSTRAINT fk_cor_alerte_degats_id_nomenclature_type_degat FOREIGN KEY (id_nomenclature_type_degat)
  REFERENCES ref_nomenclatures.t_nomenclatures (id_nomenclature) MATCH SIMPLE
      ON UPDATE CASCADE ON DELETE NO ACTION,
  CONSTRAINT check_cor_alerte_degats_type_degat CHECK (ref_nomenclatures.check_nomenclature_type_by_mnemonique(id_nomenclature_type_degat, 'OASC_TYPE_DEGAT')) NOT VALID
);
