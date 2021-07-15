#! /usr/bin/bash

#update filename for each flight
FLIGHT_DATE=12341212

# for each file in instrument data dir, compute md5sum
for file in /run/media/ads/MAIR5TB/$FLIGHT_DATE/*; do md5sum $file; done > /run/media/ads/MAIR5TB/$FLIGHT_DATE/md5sum.txt


# change to aws cli location on gs
cd /usr/local/aws-cli/v2/2.2.18/dist

# perform the aws recursive copy (change based on account info)
time aws s3 cp /run/media/ads/MAIR5TB/$FLIGHT_DATE s3://<bucket_name> --recursive
