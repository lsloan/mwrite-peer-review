<template>
    <div class="work-card mdl-card mdl-shadow--2dp">
        <div :class="headerClasses">
            <span>{{ title }}</span>
            <div class="due-date-container">
                <i class="material-icons">query_builder</i>
                <span>Due</span>
                <span v-if="dueDateUtc">{{ dueDateUtc | utcToLocal('MMMM D h:mm A') }}</span>
                <span v-else>anytime</span>
            </div>
        </div>
        <div class="actions-container mdl-grid">
            <div v-for="(entry, index) in entries" :key="entry.id"
                 class="action-item mdl-cell mdl-cell--4-col">
                <div class="student-name-container">Student {{ index + 1 }}</div>
                <div class="action-item-container">
                    <router-link
                        v-if="entry.isReady && !entry.isComplete"
                        :to="makeLink(entry)"
                        class="start-action-item-button mdl-button mdl-js-button mdl-button--colored">
                        Start {{ entry.type }}
                    </router-link>
                    <div v-else :class="{'action-item-status-container': true, 'action-item-status-container--done': entry.isComplete}">
                        <i class="material-icons">
                            <template v-if="entry.isComplete">done</template>
                            <template v-else-if="!entry.isReady">query_builder</template>
                        </i>
                        <span v-if="!entry.isReady">Not Received</span>
                        <span v-else>Submitted</span>
                    </div>

                </div>
            </div>
        </div>
    </div>
</template>

<script>
import DateFormat from '@/mixins/date-format';

export default {
  name: 'WorkCard',
  props: ['title', 'card-type', 'due-date-utc', 'entries', 'make-link'],
  mixins: [DateFormat],
  computed: {
    headerClasses() {
      return {
        'work-card__header': true,
        'work-card__header--review': this.cardType === 'review',
        'work-card__header--evaluation': this.cardType === 'evaluation'
      };
    }
  }
};
</script>

<style scoped>
    .work-card {
        min-height: initial;
        background-color: #F0F0F0;
    }

    .work-card__header {
        display: flex;
        flex-direction: row;
        align-items: center;
        padding: 0 20px;
        color: white;
        flex: 0 0 64px;
    }

    .work-card__header--review {
        background-color: #3f51b5;
    }

    .work-card__header--evaluation {
        background-color: #00796B;
    }

    .due-date-container {
        margin-left: auto;
        display: flex;
        flex-direction: row;
        align-items: center;
    }

    .due-date-container > span, .due-date-container > .material-icons {
        margin-right: 6px;
    }

    .actions-container {
        width: 100%;
        box-sizing: border-box;
    }

    .mdl-grid > .action-item {
        background-color: white;
        font-size: 14px;
        box-shadow: 0 2px 2px 0 rgba(0,0,0,.14), 0 3px 1px -2px rgba(0,0,0,.2), 0 1px 5px 0 rgba(0,0,0,.12);
    }

    .student-name-container {
        border-bottom: 1px solid lightgray;
        font-weight: bold;
        padding: 14px 8px;
    }

    .action-item-container {
        text-transform: uppercase;
        padding: 0;
        display: flex;
        flex-direction: column;
        align-items: center;
    }

    .start-action-item-button {
        padding: 0;
        height: 38px;
        width: 100%;
    }

    .action-item-status-container {
        display: flex;
        flex-direction: row;
        align-items: center;
        text-transform: uppercase;
        padding: 9px 0;
    }

    .action-item-status-container--done {
        color: #52A763;
    }

    .action-item-status-container > i.material-icons {
        font-size: 16px;
        margin-right: 4px;
    }
</style>
