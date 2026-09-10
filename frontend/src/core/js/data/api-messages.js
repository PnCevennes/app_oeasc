/**
 * Transforme une erreur d'appel API (quelle que soit sa forme : objet renvoyé par
 * le back, chaîne, erreur réseau, réponse non-JSON…) en une phrase claire, en
 * français, sans jargon technique — destinée à être affichée dans le snackbar
 * global (App.vue).
 *
 * Le back renvoie, pour les routes génériques d'écriture, un corps de la forme :
 *   { success:false, message:"…", field_errors:{ champ:["…"] }, code:409 }
 * (voir backend/oeasc/modules/oeasc/generic/errors.py)
 *
 * `options.formDefs` : définitions des champs du formulaire (clé -> { label, … }).
 *   Utilisé pour remplacer les noms techniques des champs par leur libellé.
 */

const MESSAGE_RESEAU =
  "Impossible de contacter le serveur. Vérifiez votre connexion internet puis réessayez.";

const MESSAGE_DEFAUT =
  "L'opération n'a pas pu être effectuée. Merci de réessayer ; si le problème persiste, prévenez l'administrateur.";

const MESSAGE_PAR_STATUT = {
  400: "Certaines informations sont manquantes ou ne sont pas au bon format. Merci de vérifier votre saisie.",
  401: "Votre session a expiré. Merci de vous reconnecter.",
  403: "Vous n'avez pas les droits nécessaires pour effectuer cette action.",
  404: "L'élément concerné est introuvable. Il a peut-être été supprimé : rechargez la page.",
  409: "L'opération entre en conflit avec des données déjà enregistrées.",
  413: "Le fichier envoyé est trop volumineux.",
  500: "Une erreur est survenue sur le serveur. Merci de réessayer plus tard ; si le problème persiste, prévenez l'administrateur.",
  502: "Le serveur est momentanément indisponible. Merci de réessayer dans quelques instants.",
  503: "Le serveur est momentanément indisponible. Merci de réessayer dans quelques instants.",
  504: "Le serveur met trop de temps à répondre. Merci de réessayer dans quelques instants.",
};

/**
 * Nom de champ technique -> libellé lisible, à partir des formDefs.
 */
function labelDuChamp(champ, formDefs) {
  if (!formDefs) {
    return champ;
  }
  // le back peut renvoyer "objet.sous_champ" -> on ne garde que le dernier segment connu
  const segments = String(champ).split('.');
  for (const segment of segments) {
    if (formDefs[segment] && (formDefs[segment].label || formDefs[segment].text)) {
      return formDefs[segment].label || formDefs[segment].text;
    }
  }
  return segments[segments.length - 1];
}

/**
 * Construit la liste lisible des champs en erreur : "« Nom » : information
 * obligatoire non renseignée ; « Code » : un nombre est attendu".
 */
function detailChamps(fieldErrors, formDefs) {
  if (!fieldErrors || typeof fieldErrors !== 'object') {
    return '';
  }
  const morceaux = [];
  for (const [champ, messages] of Object.entries(fieldErrors)) {
    if (champ === '_' || champ === 'freeze') {
      continue;
    }
    const label = labelDuChamp(champ, formDefs);
    const texte = Array.isArray(messages) ? messages.join(', ') : String(messages);
    morceaux.push(texte ? `« ${label} » : ${texte}` : `« ${label} »`);
  }
  return morceaux.join('\n');
}

/**
 * @param {*} error       L'erreur telle que rejetée par apiRequest / une action store.
 * @param {object} options { formDefs, action, fallback } — `action` :
 *                          "enregistrement" | "modification" | "suppression"
 *                          (oriente le message par défaut) ; `fallback` : message
 *                          à utiliser quand aucune information exploitable n'est
 *                          disponible.
 * @returns {string}       Phrase prête à afficher.
 */
export function describeApiError(error, options = {}) {
  const { formDefs, action, fallback } = options;

  // 1) Erreur réseau : fetch rejette avec un TypeError, ou l'objet n'a aucune info exploitable
  if (
    error instanceof TypeError ||
    (error && error.name === 'TypeError') ||
    error === undefined ||
    error === null
  ) {
    return MESSAGE_RESEAU;
  }

  // 2) Chaîne de caractères renvoyée directement
  if (typeof error === 'string') {
    // les messages "genericAction Error : …" sont techniques -> message générique
    if (/^genericAction Error/i.test(error) || /\bError\b/.test(error)) {
      return fallback || baseParDefaut(action);
    }
    return error;
  }

  // 3) Objet structuré renvoyé par le back
  if (typeof error === 'object') {
    const statut = error.status || error.code || error.status_code;

    // message explicite fourni par le back (errors.py, ApiResponse, …)
    const messagePrincipal =
      (typeof error.message === 'string' && error.message) ||
      (typeof error.msg === 'string' && error.msg) ||
      '';

    const champs = detailChamps(error.field_errors || error.errors, formDefs);

    if (messagePrincipal && !ressembleAJargon(messagePrincipal)) {
      return champs ? `${messagePrincipal}\n\n${champs}` : messagePrincipal;
    }

    if (champs) {
      return `Certaines informations ne sont pas valides :\n${champs}`;
    }

    if (statut && MESSAGE_PAR_STATUT[statut]) {
      return MESSAGE_PAR_STATUT[statut];
    }
  }

  return fallback || baseParDefaut(action);
}

function baseParDefaut(action) {
  if (action === 'suppression') {
    return "La suppression n'a pas pu être effectuée. Merci de réessayer ; si le problème persiste, prévenez l'administrateur.";
  }
  if (action === 'modification') {
    return "La modification n'a pas pu être enregistrée. Merci de réessayer ; si le problème persiste, prévenez l'administrateur.";
  }
  if (action === 'enregistrement') {
    return "L'enregistrement n'a pas pu être effectué. Merci de réessayer ; si le problème persiste, prévenez l'administrateur.";
  }
  return MESSAGE_DEFAUT;
}

/**
 * Repère un message manifestement technique (trace, exception Python/JS…) qu'il ne
 * faut pas montrer tel quel à l'utilisateur.
 */
function ressembleAJargon(message) {
  return (
    /Traceback|Exception|Error:|<!DOCTYPE|<html|psycopg2|sqlalchemy|marshmallow|\bNoneType\b|\bKeyError\b/i.test(
      message
    ) || message.length > 400
  );
}

export default describeApiError;
