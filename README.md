# graphbum
A Raspberry PI PISCREEN based clock / photo slideshow / weather info app

A python script that displays all images from a specific facebook photo album. Features include a clock, date, location based weather information and fading between images. 

I got a cheap PISCREEN clone from ebay with just this application in mind. It was some hassle to get up in Python, with kernel modules and emulating into /dev/fb1, so maybe this will save someone the trouble. For the Raspbian configuration, search for "dtoverlay=piscreen", that should get you there. That should also be your entry for tweaking if the fade is not flowing fluidly. 

There is a nice hack for WIFI issues on startup: I added this script as a cron job @reboot, but often my slideshow would start before WIFI was up. I solved this by adding the --wait option, which will wait on startup until /bin/hostname -I returns a valid IP address. 


