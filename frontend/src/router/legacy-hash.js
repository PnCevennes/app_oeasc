// Anciennes URLs en hash (https://domaine/front/#/declaration/liste) : le site utilisait
// createWebHashHistory. Les liens déjà diffusés (e-mails, favoris, contenus CMS en base) sont
// convertis en URLs propres (https://domaine/front/declaration/liste).

const base = import.meta.env.BASE_URL; // '/front/' en prod, '/' en dev

// '#/login?token=x' -> '/front/login?token=x'
const versUrlPropre = (hash) => base + hash.replace(/^#\/?/, '');

// à appeler AVANT app.use(router) : la navigation initiale lit l'URL déjà corrigée
export function convertirHashInitial() {
  if (window.location.hash.startsWith('#/')) {
    window.history.replaceState(null, '', versUrlPropre(window.location.hash));
  }
}

// liens `<a href="#/...">` rencontrés pendant la navigation (contenus CMS anciens)
export function ecouterAncienHash(router) {
  window.addEventListener('hashchange', () => {
    if (window.location.hash.startsWith('#/')) {
      router.replace(window.location.hash.slice(1));
    }
  });
}
