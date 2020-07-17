# Gestion des formulaires

## Les variable
- `baseModel` : : le dictionnaire contenant les valeurs du formulaire.

## Les composants

### Dynamic form
- Brique de base des formulaires


### Input
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
 - `input`,
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
  - `default`: checkbox ou radio selon le parametre `multiple`
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



### Dynamic Form Group

- Structure et agencement du formulaire

Il peut être intéressant d'avoir au moins le paramètre `condition` de chaque brique du formulaire afin de pouvoir les agencer correctement.

#### props
- `config`:
```
config: {
    forms: { ... } // tableau contenant la config des formulaires
    struct: { ... } // tableau contenant l'agencement des formulaires
    displayValue: `bool` si vrai affiche seulement les valeurs
    displayLabel: `bool` si vrai et si displayValue vrai, affiche les label????
    ...
}
```

avec 
```
forms: {
    ...
    nom_foret: {
        type: 'text',
        label: 'Nom de la forêt',
        required: true,
    }
    ...
}
```

et 
```
struct: {
    title: 'Forêt' // titre du formulaire
    groups: [
        ...
        {
            title: 'Détail de la forêt',
            forms: ['nom_foret']
        }
        ...
    ]
}
``` 

si `struct` est vide, les formulaires sont placés verticalement les uns après les autres.

- `baseModel`


### Generic form

- Gestion des données:
  - chargement des données (si modification)
- Gestion des requêtes:
  - `POST`, `PATCH` 
- Possibilité d'afficher les valeurs / 
- Gestion bouttons `Valider`, `Modifier`, `Annuller`
- Affichage de barre de progression..

#### props
- `config`: exemple de la config de la page de login
```
config: {
    forms: { ... } // tableau contenant la config des formulaires (cf DFG)
    struct: { ... } // tableau contenant l'agencement des formulaires (cf DFG)
    request: {
        method: 'text' // POST ou PATCH
        url: 'pypn/auth/login' // url relative de la requête,
        preProcess: preProcess: ({ baseModel, globalConfig }) => ({
            ...baseModel,
            id_application: globalConfig.ID_APPLICATION
        }), // preprocess de la variable baseModel (pour ajouter ID_APPLICATION depuis la config globale??)
        preLoadData: ({$store, config}) => {...} // doit renvoyer une Promise, charge des données nécessaires au formulaire... peut charger des données initiales dans config.value
        onSuccess: ({ data, $session, $store, $router, redirect }) => {
            const user = { ...data.user, expires: data.expires };
            $session.set("user", user);
            $store.commit("user", user);
            setTimeout(() => {
                $router.push(redirect || "/");
            }, 1000);
        }, // actions à effectuer après la requête
        label: 'Se connecter', // texte qui s'affiche sur le boutton de validation du formulaire 
    }
    ...
}
```

#### slots

- `prependForm` : pour rajouter du texte avant le formulaire
- `appendForm`: pour rajouter du texte après le formulaire
- `success`: s'affiche en cas de succès de la requête
   
# TODO

Généraliser les formulaires chaînés (cf alertes)
Refaire/simplifier la config.

