# Build Prerequisites

## RAF Groundstation

### System packages, install as root
```
dnf install \
    ImageMagick-perl \
    epel-release
dnf install --nogpgcheck \
    https://mirrors.rpmfusion.org/free/el/rpmfusion-free-release-9.noarch.rpm
dnf install ffmpeg ffmpeg-devel --allowerasing
```

What needs what:

- `ImageMagick-perl` - the `Image::Magick` Perl module, used by
  `combineCameras.pl` to build each combined frame. It also brings in
  ImageMagick itself, which gives you the `identify` command that
  `Image_Filter.pl` runs to judge how dark an image is.
- `epel-release` and the rpmfusion release RPM - repositories only; they carry
  no tooling themselves, they just make `ffmpeg` installable.
- `ffmpeg` and `ffmpeg-devel` - used by `combineCameras.pl` for the two-pass
  encode that turns the combined frames into the output movie. Note that
  `combineCameras.pl` calls `/usr/bin/ffmpeg` by absolute path.

May also need to install `screen`. Nothing here calls it; it is for keeping a
long movie run alive when you have to ssh to one of the machines that has
ffmpeg installed.

If ImageMagick's `display` isn't working for you when viewing images by hand,
you can try
```
dnf install ristretto
```

### Python packages

`analyze_frames.py` needs two packages that are not in the standard library.
They are listed in [requirements.txt](requirements.txt):

```
python3 -m pip install -r requirements.txt
```

Install them into the same interpreter that runs the script - see the notes at
the top of `requirements.txt`, which cover picking the right python and using a
virtual environment instead of a system or conda one.

## Mac

### Testing on a Mac

Homebrew marks its pythons as "externally managed" (PEP 668) so that pip cannot
write into a tree Homebrew owns. To test on a Mac, you will need to use a
virtual environment

```
cd scripts/camera
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

You can confirm the install by running:

```
python3 -c "import astral, pytz; print('ok')"
```

While the environment is active, `python3` is the one inside `.venv`, so
`analyze_frames.py` picks it up from its `#!/usr/bin/env python3` line with no
change to the script. Every new shell needs `source .venv/bin/activate` again;
`deactivate` when you are done.

Two Mac-specific traps:

- **`pip` and `python3` are often different installs.** If you have both
  Homebrew and miniconda, `which python3` can be
  `/opt/homebrew/bin/python3` while `which pip` is
  `/opt/miniconda3/bin/pip`. Activating the venv avoids this issue.
