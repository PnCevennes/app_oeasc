
if [[ "$ROOT_DIR" = "" ]]; then
    ROOT_DIR=$(readlink -e "${0%/*}")/../../..
fi
config_file=${ROOT_DIR}/install/scripts_db/script_config.sh
. $config_file


cat << EOF

DROP SCHEMA IF EXISTS oeasc CASCADE;

DELETE FROM ref_nomenclatures.t_nomenclatures
    WHERE source = 'OEASC';

DELETE FROM ref_nomenclatures.bib_nomenclatures_types
    WHERE source = 'OEASC';

EOF


echo '-- table ref_nomenclatures.bib_nomenclatures_types'

f_sh=${ROOT_DIR}/install/scripts_db/script_nomenclature/script_oeasc_bib_nomenclature_csv.sh
f_csv=${ROOT_DIR}/install/scripts_db/script_nomenclature/oeasc_bib_nomenclature.csv

$f_sh $f_csv


echo '-- table ref_nomenclatures.bib_nomenclatures_types'

f_sh=${ROOT_DIR}/install/scripts_db/script_nomenclature/script_oeasc_nomenclature_csv.sh
f_csv=${ROOT_DIR}/install/scripts_db/script_nomenclature/oeasc_nomenclature.csv

$f_sh $f_csv

