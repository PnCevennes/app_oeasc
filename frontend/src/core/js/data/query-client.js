import { QueryClient } from '@tanstack/query-core';

/**
 * Cache des requêtes API (TanStack Query). Une entrée par clé de requête, ex. ['list', api, params].
 * - staleTime : durée pendant laquelle une donnée est considérée fraîche (pas de nouvelle requête)
 * - les requêtes simultanées identiques sont dédupliquées
 * - toute écriture API invalide les entrées concernées (cf. invalidateForWrite)
 */
const STALE_TIME = 5 * 60 * 1000;

const queryClient = new QueryClient({
  defaultOptions: {
    queries: { staleTime: STALE_TIME, gcTime: 30 * 60 * 1000, retry: false },
  },
});

// Retire les slashs de début/fin pour comparer des chemins d'API
const clean = (s) => String(s || '').replace(/^\/+|\/+$/g, '');

/**
 * Invalide les entrées de cache touchées par une écriture sur `url` (ex: 'api/generic/chasse/bracelet/3').
 * - les listes/ressources dont le chemin d'API est un préfixe de l'URL écrite
 * - pour une route non générique, tout le module (api/<module>/...) : une écriture peut modifier
 *   plusieurs ressources liées (déclarations, imports, relances...)
 */
const invalidateForWrite = (url) => {
  const written = clean(url);
  const [a, b] = written.split('/');
  const moduleRoot = written.startsWith('api/generic/') ? null : `${a}/${b}`;
  queryClient.invalidateQueries({
    refetchType: 'none',
    predicate: (query) => {
      const api = clean(query.queryKey[1]);
      if (!api) return false;
      return (
        written === api ||
        written.startsWith(`${api}/`) ||
        written.startsWith(`${api}s`) ||
        (moduleRoot !== null && (api === moduleRoot || api.startsWith(`${moduleRoot}/`)))
      );
    },
  });
};

// true si une entrée existe, est fraîche et non invalidée
const isFresh = (queryKey) => {
  const state = queryClient.getQueryState(queryKey);
  return (
    !!state &&
    state.status === 'success' &&
    !state.isInvalidated &&
    Date.now() - state.dataUpdatedAt < STALE_TIME
  );
};

export { queryClient, invalidateForWrite, isFresh, STALE_TIME };
