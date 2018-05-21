const lastSymbolTable = {};

export const gensym = (prefix = 'symbol') => {
  lastSymbolTable[prefix] = lastSymbolTable[prefix] + 1 || 0;
  return `${prefix}${lastSymbolTable[prefix]}`;
};
