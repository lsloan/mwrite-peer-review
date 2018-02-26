<template>
    <div class="peer-review-assignment-card mdl-card mdl-cell mdl-cell--3-col mdl-shadow--2dp">

        <div class="mdl-card__title mdl-card--expand">
            <!-- TODO should be an h1? -->
            <h2 class="mdl-card__title-text">{{ peerReviewTitle }}</h2>
        </div>

        <div class="mdl-card__supporting-text">
            <div class="icon-container">
                <i :class="{'material-icons': true, 'icon-24px': true, 'ok-icon-color': rubricId}">
                    <template v-if="rubricId">done</template>
                    <template v-else>not_interested</template>
                </i>
                <span class="icon-caption">
                    <template v-if="rubricId">Rubric was configured correctly</template>
                    <template v-else>Rubric has not been created</template>
                </span>
            </div>
        </div>

        <div :class="{'mdl-card__supporting-text': true, 'invisible': !rubricId }">
            <div class="icon-container">
                <i class="material-icons icon-24px">date_range</i>
                <span class="icon-caption">
                    <template v-if="reviewsInProgress">Opened</template>
                    <template v-else>Will open</template>
                    <template v-if="dueDate">{{ openDate | formatMoment(dateFormat) }}</template>
                    <template v-else>anytime</template>
                </span>
            </div>
        </div>

        <div class="mdl-card__supporting-text">
            <div class="icon-container">
                <i class="material-icons icon-24px">query_builder</i>
                <span class="icon-caption">Due by {{ dueDate | formatMoment(dateFormat) }}</span>
            </div>
        </div>

        <!-- TODO change these <a>s to <router-link>s when these views are ported to VueJS -->
        <div class="mdl-card__actions mdl-card--border">
            <a
                :href="rubricActionUrl"
                class="rubric-action mdl-button mdl-button--colored mdl-js-button mdl-js-ripple-effect">
                {{ rubricActionText }} Rubric
            </a>
            <a
                v-if="reviewsInProgress"
                :href="viewReviewsUrl"
                class="view-reviews-action mdl-button mdl-button--colored mdl-js-button mdl-js-ripple-effect">
                View Reviews
            </a>
        </div>

    </div>
</template>

<script>
export default {
  name: 'peer-review-assignment-card',
  props: [
    'rubric-id',
    'reviews-in-progress',
    'due-date',
    'open-date',
    'peer-review-assignment-id',
    'peer-review-title',
    'date-format'
  ],
  filters: {
    formatMoment(m, format) {
      return m ? m.format(format) : '';
    }
  },
  computed: {
    rubricActionUrl() {
      // TODO remove __API_URL__ when these views are ported to VueJS
      return __API_URL__ + '/course/' + this.courseId + '/rubric/assignment/' + this.peerReviewAssignmentId;
    },
    viewReviewsUrl() {
      // TODO remove __API_URL__ when these views are ported to VueJS
      return __API_URL__ + '/course/' + this.courseId + '/status/rubric/' + this.rubricId + '/all';
    },
    rubricActionText() {
      return this.reviewsInProgress
        ? 'View'
        : (this.rubricId ? 'Edit' : 'Create');
    },
    courseId() {
      return this.$store.state.userDetails.courseId;
    }
  }
};
</script>

<style scoped>
    .peer-review-assignment-card {
        width: 330px;
    }

    .ok-icon-color {
        color: #02d60c;
    }

    .rubric-action {
        /* TODO what goes here? can this be combined with view-reviews-action? */
    }

    .view-reviews-action {
        /* TODO what goes here? can this be combined with rubric-action? */
    }

    /***********/
    /* TODO styles below this point may be needed elsewhere */
    /***********/

    .icon-container {
        display: flex;
        align-items: center;
    }

    .icon-24px {
        width: 24px;
        height: 24px;
    }

    .icon-caption {
        margin-left: 10px;
    }

    .invisible {
        visibility: hidden
    }

</style>
