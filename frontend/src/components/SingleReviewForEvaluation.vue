<template>
    <p>TODO review {{peerReviewId}} for eval by {{studentId}} goes here</p>
</template>

<script>
export default {
  name: 'SingleReviewForEvaluation',
  props: ['student-id', 'peer-review-id']
};
</script>

<style scoped>
</style>
