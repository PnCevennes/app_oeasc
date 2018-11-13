# install_ref_geo.sh

# load shell functions
. ${dir_script}/ref_geo/fonctions_ref_geo.sh

# add li_areas and others
# echo "DROP TABLE IF EXISTS ref_geo.li_areas" | $psqla >> $log_file
$psqla -f $dir_script/ref_geo/ref_geo.sql >> $log_file


# pour chaque geometries à importer
#
# import_shp : importe le contenu du shp du une table temporaire, corrige les typos et les geometries
#
# merge_by_code : regroupe les geometries qui ont le meme code pour eviter les doublons
#
# clean : efface les fichers
#
#
# les fonctions ci dessus sont definies dans le fichier install/install_db/ref_geo/fonctions_ref_geo.sh


echo process geometries

modifs=0

# clear_geometry OEASC_ONF_FRT
# clear_geometry OEASC_DGD
# clear_geometry OEASC_COMMUNE
# clear_geometry OEASC_ONF_UG

if [ "$reset_geom" == "true" ] || [ "$GEOM_TO_CLEAR" == "all" ]
then

echo reinit geometries
clear_all

fi

if [ "$GEOM_TO_CLEAR" != "" ]
then

clear_geometry $GEOM_TO_CLEAR

fi

reinit_seq_l_areas
#Perimetres

#OEASC
name=OEASC_PERIMETRE

keys_code="'OEASC_PERIMETRE'"
keys_name="'Périmètre OEASC'"
keys_label=$keys_name

keys_dept="''"
keys_surf="surf_ha"

shp_file=${dir_data}/Zonage_OEASC/Perimetre_OEASC
shp_coding=ISO-8859-1

label_file=""

type_name="Périmètre de l''OEASC"
type_desc="Périmètre de l''OEASC"

merge=0
index=0
select=0

# clear_geometry $name
process_geom $name
simplify_geom $name 50

#ZCPNC

name=ZC_PNC

keys_code="'$name'"
keys_name="nom"
keys_label=$keys_name

keys_dept="''"
keys_surf="ha_arrete"

shp_file=${dir_data}/limites_pnc/zone_coeur
shp_coding=ISO-8859-1

label_file=""

type_name="Zone coeur du PNC"
type_desc="Zone coeur du PNC"

merge=0
index=0
select=0

# clear_geometry $name
process_geom $name
simplify_geom $name 50

name=AA_PNC

keys_code="'$name'"
keys_name="nom"
keys_label=$keys_name

keys_dept="''"
keys_surf="surf_ha"

shp_file=${dir_data}/limites_pnc/aire_adhesion
shp_coding=ISO-8859-1

label_file=""

type_name="Aire d''adhésion du PNC"
type_desc="Aire d''adhésion du PNC"

merge=0
index=0
select=0

# clear_geometry $name
process_geom $name
simplify_geom $name 50

#MASSIF OEASC

name=OEASC_SECTEUR

keys_code="zon_cyneg"
keys_name=$keys_code
keys_label=$keys_name

keys_dept="''"
keys_surf="surf_ha"

shp_file=${dir_data}/Zonage_OEASC/Secteurs_etude_OEASC
shp_coding=ISO-8859-1

label_file=""

type_name="Secteurs / Massifs OEASC"
type_desc="Secteurs / Massifs OEASC"

merge=0
index=0
select=0

# clear_geometry $name
process_geom $name
# simplify_topology_geom $name 10
simplify_geom $name 50

# correction nom
echo "UPDATE ref_geo.li_areas SET label = 'Mont Aigoual' WHERE area_name = 'Aigoual'" | $psqla >> $log_file



#AA

#COMMUNES

process_communes
simplify_topology_geom OEASC_COMMUNE 50




#ONF_FRT

name=OEASC_ONF_FRT

keys_code="CONCAT(dept,'-',ccod_frt)"
keys_name="llib_frt"
keys_label="CONCAT(dept,'-',llib_frt)"

keys_dept="dept"
keys_surf="qsret_frt"

shp_file=${dir_data}/donnees_gestion_foret/forets_gestion_onf_pec
shp_coding=CP1250

label_file=${dir_data}/csv/foret/liens_foret_onf_nom_propre.csv

type_name="Forêts ONF"
type_desc="Forêts relevant du régime forestier"

merge=1
index=0
select=1


# clear_geometry $name
process_geom
simplify_topology_geom OEASC_ONF_FRT 50


#ONF PRF
# OEASC_ONF_PRF   parcellaire_foret_publique_pec      CP1250          "dept,'-',ccod_frt,'-',ccod_prf"                        "ccod_prf"

name=OEASC_ONF_PRF

keys_code="CONCAT(dept,'-',ccod_frt,'-',ccod_prf)"
keys_name="ccod_prf"
keys_label="ccod_prf"

keys_dept="dept"
keys_surf="qsret_prf"

shp_file=${dir_data}/donnees_gestion_foret/parcellaire_foret_publique_pec
shp_coding=CP1250

label_file=""

type_name="Parcelles ONF"
type_desc="parcelles de forêt relevant du régime forestier"

merge=1
index=0
select=1

# clear_geometry    $name
process_geom
simplify_geom OEASC_ONF_PRF 10


#ONF UG
# OEASC_ONF_UG    unites_gestion_foret_publique_pec   latin1          "dept,'-',ccod_frt,'-',ccod_prf,'-',ccod_ug,'-',suffix" "ccod_prf,'-',ccod_ug,'_',suffix"

name=OEASC_ONF_UG

keys_code="ref_geo.clean_ug_name(CONCAT(dept,'-',ccod_frt,'-',ccod_prf,'-',ccod_ug,'-',suffix))"
keys_name="ref_geo.clean_ug_name(CONCAT(ccod_prf,'-',ccod_ug,'_',suffix))"
keys_label="ref_geo.clean_ug_name(CONCAT(ccod_prf,'-',ccod_ug,'_',suffix))"

keys_dept="dept"
keys_surf="qsret_ugs"

shp_file=${dir_data}/donnees_gestion_foret/unites_gestion_foret_publique_pec
shp_coding=latin1

label_file=""

type_name="Unités de gestion ONF"
type_desc="Unités de gestion relevant du régime forestier"

merge=0
index=1
select=1

# clear_geometry    $name
process_geom
simplify_geom OEASC_ONF_UG 10



#DGD

name=OEASC_DGD

keys_code="CONCAT(forid,'-',proref)"
keys_name="fornom"
keys_label="CONCAT(forinsee,'-',fornom)"

keys_dept="SUBSTRING(forinsee,1,2)"
keys_surf="prosur"

shp_file=${dir_data}/donnees_gestion_foret/documents_gestion_durable_pec
shp_coding=ISO-8859-1


label_file=${dir_data}/csv/foret/liens_dgd_nom_propre.csv

type_name="Forêts DGD"
type_desc="Forêts relevant du régime privé et possédant un document de gestion durable"

merge=0
index=0
select=1

# clear_geometry $name
process_geom
simplify_topology_geom OEASC_DGD 10


# OEASC_CADASTRE  cadastre_pec                        windows-1250    "insee_com,'-',section,'-',num_parc"                    "insee_com,'-',section,'-',num_parc"

name=OEASC_CADASTRE

keys_code="CONCAT(insee_com,'-',section,'-',num_parc)"
keys_name="CONCAT(insee_com,'-',section,'-',num_parc)"
keys_label="CONCAT(insee_com,'-',section,'-',num_parc)"

keys_dept="SUBSTRING(insee_com,1,2)"
keys_surf="surf_parc"

shp_file=${dir_data}/donnees_gestion_foret/cadastre_pec
shp_coding=windows-1250


label_file=""

type_name="Parcelles cadastrales"
type_desc="Parcelles cadastrales"

merge=0
index=0
select=1

# clear_geometry $name
process_geom
simplify_geom OEASC_CADASTRE 5


# OEASC SECTION

name=OEASC_SECTION

create_sections
simplify_geom OEASC_SECTION 50

reinit_index

process_cor_old_communes
process_cor_dgd_cadastre

# OEASC_ONF_FRT   forets_gestion_onf_pec              CP1250          "dept,'-',ccod_frt"                                     "dept,'-',llib_frt"
# OEASC_ONF_PRF   parcellaire_foret_publique_pec      CP1250          "dept,'-',ccod_frt,'-',ccod_prf"                        "ccod_prf"
# OEASC_ONF_UG    unites_gestion_foret_publique_pec   latin1          "dept,'-',ccod_frt,'-',ccod_prf,'-',ccod_ug,'-',suffix" "ccod_prf,'-',ccod_ug,'_',suffix"
# OEASC_DGD       documents_gestion_durable_pec       ISO-8859-1      "forid,'-',proref"                                      "forinsee,'-',fornom"
# OEASC_CADASTRE  cadastre_pec                        windows-1250    "insee_com,'-',section,'-',num_parc"                    "insee_com,'-',section,'-',num_parc"
