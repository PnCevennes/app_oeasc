from utils_flask_sqla.generic import GenericTable
from flask import request, current_app
from ..generic.repository import getlist
from ..resultat.repository import result_custom
from sqlalchemy import func, cast, select, Integer
from ..commons.models import TEspeces, TSecteurs
from sqlalchemy.exc import SQLAlchemyError
from .models import (
    TSaisons,
    TZoneCynegetiques,
    TZoneIndicatives,
    TAttributionMassifs,
    VPlanChasseRealisationBilan,
    TRealisationsChasse
)

from flask import jsonify
import pandas as pd
import io

config = current_app.config
DB = config["DB"]

def api_import_traitement_csv():
    """
    Endpoint pour recevoir un fichier CSV via POST (FormData), le lire avec pandas
    et effectuer le traitement en mémoire (sans sauvegarde sur disque).
    Accepte les champs FormData : file (fichier), saison (optionnel), update (true/false)
    """
    try:
        # récupération du fichier
        file_storage = request.files.get('file')
        saison = request.form.get('saison') or request.args.get('saison')
        update_flag = request.form.get('update', 'false').lower() in ('1','true','yes')

        if not file_storage:
            return jsonify({"error": "Aucun fichier envoyé"}), 400

    
        # file_storage est un FileStorage. on peut lire avec .stream
        file_storage.stream.seek(0)
        # essayer de détecter le séparateur; par défaut ';' ou ','
        content = file_storage.stream.read()
        # tenter lecture avec sep=';'
        try:
            df = pd.read_csv(io.BytesIO(content), sep=';')
        except Exception:
            # fallback sur virgule
            df = pd.read_csv(io.BytesIO(content), sep=',')

        # Exécuter un traitement minimal en exemple : compter lignes et colonnes
        nrows, ncols = df.shape

        jsondf = df.to_json(orient='records')

        # Ici, l'utilisateur pourra implémenter le traitement via pandas (insertion BDD, validation, etc.)
        current_app.logger.info(f"Traitement CSV saison={saison} update={update_flag} rows={nrows} cols={ncols}")

        # retourner un résumé
        return jsonify({"message": "Fichier traité", "json_data_bdd": jsondf, "rows": int(nrows), "cols": int(ncols), "saison": saison, "update": bool(update_flag)})

    except Exception as e:
        current_app.logger.exception('Erreur traitement CSV')
        return jsonify({"error": str(e)}), 500
    


