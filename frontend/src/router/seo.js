// SEO côté client : titre, description, URL canonique, robots et Open Graph mis à jour à chaque
// navigation (le frontend est une SPA : index.html ne porte que les valeurs par défaut).

import { config } from '@/config/config.js';

const TITRE_SITE = 'OEASC';
const DESCRIPTION_DEFAUT =
  "Observatoire d'Étude Agro-Sylvo-Cynégétique (OEASC) du Parc national des Cévennes : suivi de la présence des grands gibiers (cerf, chevreuil, mouflon…), plans de chasse et dégâts en forêt et en agriculture.";
const LONGUEUR_DESCRIPTION = 160;

// crée ou met à jour une balise <meta> / <link> dans le <head>
function majBalise(selecteur, creation, attribut, valeur) {
  let el = document.head.querySelector(selecteur);
  if (!valeur) {
    if (el) el.remove();
    return;
  }
  if (!el) {
    el = document.createElement(creation.tag);
    Object.entries(creation.attrs).forEach(([k, v]) => el.setAttribute(k, v));
    document.head.appendChild(el);
  }
  el.setAttribute(attribut, valeur);
}

const meta = (name, content) =>
  majBalise(`meta[name="${name}"]`, { tag: 'meta', attrs: { name } }, 'content', content);
const og = (property, content) =>
  majBalise(`meta[property="${property}"]`, { tag: 'meta', attrs: { property } }, 'content', content);

// URL absolue publique d'un chemin de route (sans query ni hash)
export function urlCanonique(path) {
  return `${config.URL_FRONTEND.replace(/\/+$/, '')}${path === '/' ? '/' : path}`;
}

// texte brut d'un contenu HTML, raccourci pour une meta description
export function descriptionDepuisHtml(html) {
  if (!html) return '';
  const doc = new DOMParser().parseFromString(html, 'text/html');
  doc.querySelectorAll('script,style').forEach((n) => n.remove());
  const texte = (doc.body.textContent || '').replace(/\s+/g, ' ').trim();
  if (texte.length <= LONGUEUR_DESCRIPTION) return texte;
  return `${texte.slice(0, LONGUEUR_DESCRIPTION - 1).replace(/\s+\S*$/, '')}…`;
}

// premier titre (h1/h2) d'un contenu HTML
export function titreDepuisHtml(html) {
  if (!html) return '';
  const doc = new DOMParser().parseFromString(html, 'text/html');
  const h = doc.querySelector('h1, h2');
  return h ? h.textContent.trim() : '';
}

// applique les meta de la page courante. `route` donne le chemin canonique et le niveau d'accès,
// `titre` et `description` (facultatifs) priment sur les valeurs de la route.
export function appliquerSeo(route, { titre, description } = {}) {
  const titreRoute = titre || route.meta.title || route.meta.label;
  const titrePage = titreRoute ? `${TITRE_SITE} - ${titreRoute}` : TITRE_SITE;
  const desc = description || route.meta.description || DESCRIPTION_DEFAUT;
  // pages réservées aux connectés, connexion, édition : pas d'indexation
  const prive = (route.meta.access || 0) > 0 || route.name === 'user.login';
  const canonique = urlCanonique(route.path);

  document.title = titrePage;
  meta('description', desc);
  meta('robots', prive ? 'noindex, nofollow' : 'index, follow');
  majBalise('link[rel="canonical"]', { tag: 'link', attrs: { rel: 'canonical' } }, 'href', canonique);
  og('og:title', titrePage);
  og('og:description', desc);
  og('og:url', canonique);
}
