# SEO (référencement)

## Principes

Le frontend est une SPA Vue 3. Pour être indexable :

- **URLs propres** : `createWebHistory` (et non plus `createWebHashHistory`). Les pages sont de la forme
  `https://<domaine>/front/observatoire/presentation` (et non plus `/front/#/observatoire/presentation`,
  dont Google ignore la partie après `#`).
- **Anciens liens** : `frontend/src/router/legacy-hash.js` convertit `#/xxx` en `/front/xxx` au chargement
  (e-mails déjà envoyés, favoris, contenus CMS en base) et écoute `hashchange` pour les liens `<a href="#/xxx">`.
- **Meta par page** : `frontend/src/router/seo.js`, appelé à chaque navigation (`router/guards.js`) :
  `<title>`, `description`, `canonical`, `robots` et `og:*`.
  - Les pages avec `meta.access > 0` et la page de connexion reçoivent `noindex, nofollow`.
  - Les pages CMS (`modules/content/content.vue`) affinent la description (début du texte) et, pour les
    actualités, le titre (premier `h1`/`h2`) une fois le contenu chargé.
  - Une route peut fournir sa propre description avec `description: '...'` dans sa config de route
    (à ajouter dans `router/index.js` → `meta` si besoin).
- **Valeurs par défaut** dans `frontend/index.html` : description, Open Graph, JSON-LD `Organization`.

## robots.txt et sitemap.xml

Générés dynamiquement par `backend/oeasc/modules/oeasc/seo/api.py` (blueprint `/seo`) :

| URL publique              | Route Flask         |
|---------------------------|---------------------|
| `/front/sitemap.xml`      | `/seo/sitemap.xml`  |
| `/robots.txt`             | `/seo/robots.txt`   |

- Le sitemap liste `PAGES_PUBLIQUES` (liste en dur dans `seo/api.py`, **à tenir à jour** quand une route
  publique est ajoutée dans `frontend/src/modules/*/index.js`) et les actualités de `t_contents`
  (`type_page = 'actualite'`, avec `lastmod`).
- `robots.txt` interdit l'API (`/oeasc/`) et les pages privées (`CHEMINS_PRIVES`) et référence le sitemap.
- Les URLs sont construites à partir de `urls.frontend` de `install/config_principal.yaml`.

## Apache

`install/assets/apache2/oeasc.conf` ajoute :

- `FallbackResource /front/index.html` : indispensable en mode history, sinon un rechargement de
  `/front/observatoire/presentation` renvoie une 404 ;
- `ProxyPass` pour `/front/sitemap.xml` et `/robots.txt` vers Flask. Si le domaine a déjà un `robots.txt`,
  retirer la deuxième ligne et y ajouter `Sitemap: https://<domaine>/front/sitemap.xml`.

Après mise à jour : `apache2ctl configtest`, recharger Apache, reconstruire le frontend (`install/install.sh`),
redémarrer le service `oeasc`.

## Liens dans les e-mails

Les gabarits (`backend/oeasc/templates/modules/oeasc/mail/*.html`, `declaration/api.py`, `declaration/mail.py`)
utilisent encore `URL_FRONTEND + '#/...'` : ils continuent de fonctionner grâce à la redirection des anciens
liens. Les passer en URLs propres (`URL_FRONTEND + 'declaration/...'`) est possible plus tard.

## Après la mise en production

1. Vérifier `https://<domaine>/robots.txt` et `https://<domaine>/front/sitemap.xml`.
2. Soumettre le sitemap dans Google Search Console (et Bing Webmaster Tools).
3. Contrôler l'indexation avec « Inspection de l'URL » sur quelques pages (accueil, une actualité).

## Limites connues

Pas de rendu serveur : les moteurs qui exécutent JavaScript (Google, Bing) indexent bien le site, mais les
aperçus de liens (Facebook, LinkedIn, Slack…) ne voient que les meta par défaut de `index.html`. Une
injection des meta côté serveur ou un passage à Nuxt (voir `TODO.md`) règlerait ce point.
