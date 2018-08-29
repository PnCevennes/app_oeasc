#script_oeasc_bib_nomenclature_csv.sh

f=$1

tmp_sql=/tmp/tmp_nom.sql

cat <<EOF >$tmp_sql
INSERT INTO ref_nomenclatures.bib_nomenclatures_types (mnemonique, label_default, definition_default, label_fr, definition_fr, source, statut)
    VALUES
EOF

statut=\'Validé\'


while IFS=';' read mnemonique label definition source
do
    if [ "$mnemonique" = "" ]
    then
        continue
    fi

    echo "($mnemonique, $label, $definition, $label, $definition, $source, $statut),"

done < $f >> $tmp_sql

# remplace la derniere virgule du fichier par un point virgule
sed '$s/,$/;/' $tmp_sql
