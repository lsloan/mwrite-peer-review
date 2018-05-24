<template>
    <div class="mdl-grid">
        <div class="mdl-cell mdl-cell--2-col mdl-cell--hide-tablet mdl-cell--hide-phone" v-if="sectionNumber"></div>
        <div class="mdl-cell mdl-cell--1-col mdl-cell--1-col-tablet mdl-cell--hide-phone" v-if="sectionNumber">
            <aside class="section-number-container">
                <p class="section-number">{{ sectionNumber }}</p>
            </aside>
        </div>
        <div class="mdl-cell mdl-cell--3-col mdl-cell--1-col-tablet mdl-cell--hide-phone" v-else></div>
        <section class="mdl-cell mdl-cell--6-col mdl-cell--6-col-tablet mdl-cell--4-col-phone">
            <slot></slot>
        </section>
        <div class="mdl-cell mdl-cell--3-col mdl-cell--1-col-table mdl-cell--hide-phone"></div>
    </div>
</template>

<script>
export default {
  name: 'PeerReviewSection',
  props: ['section-number']
};
</script>

<style scoped>
    .section-number-container {
        display: flex;
        flex-direction: row-reverse;
    }

    .section-number {
        text-align: center;
        color: white;
        background: #4187CD;
        width: 36px;
        height: 36px;
        line-height: 36px;
        -moz-border-radius: 18px;
        -webkit-border-radius: 18px;
        border-radius: 18px;
    }
</style>
