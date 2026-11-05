

### Fonctionnement global

Vuex ; fabrique générique : `addStore` dans `frontend/src/store/utils.js`. Les routes REST associées sont les routes
génériques du backend (`backend/oeasc/modules/oeasc/generic/`, voir aussi les `droits` C/R/U/D déclarés par module,
par ex. dans `chasse/api.py`). Les échecs d'écriture remontent dans le snackbar global (`describeApiError()`).

    Les stores sont configurés dans le "index.js" de chaque module
    - Dans l'index.js
        -- On crée un const STORE dans lequel on peut ajouter des state, getter, actions spécifiques aux modules
        -- À la fin la fonction addStore qui se trouve dans 'store/utils.js' est utilisée pour créé un configStore générique à   partir du fichier de configuration situé dans `modules/<module>/config/store-bidule.js` (exemple : `modules/chasse/config/store-saison.js`)
        Un exemple est à la fin du fichier.
        -- les getters, mutations, et actions sont créé à partir du nom du store (storeName) à qui on a rajouté une majuscule au début. ex. getChasseZoneIndicative, postChasseZoneIndicative, getAllChasseZoneIndicative etc..
        -- les données inscrites dans "options": seront ajoutés à la requête GET

           /**
            * LES FONCTIONS GÉNÉRIQUES CRÉÉS SONT DU TYPE
            * 
            * @param {string} requestType - La méthode HTTP à utiliser (GET, POST, PATCH, DELETE).
            * @returns {Function} Une fonction d'action du store qui prend un contexte ({ getters, commit }) et des options.
            * @param {Object} options - Les options pour la requête.
            * @param {*} [options.value=null] - La valeur d'identifiant pour la requête, requise pour GET, PATCH et DELETE.
            * @param {string} [options.fieldName=configStore.idFieldName] - Le nom du champ à utiliser comme identifiant.
            * @param {Object} [options.postData=null] - Les données à envoyer dans le corps de la requête, requis pour POST et PATCH.
            * @returns {Promise<Object>} Une promesse qui se résout avec les données de réponse ou rejette avec une erreur.
            * 
            * Retourne une erreur Lorsque des paramètres requis sont manquants selon le type de requête.
            * 
            * @example
            * // Définir une action GET
            * const getItem = genericAction('GET');
            * // Utilisation dans le store
            * dispatch('getItem', { value: 123 });
            * 
            * @example
            * // Créer un nouvel élément
            * dispatch('postChasseBracelet', { 
            *   postData: { code_bracelet: 'BR001', description: 'Bracelet chevreuil' } 
            * });
            * 
            * @example
            * // Mettre à jour un élément existant
            * dispatch('patchChasseBracelet', { 
            *   value: 42, 
            *   postData: { description: 'Bracelet chevreuil modifié' } 
            * });
            * 
            * @example
            * // Supprimer un élément
            * dispatch('deleteChasseBracelet', { value: 42 });
            * 
            * @example
            * // Récupérer un élément avec un champ personnalisé
            * dispatch('getChasseBracelet', { 
            *   value: 'BR001', 
            *   fieldName: 'code_bracelet' 
            * });
            */












Exemple d'un configStore

(sortie de `addStore`, générée à partir d'un fichier `store-*.js` qui ne contient que `group`, `name`, `label`,
`serverSide`, `options`, `defs`...; les champs `storeName`, `api`, `get`, `post`, `configForm`, `configTable`... sont ajoutés. Exemple
simplifié : les réglages d'affichage de `configTable` (`dense`, `striped`, `small`) évoluent avec la migration Vuetify 3,
se référer à `generic-table.vue`. Dans `options`, `sortBy` / `sortDesc` restent des tableaux simples : `generic-table.vue`
convertit le format Vuetify 3 `[{key, order}]` vers celui-ci avant de requêter le backend.)


"chassePersonneConfigStore": {
    "group": "chasse",
    "name": "personne",
    "label": "Personne",
    "serverSide": true,
    "options": {
      "page": 1,
      "sortBy": [
        "id_personne"
      ],
      "sortDesc": [
        false
      ],
      "fields": [
        "id_personne",
        "nom_personne"
      ]
    },
    "defs": {
      "id_personne": {
        "label": "ID",
        "type": "text",
        "hidden": true
      },
      "nom_personne": {
        "label": "Nom",
        "type": "text",
        "required": true
      }
    },
    "storeName": "chassePersonne",
    "storeNames": "chassePersonnes",
    "snakeName": "personne",
    "apis": "api/generic/chasse/personnes/",
    "api": "api/generic/chasse/personne",
    "labels": "Personnes",
    "get": "getChassePersonne",
    "post": "postChassePersonne",
    "patch": "patchChassePersonne",
    "delete": "deleteChassePersonne",
    "getAll": "getAllChassePersonne",
    "count": "countChassePersonne",
    "find": "findChassePersonne",
    "idFieldName": "id_personne",
    "displayFieldName": "nom_personne",
    "loaded": false,
    "configForm": {
      "storeName": "chassePersonne",
      "idFieldName": "id_personne",
      "displayLabel": true,
      "formDefs": {
        "id_personne": {
          "label": "ID",
          "type": "text",
          "hidden": true
        },
        "nom_personne": {
          "label": "Nom",
          "type": "text",
          "required": true
        }
      }
    },
    "configTable": {
      "storeName": "chassePersonne",
      "options": {
        "page": 1,
        "sortBy": [
          "id_personne"
        ],
        "sortDesc": [
          false
        ],
        "fields": [
          "id_personne",
          "nom_personne"
        ]
      },
      "idFieldName": "id_personne",
      "dense": true,
      "striped": true,
      "small": true,
      "configForm": {
        "storeName": "chassePersonne",
        "idFieldName": "id_personne",
        "displayLabel": true,
        "formDefs": {
          "id_personne": {
            "label": "ID",
            "type": "text",
            "hidden": true
          },
          "nom_personne": {
            "label": "Nom",
            "type": "text",
            "required": true
          }
        }
      },
      "headerDefs": {
        "id_personne": {
          "label": "ID",
          "type": "text",
          "hidden": true,
          "text": "ID"
        },
        "nom_personne": {
          "label": "Nom",
          "type": "text",
          "required": true,
          "text": "Nom"
        }
      }
    }
  }, 

