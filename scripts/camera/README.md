# Create Digital Camera Movies from RAF still images

## RAF Aircraft Camera Image processing notes
Over time RAF has operated multiple different camera types. The best way to determine the type for a project is to ask the software engineers. For older projects, you can also check the camera and movie writeup in the aircraft project documentation off the [project pages](https://www.eol.ucar.edu/all-field-programs) or check the Digital Camera Imagery Notes associated with the camera and movie datasets in the [Field Data Archive](https://data.eol.ucar.edu).

## To create movies from the camera still images:
**Work on a physical server rather than a VM as these scripts take quite a bit of cpu. As of May, 2024, eol-saturn running Alma9 and mercury running RHEL8 are both good options**

**When running scripts, work in /net/jlocal/projects on the servers - referred to as proj below - under the <project>/<platform> dir for the project you are working on. **

1. Ensure the still images (forward, down, left, right) are archived to the Field Data Archive (FDA). If not, archive them using the archAC.sh script located in Production/archive under the proj dir.

1. Determine the desired list of variables for annotation or for animated plots. Work with the project PIs to generate a list. Request help from the RAF Project Manager if you are not sure who on the PI team to reach out to.

1. Delete nighttime images; Delete images taken prior to takeoff, after landing, in hanger, etc.
- You can browse the images with `ristretto` to check for dark/ground images:
  > ssh -Y <server you are working on>
  > ristretto
  > Use the GUI to navigate to the image directory you want to view
- You can also use `flt_time` to extract takeoff and landing times from the netCDF files and use those times to remove images that are on the ground. Run `flt_time` without any options for a usage statement.
- To delete images:
  - Update the `filter_images.sh` script in the proj/<project>/<platform>/scripts dir to have the project and flight variables and comment/uncomment the desired camera directions.
  - Run `filter_images.sh`

1. Generate preliminary movies if final netCDF data is not available yet and movies have been requested. Otherwise, generate final production movies:
- Edit `proj/<project>/<platform>/movieParamFile` to point to the correct netcdf and camera subdirs and list the params desired for the movies. Here is a sample file format:
```
#includeData is required
includeData = no          ----------> can be yes (to include data to the right) or no (to omit).
netcdfFile = /scr/raf_data/NOMADSS####.nc  ----------> Not needed if includeData = no; may also exist in /scr/raf/Prod_Data/
gravityD = East ----------> Optional
# Times will be determined from the images in imageDir1
# All other image dirs will try to match these times.
imageDir1 = /scr/raf/Raw_Data/<project>/camera_images/flight_number_####/forward
#gravity1 = West
gravity1 = North ---------------> North = Front facing; South = down.
#movieDirectory is required  --------------> set dir to Raw_Data for preliminary videos; Prod_Data for final videos
movieDirectory = /scr/raf/Raw_Data/<project>/Movies
#2 overlays are required --------> You must set to 'no' if not desired
overlayImageTime = yes
overlayImagePointing = yes
#numCameras is required
numCameras = 2
# If numCameras > 1, add additional optional dirs and cameras here:
#imageDir2 = /scr/raf/Raw_Data/MPEX/camera_images/flight_number_####/left
#gravity2 = SouthWest
#gravity2 = West
#imageDir3 = /scr/raf/Raw_Data/MPEX/camera_images/flight_number_####/right
#gravity3 = SouthEast
#gravity3 = East
imageDir2 = /scr/raf/Raw_Data/NOMADSS/camera_images/flight_number_####/down
#gravity4 = NorthEast
gravity2 = South

# For the moment, assume all cameras are the same type - required.
cameraName = Flea

# The outputResolution should be proportional to the scale:
# For one image per frame, leave the ht and add 200 to the width
# For two images, double the ht and add 50 or so padding,
#   and add 200 to the width
# For three images, double the ht and width (plus padding).
#outputResolution=1536x768
scale = 512x384!     #(w X h)  -------------> set scale & resolution to 1024x768 for hi-res movies
outputResolution=512x768
outputResolutionD=712x768
#scale = 341x256!
outputFrameRate = 15
mp4BitRate = 1500000
endParameters

GGALT
GGLAT
GGLON
ATX
DPXC
PSXC
RHUM
TASX
THDG
PITCH
ROLL
WSC
WDC
DP_VXL
VMR_VXL
endVariablesLT  --------------> The above params are not needed if data is not included
```
- Do not include Time in the variable list in movieParamFile. The code will die with an obscure error.

- Start a screen session as these commands usually take awhile to complete:
> screen
- Edit createMovies.sh and set the flight number
  - If you would like to run more than one flight at a time, be sure to use the nice command so as not to overload the CPU

  > nice +19 /net/jlocal/projects/scripts/camera/combineCameras.pl ../movieParamFile RF01
  - Otherwise, comment out all but one line and run 1 instance at a time

- Run createMovies.sh from the scripts dir:
> ./createMovies.sh
- Once the script starts, go into the movie dir and then into the Annotated_images_## dir and look at an image using:
 xdg-open 00001.jpg
- Make sure that the layout, resolution, data overlays, etc are correct. If they are not, kill the createMovies script, modify params file, and try again.

- If the .jpg images are all created, but the movie fails to automatically generate or needs to be re-made, you can run ffmpeg manually as follows:
  > ffmpeg -passlogfile ./ffmpeg_rf## -r 15 -b 1500000 -y -pass 1 -i /scr/raf/<data_dir>/<PROJECT>/Movies/AnnotatedImages_rf##/%05d.jpg /scr/raf/<data_dir>/<PROJECT>/Movies/rf##.YYYYMMyy.HHmmSS_HHmmSS.mp4

and then run the same command a second time with "–pass 2" insteadl of "-pass 1"

  > /usr/bin/ffmpeg -passlogfile ./ffmpeg_rf## -r 15 -b 1500000 -y -pass 2 -i /scr/raf/<data_dir>/<PROJECT>/Movies/AnnotatedImages_rf##/%05d.jpg /scr/raf/<data_dir>/<PROJECT>/Movies/rf##.YYYYMMyy.HHmmSS_HHmmSS.mp4


**If you wish to combine the .mp4 file with a set of animated plots, please follow the instructions in the [aircraft_movie_animations](https://github.com/NCAR/aircraft_movies_animations) GitHub repository. A python program takes a set of parameters defined in a configuration file to generate a set of animated plots that are then combined with the original .mp4 using ffmpeg. This must be done on eol-saturn.**


1. Load the data into the FDA as a dataset. Enable previews for videos & copy/load them to/from  `/net/archive/data/<project>/aircraft/<platform>/movies/`


1. Create a documentation file for the camera images and movies to be added to the project documentation online. There are examples in /net/jlocal/projects/scripts/camera/docs. For each project, reach out to an RAF SE to confirm which cameras flew (for example, in the future there will be left and right cameras for the C-130, sometimes we don't fly all cameras on the G-V, and cameras are occasionally upgraded to new versions with new specs) and modify a copy of the example files as needed.

**NOTE:** For help writing up the Digital Camera Imagery Notes, reach out to the RAF SEs and/or Josh Carnes.

1. If the SE's say that a camera has changed permanently, update the example files to reflect this for all future projects.
1. Add the documentation file to the loaded dataset in the FDA. 

## Notes
Optional - Convert Axis images to 640x480 for square pixels,

Optional - Apply sharpening, possibly reduce resolution for Flea images.

### Movie parameters
From Stuart: The H.264 codec is the best I've seen for quality and size and is widely supported.
Presumably ffmpeg supports this codec but I don't think our installation currently does.
Quicktime supports H.264.

  * Final H & V resolutions should be a multiple of 16.
  * Typical bit rate is 1000 - 1500 Mb/s. Downward images might need more (faster scene change).
