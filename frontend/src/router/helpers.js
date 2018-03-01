import store from '@/store';

export const hasRoleTest = (targetRole, to, from, next) => {
  const {roles} = store.state.userDetails;
  const shouldProceed = roles.find(role => role === targetRole);
  next(!!shouldProceed);
};

export const checkOrFetchUserDetails = (next, shouldFetch) => {
  if(next && 'roles' in store.state.userDetails) {
    next();
  }
  else if(shouldFetch) {
    return store.dispatch('fetchUserDetails').then(() => {
      checkOrFetchUserDetails(next, false);
    });
  }
};
