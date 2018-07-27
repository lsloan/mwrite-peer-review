<template>
    <div>
        <div class="mdl-grid">
            <div class="mdl-cell mdl-cell--2-col mdl-cell--1-col-tablet mdl-cell--hide-phone"></div>
            <div class="mdl-cell mdl-cell--8-col mdl-cell--6-col-tablet mdl-cell--4-col-phone">
                <h1>Completed work</h1>
            </div>
            <div class="mdl-cell mdl-cell--2-col mdl-cell--1-col-tablet mdl-cell--hide-phone"></div>
        </div>
        <div class="mdl-grid">
            <div class="mdl-cell mdl-cell--2-col mdl-cell--1-col-tablet mdl-cell--hide-phone"></div>
            <div class="mdl-cell mdl-cell--8-col mdl-cell--6-col-tablet mdl-cell--4-col-phone">

                <!-- TODO need a case for no completed reviews -->
                <div class="mdl-grid">
                    <!-- TODO maybe use rubric ID? more semantically relevant-->
                    <div v-for="review in sortedReviews" :key="review.rubricId"
                         class="mdl-card mdl-shadow--2dp mdl-cell mdl-cell--6-col mdl-cell--8-col-tablet mdl-cell--4-col-phone">
                        <div class="mdl-card__title">
                            <h2 class="">{{ review.promptName }}</h2>
                            <div class="due-date-container">
                                <i class="material-icons">query_builder</i>
                                <span>Due</span>
                                <span
                                    v-if="review.dueDateUtc">{{ review.dueDateUtc | utcToLocal('MMMM D h:mm A') }}</span>
                                <span v-else>anytime</span>
                            </div>
                        </div>
                        <div class="mdl-card__supporting-text">
                            <div class="completed-work__sub-container">
                                <span>{{ review.reviews.received.completed }}</span>
                                <span>/</span>
                                <span>{{ review.reviews.received.total }}</span>
                                <span>reviews received</span>
                            </div>
                            <div class="completed-work__sub-container">
                                <span>{{ review.reviews.given.completed }}</span>
                                <span>/</span>
                                <span>{{ review.reviews.given.total }}</span>
                                <span>reviews given</span>
                            </div>
                        </div>
                        <div class="mdl-card__actions mdl-card--border">
                            <router-link v-if="review.reviews.received.completed > 0"
                                class="mdl-button mdl-js-button mdl-button--colored"
                                :to="{name: 'ReviewsReceived', params: {studentId: studentId, rubricId: review.rubricId}}">
                                Reviews I Received
                            </router-link>
                            <router-link v-if="review.reviews.given.completed > 0"
                                class="mdl-button mdl-js-button mdl-button--colored"
                                :to="{name: 'ReviewsGiven', params: {studentId: studentId, rubricId: review.rubricId}}">
                                Reviews I Gave
                            </router-link>
                        </div>
                    </div>
                </div>

            </div>
            <div class="mdl-cell mdl-cell--2-col mdl-cell--1-col-tablet mdl-cell--hide-phone"></div>
        </div>

        <!-- TODO this is a row -->
        <div class="mdl-grid">
            <div class="mdl-cell mdl-cell--2-col mdl-cell--1-col-tablet mdl-cell--hide-phone"></div>

            <!-- TODO 8 desktop / 6 tablet / 4 phone columns go here -->

            <div class="mdl-cell mdl-cell--2-col mdl-cell--1-col-tablet mdl-cell--hide-phone"></div>
        </div>
    </div>
</template>

<script>
import { MdlAnchorButton } from 'vue-mdl';

import {byDateAscending} from '@/services/util';
import DateFormat from '@/mixins/date-format';

export default {
  name: 'CompletedWork',
  props: ['reviews'],
  components: {
    MdlAnchorButton
  },
  computed: {
    sortedReviews() {
      return this.reviews.concat().sort(byDateAscending);
    },
    studentId() {
      return this.$store.state.userDetails.userId;
    }
  },
  mixins: [DateFormat]
};
</script>

<style scoped>
    h1 {
        font-size: 24px;
        margin: 4px 0;
        font-weight: bolder;
    }

    .mdl-grid {
        background-color: #F0F0F0;
        padding: 0;
    }

    .mdl-card {
        min-height: initial;
        font-family: "Roboto","Helvetica","Arial",sans-serif;
    }

    .mdl-card__title {
        padding: 14px 14px 8px 14px;
        display: block;
    }

    .mdl-card__title > h2 {
        padding: 0;
    }

    .mdl-card__title, .mdl-card__title > h2 {
        font-size: 16px;
        line-height: 16px;
        margin: 0;
    }

    .mdl-card__title > h2 {
        font-weight: bold;
        margin-bottom: 7px;
    }

    .mdl-card__title i, .mdl-card__title span {
        font-weight: 300;
        font-size: 15px;
    }

    .due-date-container {
        margin-left: auto;
        display: flex;
        flex-direction: row;
        align-items: center;
    }

    .due-date-container span {
        margin-left: 6px;
    }

    .mdl-card__supporting-text {
        padding: 4px 14px;
        display: flex;
        width: 100%;
        box-sizing: border-box;
    }

    .mdl-card__supporting-text {
        display: initial;
    }

    .completed-work__sub-container {
        font-size: 14px;
    }

    .mdl-card__actions {
        display: flex;
        flex-wrap: wrap;
    }

    .mdl-card__actions > .mdl-button {
        flex: 1 1 auto;
    }
</style>
