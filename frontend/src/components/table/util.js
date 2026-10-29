// Clé triable (AAAAMMJJ) d'une date au format JJ/MM/AAAA ; les autres formats (ISO...) sont comparés tels quels
const dateKey = (value) => {
  if (typeof value === 'string' && value.includes('/')) {
    const [day, month, year] = value.split('/');
    return `${year}${month.padStart(2, '0')}${day.padStart(2, '0')}`;
  }
  return String(value);
};

// Comparateur de dates pour tableau : valeurs vides d'abord
const sortDateTable = (a, b) => {
  if (!a && !b) return 0;
  if (!a) return -1;
  if (!b) return 1;
  const ka = dateKey(a);
  const kb = dateKey(b);
  return ka === kb ? 0 : ka < kb ? -1 : 1;
};

export { sortDateTable };
