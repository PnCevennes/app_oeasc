# script d'installation de la base donnée pour l'oeasc

usage ()
{
    echo 'Usage install.sh'
    echo 'Options :'
    echo '    -remove-venv : remove the venv directory'
    exit
}

DB_TYPE="all"
GEOM_TO_CLEAR=""

while getopts ":ht:g:" opt; do
    case $opt in
        h)
            usage
            exit 1
            ;;
        t)
            DB_TYPE="${OPTARG}"
            ;;
        g)
            GEOM_TO_CLEAR="${OPTARG}"
            ;;
        h)
            usage
            exit 1
            ;;
    esac
done


echo DB_TYPE $DB_TYPE
echo GEOM_TO_CLEAR $GEOM_TO_CLEAR

# on part d'une base geonature existante


# initialisation

if [[ "$ROOT_DIR" = "" ]]; then
    ROOT_DIR=$(readlink -e "${0%/*}")/../..
fi

dir_sql=$ROOT_DIR/install/install_db/sql
dir_script=$ROOT_DIR/install/install_db
dir_data=$ROOT_DIR/data


# chargement de la configuration SQL dans settings.ini et tests de connextion

setting_file=${ROOT_DIR}/config/settings.ini
log_file=$ROOT_DIR/var/log/install_db.log

echo "install_db" > $log_file

if [ ! -f $setting_file ]
then
    echo Le fichier de configuration $setting_file n''est pas présent
    exit -1;
fi

. $setting_file

if [ "$db_name" = "" ] || [ "$db_host" = "" ] || [ "$db_port" = "" ] || [ "$user_pg" = "" ] || [ "$user_pg_pass" = "" ]
then
    echo Le fichier $setting_file est mal configuré
    exit -1;
fi

# si on a besoin d'installer avec un autre utilisateur qui a plus de droits

if [ "$user_install" != "" ] && [ "$user_install_pass" != "" ]
then

    user_pg_save=$user_pg
    user_pg=$user_install
    export PGPASSWORD="$user_install_pass"

else

    export PGPASSWORD="$user_pg_pass"

fi


# test de la connextion SQL

pg_isready -d $db_name -h $db_host -U $user_pg

resultat_test_connexion=$(echo $?)

if [ $resultat_test_connexion != 0 ]
then

    echo Erreur de connextion a la base de donnée.
    echo Veuillez vérifier vos paramètres db_port ou db_host dans le fichier $setting_file
    exit 1

fi

# creation d'un alias pour la commande

psqla=$(echo "psql -d $db_name -h $db_host -U $user_pg")

# test si la BDD existe

psql -tAl -U $user_pg -h $db_host | grep $db_name

resultat_test_psql=$?

if [ $resultat_test_psql != 0 ]
then

    echo Erreur de connextion a la base de donnée la base $db_name n''existe pas.
    echo Veuillez vérifier vos paramètres user_pg ou db_name dans le fichier $setting_file
    echo Veuillez vérifier quela base $db_name à bien été crée avec le script install_db de géonature
    exit 1

fi

# debut de la mise en place des données pour l''oeasc

echo mise en place de la BDD $db_name  sur le serveur $db_host pour l''oeasc

echo "DROP SCHEMA IF EXISTS oeasc CASCADE" | $psqla >> $log_file


# les fonctions additionelles (ref_geo et nomenclatures)

echo ajout des fonctions additionelles pour ref_geo
$psqla -f $dir_script/ref_geo/fonctions_ref_geo.sql >> $log_file
$psqla -f $dir_script/ref_geo/fonctions_simplify_geom.sql >> $log_file


# les données geographiques

if [ "$DB_TYPE" == "all" ] || [ "$DB_TYPE" == "geometrie" ]
then

    echo ajout des données géographiques
    . ${dir_script}/ref_geo/install_ref_geo.sh

fi

# les données de nomenclature

if [ "$DB_TYPE" == "all" ] || [ "$DB_TYPE" == "nomenclature" ]
then

    echo ajout des données nomenclature
    . ${dir_script}/nomenclature/nomenclature.sh

fi

# la base oeasc

if [ "$DB_TYPE" == "all" ] || [ "$DB_TYPE" == "nomenclature" ]
then

    echo ajout du shéma oeasc
    . ${dir_script}/oeasc/oeasc.sh

fi

# les utilisateurs

if [ "$DB_TYPE" == "all" ] || [ "$DB_TYPE" == "user" ]
then

    echo ajout de l''application oeasc et utilisateurs de base 
    . ${dir_script}/user/user.sh

fi


# cas ou l'utilisateur n'est pas superuser
# on donne les droits a l'utilisateur pour le schema oeasc et +

if [ "$user_install" != "" ] && [ "$user_install_pass" != "" ]
then

    echo "GRANT USAGE ON SCHEMA oeasc TO $user_pg_save;
    GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA oeasc TO $user_pg_save;
    GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA oeasc TO $user_pg_save;
    GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA ref_geo TO $user_pg_save;
    GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA ref_geo TO $user_pg_save;
    GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA utilisateurs TO $user_pg_save;
    GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA utilisateurs TO $user_pg_save;
    " | $psqla >> $log_file

fi

#creation de la base
