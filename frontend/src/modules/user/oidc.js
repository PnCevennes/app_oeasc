// Connexion OpenID Connect (flux « authorization code » + PKCE) via le Nextcloud « Échange ».
//
// Principe : à l'ouverture de la page de connexion, une SONDE silencieuse (prompt=none) est
// lancée : le navigateur part chez Échange qui le renvoie aussitôt sur /oidc/retour, avec
//  - un `code` si la personne est connectée à Échange : on le garde quelques minutes et le bouton
//    « Se connecter via Échange » s'affiche ;
//  - une erreur sinon : aucun bouton.
// Le code n'est échangé (côté back, avec le secret client) qu'au clic sur le bouton.
import { apiRequest } from '@/core/js/data/api.js';

const PREFIXE = 'oeasc:oidc_';
const CLE_STATE = PREFIXE + 'state';
const CLE_VERIFIER = PREFIXE + 'verifier';
const CLE_RETOUR = PREFIXE + 'retour';
const CLE_SILENCIEUX = PREFIXE + 'silencieux';
// résultat de la sonde : { etat: 'ok' | 'non', code?, verifier?, ts }
const CLE_SONDE = PREFIXE + 'sonde';
// un code d'autorisation vit peu de temps chez le fournisseur : on ne le garde que 3 minutes
const VALIDITE_MS = 3 * 60 * 1000;

// base64url sans remplissage, comme l'exige PKCE (RFC 7636)
const base64url = (octets) =>
  btoa(String.fromCharCode(...octets)).replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '');

// le stockage du navigateur peut être refusé (navigation privée…) : sans lui, pas de sonde
function lit(cle) {
  try {
    return sessionStorage.getItem(cle);
  } catch (err) {
    return null;
  }
}

function ecrit(cle, valeur) {
  try {
    if (valeur === null) sessionStorage.removeItem(cle);
    else sessionStorage.setItem(cle, valeur);
    return true;
  } catch (err) {
    return false;
  }
}

// configuration OpenID du back, lue une fois (null si l'API ne répond pas)
let config = null;
export function configOidc() {
  if (!config) {
    config = apiRequest('GET', 'api/user/oidc/config').catch(() => null);
  }
  return config;
}

// redirige le navigateur vers Échange. PKCE : le fournisseur ne reçoit que l'empreinte du
// `code_verifier`, qui ne quitte le navigateur qu'à l'échange du code.
// `silencieux` : aucune page chez le fournisseur (prompt=none)
export async function demarreOidc(retour, { silencieux = false } = {}) {
  const state = crypto.randomUUID();
  const verifier = base64url(crypto.getRandomValues(new Uint8Array(32)));
  const empreinte = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(verifier));
  const { url } = await apiRequest('GET', 'api/user/oidc/authorize', {
    params: {
      state,
      code_challenge: base64url(new Uint8Array(empreinte)),
      ...(silencieux ? { silencieux: 1 } : {}),
    },
  });
  if (!ecrit(CLE_STATE, state)) throw new Error('stockage indisponible');
  ecrit(CLE_VERIFIER, verifier);
  ecrit(CLE_RETOUR, retour || '/');
  ecrit(CLE_SILENCIEUX, silencieux ? '1' : null);
  window.location.assign(url);
}

// vérifie le `state` renvoyé par le fournisseur ; retourne la page où revenir, le `code_verifier`
// et si la demande était silencieuse (null si le state ne correspond pas à la demande)
export function termineOidc(state) {
  const attendu = lit(CLE_STATE);
  const verifier = lit(CLE_VERIFIER);
  const retour = lit(CLE_RETOUR) || '/';
  const silencieux = lit(CLE_SILENCIEUX) === '1';
  for (const cle of [CLE_STATE, CLE_VERIFIER, CLE_RETOUR, CLE_SILENCIEUX]) ecrit(cle, null);
  return attendu && attendu === state && verifier ? { retour, verifier, silencieux } : null;
}

// mémorise le résultat de la sonde silencieuse
export function memoriseSonde(etat, { code, verifier } = {}) {
  ecrit(CLE_SONDE, JSON.stringify({ etat, code, verifier, ts: Date.now() }));
}

// résultat récent de la sonde : 'ok' (connecté à Échange, code disponible), 'non' ou null
// (à (re)faire : jamais tentée ou périmée)
export function etatSonde() {
  try {
    const s = JSON.parse(lit(CLE_SONDE));
    if (s && Date.now() - s.ts < VALIDITE_MS && ['ok', 'non'].includes(s.etat)) return s.etat;
  } catch (err) {
    // valeur illisible : on refait la sonde
  }
  return null;
}

// code mémorisé par la sonde (à usage unique : il est retiré dès qu'on le lit)
export function prendCodeSonde() {
  let s = null;
  try {
    s = JSON.parse(lit(CLE_SONDE));
  } catch (err) {
    s = null;
  }
  ecrit(CLE_SONDE, null);
  return s && s.code && s.verifier && Date.now() - s.ts < VALIDITE_MS ? s : null;
}

// échange le code contre une session OEASC (le back vérifie le compte)
export function connecteOidc(code, verifier) {
  return apiRequest('POST', 'api/user/oidc/callback', {
    postData: { code, code_verifier: verifier },
  });
}

// ouvre la session dans le store et va à la page demandée (redirection interne uniquement :
// chemin absolu de la SPA, ni URL externe ni '//')
export function ouvreSession(vm, data, retour) {
  vm.$store.commit('user', { ...data.user, expires: data.expires });
  let redirect = '/';
  try {
    const demande = vm.$router.resolve(retour || '/').query.redirect;
    if (typeof demande === 'string' && /^\/(?![/\\])/.test(demande)) redirect = demande;
  } catch (err) {
    // retour illisible : accueil
  }
  vm.$router.replace(redirect);
}
