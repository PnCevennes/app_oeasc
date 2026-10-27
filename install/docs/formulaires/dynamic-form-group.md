

### Dynamic Form Group

- Structure et agencement du formulaire

Ce composant tient compte du paramètre `condition` de chaque brique du formulaire afin de pouvoir les affichier ou non et les agencer correctement.

#### props
- `config`:
```
config: {
    formDefs: { ... } // dictionnaire contenant la config des formulaires
    groups: [... { ... } ...] // tableau de groupes
    forms:  [...] // ensemble de formulaires
}
```

avec 
```
formDefs: {
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
groups: [
    {
        title: 'Forêt' // titre du formulaire
        groups: [
            ...
            {
                title: 'Détail de la forêt',
                forms: ['nom_foret', 'superficie_foret]
                direction: 'row'
            }
            ...
        ]
    }
]
``` 


- si forms est défini, le groupe sera composé des formulaires dont les clés sont contenues dans `forms`
- si `groups` est vide et `forms` est vide, le formulaire sera composé de l'ensemble des formulaires de `formDefs`.
