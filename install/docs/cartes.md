# Cartes

## Fonds de carte (frontend)

Configuration dans `frontend/src/config/config-map.js` (centre, zoom, fond initial `INIT_TILE`, liste `tileList`).
Fonds disponibles : IGN (Cartes / Plan IGN, WMTS `data.geopf.fr`), OpenTopoMap, Mapbox (clé dans la section
`frontend` du yaml, voir [configuration.md](configuration.md)).

Les cartes Leaflet sont encapsulées dans des composants dédiés (`modules/declaration/map/`, `restitution-map.vue`,
`modules/degats_agricoles/map/`). Elles libèrent leurs ressources au démontage ([performance-frontend.md](performance-frontend.md)).

## Proxy de tuiles (fiche déclaration)

Les cartes de `voir_declaration.vue` récupèrent leur fond via le backend (`/api/declaration/tiles/v2/<z>/<x>/<y>.png`)
avec cache disque dans `data/cache/tile/`. Paramétrage et vérifications : [Mise_en_production.md](Mise_en_production.md#cartes--proxy-des-tuiles).
