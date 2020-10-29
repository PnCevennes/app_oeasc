# DynamicForm

### Input
- `config`: `dict` la configuration du formulaire dynamique:

- `baseModel`: `dict` les valeurs du formulaire.

- `config`: `dict` la configuration du formulaire dynamique:

- `baseModel`: `dict`

#### Paramètres de la config

Le dictionnaire `config` contient plusieurs paramètres.
Certains paramêtres peuvent être dynamique : à la place de la valeur, on définit une fonction qui depend de:
- baseModel : voir plus haut.
- $store : le $store de view, pour avoir accès à des données/fonctions globales. 

Les paramètres dynamique peuvent être `required`, `condition`, ....,
Il sont signalé par `func` dans la liste ci-dessous. 

Les paramètres principaux sont:

- `required`: `bool|func`, spécifie si le champs est obligatoire,
- `condition`: `func`, spécifie si le champs s'affiche ou non, 
- `disabled`: `bool|func`, spécifie si le champs est visible mais non modifiable (grisé)
- `label`: `string`, Texte du champs de formulaire,
- `type`: le type de formulaire (texte, liste déroulante, ect...),
- ``

#### Les types
- champs classiques:
 - `date`,
 - `text`,
 - `text_area`,
 - `number`,
 - `password`,
- choix binaire:
 - `bool_radio`,
 - `bool_switch`,
- choix dans une liste:
 - `list_form`: se décline en plusieurs versions selon le paramètre `display`:
  - `button`: choix dans une liste de bouttons
  - `select`: choix dans une liste classique
  - `autocomplete`: avec l'autocomplete
  - `combobox`: choix dans une liste et possibilité d'ajouter des nouveaux champs
  - par default: checkbox ou radio selon le parametre `multiple`
  - les autres paramètres des `list_form` sont:
    - `items`: on peut donner une liste de valeurs ou d'objets en configuration.
    - `valueFieldName` *value*: le nom du champs pour la valeur renvoyée
    - `displayFieldName` *text*: le nom du champs pour la valeur affichée
    - `url`: l'URL de l'api qui renvoie la liste des items
 - `nomenclature`: se base sur le précédent pour le choix des nomenclatures,
 - `essence`: se base sur le précédent pour le  choix des essences (+ gestion de celles déjà choisie...),
- choix dans une liste et sur une carte:
 - `select_map`,

- edition de contenu:
 - `content`,

- liste d'object (ou liste de formulaires)
 - `list`

- sur mesure
 - `degats`,

