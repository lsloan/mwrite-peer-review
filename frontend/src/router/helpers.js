import store from '@/store';

export const hasRoleTest = (targetRole, to, from, next) => {
  const {roles} = store.state.userDetails;
  const shouldProceed = roles.find(role => role === targetRole);
  next(!!shouldProceed);
};

export const checkOrFetchUserDetails = (next, tryAgain) => {
  if('roles' in store.state.userDetails) {
    next();
  }
  else if(tryAgain) {
    store.dispatch('fetchUserDetails').then(() => {
      checkOrFetchUserDetails(next, false);
    });
  }
};
