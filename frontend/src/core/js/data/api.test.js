import { describe, it, expect, vi, afterEach } from 'vitest';
import { apiRequest } from './api.js';

const jsonResponse = (status, body) => ({
  status,
  json: () => Promise.resolve(body),
  text: () => Promise.resolve(typeof body === 'string' ? body : JSON.stringify(body)),
});

afterEach(() => vi.unstubAllGlobals());

describe('apiRequest', () => {
  it('résout avec le JSON pour un statut accepté', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(jsonResponse(200, { a: 1 })));
    await expect(apiRequest('GET', 'api/x')).resolves.toEqual({ a: 1 });
  });

  it('rejette avec { status, ...corps } pour un statut refusé', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue(jsonResponse(409, { message: 'conflit', field_errors: { a: ['x'] } }))
    );
    await expect(apiRequest('POST', 'api/x', { postData: {} })).rejects.toEqual({
      status: 409,
      message: 'conflit',
      field_errors: { a: ['x'] },
    });
  });

  it('rejette avec un message null pour une page HTML', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(jsonResponse(500, '<html>erreur</html>')));
    await expect(apiRequest('GET', 'api/x')).rejects.toEqual({ status: 500, message: null });
  });

  it('accepte les statuts listés dans acceptedStatus', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(jsonResponse(302, { ok: true })));
    await expect(apiRequest('GET', 'api/x', { acceptedStatus: [200, 302] })).resolves.toEqual({
      ok: true,
    });
  });

  it('partage un GET identique en cours avec dedupe, puis le libère', async () => {
    const fetchMock = vi.fn().mockResolvedValue(jsonResponse(200, [1]));
    vi.stubGlobal('fetch', fetchMock);
    await Promise.all([
      apiRequest('GET', 'api/l', { dedupe: true }),
      apiRequest('GET', 'api/l', { dedupe: true }),
    ]);
    expect(fetchMock).toHaveBeenCalledTimes(1);
    await apiRequest('GET', 'api/l', { dedupe: true });
    expect(fetchMock).toHaveBeenCalledTimes(2);
  });

  it('libère la requête partagée après un échec', async () => {
    const fetchMock = vi.fn().mockRejectedValue(new TypeError('réseau'));
    vi.stubGlobal('fetch', fetchMock);
    vi.spyOn(console, 'error').mockImplementation(() => {});
    await expect(apiRequest('GET', 'api/e', { dedupe: true })).rejects.toThrow('réseau');
    await expect(apiRequest('GET', 'api/e', { dedupe: true })).rejects.toThrow('réseau');
    expect(fetchMock).toHaveBeenCalledTimes(2);
  });
});
