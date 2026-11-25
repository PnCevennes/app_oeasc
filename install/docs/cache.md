# Système de cache

## Frontend (TanStack Query)
- `frontend/src/core/js/data/query-client.js` : `QueryClient` (données fraîches 5 min), `invalidateForWrite`, `isFresh`.
- `store/utils.js` : `getAll` (addStore) et `addSimpleStore` passent par `queryClient.fetchQuery` ; clé `['list'|'simple', url, params]`.
- `store/store.js` : l'événement `api-write` invalide les entrées liées ; cache vidé au login/logout (mutation `user`) et sur `session-expired`.

## Backend (Flask-Caching, stockage fichier)
- `backend/oeasc/utils/cache.py` ; dossier `data/cache/app/` (ignoré par git), **partagé entre les workers gunicorn et la CLI** (pas de Redis nécessaire).
- Données de référence (`nomenclature_oeasc`, `get_area_from_id`) : TTL 1 h. Remplacent les anciens dicts en mémoire `config["_nomenclature"]` / `config["_areas"]`, propres à chaque process et jamais invalidés.
- Résultats calculés (`/api/chasse/results/bilan`) : clé = paramètres + `data_version()`, TTL 10 min. Toute écriture API réussie (POST/PATCH/PUT/DELETE, `after_request` dans `app.py`) et la fin d'un import chasse asynchrone appellent `invalidate_data()`.
- Écriture sur une route contenant « nomenclature » : le cache des nomenclatures est supprimé.
- `flask clear-cache` vide tout ; `flask refresh-ref-geo` le fait automatiquement en fin de succès.
- Pour mettre en cache une nouvelle route : `key = f"nom:{data_version()}:{params}"`, `cache.get/set(key, ..., timeout=TTL_RESULTATS)`.
