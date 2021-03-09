# Migration to convert all tables and text columns to utf8mb4

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        # The last migration name for each application at the time
        # this migration was written.

        # MPR migrations
        ('peer_review', '0009_auto_20181203_1216'),

        # django.contrib migrations
        ('admin', '0002_logentry_remove_auto_add'),
        ('auth', '0008_alter_user_username_max_length'),
        ('contenttypes', '0002_remove_content_type_name'),
        ('sessions', '0001_initial'),

        # third-party module migrations
        ('djangolti', '0001_initial'),
    ]

    operations = [
        # Disable Foreign Key Checks
        migrations.RunSQL("""
            SET FOREIGN_KEY_CHECKS=0;
            """),

        # Alter database
        migrations.RunSQL("""
            ALTER DATABASE CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci;
            """),

        # Alter tables
        migrations.RunSQL("""
            ALTER TABLE `auth_group` ROW_FORMAT = DYNAMIC, CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
            ALTER TABLE `auth_group_permissions` ROW_FORMAT = DYNAMIC, CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
            ALTER TABLE `auth_permission` ROW_FORMAT = DYNAMIC, CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
            ALTER TABLE `auth_user` ROW_FORMAT = DYNAMIC, CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
            ALTER TABLE `auth_user_groups` ROW_FORMAT = DYNAMIC, CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
            ALTER TABLE `auth_user_user_permissions` ROW_FORMAT = DYNAMIC, CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
            ALTER TABLE `canvas_assignments` ROW_FORMAT = DYNAMIC, CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
            ALTER TABLE `canvas_courses` ROW_FORMAT = DYNAMIC, CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
            ALTER TABLE `canvas_section` ROW_FORMAT = DYNAMIC, CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
            ALTER TABLE `canvas_students` ROW_FORMAT = DYNAMIC, CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
            ALTER TABLE `canvas_students_courses` ROW_FORMAT = DYNAMIC, CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
            ALTER TABLE `canvas_students_sections` ROW_FORMAT = DYNAMIC, CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
            ALTER TABLE `canvas_submissions` ROW_FORMAT = DYNAMIC, CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
            ALTER TABLE `criteria` ROW_FORMAT = DYNAMIC, CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
            ALTER TABLE `djangolti_noncehistory` ROW_FORMAT = DYNAMIC, CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
            ALTER TABLE `django_admin_log` ROW_FORMAT = DYNAMIC, CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
            ALTER TABLE `django_content_type` ROW_FORMAT = DYNAMIC, CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
            ALTER TABLE `django_migrations` ROW_FORMAT = DYNAMIC, CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
            ALTER TABLE `django_session` ROW_FORMAT = DYNAMIC, CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
            ALTER TABLE `job_log` ROW_FORMAT = DYNAMIC, CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
            ALTER TABLE `peer_reviews` ROW_FORMAT = DYNAMIC, CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
            ALTER TABLE `peer_review_comments` ROW_FORMAT = DYNAMIC, CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
            ALTER TABLE `peer_review_distributions` ROW_FORMAT = DYNAMIC, CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
            ALTER TABLE `peer_review_evaluations` ROW_FORMAT = DYNAMIC, CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
            ALTER TABLE `rubrics` ROW_FORMAT = DYNAMIC, CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
            ALTER TABLE `rubrics_sections` ROW_FORMAT = DYNAMIC, CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
            """),

        # Alter columns
        migrations.RunSQL("""
            ALTER TABLE `auth_group` CHANGE `name` `name` varchar(80) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
            ALTER TABLE `auth_permission` CHANGE `name` `name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
            ALTER TABLE `auth_permission` CHANGE `codename` `codename` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
            ALTER TABLE `auth_user` CHANGE `password` `password` varchar(128) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
            ALTER TABLE `auth_user` CHANGE `username` `username` varchar(150) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
            ALTER TABLE `auth_user` CHANGE `first_name` `first_name` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
            ALTER TABLE `auth_user` CHANGE `last_name` `last_name` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
            ALTER TABLE `auth_user` CHANGE `email` `email` varchar(254) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
            ALTER TABLE `canvas_submissions` CHANGE `filename` `filename` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
            ALTER TABLE `django_admin_log` CHANGE `object_repr` `object_repr` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
            ALTER TABLE `django_content_type` CHANGE `app_label` `app_label` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
            ALTER TABLE `django_content_type` CHANGE `model` `model` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
            ALTER TABLE `django_migrations` CHANGE `app` `app` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
            ALTER TABLE `django_migrations` CHANGE `name` `name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
            ALTER TABLE `django_session` CHANGE `session_key` `session_key` varchar(40) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
            ALTER TABLE `djangolti_noncehistory` CHANGE `client_key` `client_key` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
            ALTER TABLE `djangolti_noncehistory` CHANGE `nonce` `nonce` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
            ALTER TABLE `canvas_assignments` CHANGE `title` `title` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
            ALTER TABLE `canvas_courses` CHANGE `name` `name` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
            ALTER TABLE `canvas_section` CHANGE `name` `name` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
            ALTER TABLE `canvas_students` CHANGE `full_name` `full_name` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
            ALTER TABLE `canvas_students` CHANGE `sortable_name` `sortable_name` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
            ALTER TABLE `canvas_students` CHANGE `username` `username` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
            ALTER TABLE `criteria` CHANGE `description` `description` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
            ALTER TABLE `django_admin_log` CHANGE `object_id` `object_id` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
            ALTER TABLE `django_admin_log` CHANGE `change_message` `change_message` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
            ALTER TABLE `django_session` CHANGE `session_data` `session_data` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
            ALTER TABLE `job_log` CHANGE `message` `message` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
            ALTER TABLE `peer_review_comments` CHANGE `comment` `comment` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
            ALTER TABLE `peer_review_evaluations` CHANGE `comment` `comment` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
            ALTER TABLE `rubrics` CHANGE `description` `description` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
            """),

        # Re-enable foreign key checks
        migrations.RunSQL("""
            SET FOREIGN_KEY_CHECKS=1;
            """),
    ]
