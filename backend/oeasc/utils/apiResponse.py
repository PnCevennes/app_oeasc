###### CREATION D'UNE CLASSE apiRpesponse POUR UN FORMAT DE REPONSE UNIFORME AUX APPELS API ######

from app import app
import logging
from flask import jsonify
from datetime import datetime
import os


path_log = os.path.join(app.config["ROOT_DIR"], "logs/")
os.makedirs(path_log, exist_ok=True)

class ApiResponse:
    def __init__(
        self,
        success=True,
        message="",
        data={},
        system_error="",
        status_code=200,
        id_role=None,
        nom_complet=None,
        log_file="all_logs_files.log",
        session=None,
    ):
        self.debug_mode = app.config[
            "DEBUG"
        ]  # mode debug de l'application, à utiliser pour les opérations qui nécessitent un comportement différent en mode debug (ex: afficher des messages de debug dans le journal de l'application, retourner des messages d'erreur plus détaillés à l'utilisateur, etc.). Cet attribut est défini à partir de la configuration de l'application Flask et peut être utilisé pour adapter le comportement de la classe ApiResponse en fonction du mode d'exécution de l'application.
        self.success = success  # Boolean indiquant si l'opération a réussi ou échoué. Par défaut, il est défini sur True, ce qui signifie que l'opération est considérée comme réussie à moins qu'une erreur ne soit ajoutée.
        self.message = message  # message destiné à être retourné à l'utilisateur. Il doit être clair et compréhensible pour un utilisateur non technique.
        self.data = data  # données à retourner à l'utilisateur. Il peut s'agir de n'importe quelle structure de données (dictionnaire, liste, etc.) qui sera convertie en JSON pour la réponse de l'API.
        self.system_error = system_error  # message d'erreur technique destiné à être utilisé pour le debug et le journal de l'application. Il ne doit pas être retourné à l'utilisateur.
        self.status_code = status_code  # code de statut HTTP à retourner avec la réponse de l'API. Par défaut, il est défini sur 200 (OK), mais il peut être modifié en fonction du résultat de l'opération (ex: 400 pour une erreur client, 500 pour une erreur serveur, etc.).
        self.journal = (
            []
        )  # liste de chaine de caractères qui sera retournée dans le journal de l'application. Elle peut être utilisée pour stocker des messages de debug ou des informations sur l'exécution de l'opération. Ces messages ne sont pas destinés à être retournés à l'utilisateur, mais peuvent être utiles pour le développement et la maintenance de l'application.
        self.return_journal = False  # si return_journal est à True, le journal sera retourné dans la réponse de l'API. Si return_journal est à False, le journal ne sera pas retourné dans la réponse de l'API.
        
        # print (f"session dans ApiResponse => {session}")
        if id_role is not None:
            self.id_role = id_role  # id_role de l'utilisateur connecté, à utiliser pour les opérations qui nécessitent une identification de l'utilisateur (ex: enregistrement d'une action dans le journal de l'application, attribution d'une ressource à un utilisateur, etc.). Cet attribut doit être défini manuellement après l'initialisation de l'objet ApiResponse, en fonction de l'utilisateur connecté.
        else:
            if ((session is not None) and (session.get("current_user", {}))):
                self.id_role = session.get("current_user", {}).get("id_role", None)

        if nom_complet is not None:
            self.nom_complet = nom_complet  # nom complet de l'utilisateur connecté, à utiliser pour les opérations qui nécessitent une identification de l'utilisateur (ex: enregistrement d'une action dans le journal de l'application, attribution d'une ressource à un utilisateur, etc.). Cet attribut doit être défini manuellement après l'initialisation de l'objet ApiResponse, en fonction de l'utilisateur connecté.
        else:
            if ((session is not None) and (session.get("current_user", {}))):
                self.nom_complet = session.get("current_user", {}).get("nom_complet", "Utilisateur non connecté")

        self.log_file = os.path.join(
            path_log, log_file
        )  # chemin du fichier de log où les entrées du journal seront écrites. Par défaut, il est défini sur "all_logs_files.log" dans le dossier de logs de l'application, mais il peut être modifié en fonction des besoins de l'application (ex: "error_logs.log" pour les erreurs, "debug_logs.log" pour les messages de debug, etc.).


    def print_all(self):
        """Affiche tous les attributs de l'objet ApiResponse pour le debug."""
        print(f"success: {self.success}")
        print(f"message: {self.message}")
        print(f"DATA: {self.data}")
        print(f"system_error: {self.system_error}")
        print(f"status_code: {self.status_code}")
        print("journal: \n")
        for log in self.journal:
            print(f"log => {log}")

        print(f"return_journal: {self.return_journal}")
        print(f"id_role: {self.id_role}")
        print(f"nom_complet: {self.nom_complet}")
        print(f"log_file: {self.log_file}")

    # -------------------------
    # Ajouter une entrée au journal
    # -------------------------
    def add_log(
        self,
        message: str,
        type_log: str = "",
        with_timestamp: bool = False,
        with_user_info: bool = False,
    ):
        """Ajoute une entrée au journal.
        type_log peut être utilisé pour indiquer le type de message (ex: "INFO", "ERROR", "WARNING"). Si type_log est vide, le message sera ajouté sans type.
        Si with_timestamp est True, ajoute un timestamp à l'entrée.
        Si with_user_info est True et que id_role et nom_complet sont définis, ajoute les informations de l'utilisateur à l'entrée.
        """
        entry = ""
        if with_timestamp:
            timestamp = datetime.now().isoformat()
            entry += f"[{timestamp}] "
        if type_log:
            entry += f"[{type_log}] "
        if with_user_info and self.id_role and self.nom_complet:
            entry += f"[User: {self.nom_complet} (ID: {self.id_role})] "

        entry += message

        self.journal.append(entry)

    # -------------------------
    # Ecrire le journal dans un fichier
    # -------------------------
    def write_in_log_file(self, filename=None, with_timestamp: bool = False):
        """Ajoute les entrées du journal dans un fichier de log. Les entrées sont écrites avec un niveau INFO si success est True, sinon avec un niveau ERROR."""
        logger = logging.getLogger("ApiResponseLogger")
        logger.setLevel(logging.INFO)

        if not logger.handlers:
            if (
                filename is None
            ):  # si le fichier n'est pas définie, on utilise celui enregistré à l'initialisation de l'objet ApiResponse
                filename = self.log_file
            else:  # Si un fichier est défini, on créé un chemin et on utilise ce fichier pour le log
                filename = os.path.join(path_log, filename)

            # si le fichier de log n'existe pas, on le créé
            if not os.path.exists(filename):
                with open(filename, "w"):
                    pass

            handler = logging.FileHandler(filename)
            if with_timestamp:
                formatter = logging.Formatter(
                    "%(asctime)s - %(levelname)s - %(message)s"
                )
            else:
                formatter = logging.Formatter("%(message)s")

            handler.setFormatter(formatter)
            logger.addHandler(handler)

        for entry in self.journal:
            if self.success:
                logger.info(entry)
            else:
                logger.error(entry)

    # -------------------------
    # -------------------------
    # Ajouter une erreur
    # -------------------------
    def add_error(
        self,
        system_error: str="",
        user_message: str = "",
        with_timestamp: bool = True,
        status_code: int = 400,
    ):
        """Ajoute un message d'erreur à la réponse et marque la réponse comme un échec.
        system_error est le message d'erreur technique destiné au journal de l'application.
        user_message est le message d'erreur destiné à être retourné à l'utilisateur. Si user_message est vide, aucun message ne sera retourné à l'utilisateur.
        with_timestamp indique si un timestamp doit être ajouté au message d'erreur dans le journal de l'application.
        status_code est le code de statut HTTP à retourner avec la réponse de l'API. Par défaut, il est défini sur 400 (Bad Request), mais il peut être modifié en fonction du type
        """
        self.success = False
        self.system_error = system_error
        self.status_code = status_code
        if system_error != "":
            self.system_error = system_error
        
        if user_message != "":
            self.message = user_message
        else:
            if system_error == "":
                self.system_error = user_message
        # toujours journaliser l'erreur système
        self.add_log(system_error, type_log="ERROR", with_timestamp=with_timestamp)

    # -------------------------
    # Convertir en dict
    # -------------------------
    def to_dict(self):
        """Convertit l'objet ApiResponse en dictionnaire pour une réponse JSON uniforme."""
        response = {
            "success": self.success,
            "message": self.message,
            "data": self.data,
            "errors": self.system_error,
        }
        if self.return_journal:
            response["journal"] = self.journal
        if self.debug_mode:
            response["system_error"] = self.system_error
            response["log_file"] = self.log_file

        return response

    # -------------------------
    # Convertir en réponse Flask
    # -------------------------
    def response_to_frontend(self):
        """Convertit l'objet ApiResponse en une réponse Flask JSON avec le code de statut approprié.
        exemple de response JSON :
        {
            "success": true,
            "message": "Opération réussie",
            "data": {"id": 123, "name": "Example"},
            "errors": [],
            "journal": ["[2024-06-01T12:00:00Z] Opération commencée", "[2024-06-01T12:00:01Z] Opération réussie"]
        }
        """
        with app.app_context():
            return jsonify(self.to_dict()), self.status_code
