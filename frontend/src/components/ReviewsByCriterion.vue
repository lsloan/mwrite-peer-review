<template>
    <div>
        <div class="criterion-entry" v-for="entry in data" :key="entry.id">
            <p class="criterion-name">{{ entry.title }}</p>
            <p class="criterion-description">{{ entry.criterion }}</p>
            <p class="student-review" v-for="comment in entry.entries" :key="comment.id">
                <span class="student-name">{{ comment.reviewerName }}:</span>
                <span>{{ comment.text }}</span>
            </p>
        </div>
    </div>
</template>

<script>
export default {
  name: 'reviews-by-criterion',
  props: ['data']
};
</script>

<style scoped>
    .criterion-entry {
        padding-left: 16px;
        border-left: 2px solid #4157AF;
        margin-bottom: 20px;
    }

    .criterion-name, .criterion-description {
        color: #4157AF;
    }

    .criterion-name {
        margin-bottom: 0;
        font-size: 14px;
    }

    .criterion-description {
        margin-top: 0;
    }

    .criterion-description, .student-name {
        font-size: 13px;
    }

    .student-name {
        font-weight: bolder;
    }

    .student-review, .criterion-description {
        margin-bottom: 4px;
    }
</style>
