<template>
    <div class='mdl-card__supporting-text datetime-container'>
        <p>{{ descriptionText }}</p>
        <div>
            <datepicker
                    format='MMM d yyyy'
                    placeholder='Day'
                    :disabled-dates='disabledDates'
                    :disabled='disabled'
                    v-model='models.selectedDate'>
            </datepicker>
        </div>
        <div>
            <mdl-select
                    id='peer-review-open-hour-select'
                    label='Hour'
                    v-model='models.selectedHour'
                    :options='HOUR_CHOICES'>
            </mdl-select>
        </div>
        <div>
            <mdl-select
                    id='peer-review-open-minute-select'
                    label='Minute'
                    v-model='models.selectedMinute'
                    :options='MINUTE_CHOICES'>
            </mdl-select>
        </div>
        <div>
            <mdl-select
                    id='peer-review-open-ampm-select'
                    label='AM / PM'
                    v-model='models.selectedMeridian'
                    :options='MERIDIAN_CHOICES'>
            </mdl-select>
        </div>

    </div>
</template>

<script>
import * as R from 'ramda';
import moment from 'moment';

import Datepicker from 'vuejs-datepicker';
import { MdlSelect } from 'vue-mdl';

export default {
  components: { Datepicker, MdlSelect },
  name: 'DateTimePicker',
  props: [
    'text',
    'disabled',
    'available-start-date',
    'available-end-date'
  ],
  data() {
    return {
      descriptionText: this.text || 'Enter a custom date:',

      models: {
        selectedDate: null,
        selectedHour: null,
        selectedMinute: null,
        selectedMeridian: null
      },

      HOUR_CHOICES: R.range(1, 13).map(i => i.toString()),
      MINUTE_CHOICES: ['00', '15', '30', '45'],
      MERIDIAN_CHOICES: ['AM', 'PM']
    };
  },
  computed: {
    disabledDates() {
      return this.availableStartDate && this.availableEndDate
        ? { to: this.availableStartDate.local().toDate(), from: this.availableEndDate.local().toDate() }
        : {};
    },
    dateTimeValue() {
      return this.getSynthesizeDateTimeValue();
    }
  },
  watch: {
    dateTimeValue: {
      handler: function(newValue, oldValue) {
        if(newValue !== oldValue) {
          this.$emit('change', newValue);
        }
      },
      deep: true
    }
  },
  methods: {
    getSynthesizeDateTimeValue() {
      const {selectedDate: date, selectedHour: hour, selectedMinute: minute, selectedMeridian: meridian} = this.models;
      if(date && hour && minute && meridian) {
        const hours12 = parseInt(hour);
        const hours24 = meridian === 'AM'
          ? (hours12 === 12 ? 0 : hours12)
          : (hours12 === 12 ? 12 : hours12 + 12);
        const minutes = parseInt(minute);
        return moment(date)
          .hours(hours24)
          .minutes(minutes)
          .utc();
      }
      else {
        return null;
      }
    }
  }
};
</script>

<style scoped>
.vdp-datepicker input[type='text'] {
  font-size: 14px;
  padding: 1%;
  max-width: 120px;
}

.datetime-container > div,
.datetime-container .vdp-datepicker,
.datetime-container .vdp-datepicker div {
  display: inline;
}

.datetime-container >>> .vdp-datepicker input {
  padding: 8px;
  margin-bottom: 6px;
  font-size: 14px;
}

.datetime-container .mdl-textfield {
  width: 80px;
  margin-left: 3px;
  margin-right: 3px;
}

.mdl-textfield {
  width: 100%;
}
</style>
