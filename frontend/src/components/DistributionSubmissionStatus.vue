<template>
    <div class="icon-container">
        <i class="material-icons icon-24px">
            <template v-if="submissionStatus === 'submitted-late'">assignment_late</template>
            <template v-else-if="submissionStatus === 'not-submitted'">close</template>
        </i>
        <span class="icon-caption">
            <template v-if="submissionStatus === 'submitted-late'">
                Late submission
            </template>
            <template v-else-if="submissionStatus === 'not-submitted'">
                Not submitted
            </template>
        </span>
    </div>
</template>

<script>
export default {
  name: 'DistributionSubmissionStatus',
  props: ['submission-status']
};
</script>

<style scoped>
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
        color: red;
    }
</style>
