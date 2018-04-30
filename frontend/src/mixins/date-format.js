import moment from 'moment';

export default {
  filters: {
    utcToLocal(date, format) {
      const m = date ? moment(date).local() : null;
      return m ? m.format(format) : '';
    }
  }
};
