# Build Prerequisites

## EOL Groundstations
As root:
```
dnf install \
    ImageMagick-perl \
    epel-release \
dnf install --nogpgcheck \
    https://mirrors.rpmfusion.org/free/el/rpmfusion-free-release-9.noarch.rpm
dnf install ffmpeg ffmpeg-devel --allowerasing
```
May also need to install `screen`
if "display" isn't working for you, you can try
```
dnf install ristretto
```
