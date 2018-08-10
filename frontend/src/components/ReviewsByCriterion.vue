<template>
    <div>
        <div class="criterion-entry" v-for="entry in data" :key="entry.id">
            <p class="criterion-name">{{ entry.title }}</p>
            <p class="criterion-description">{{ entry.criterion }}</p>
            <p class="student-review" v-for="comment in entry.entries" :key="comment.id">
                <span class="student-name">{{ comment.heading }}:</span>
                <span>{{ comment.content }}</span>
            </p>
        </div>
        <div class="evaluation-entry">
            <p class="evaluation-name">Evaluation</p>
            <p class="evaluation-rating">** Rating here **</p>
            <p class="student-review">** Comment here **</p>
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

    .evaluation-entry {
        padding-left: 16px;
        border-left: 2px solid #52A763;
        margin-bottom: 20px;
    }

    .evaluation-name {
        color: #000000;
    }

    .evaluation-rating {
        color: #52A763;
    }

    .criterion-name, .criterion-description {
        color: #4157AF;
    }

    .criterion-name, .evaluation-name {
        margin-bottom: 0;
        font-size: 14px;
    }

    .criterion-description, .evaluation-rating {
        margin-top: 0;
    }

    .criterion-description, .student-name, .evaluation-rating {
        font-size: 13px;
    }

    .student-name {
        font-weight: bolder;
    }

    .student-review, .criterion-description, .evaluation-rating {
        margin-bottom: 4px;
    }
</style>
