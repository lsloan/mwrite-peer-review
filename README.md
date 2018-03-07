# M-Write Peer Review

## OpenShift Setup Instructions

To allow OpenShift to pull from a private Github repository:
1. Create a deployment key
    ```bash
    $ ssh-keygen -t rsa -C "you@email.com" -f mwrite-peer-review-github-key
    ```
2. Add the deployment key to your Github repository
3. Add the key as an OpenShift secret
    ```bash
    $ oc secrets mwrite-peer-review-github-key --ssh-secret=mwrite-peer-review-github-key
    ```

To add a course instance (make sure to change names where appropriate):
1. Create database, configuring as appropriate (only if in Dev / Staging):
    ```bash
    oc new-app mysql-persistent --name mwrite-peer-review-dev-test-db \
        -p MYSQL_USER=username                                        \
        -p MYSQL_PASSWORD=password                                    \ 
        -p MYSQL_DATABASE=db_name                                     \
        -p MYSQL_ROOT_PASSWORD=root_password                          \
        -p VOLUME_CAPACITY=512Mi                                      \
        -p MYSQL_VERSION=5.7                                          \
        -p MEMORY_LIMIT=512Mi                                         \
        -p DATABASE_SERVICE_NAME=mwrite-test-db
    ```
2. Create a persistent volume claim file called `pvc.yaml` for submission file storage:
    ```yaml
    apiVersion: "v1"
    kind: "PersistentVolumeClaim"
    metadata:
      name: "mwrite-peer-review-dev-storage-claim"
    spec:
      accessModes:
        - "ReadWriteOnce"
      resources:
        requests:
          storage: "1Gi"
    ```
    ```bash
    $ oc create -f pvc.yaml
    ```
    N.B. It might be necessary to create a ticket with the container team
    to create the underlying volumes.  They will need to know the
    requested size and access mode.  Do *not* specify a volumeName (or
    tell them what you give it, if you do).
3. Create an OpenShift secret with the following files and contents:
    * `secret.key` -- secret key file for Django; generate with
        ```bash
        $ python -c "import string,random; uni=string.ascii_letters+string.digits+string.punctuation; print ''.join([random.SystemRandom().choice(uni) for i in range(random.randint(45,50))])" >> secret.key
        ```
    * `lti_credentials.json`
        ```bash
        # to generate consumer_key / consumer_secret
        $ cat /dev/urandom | env LC_CTYPE=C tr -dc 'a-zA-Z0-9' | fold -w 32 | head -n 1
        ```
        ```json
        {"consumer_key": "consumer_secret"}
        ```
    * `database.json`
        ```json
        {
          "ENGINE": "django.db.backends.mysql",
          "NAME": "mwrite",
          "USER": "mwrite",
          "PASSWORD": "mwrite",
          "HOST": "192.168.99.100",
          "PORT": "3306"
        }
        ```
    * `mwrite-test-course-secret.yaml`
        ```yaml
        apiVersion: v1
        kind: Secret
        metadata:
          name: mwrite-test-course-secret
          namespace: mwrite-peer-review-dev
        data:
          secret.key: <... base64 encoded file ...>
          lti_credentials.json: <... base64 encoded file ...>
          database.json: <... base64 encoded file ...>
        ```
    * Once that's done:
        ```bash
        $ oc create -f mwrite-test-course-secret.yaml
        ```
4. Create the app (replacing values where appropriate); TODO check git URL
    ```bash
    $ oc new-app https://github.com/M-Write/mwrite-peer-review.git \
          --name=mwrite-peer-review-dev-test-course                \
          -e MWRITE_PEER_REVIEW_SECRET_KEY_PATH=/etc/mwrite-peer-review/secret.key \
          -e MWRITE_PEER_REVIEW_DEBUG_MODE=true    # false for prod/staging \
          -e MWRITE_PEER_REVIEW_LTI_CREDENTIALS_PATH=/etc/mwrite-peer-review/lti_credentials.json \
          -e MWRITE_PEER_REVIEW_DATABASE_CONFIG_PATH=/etc/mwrite-peer-review/database.json \
          -e MWRITE_PEER_REVIEW_CANVAS_API_URL=https://umich-dev.instructure.com/api/v1/ \
          -e MWRITE_PEER_REVIEW_CANVAS_API_TOKEN=<canvas api token> \
          -e MWRITE_PEER_REVIEW_LMS_URL=https://umich-dev.instructure.com \
          -e MWRITE_PEER_REVIEW_TIMEZONE=America/Detroit \
          -e MWRITE_PEER_REVIEW_APP_HOST=peer-review-dev.mwrite.openshift.dsc.umich.edu \
          -e MWRITE_PEER_REVIEW_SUBMISSIONS_PATH=/srv/mwrite-peer-review
          -e MWRITE_PEER_REVIEW_ALLOWED_HOSTS=peer-review-dev.mwrite.openshift.dsc.umich.edu
          -e MWRITE_PEER_REVIEW_LANDING_ROUTE=/course/15
          -e MWRITE_PEER_REVIEW_GOOGLE_ANALYTICS_TRACKING_ID=<your GA tracking ID>
    ```
5. Add the config secret that was created in step 3 as a volume mount
    ```bash
    $ oc volume dc/mwrite-peer-review-test-course --add \
          -t secret                                     \
          -m /etc/mwrite-peer-review                    \
          --secret-name mwrite-test-course-secret
    ```
6. Add the file storage PVC as a volume mount
    ```bash
    $ oc volume dc/mwrite-peer-review-test-course --add \
          -t persistentVolumeClaim                      \
          -m /srv/mwrite-peer-review                    \
          --claim-name mwrite-peer-review-dev-storage-claim
    ```
7. Edit the created buildconfig to correct the Git repository URL (TODO still needed?), remove
   the Github secret under the `spec.triggers` section and add the correct 
   secret under `spec.source.sourceSecret` and `spec.source.name`
8. Create a route pointing to the service that was just created as
   `mwrite-test-course-route.yaml` (replacing details as appropriate)
    ```yaml
    apiVersion: v1
      kind: Route
      metadata:
        name: mwrite-peer-review-dev-course-15
        namespace: mwrite-peer-review-dev
      spec:
        host: peer-review-dev.mwrite.openshift.dsc.umich.edu
        path: /course/15
        port:
          targetPort: 8000-tcp
        tls:
          termination: edge
          insecureEdgeTerminationPolicy: Redirect
          certificate: |
            -----BEGIN CERTIFICATE-----
              ... cert details ...
            -----END CERTIFICATE-----
          key: |
            -----BEGIN PRIVATE KEY-----
              ... key details ...
            -----END PRIVATE KEY-----
        to:
          kind: Service
          name: mwrite-peer-review-dev-test-course
    ```
    ```bash
    $ oc create -f mwrite-test-course-route.yaml
    ```
9. Start a build to make sure that everything configured so far is working
    ```bash
    $ oc start-build bc/mwrite-peer-review-dev-test-course --follow
    ```
10. Once the build is done and the pod is running, rsh and run Django migration
11. Add LTI tool to Canvas using lti_config.xml
