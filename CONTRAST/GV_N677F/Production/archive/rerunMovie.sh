#/usr/bin/ffmpeg -passlogfile ./ffmpeg_rf02 -r 15 -b 1500000 -y -pass 1 -i /scr/raf/Prod_Data/CONTRAST/Movies/AnnotatedImages_rf02/%05d.jpg /scr/raf/Prod_Data/CONTRAST/Movies/rf02.20140113.201425_295843.mp4
#/usr/bin/ffmpeg -passlogfile ./ffmpeg_rf02 -r 15 -b 1500000 -y -pass 2 -i /scr/raf/Prod_Data/CONTRAST/Movies/AnnotatedImages_rf02/%05d.jpg /scr/raf/Prod_Data/CONTRAST/Movies/rf02.20140113.201425_295843.mp4
#/usr/bin/ffmpeg -passlogfile ./ffmpeg_rf03 -r 15 -b 1500000 -y -pass 1 -i /scr/raf/Prod_Data/CONTRAST/Movies/AnnotatedImages_rf03/%05d.jpg /scr/raf/Prod_Data/CONTRAST/Movies/rf03.20140117.001451_065344.mp4
#/usr/bin/ffmpeg -passlogfile ./ffmpeg_rf03 -r 15 -b 1500000 -y -pass 2 -i /scr/raf/Prod_Data/CONTRAST/Movies/AnnotatedImages_rf03/%05d.jpg /scr/raf/Prod_Data/CONTRAST/Movies/rf03.20140117.001451_065344.mp4
#/usr/bin/ffmpeg -passlogfile ./ffmpeg_rf04 -r 15 -b 1500000 -y -pass 1 -i /scr/raf/Prod_Data/CONTRAST/Movies/AnnotatedImages_rf04/%05d.jpg /scr/raf/Prod_Data/CONTRAST/Movies/rf04.20140119.002944_072554.mp4
#/usr/bin/ffmpeg -passlogfile ./ffmpeg_rf04 -r 15 -b 1500000 -y -pass 2 -i /scr/raf/Prod_Data/CONTRAST/Movies/AnnotatedImages_rf04/%05d.jpg /scr/raf/Prod_Data/CONTRAST/Movies/rf04.20140119.002944_072554.mp4
#/usr/bin/ffmpeg -passlogfile ./ffmpeg_rf05 -r 15 -b 1500000 -y -pass 1 -i /scr/raf/Prod_Data/CONTRAST/Movies/AnnotatedImages_rf05/%05d.jpg /scr/raf/Prod_Data/CONTRAST/Movies/rf05.20140122.001818_074703.mp4
#/usr/bin/ffmpeg -passlogfile ./ffmpeg_rf05 -r 15 -b 1500000 -y -pass 2 -i /scr/raf/Prod_Data/CONTRAST/Movies/AnnotatedImages_rf05/%05d.jpg /scr/raf/Prod_Data/CONTRAST/Movies/rf05.20140119.001818_074703.mp4
#/usr/bin/ffmpeg -passlogfile ./ffmpeg_rf09 -r 15 -b 1500000 -y -pass 1 -i /scr/raf/Prod_Data/CONTRAST/Movies/AnnotatedImages_rf09/%05d.jpg /scr/raf/Prod_Data/CONTRAST/Movies/rf09.20140204.000454_072657.mp4
#/usr/bin/ffmpeg -passlogfile ./ffmpeg_rf09 -r 15 -b 1500000 -y -pass 2 -i /scr/raf/Prod_Data/CONTRAST/Movies/AnnotatedImages_rf09/%05d.jpg /scr/raf/Prod_Data/CONTRAST/Movies/rf09.20140204.000454_072657.mp4

# Mar 2016 - ffmpeg inputs changed per below
#/usr/bin/ffmpeg -r:15 -b:1500000 -y -i /scr/raf/Prod_Data/CONTRAST/Movies/AnnotatedImages_rf09/%05d.jpg -passlogfile test -pass 1 /scr/raf/Prod_Data/CONTRAST/Movies/rf09.20140204.000454_072657.mp4
