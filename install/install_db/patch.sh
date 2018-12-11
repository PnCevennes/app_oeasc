# patch.sh
. install/install_db/pgsqla.sh

echo "
-- UPDATE utilisateurs.bib_organismes
-- SET nom_organisme='Aucun' WHERE nom_organisme LIKE 'Pas d%'
-- ;

-- INSERT INTO ref_nomenclatures.t_nomenclatures(
--            id_type, cd_nomenclature, mnemonique, 
--            label_default, definition_default, 
--            label_fr, definition_fr, 
--            source)
--    VALUES (ref_nomenclatures.get_id_nomenclature_type('OEASC_DEGAT_TYPE'), 'LIEV', 'Lièv.', 
--        'Dégâts de lièvre', 'Dégâts de lièvre',
--        'Dégâts de lièvre', 'Dégâts de lièvre',
--        'OEASC')
--        ;

DELETE FROM ref_nomenclatures.t_nomenclatures
    WHERE id_type=ref_nomenclatures.get_id_nomenclature_type('OEASC_DEGAT_TYPE')
        AND cd_nomenclature='LIEV'

" | $psqla
