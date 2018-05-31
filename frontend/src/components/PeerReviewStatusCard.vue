<template>
    <div class="status-card mdl-card mdl-shadow--2dp">
        <div class="title-bar mdl-card__title" :class="{'title-bar': true, 'mdl-card__title': true, 'title-bar__issue': !review.completedAt}">
           {{ direction }} {{ review.name }}
        </div>
        <div class="mdl-card__supporting-text">
            <div class="status-line">
                <i class="material-icons">
                    <template v-if="!review.completedAt">info_outline</template>
                    <template v-else-if="reviewSubmittedLate">report_problem</template>
                    <template v-else>done</template>
                </i>
                <span>
                    <template v-if="review.completedAt">
                        Submitted
                        <template v-if="reviewSubmittedLate">
                            late
                        </template>
                        <template v-else>
                            on time
                        </template>
                        ({{ completedAtDisplay }})
                    </template>
                    <template v-else>
                        {{ source }} did not {{ action }} a peer review {{ adjective }} {{ destination }}
                    </template>
                </span>
            </div>
        </div>
        <div class="mdl-card__actions mdl-card--border">
            derp
        </div>
    </div>
</template>

<script>
import {sortableNameToFirstName} from '@/services/students';

export default {
  name: 'PeerReviewStatusCard',
  props: ['review', 'direction', 'subject', 'due-date'],
  computed: {
    reviewSubmittedLate() {
      const {review: {completedAt} = {}} = this.review;
      return completedAt
        ? completedAt.isSameOrAfter(this.dueDate)
        : true;
    },
    completedAtDisplay() {
      const date = this.review.completedAt;
      return date
        ? date.local().format('M/D/YY h:mmA')
        : '';
    },
    revieweeName() {
      return sortableNameToFirstName(this.review.name);
    },
    source() {
      return this.direction === 'To'
        ? this.subject
        : this.revieweeName;
    },
    destination() {
      return this.direction === 'To'
        ? this.revieweeName
        : this.subject;
    },
    action() {
      return this.direction === 'To'
        ? 'submit'
        : 'receive';
    },
    adjective() {
      return this.direction === 'To'
        ? 'for'
        : 'from';
    }
  }
};
</script>

<style scoped>
    .status-card {
        margin-bottom: 20px;
        min-height: initial;
    }

    .title-bar {
        color: white;
        background-color: rgb(63,81,181);
    }

    .title-bar__issue {
        background-color: #DD5465;
    }

    .status-line {
        display: flex;
        align-items: center;
    }

    .status-line > i {
        margin-right: 10px;
    }
</style>
