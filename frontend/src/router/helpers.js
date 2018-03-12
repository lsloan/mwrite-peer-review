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

// TODO find somewhere better for this function
const goTo = (vm, next, uri) => {
  if(vm) {
    vm.$router.push(uri);
  }
  else if(next) {
    next(uri);
  }
  else {
    throw Error('Can\'t navigate without vm or next');
  }
};

// TODO find somewhere better for this function
export const navigateToErrorPage = (vm, next, error) => {
  // TODO find somewhere better for these urls
  const errorRoute = '/error';
  const permissionDeniedRoute = '/permission-denied';

  if(error.response) {
    switch(error.response.status) {
      case 401:
      case 403:
        goTo(vm, next, permissionDeniedRoute);
        break;
      default:
        goTo(vm, next, errorRoute);
    }
  }
  else {
    goTo(vm, next, errorRoute);
  }

  throw error;
};
