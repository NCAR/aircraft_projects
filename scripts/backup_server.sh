#!/bin/bash
rsync -avh --exclude=data --exclude=eolroot --exclude=tmp --exclude=lost+found --exclude=opt --exclude=/ads/Desktop/RAF_TECHS_INFO /home/ /run/media/ads/Drive6/C130_centos8/home 
