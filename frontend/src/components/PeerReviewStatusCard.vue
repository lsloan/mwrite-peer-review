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
            <a v-if="!review.completedAt" class="mdl-button" :href="contactEmailLink">
                Email {{ contactName }}
            </a>
            <router-link v-else class="mdl-button" to="#/">See Review</router-link>
            <a class="mdl-button" :href="submissionDownloadUrl">See {{ contactName }}'s Submission</a>
        </div>
    </div>
</template>

<script>
import {sortableNameToFirstName} from '@/services/students';

export default {
  name: 'PeerReviewStatusCard',
  props: ['review', 'direction', 'subject-name', 'subject-email', 'due-date'],
  computed: {
    courseId() {
      return this.$store.state.userDetails.courseId;
    },
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
        ? this.subjectName
        : this.revieweeName;
    },
    destination() {
      return this.direction === 'To'
        ? this.revieweeName
        : this.subjectName;
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
    },
    contactEmailLink() {
      const email = this.direction === 'To'
        ? this.subjectEmail
        : this.review.email;
      return `mailto:${email}`;
    },
    contactName() {
      return this.direction === 'To'
        ? this.source
        : this.destination;
    },
    submissionDownloadUrl() {
      return `${__API_URL__}/course/${this.courseId}/reviews/${this.review.id}/submission`;
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

    .mdl-card__actions {
        display: flex;
        flex-wrap: wrap;
    }

    .mdl-card__actions > .mdl-button {
        flex: 1 1 auto;
    }

    .mdl-button {
        width: 100%;
        box-sizing: border-box;
        color: #777777;
    }
</style>
