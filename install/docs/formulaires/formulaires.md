# Gestion des formulaires

# Remarques générales

Les concept généraux, les composants et les input partagées par ces composants sont présentées ici.



## Les Input

- `baseModel` : le dictionnaire contenant les valeurs du formulaire.
  - à chaque clé est associée une valeur correspondant à un champs du formulaire
  - les composants surveilles ces changement afin de pouvoir adapter le formulaire aux valeurs.

- `config` : un dictionnaire contenant la définition d'un composant
  - par exemple: 
    - la définition d'un champs formulaire pour `DynamicForm`,
    - l'agencement de groupes de formulaire pour `DynamicFormGroup`
    - les paramètre de la requêtes pour `GenericForm`
    -   - les paramètres (la plupart sauf un liste) 
    - peuvent avoir une valeurs fixe ou bien 
    - peuvent être dynamiques et dépendre de plusieurs variables comme:
      - les valeurs du fomulaires (`baseModel`),
      - le `$store` pouyr accéder à des variables ou fonctions globales
      - la configuration (`config`)
    - la variable condition est forcement dynamique, et permet de choisir l'affichage d'un composant en fonction des valuers des autres composants.

    - cet Input sera mieux décrit dans les sections correspondant aux différents composants.

## Les composants

### [DynamicForm](./dynamic-form.md)
- Brique de base des formulaires, ce composant , défini par sa configuration représente une entrée du formulaire.

### [DynamicGroupForm](./dynamic-form-group.md)
- Ce composant permet d'agencer les différents éléments du formulaire (en ligne en colonne)

### [GenericForm](./generic-form.md)
- Ce composant permet de gérer un formulaire au niveau des actions à faire en cas de validation (requêtes, ...) ou annulation

Des exemples de configurations de formulaires peuvent être trouvés à :
- [creation d'utilisateur](../../frontend/src/modules/user/config/form-create-user.js)

- le formulaire de déclaration de dégâts en forêt est un composant sur mesure : `frontend/src/components/form/degats_declaration_form.vue` (configuration dans `frontend/src/modules/declaration/`).

Les composants sont dans `frontend/src/components/form/` (`generic-form.vue`, `dynamic-form-group.vue`, `dynamic-form.vue`, `list-form.vue`, `nomenclature-form.vue`).
Le composant `ChainedForm` (formulaires enchaînés) n'existe plus.

## Les patchs et remarque

- La variable `baseModel` peux contenir un champs `freeze` qui peut geler d'autres les autres composants, bouttons valider et liens *fil d'arrianne*.
