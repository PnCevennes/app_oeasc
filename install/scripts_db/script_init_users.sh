# reinit

if [[ "$ROOT_DIR" = "" ]]; then
    ROOT_DIR=$(readlink -e "${0%/*}")/../..
fi
config_file=${ROOT_DIR}/install/scripts_db/script_config.sh
. $config_file

echo ${0##/*/}

echo "DELETE FROM utilisateurs.t_roles WHERE remarques = 'utilisateur test OEASC'" | psql -t -d $db_name -h $db_host -U $user_pg

echo "SELECT setval('utilisateurs.t_roles_id_role_seq', COALESCE((SELECT MAX(id_role)+1 FROM utilisateurs.t_roles), 1), false);" | psql -t -d $db_name -h $db_host -U $user_pg

id_pnc=$(echo "SELECT id_organisme FROM utilisateurs.bib_organismes WHERE nom_organisme = 'EP PNC'" | psql -t -d $db_name -h $db_host -U $user_pg | awk '{print $1}')
id_jubil=$(echo "SELECT id_organisme FROM utilisateurs.bib_organismes WHERE nom_organisme = 'Jubil Interim'" | psql -t -d $db_name -h $db_host -U $user_pg | awk '{print $1}')
id_onf=$(echo "SELECT id_organisme FROM utilisateurs.bib_organismes WHERE nom_organisme = 'ONF 48'" | psql -t -d $db_name -h $db_host -U $user_pg | awk '{print $1}')
id_particulier=$(echo "SELECT id_organisme FROM utilisateurs.bib_organismes WHERE nom_organisme = 'Particulier'" | psql -t -d $db_name -h $db_host -U $user_pg | awk '{print $1}')

# echo $id_pnc $id_onf $id_jubil $id_particulier

# jubil -1

password="1234"
password_confirmation=$password
remarques="utilisateur test OEASC"
id_app=500


nom_role=CLEMENT
prenom_role=Joel
email=joelclems@gmail
identifiant=$email
id_droit=1
id_organisme=$id_jubil

echo '{"nom_role":"'$nom_role'","prenom_role":"'$prenom_role'","identifiant":"'$identifiant'","email":"'$email'",'\
'"password":"'$password'","password_confirmation":"'$password_confirmation'","applications":[{"id_app":'$id_app',"id_droit":'$id_droit'}],'\
'"groupe":false,"pn":true,"remarques":"'"$remarques"'","desc_role":null,"id_unite":-1,"id_organisme":"'$id_organisme'"}'

curl --header "Content-Type: application/json" \
--request POST \
--data '{"nom_role":"'$nom_role'","prenom_role":"'$prenom_role'","identifiant":"'$identifiant'","email":"'$email'",'\
'"password":"'$password'","password_confirmation":"'$password_confirmation'","applications":[{"id_app":'$id_app',"id_droit":'$id_droit'}],'\
'"groupe":false,"pn":true,"remarques":"'"$remarques"'","desc_role":null,"id_unite":-1,"id_organisme":"'$id_organisme'"}' \
http://localhost:5001/api_register/role

# pnc - agent

nom_role=PNC
prenom_role=agent
email=agent@pnc.frt
identifiant=$email
id_droit=1
id_organisme=$id_pnc

curl --header "Content-Type: application/json" \
--request POST \
--data '{"nom_role":"'$nom_role'","prenom_role":"'$prenom_role'","identifiant":"'$identifiant'","email":"'$email'",'\
'"password":"'$password'","password_confirmation":"'$password_confirmation'","applications":[{"id_app":'$id_app',"id_droit":'$id_droit'}],'\
'"groupe":false,"pn":true,"remarques":"'"$remarques"'","desc_role":null,"id_unite":-1,"id_organisme":"'$id_organisme'"}' \
http://localhost:5001/api_register/role

# pnc - directeur

nom_role=PNC
prenom_role=directeur
email=directeur@pnc.frt
identifiant=$email
id_droit=3
id_organisme=$id_pnc

curl --header "Content-Type: application/json" \
--request POST \
--data '{"nom_role":"'$nom_role'","prenom_role":"'$prenom_role'","identifiant":"'$identifiant'","email":"'$email'",'\
'"password":"'$password'","password_confirmation":"'$password_confirmation'","applications":[{"id_app":'$id_app',"id_droit":'$id_droit'}],'\
'"groupe":false,"pn":true,"remarques":"'"$remarques"'","desc_role":null,"id_unite":-1,"id_organisme":"'$id_organisme'"}' \
http://localhost:5001/api_register/role

# pnc - animateur

nom_role=PNC
prenom_role=animateur
email=animateur@pnc.frt
identifiant=$email
id_droit=4
id_organisme=$id_pnc

curl --header "Content-Type: application/json" \
--request POST \
--data '{"nom_role":"'$nom_role'","prenom_role":"'$prenom_role'","identifiant":"'$identifiant'","email":"'$email'",'\
'"password":"'$password'","password_confirmation":"'$password_confirmation'","applications":[{"id_app":'$id_app',"id_droit":'$id_droit'}],'\
'"groupe":false,"pn":true,"remarques":"'"$remarques"'","desc_role":null,"id_unite":-1,"id_organisme":"'$id_organisme'"}' \
http://localhost:5001/api_register/role

# pnc - administrateur

nom_role=PNC
prenom_role=administrateur
email=administrateur@pnc.frt
identifiant=$email
id_droit=6
id_organisme=$id_pnc

curl --header "Content-Type: application/json" \
--request POST \
--data '{"nom_role":"'$nom_role'","prenom_role":"'$prenom_role'","identifiant":"'$identifiant'","email":"'$email'",'\
'"password":"'$password'","password_confirmation":"'$password_confirmation'","applications":[{"id_app":'$id_app',"id_droit":'$id_droit'}],'\
'"groupe":false,"pn":true,"remarques":"'"$remarques"'","desc_role":null,"id_unite":-1,"id_organisme":"'$id_organisme'"}' \
http://localhost:5001/api_register/role


# onf - agent

nom_role=ONF
prenom_role=agent
email=agent@onf.frt
identifiant=$email
id_droit=1
id_organisme=$id_onf

curl --header "Content-Type: application/json" \
--request POST \
--data '{"nom_role":"'$nom_role'","prenom_role":"'$prenom_role'","identifiant":"'$identifiant'","email":"'$email'",'\
'"password":"'$password'","password_confirmation":"'$password_confirmation'","applications":[{"id_app":'$id_app',"id_droit":'$id_droit'}],'\
'"groupe":false,"pn":true,"remarques":"'"$remarques"'","desc_role":null,"id_unite":-1,"id_organisme":"'$id_organisme'"}' \
http://localhost:5001/api_register/role

# onf directeur

nom_role=ONF
prenom_role=directeur
email=directeur@onf.frt
identifiant=$email
id_droit=3
id_organisme=$id_onf

curl --header "Content-Type: application/json" \
--request POST \
--data '{"nom_role":"'$nom_role'","prenom_role":"'$prenom_role'","identifiant":"'$identifiant'","email":"'$email'",'\
'"password":"'$password'","password_confirmation":"'$password_confirmation'","applications":[{"id_app":'$id_app',"id_droit":'$id_droit'}],'\
'"groupe":false,"pn":true,"remarques":"'"$remarques"'","desc_role":null,"id_unite":-1,"id_organisme":"'$id_organisme'"}' \
http://localhost:5001/api_register/role
