<template>
    <div class="peer-review-assignment-card mdl-card mdl-cell mdl-cell--4-col mdl-cell--8-col-tablet mdl-cell--4-col-phone mdl-shadow--2dp">

        <div class="mdl-card__title mdl-card--expand">
            <!-- TODO should be an h1? -->
            <h2 class="mdl-card__title-text">{{ peerReviewTitle }}</h2>
        </div>

        <div class="mdl-card__supporting-text">
            <div class="icon-container">
                <i :class="validationIconClasses">
                    <template v-if="!rubricExists">not_interested</template>
                    <template v-else-if="issues.length === 0">done</template>
                    <template v-else-if="rubricHasFatalIssues">warning</template>
                    <template v-else-if="rubricHasNonFatalIssues">error_outline</template>
                </i>
                <span class="icon-caption">
                    <template v-if="rubricExists">
                        <template v-if="issues.length > 0">
                            {{ rubricActionText }} rubric to see
                            <template v-if="rubricHasFatalIssues">problems</template>
                            <template v-else>suggested changes</template>
                        </template>
                        <template v-else>Rubric was configured correctly</template>
                    </template>
                    <template v-else>Rubric has not been created</template>
                </span>
            </div>
        </div>

        <div class="mdl-card__supporting-text">
            <div class="icon-container">
                <i class="material-icons icon-24px">date_range</i>
                <span class="icon-caption">

                    <template v-if="rubricExists">
                        <template v-if="reviewsInProgress">Opened</template>
                        <template v-else>Will open</template>
                    </template>
                    <template v-else>Rubric has not been created</template>

                    <template v-if="dueDate">{{ openDate | utcToLocal(dateFormat) }}</template>
                    <template v-else>anytime</template>

                </span>
            </div>
        </div>

        <div class="mdl-card__supporting-text">
            <div class="icon-container">
                <i class="material-icons icon-24px">query_builder</i>
                <span class="icon-caption">Due by {{ dueDate | utcToLocal(dateFormat) }}</span>
            </div>
        </div>

        <div class="mdl-card__supporting-text" v-if="reviewsInProgress">
            <div class="icon-container">
                <i class="material-icons icon-24px">trending_up</i>
                <span class="icon-caption">{{ numberOfCompletedReviews }} out of {{ numberOfAssignedReviews }} reviews received</span>
            </div>
        </div>

        <div class="mdl-card__actions mdl-card--border">
            <router-link class="mdl-button mdl-button--colored mdl-js-button mdl-js-ripple-effect"
                         :to="{name: 'Rubric', params: {peerReviewAssignmentId: this.peerReviewAssignmentId}}">
                {{ rubricActionText }} Rubric
            </router-link>
            <router-link v-if="reviewsInProgress"
                         class="mdl-button mdl-button--colored mdl-js-button mdl-js-ripple-effect"
                         :to="{name: 'ReviewStatus', params: {rubricId: this.rubricId}}">
                See Reviews
            </router-link>
            <router-link v-if="reviewsInProgress"
                         class="mdl-button mdl-button--colored mdl-js-button mdl-js-ripple-effect"
                         :to="{name: 'UnassignedStudents', params: {rubricId: rubricId}}">
                Assign Reviews
            </router-link>

        </div>

    </div>
</template>

<script>
import {validationInfoAsIssues} from '@/services/validation';
import DateFormat from '@/mixins/date-format';

export default {
  name: 'peer-review-assignment-card',
  props: [
    'rubric-id',
    'reviews-in-progress',
    'due-date',
    'open-date',
    'peer-review-assignment-id',
    'peer-review-title',
    'date-format',
    'validation-info',
    'number-of-assigned-reviews',
    'number-of-completed-reviews'
  ],
  mixins: [DateFormat],
  computed: {
    rubricActionText() {
      return this.reviewsInProgress
        ? 'View'
        : (this.rubricId ? 'Edit' : 'Create');
    },
    courseId() {
      return this.$store.state.userDetails.courseId;
    },
    issues() {
      return validationInfoAsIssues(this.validationInfo);
    },
    rubricExists() {
      return Boolean(this.rubricId);
    },
    rubricHasFatalIssues() {
      return this.issues.length > 0 && this.issues.some(i => i.fatal);
    },
    rubricHasNonFatalIssues() {
      return this.issues.length > 0 && this.issues.some(i => !i.fatal);
    },
    validationIconClasses() {
      return {
        'material-icons': true,
        'icon-24px': true,
        'icon-color-ok': this.rubricExists && this.issues.length === 0,
        'icon-color-warning': this.rubricExists && this.rubricHasNonFatalIssues,
        'icon-color-error': this.rubricExists && this.rubricHasFatalIssues
      };
    }
  }
};
</script>

<style scoped>
    .peer-review-assignment-card {
        /*width: 330px;*/
    }

    .mdl-card__actions {
        display: block;
        text-align: center;
    }

    .icon-color-ok {
        color: #02d60c;
    }

    .icon-color-warning {
        color: #d17302;
    }

    .icon-color-error {
        color: #c40000;
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
</style>
