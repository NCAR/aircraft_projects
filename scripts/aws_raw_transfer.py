#! /usr/bin/env python3

import argparse
import sys
import os

def main():

    awsupload = AWSUpload()
    args = awsupload.parse_args()
    awsupload.s3copy(args)

class AWSUpload(self):

    def parse_args(self):

        parser = argparse.ArgumentParser(
            description='Provide a project name and processing dir.')
        parser.add_argument('project_name', type=str, help='provide project name in all caps')
        parser.add_argument('scratch_dir', type=str, help='provide a processing dir')

        if len(sys.argv) ==1:
        parser.print_help(sys.stderr)
        sys.exit(1)
    args = parser.parse_args()
    return(args)

    def s3copy(self, args):

        project_name = args.project_name
        scratch_dir = args.scratch_dir
        try:
            os.mkdir('/'+scratch_dir+'/'+project_name)
            os.cd('/'+scratch_dir+'/'+project_name)

        except:
            print('Error making processing dir.')

        try:
            os('tar -cvjf '+project_name+'.tar.bz2 /scr/raf_Raw_Data/'+project_name)
            os('split -b 500m '+project_name+'.tar.bz2 '+project_name+'.tar.bz2.split')
            os('aws s3 cp /scr/tmp/taylort/'+project_name+' s3://raf-rawdatabackup/ --recursive --profile raf-databackup')
            os.rm(project_name+'.tar.bz2')

if __name__ == "__main__":
    main()
