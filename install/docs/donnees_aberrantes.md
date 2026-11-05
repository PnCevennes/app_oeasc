# Données aberrantes (chasse)

Page `/chasse/donnees-aberrantes` (menu Chasse, droit ≥ 4) : liste les réalisations dont le **poids** ou la **longueur des dagues** sort de la fourchette standard de l'espèce, de la classe d'âge et du sexe, et permet de les corriger directement dans le tableau.

## Standards de mesures

Table `oeasc_chasse.t_standards_mesures` (migration `a7c2e91b4d30_add_t_standards_mesures`), modifiable dans **Données chasse → onglet Standards de mesures** :

| Colonne | Contenu |
| --- | --- |
| `id_espece` | espèce |
| `id_nomenclature_classe_age` | classe d'âge (type `STADE_VIE` : 1 indéterminé, 2 adulte, 3 juvénile, 5 sub-adulte) |
| `id_nomenclature_sexe` | sexe ; **vide = tous les sexes** |
| `mesure` | `poid_entier`, `poid_vide`, `poid_c_f_p` (kg) ou `long_dagues` (mm) |
| `valeur_min`, `valeur_max` | fourchette acceptée (bornes incluses) |

- Une seule ligne par (espèce, classe d'âge, sexe, mesure). Pour une réalisation, on utilise le standard de son sexe, à défaut celui sans sexe. Une mesure sans standard n'est pas contrôlée.
- Pré-remplissage (sexe vide) : bornes déjà utilisées à l'import CSV (`importation_csv.py` : dagues cerf/chevreuil, poids vide cerf/chevreuil/mouflon). Les bornes de `poid_entier` et `poid_c_f_p` (cerf, chevreuil) sont déduites des bornes de poids vide en inversant les formules de `oeasc_chasse.fct_poid_vide`. **Ces bornes sont à relire et à ajuster** ; l'import CSV garde ses propres constantes.
- Les valeurs nulles ou égales à 0 sont ignorées (non renseigné). Pour les dagues, c'est la plus grande des deux longueurs qui est comparée.

## API

- `GET /api/chasse/donnees-aberrantes?id_saison=&id_espece=&type=poids|dagues` (droit ≥ 4) → `{success, nb, data}` ; chaque ligne porte la liste `anomalies` (`mesure`, `valeur`, `valeur_min`, `valeur_max`).
- `PATCH /api/chasse/donnees-aberrantes/<id_realisation>` (droit ≥ 4) : corps JSON avec un sous-ensemble de `poid_entier`, `poid_vide`, `poid_c_f_p`, `long_dagues_droite`, `long_dagues_gauche` (`null` efface la valeur). Valeurs négatives ou non numériques refusées (400). Met à jour `meta_update_date`.

Code : `chasse/repositories.py` (`get_donnees_aberrantes`, `update_mesures_realisation`), `chasse/api.py`, front `modules/chasse/donnees-aberrantes-chasse.vue`.

## Poids entier, vidé et c.f.p.

Pour le cerf et le chevreuil, les trois poids se déduisent les uns des autres : `poids_vide = exp(a) × poids^b` avec des coefficients propres au poids entier et au poids c.f.p. (dans `chasse/poids.py`, identiques à `fct_poid_vide`). Le poids vidé sert de pivot : entier et c.f.p. se déduisent l'un de l'autre via lui, donc avec deux arrondis (écart possible de quelques centièmes de kg). Modifier un poids dans le tableau recalcule les deux autres (arrondi à 2 décimales) ; si plusieurs sont saisis, les valeurs saisies sont conservées. Pas de conversion pour les autres espèces.

## Utilisation

Filtres saison / espèce / type de donnée. Les mesures hors fourchette sont en rouge, la fourchette attendue est affichée à droite. Modifier une valeur puis enregistrer la ligne (bouton disquette ou Entrée) : si la ligne rentre dans la fourchette, elle disparaît de la liste. Les graphiques ICE utilisent les valeurs corrigées au prochain chargement.
