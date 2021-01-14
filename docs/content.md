# Gestion des contenus


## Créer un nouveau contenu / Modifier un contenu

Tropis possibilités

- Aller sur la page concernée et éditer
- Depuis la page d'administration
- Aller sur la page `#/content/<code>`, en remplacant `<code>` par n'importe quelle chaîne de caractère raisonnable.
  - Pratique pour tester avant de publier ailleurs, attention à ne pas modifier un contenu existant   



## Format markdown

* exemple de [documentation](https://www.christopheducamp.com/2014/09/18/love-markdown/)
## Icones image et document

Permet de
  * choisir une image / un document dans une liste
  * ou bien d'uploader une image / un document
  * place le code dans le presse-papier, à coller dans le texte
  * priorité au fichier uploadé (si un fichier est déjà choisi dans la liste) 

### Précisions images

  * pour les images, possibilité de choisir un positionnement à gauche ou à droite
  * dans ce cas il est nécessaire de rajouter la balise `  <div style="clear:both"></div>` à la fin du texte qui suit l'image dans le markdown (pour la fin du texte qui sera en face de l'image dans le rendu final (prende en exemple la page `#/observatoire/contenu`))
  * Les dimension s'expriment selon le language css, soit en pixel (`200px`) ou bine en pourcentage (`50%`)


# Graphique

Sur la page `#/restitution/test` accessible depuis le menu de droite pour un utilisateur ayant des droit >= 5, on peut

* Créer des éléments de restituion
* Copier le code du widget dans un presse papier
* Placer ce code dans un contenu

## Colonnes

On peut ici  utiliser les composant de vuetify `<v-row>` et `<v-col>` (à mettre dans un div).

```
<div>
<v-row>
  <v-col>
  ...
  </v-col>
  <v-col>
  ...
  </v-col>
</v-row>

</div>
```

A partir du moment ou l'on utilise un div, le markdown ne sera pas utilisé.
## Gestion des actualités

* Aller sur la page /#/actualites/
* Se connecter en tant qu'admin
* Cliquer sur ajouter actualité

## Convention de nommage des codes des contenus

* pas d'espaces, d'accents ou de caratères spéciaux sauf `.` et `_`
  * `actualite.chasse_en_periode_de_confinement`

* Préfixer par:
  * `actualite.` 
  * `page.` 
  * `form.` 
  * `tooltip.` 


## Administration des contenu

La page d'administration des contenus `#/content/admin` (accessible en droit >= 5)
permet de gérer les différents éléments

### Content
Tableau des contenus, possibilité d'éditer, modifier, supprimer les contenus

### Tags
Possibilité de gérer des tags pour organiser ces contenus 
