

if [[ "$ROOT_DIR" = "" ]]; then
    ROOT_DIR=$(readlink -e "${0%/*}")/../..
fi

settings_file=${ROOT_DIR}/config/settings.ini

. $settings_file

export PGPASSWORD=$user_pg_pass

sql_dir=install/scripts_db
dir_data=${ROOT_DIR}/data

config_csv=$ROOT_DIR/$sql_dir/config.csv

cat <<EOF > $config_csv
OEASC_ONF_FRT forets_gestion_onf_pec            CP1250          "dept,'-',ccod_frt"                                     "dept,'-',llib_frt"
OEASC_ONF_PRF parcellaire_foret_publique_pec    CP1250          "dept,'-',ccod_frt,'-',ccod_prf"                        "ccod_prf,'-',llib_prf"
OEASC_ONF_UG  unites_gestion_foret_publique_pec latin1          "dept,'-',ccod_frt,'-',ccod_prf,'-',ccod_ug,'-',suffix" "ccod_prf,'-',ccod_ug,'_',suffix"
OEASC_DGD documents_gestion_durable_pec         ISO-8859-1      "forid,'-',proref"                                                "forinsee,'-',fornom"
OEASC_CADASTRE  cadastre_pec                      windows-1250    "insee_com,'-',section,'-',num_parc" "insee_com,'-',section,'-',num_parc"
EOF


list_name=$(awk '{print $1}' $config_csv)
for name in $list_name
do
eval table_$name=l_$name
eval shp_$name=$(awk '{if($1=="'$name'") {print $2}}' $config_csv)
eval codage_$name=$(awk '{if($1=="'$name'") {print $3}}' $config_csv)
eval keys_$name=$(awk '{if($1=="'$name'") {print $4}}' $config_csv)
eval keys_label_$name=$(awk '{if($1=="'$name'") {print $5}}' $config_csv)
done
