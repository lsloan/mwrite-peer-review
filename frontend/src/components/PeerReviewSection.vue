<template>
    <div class="mdl-grid">
        <div class="mdl-cell mdl-cell--2-col" v-if="sectionNumber"></div>
        <div class="mdl-cell mdl-cell--1-col" v-if="sectionNumber">
            <aside class="section-number-container">
                <p class="section-number">{{ sectionNumber }}</p>
            </aside>
        </div>
        <div class="mdl-cell mdl-cell--3-col" v-else></div>
        <section class="mdl-cell mdl-cell--6-col">
            <slot></slot>
        </section>
        <div class="mdl-cell mdl-cell--3-col"></div>
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
