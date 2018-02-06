<template>
    <div class="peer-review-assignment-card mdl-card mdl-cell mdl-cell--3-col mdl-shadow--2dp">

        <div class="mdl-card__title mdl-card--expand">
            <!-- TODO should be an h1? -->
            <h2 class="mdl-card__title-text">{{ prompt.title }}</h2>
        </div>

        <div class="mdl-card__supporting-text">
            <div class="icon-container">
                <i v-bind:class="{'material-icons': true, 'icon-24px': true, 'ok-icon-color': rubric}">
                    <template v-if="rubric">done</template>
                    <template v-else>not_interested</template>
                </i>
                <span class="icon-caption">
                    <template v-if="rubric">Rubric was configured correctly</template>
                    <template v-else>Rubric has not been created</template>
                </span>
            </div>
        </div>

        <div v-if="rubric" class="mdl-card__supporting-text">
            <div class="icon-container">
                <i class="material-icons icon-24px">date_range</i>
                <span class="icon-caption">
                    <template v-if="rubric.distributionIsComplete">Opened</template>
                    <template v-else>Will open</template>
                    <!-- TODO fix the below -->
                    <template v-if="prompt.dueDateUtc">{{ openDate }}</template>
                    <template v-else>anytime</template>
                </span>
            </div>
        </div>

        <div class="mdl-card__supporting-text">
            <div class="icon-container">
                <i class="material-icons icon-24px">query_builder</i>
                <span class="icon-caption">Due by {{ dueDate }}</span>
            </div>
        </div>

        <!-- TODO fix link paths -->
        <div class="mdl-card__actions mdl-card--border">
            <router-link
                to="/course/{{ courseId }}/rubric/assignment/{{ review.assignmentId }}"
                class="rubric-action mdl-button mdl-button--colored mdl-js-button mdl-js-ripple-effect">
                {{ rubricActionText }} Rubric
            </router-link>
            <router-link
                v-if="rubric.distributionIsComplete"
                to="/course/{{ courseId }}/status/rubric/{{ rubric.id }}"
                class="view-reviews-action mdl-button mdl-button--colored mdl-js-button mdl-js-ripple-effect">
                View Reviews
            </router-link>
        </div>

    </div>
</template>

<script>
  export default {
      name: 'peer-review-assignment-card',
      props: ['prompt', 'rubric', 'review'], // TODO play with props and data layout
      computed: {
          openDate() {
              return 'TODO open date';
          },
          dueDate() {
              return 'TODO due date';
          },
          rubricActionText() {
              return 'TODO rubric action text';
          },
          courseId() {
              return this.$store.state.userDetails.courseId;
          }
      }
  }
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

</style>
