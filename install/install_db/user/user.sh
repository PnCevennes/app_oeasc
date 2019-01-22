

cp $dir_data/csv/user/*.csv /tmp/.
echo oeasc_populate_organismes >> $log_file
$psqla -f $dir_script/oeasc/oeasc_populate_organismes.sql >> $log_file

echo init user >> $log_file

md5_admin_oeasc=$(echo -n $ADMIN_APPLICATION_PASSWORD | md5sum | awk '{print "'\''" $1 "'\''"}')
sha1_admin_oeasc=$(htpasswd -bnBC 10 "" $ADMIN_APPLICATION_PASSWORD | tr -d ':\n')
sha1_admin_oeasc="'"${sha1_admin_oeasc}"'"
# export FLASK_APP=server.py
# . venv/bin/activate

# sha1_admin_oeasc="'"$(flask password_hash $ADMIN_APPLICATION_PASSWORD)"'"


identifiant_admin_oeasc="'"${ADMIN_APPLICATION_LOGIN}"'"
email_admin_oeasc="'"${ADMIN_APPLICATION_MAIL}"'"

# creation des tables d'utilisateurs temporaires
$psqla -f $dir_script/user/temp_user.sql >> $log_file

id_pnc=$(echo "SELECT id_organisme FROM utilisateurs.bib_organismes WHERE nom_organisme = 'Parc national des Cévennes'" | psql -t -d $db_name -h $db_host -U $user_pg | awk '{print $1}')
id_jubil=$(echo "SELECT id_organisme FROM utilisateurs.bib_organismes WHERE nom_organisme = 'Jubil Interim'" | psql -t -d $db_name -h $db_host -U $user_pg | awk '{print $1}')
id_onf=$(echo "SELECT id_organisme FROM utilisateurs.bib_organismes WHERE nom_organisme = 'ONF 48'" | psql -t -d $db_name -h $db_host -U $user_pg | awk '{print $1}')
id_particulier=$(echo "SELECT id_organisme FROM utilisateurs.bib_organismes WHERE nom_organisme = 'Particulier'" | psql -t -d $db_name -h $db_host -U $user_pg | awk '{print $1}')

col_id_pnc="'"$id_pnc"'"

cat << EOF | $psqla >> $log_file

DELETE FROM utilisateurs.t_applications WHERE nom_application='OEASC' OR id_application=500;

-- add application

INSERT INTO utilisateurs.t_applications(
            id_application, nom_application, desc_application)
    VALUES (500, 'OEASC', 'application oeasc');

-- DELETE FROM utilisateurs.cor_role_droit_application WHERE id_role=1 and id_application=500;

-- ajout des droit pour admin
INSERT INTO utilisateurs.cor_role_droit_application(id_role, id_droit, id_application)
    VALUES (1, 6, 500);

-- creation utilisateur admin_oeasc avec droits pour userhub

DELETE FROM utilisateurs.cor_role_droit_application as c
    USING utilisateurs.t_roles as r
    WHERE r.id_role = c.id_role
        AND r.identifiant=$identifiant_admin_oeasc;

DELETE FROM utilisateurs.t_roles
    WHERE identifiant=$identifiant_admin_oeasc;

SELECT setval('utilisateurs.t_roles_id_role_seq', COALESCE((SELECT MAX(id_role)+1 FROM utilisateurs.t_roles), 1), false);

INSERT INTO utilisateurs.t_roles(identifiant, nom_role, pass, pass_plus, email, id_organisme, organisme)
    VALUES ($identifiant_admin_oeasc, 'Admin_OEASC', $md5_admin_oeasc, $sha1_admin_oeasc, $email_admin_oeasc, $col_id_pnc, 'PNC');

-- ajout droits OEASC (6)
INSERT INTO utilisateurs.cor_role_droit_application(id_role, id_droit, id_application)
    (SELECT id_role, 6, 500
        FROM utilisateurs.t_roles
        WHERE identifiant=$identifiant_admin_oeasc);

-- ajout droits USERSHUB (5)
INSERT INTO utilisateurs.cor_role_droit_application(id_role, id_droit, id_application)
    (SELECT r.id_role, 5, a.id_application
        FROM utilisateurs.t_roles as r, utilisateurs.t_applications as a
        WHERE r.identifiant = $identifiant_admin_oeasc
        AND a.nom_application = 'UsersHub');
EOF

if [ "cpasvrai" == "ouicpasvrai" ]
then

password="1234"
password_confirmation=$password
remarques="utilisateur test OEASC"
id_app=500

# pnc - agent

nom_role=CLEMENT
prenom_role=Joel
email=testdelesite@gmail.com
identifiant=$email
id_droit=1
id_organisme=$id_pnc

curl --header "Content-Type: application/json" \
--request POST \
--data '{"nom_role":"'$nom_role'","prenom_role":"'$prenom_role'","identifiant":"'$identifiant'","email":"'$email'",'\
'"password":"'$password'","password_confirmation":"'$password_confirmation'","applications":[{"id_app":'$id_app',"id_droit":'$id_droit'}],'\
'"groupe":false,"pn":true,"remarques":"'"$remarques"'","desc_role":"Agent","id_unite":-1,"id_organisme":"'$id_organisme'"}' \
$URL_USERHUB/api_register/role


nom_role=Nacer
prenom_role=Vidais
email=agent@pnc.frt
identifiant=$email
id_droit=1
id_organisme=$id_pnc

curl --header "Content-Type: application/json" \
--request POST \
--data '{"nom_role":"'$nom_role'","prenom_role":"'$prenom_role'","identifiant":"'$identifiant'","email":"'$email'",'\
'"password":"'$password'","password_confirmation":"'$password_confirmation'","applications":[{"id_app":'$id_app',"id_droit":'$id_droit'}],'\
'"groupe":false,"pn":true,"remarques":"'"$remarques"'","desc_role":"Agent","id_unite":-1,"id_organisme":"'$id_organisme'"}' \
$URL_USERHUB/api_register/role


# pnc - directeur

nom_role=Vincent
prenom_role=GLILLET
email=directeur@pnc.frt
identifiant=$email
id_droit=3
id_organisme=$id_pnc

curl --header "Content-Type: application/json" \
--request POST \
--data '{"nom_role":"'$nom_role'","prenom_role":"'$prenom_role'","identifiant":"'$identifiant'","email":"'$email'",'\
'"password":"'$password'","password_confirmation":"'$password_confirmation'","applications":[{"id_app":'$id_app',"id_droit":'$id_droit'}],'\
'"groupe":false,"pn":true,"remarques":"'"$remarques"'","desc_role":"Directeur","id_unite":-1,"id_organisme":"'$id_organisme'"}' \
$URL_USERHUB/api_register/role



# pnc - animateur

nom_role=José
prenom_role=CORSAGE
email=animateur@pnc.frt
identifiant=$email
id_droit=4
id_organisme=$id_pnc

curl --header "Content-Type: application/json" \
--request POST \
--data '{"nom_role":"'$nom_role'","prenom_role":"'$prenom_role'","identifiant":"'$identifiant'","email":"'$email'",'\
'"password":"'$password'","password_confirmation":"'$password_confirmation'","applications":[{"id_app":'$id_app',"id_droit":'$id_droit'}],'\
'"groupe":false,"pn":true,"remarques":"'"$remarques"'","desc_role":"Animateur","id_unite":-1,"id_organisme":"'$id_organisme'"}' \
$URL_USERHUB/api_register/role


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
'"groupe":false,"pn":true,"remarques":"'"$remarques"'","desc_role":"Animateur","id_unite":-1,"id_organisme":"'$id_organisme'"}' \
$URL_USERHUB/api_register/role



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
'"groupe":false,"pn":true,"remarques":"'"$remarques"'","desc_role":"Agent","id_unite":-1,"id_organisme":"'$id_organisme'"}' \
$URL_USERHUB/api_register/role


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
'"groupe":false,"pn":true,"remarques":"'"$remarques"'","desc_role":"Directeur","id_unite":-1,"id_organisme":"'$id_organisme'"}' \
$URL_USERHUB/api_register/role

fi
