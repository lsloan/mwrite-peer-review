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
