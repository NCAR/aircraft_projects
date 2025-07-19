#!/bin/bash
echo "unmounting camera directory from ads"
sudo umount /data/r1/GOTHAAM/camera_images -l
echo "powering off camera server"
ssh camera sudo poweroff
echo "camera server will be entirelly off when front light stop blinking"
sleep 30
