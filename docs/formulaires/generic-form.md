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
    formDefs: { ... } // tableau contenant la config des formulaires (cf DFG)
    groups: { ... } // tableau contenant l'agencement des formulaires (cf DFG)
    forms: [...], // tableau contenant une liste de clé de formulaires (prioritaire sur groups)
    preLoadData: ({$store, config}) => {...} // doit renvoyer une Promise, charge des données nécessaires au formulaire... peut charger des données initiales dans config.value

    action: { // lié au boutton de validation du formulaire
        label: 'Se connecter', // texte qui s'affiche sur le boutton de validation du formulaire 
        request: {
            method: 'POST' // POST ou PATCH
            url: 'pypn/auth/login' // url relative de la requête,
            preProcess: preProcess: ({ baseModel, globalConfig }) => ({
                ...baseModel,
                id_application: globalConfig.ID_APPLICATION
            }), // preprocess de la variable baseModel (pour ajouter ID_APPLICATION depuis la config globale??)
            onSuccess: ({ data, $session, $store, $router, redirect }) => {
                const user = { ...data.user, expires: data.expires };
                $session.set("user", user);
                $store.commit("user", user);
                setTimeout(() => {
                    $router.push(redirect || "/");
                }, 1000);
            }, // actions à effectuer après la requête
        }
        process:({baseModel, config, $store}) // action à effectuer à la validation d'un formulaire, si on veut faire autre chose qu'une requête
    ...
}
```

#### slots

- `prependForm` : pour rajouter du texte avant le formulaire
- `appendForm`: pour rajouter du texte après le formulaire
- `success`: s'affiche en cas de succès de la requête
   