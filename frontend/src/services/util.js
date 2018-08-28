import moment from 'moment';

const lastSymbolTable = {};

export const gensym = (prefix = 'symbol') => {
  lastSymbolTable[prefix] = lastSymbolTable[prefix] + 1 || 0;
  return `${prefix}${lastSymbolTable[prefix]}`;
};

export const byDateAscending = (a, b) => {
  const dateA = moment.utc(a.dueDateUtc);
  const dateB = moment.utc(b.dueDateUtc);
  return dateA.diff(dateB);
};

const ordinals = {
  special: ['zeroth', 'first', 'second', 'third', 'fourth', 'fifth', 'sixth', 'seventh', 'eighth', 'ninth', 'tenth', 'eleventh', 'twelfth', 'thirteenth', 'fourteenth', 'fifteenth', 'sixteenth', 'seventeenth', 'eighteenth', 'nineteenth'],
  tens: ['twent', 'thirt', 'fort', 'fift', 'sixt', 'sevent', 'eight', 'ninet']
};

// TODO only works for <= 99; fix
// from https://stackoverflow.com/a/20426113
export const numberToOrdinal = n => {
  if(n > 99) {
    throw Error('Number out of range');
  }
  else if(n < 20) {
    return ordinals.special[n];
  }
  else if(n % 10 === 0) {
    return ordinals.tens[Math.floor(n / 10) - 2] + 'ieth';
  }
  else {
    return ordinals.tens[Math.floor(n / 10) - 2] + 'y-' + ordinals.special[n % 10];
  }
};
