import { describe, it, expect } from 'vitest';
import { sortDateTable } from './util.js';

describe('sortDateTable', () => {
  it('place les valeurs vides en premier', () => {
    expect(['02/01/2020', null, '', '01/01/2020'].sort(sortDateTable)).toEqual([
      null,
      '',
      '01/01/2020',
      '02/01/2020',
    ]);
  });

  it('trie par année, puis mois, puis jour (JJ/MM/AAAA)', () => {
    const sorted = ['15/02/2021', '03/12/2020', '20/02/2020', '1/3/2020'].sort(sortDateTable);
    expect(sorted).toEqual(['20/02/2020', '1/3/2020', '03/12/2020', '15/02/2021']);
  });

  it('compare les dates ISO telles quelles', () => {
    expect(sortDateTable('2020-01-02', '2020-01-01')).toBe(1);
    expect(sortDateTable('2020-01-01', '2020-01-01')).toBe(0);
  });
});
