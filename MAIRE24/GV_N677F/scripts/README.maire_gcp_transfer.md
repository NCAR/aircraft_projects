# Steps required to get the GCP bucket configured for MAIRE 2024

1. Install gsutil
    -  we followed the steps at https://cloud.google.com/storage/docs/gsutil_install#windows [Accessed June 28, 2024]

2. If "nice"-ing the command is desired, install time (not done for MAIRE 2024)

3. Configure gcloud to use the ncar account:
    gcloud config configurations create mair
    gcloud config set account ncar-upload@methanesat.org
    gcloud config configurations list # should see mair set to true, with email near-upload@methanesat.org
    gcloud auth login # enter the email address ncar-upload@methanesat.org and the password sent by Tom Melendez at methanesat

4. From PowerShell run: 
    gsutil -m cp -r <location where data dir is mounted> gs://msat-prod-data-methaneair-upload

   The bucket name is: msat-prod-data-methaneair-upload
   The project name should be: msat-prod-data-9475 (might not be asked for this)
   The email account is: near-upload@methanesat.org
