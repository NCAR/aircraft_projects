#! /usr/bin/bash
# script to copy data files from MethaneAIR airborne instrument to a Harvard AWS S3 bucket

# MethaneAIR instrument organizes flight files into a single dir per flight. Update filename for each flight
FLIGHT_DATE=20191108

# for each file in instrument data dir, compute md5sum
for file in /run/media/ads/MAIR5TB/$FLIGHT_DATE/*; do md5sum $file; done > /run/media/ads/MAIR5TB/$FLIGHT_DATE/md5sum.txt


# change to aws cli location on gs
cd /usr/local/aws-cli/v2/2.2.18/dist

# perform the aws recursive copy (change based on account info)
time aws s3 cp /run/media/ads/MAIR5TB/$FLIGHT_DATE s3://raf-rawdatabackup/methaneairtest/ --recursive --profile raf-databackup

