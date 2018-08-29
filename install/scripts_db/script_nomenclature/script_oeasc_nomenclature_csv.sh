#script_oeasc_nomenclature_csv.sh

f=$1

tmp_sql=/tmp/tmp_nom.sql

cat <<EOF >$tmp_sql

INSERT INTO ref_nomenclatures.t_nomenclatures (id_type, cd_nomenclature, mnemonique,
label_default, definition_default, label_fr, definition_fr,
source, statut)
    VALUES
EOF



n_line=$(cat $f | wc -l)

statut=\'Validé\'

code_type_cur=""

cpt=0

line=""

while IFS=';' read code_type mnemonique label definition source
do

    if [ "$code_type" = "" ]
    then
        continue
    fi

    cpt=`expr $cpt + 1`

    if [ "$code_type" != "$code_type_cur" ]
    then
        cpt=1
        code_type_cur=$code_type
    fi

    cd_nomenclature=$cpt
    echo "(ref_nomenclatures.get_id_nomenclature_type($code_type), $cd_nomenclature, $mnemonique, $label, $definition, $label, $definition, $source, $statut)",

done < $f >> $tmp_sql

# remplace la derniere virgule du fichier par un point virgule
sed '$s/,$/;/' $tmp_sql

