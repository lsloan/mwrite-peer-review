#!/usr/bin/env bash

MPR_BACKUP_PREFIX="${MPR_BACKUP_PREFIX:-/tmp/backups}"
MPR_DB_CONFIG_FILE="${MPR_DB_CONFIG_FILE:-/etc/mwrite-peer-review/database.json}"
MPR_SUBMISSIONS_PATH="${MPR_SUBMISSIONS_PATH:-/srv/mwrite-peer-review/submissions}"
MPR_BACKUP_S3_BUCKET="${MPR_BACKUP_S3_BUCKET:-mwrite-peer-review-backup}"
MYSQLDUMP_OPTIONS="${MYSQLDUMP_OPTIONS}"

MYSQL_PASSWORD_FILE="${HOME}/.my.cnf"

# TODO currently this writes .tar.gz and .sql files to a temp directory, then 'aws s3 mv'es them to
# TODO s3.  this could also be implemented to just pipe directly to 'aws s3 mv' and thus skip
# TODO the temp step.  is this wise / robust?

create_mysql_password_file() {
    if [ ! -e "${MYSQL_PASSWORD_FILE}" ]
    then
        local db_user=$(jq -r .USER "${MPR_DB_CONFIG_FILE}")
        local db_password=$(jq -r .PASSWORD "${MPR_DB_CONFIG_FILE}")

        echo '[mysqldump]'              >> "${MYSQL_PASSWORD_FILE}"
        echo "user=${db_user}"          >> "${MYSQL_PASSWORD_FILE}"
        echo "password=${db_password}"  >> "${MYSQL_PASSWORD_FILE}"
    fi
}

create_backup_directories() {
    mkdir -p "${MPR_BACKUP_PREFIX}"/{db,submissions}
}

create_database_backup() {
    local db_name=$(jq -r .NAME "${MPR_DB_CONFIG_FILE}")
    local db_host=$(jq -r .HOST "${MPR_DB_CONFIG_FILE}")
    local db_port=$(jq -r .PORT "${MPR_DB_CONFIG_FILE}")

    db_backup_name=mwrite_db_backup_"${datestamp}"
    db_backup_file="${MPR_BACKUP_PREFIX}"/db/"${db_backup_name}".sql

    # FIXME what if that ${db_name} already exists?
    # FIXME check error code
    mysqldump ${MYSQLDUMP_OPTIONS} -h "${db_host}" -P "${db_port}" "${db_name}" > "${db_backup_file}" || exit 1
}

create_submissions_backup() {
    submission_backup_name=mwrite_submissions_backup_"${datestamp}"
    submission_backup_file="${MPR_BACKUP_PREFIX}"/submissions/"${submission_backup_name}".tar.gz

    # FIXME what if that ${submission_backup_file} already exists?
    # FIXME check error code
    cd "$(dirname ${MPR_SUBMISSIONS_PATH})"
    tar czf "${submission_backup_file}" "$(basename ${MPR_SUBMISSIONS_PATH})" || exit 1
    cd "${OLDPWD}"
}

upload_backups_to_s3() {
    aws s3 mv "${db_backup_file}" s3://"${MPR_BACKUP_S3_BUCKET}"/"$(basename ${db_backup_file})" || exit 1
    aws s3 mv "${submission_backup_file}" s3://"${MPR_BACKUP_S3_BUCKET}"/"$(basename ${submission_backup_file})" || exit 1
}

main() {
    datestamp=$(date +"%m%d%y")
    create_backup_directories
    create_mysql_password_file
    create_database_backup
    create_submissions_backup
    upload_backups_to_s3
}

main
