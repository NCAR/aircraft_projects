# Build Prerequisites

## EOL Groundstations
As root:
```
dnf install \
    ristretto \
    ImageMagick-perl \
    epel-release \
dnf install --nogpgcheck \
    https://mirrors.rpmfusion.org/free/el/rpmfusion-free-release-9.noarch.rpm
dnf install ffmpeg ffmpeg-devel --allowerasing
```
May also need to install `screen`
