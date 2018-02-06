<template>
    <div class="mdl-grid">
        <!-- TODO play with props and data layout -->
        <template v-for="assignment in assignments">
            <peer-review-assignment-card
                :prompt="assignment.prompt"
                :rubric="assignment.rubric"
                :review="assignment.review" />
        </template>
    </div>
</template>

<script>
    import PeerReviewAssignmentCard from "./PeerReviewAssignmentCard";

    export default {
        components: {PeerReviewAssignmentCard},
        props: ['assignments'],
        name: 'instructor-dashboard'
    }
</script>

<style scoped>
</style>
