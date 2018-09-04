# reinit

if [[ "$ROOT_DIR" = "" ]]; then
    ROOT_DIR=$(readlink -e "${0%/*}")/../..
fi
config_file=${ROOT_DIR}/install/scripts_db/script_config.sh
. $config_file

echo ${0##/*/}

id_pnc=$(echo "SELECT id_organisme FROM utilisateurs.bib_organismes WHERE nom_organisme = 'EP PNC'" | psql -t -d $db_name -h $db_host -U $user_pg | awk '{print $1}')
id_jubil=$(echo "SELECT id_organisme FROM utilisateurs.bib_organismes WHERE nom_organisme = 'Jubil Interim'" | psql -t -d $db_name -h $db_host -U $user_pg | awk '{print $1}')
id_onf=$(echo "SELECT id_organisme FROM utilisateurs.bib_organismes WHERE nom_organisme = 'ONF 48'" | psql -t -d $db_name -h $db_host -U $user_pg | awk '{print $1}')
id_particulier=$(echo "SELECT id_organisme FROM utilisateurs.bib_organismes WHERE nom_organisme = 'Particulier'" | psql -t -d $db_name -h $db_host -U $user_pg | awk '{print $1}')
# echo "SELECT id_organisme FROM utilisateurs.bib_organismes WHERE nom_organisme = 'EP PNC'" | psql -t -d $db_name -h $db_host -U $user_pg

echo $id_pnc $id_onf $id_jubil $id_particulier

# exit 1;

# jubil -1

curl --header "Content-Type: application/json" \
--request POST \
--data '{"nom_role":"CLEMENT","prenom_role":"Joel","identifiant":"joelclems@gmail.com","email":"joelclems@gmail.com","password":"1234","password_confirmation":"1234","applications":[{"id_app":500,"id_droit":1}],"groupe":false,"pn":true,"remarques":"utilisateur test OEASC","desc_role":null,"id_unite":-1,"id_organisme":"'$id_jubil'"}' \
http://localhost:5001/api_register/role


# pnc -agent 1

curl --header "Content-Type: application/json" \
--request POST \
--data '{"nom_role":"DUPARC","prenom_role":"Lagent","identifiant":"agent@pnc-oeasc.fr","email":"agent@pnc-oeasc.fr","password":"1234","password_confirmation":"1234","applications":[{"id_app":500,"id_droit":1}],"groupe":false,"pn":true,"remarques":"utilisateur test OEASC","desc_role":null,"id_unite":-1,"id_organisme":"'$id_pnc'"}' \
http://localhost:5001/api_register/role

# pnc administrateur 6

curl --header "Content-Type: application/json" \
--request POST \
--data '{"nom_role":"DUPARC","prenom_role":"admin","identifiant":"admin@pnc-oeasc.fr","email":"admin@pnc-oeasc.fr","password":"1234","password_confirmation":"1234","applications":[{"id_app":500,"id_droit":6}],"groupe":false,"pn":true,"remarques":"utilisateur test OEASC","desc_role":null,"id_unite":-1,"id_organisme":"'$id_pnc'"}' \
http://localhost:5001/api_register/role


# ONF -agent 1

curl --header "Content-Type: application/json" \
--request POST \
--data '{"nom_role":"DELONF","prenom_role":"Lagent","identifiant":"agent@onf-oeasc.fr","email":"agent@onf-oeasc.fr","password":"1234","password_confirmation":"1234","applications":[{"id_app":500,"id_droit":1}],"groupe":false,"pn":true,"remarques":"utilisateur test OEASC","desc_role":null,"id_unite":-1,"id_organisme":"'$id_onf'"}' \
http://localhost:5001/api_register/role


# ONF directeur 4

curl --header "Content-Type: application/json" \
--request POST \
--data '{"nom_role":"DELONF","prenom_role":"admin","identifiant":"admin@onf-oeasc.fr","email":"admin@onf-oeasc.fr","password":"1234","password_confirmation":"1234","applications":[{"id_app":500,"id_droit":4}],"groupe":false,"pn":true,"remarques":"utilisateur test OEASC","desc_role":null,"id_unite":-1,"id_organisme":"'$id_onf'"}' \
http://localhost:5001/api_register/role

# particulier

curl --header "Content-Type: application/json" \
--request POST \
--data '{"nom_role":"DUCAUSSE","prenom_role":"Roger","identifiant":"roger@particulier-oeasc.fr","email":"roger@particulier-oeasc.fr","password":"1234","password_confirmation":"1234","applications":[{"id_app":500,"id_droit":1}],"groupe":false,"pn":true,"remarques":"utilisateur test OEASC","desc_role":null,"id_unite":-1,"id_organisme":"'$id_particulier'"}' \
http://localhost:5001/api_register/role
