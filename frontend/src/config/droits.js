// Niveaux de droits (code_profil du groupe UsersHub de l'utilisateur). Cumulatifs.
// Miroir de backend/oeasc/modules/oeasc/user/droits.py : garder les deux fichiers synchronisés.
// Détail de ce que permet chaque niveau : install/docs/droits.md
// Ne pas écrire de niveau en dur (droitMax >= 4) : utiliser ces constantes
// (dans les templates / composants : this.$droits.ADMIN, enregistré dans main.js).
export const DROITS = Object.freeze({
  VISITEUR: 0, // non connecté
  CONNECTE: 1, // ses propres déclarations
  ORGANISME: 2, // + voir/modifier/renouveler les déclarations de son organisme (niveaux 2 et 3 identiques)
  ADMIN: 4, // + suppression/validation de déclarations, utilisateurs, données chasse
  ANIMATEUR: 5, // + toutes les déclarations, contenus, dégâts agricoles, relances auto
  GESTIONNAIRE: 6, // + référentiels de zonage, import du plan de chasse
});

export default DROITS;

// Un modérateur (ADMIN) ou plus peut modifier un utilisateur de droit strictement inférieur au sien ;
// le gestionnaire (GESTIONNAIRE) n'a pas cette limite. Miroir de peut_gerer_utilisateur (droits.py).
export const peutGererUtilisateur = (droitAppelant, droitCible) =>
  (droitAppelant || 0) >= DROITS.ADMIN &&
  ((droitAppelant || 0) >= DROITS.GESTIONNAIRE || droitAppelant > (droitCible || 0));
