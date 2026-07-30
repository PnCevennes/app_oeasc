import { describe, it, expect } from 'vitest';
import {
  copy,
  sortDate,
  upFirstLetter,
  camelToSnakeCase,
  round,
  isObject,
  jsoncopy,
  fde,
} from './util.js';

describe('util.js', () => {
  it('copy fait une copie profonde sans garder de référence', () => {
    const original = { a: 1, nested: { b: 2 } };
    const cloned = copy(original);
    expect(cloned).toEqual(original);
    expect(cloned.nested).not.toBe(original.nested);
  });

  it('jsoncopy fait une copie profonde et retourne null pour une valeur falsy', () => {
    expect(jsoncopy({ a: 1 })).toEqual({ a: 1 });
    expect(jsoncopy(null)).toBeNull();
  });

  it('fde compare deux objets en profondeur', () => {
    expect(fde({ a: 1 }, { a: 1 })).toBe(true);
    expect(fde({ a: 1 }, { a: 2 })).toBe(false);
  });

  it('sortDate compare des dates au format JJ/MM/AAAA', () => {
    expect(sortDate('01/01/2024', '02/01/2024')).toBeLessThan(0);
    expect(sortDate('02/01/2024', '01/01/2024')).toBeGreaterThan(0);
    expect(sortDate('01/01/2024', '01/01/2024')).toBe(0);
  });

  it('upFirstLetter met la première lettre en majuscule', () => {
    expect(upFirstLetter('chasse')).toBe('Chasse');
  });

  it('camelToSnakeCase convertit en snake_case', () => {
    expect(camelToSnakeCase('idEspece')).toBe('id_espece');
  });

  it('round arrondit au nombre de décimales demandé', () => {
    expect(round(1.2345, 2)).toBe(1.23);
    expect(round(0, 2)).toBe(0);
  });

  it('isObject distingue les objets des tableaux', () => {
    expect(isObject({})).toBe(true);
    expect(isObject([])).toBe(false);
  });
});
