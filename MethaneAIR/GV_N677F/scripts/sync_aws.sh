#! /usr/bin/bash
# script to copy data files from MethaneAIR airborne instrument to a Harvard AWS S3 bucket

# MethaneAIR instrument organizes flight files into a single dir per flight. Update filename for each flight
FLIGHT_DATE=20191108

# for each file in instrument data dir, compute md5sum
find /run/media/ads/MAIR5TB/$FLIGHT_DATE -type f -exec md5sum {} \; > /run/media/ads/MAIR5TB/$FLIGHT_DATE/md5sum.txt

# change to aws cli location on gs
cd /usr/local/aws-cli/v2/2.2.18/dist

# perform the aws recursive copy default aws configuration for MSAT
time aws s3 cp /run/media/ads/MAIR5TB/$FLIGHT_DATE s3://msat-ball-sao-hrvd/MethaneAIR-July-2021/$FLIGHT_DATE --recursive
