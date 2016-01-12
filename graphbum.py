import facebook
import requests
import os
import pygame
import sys
import time
from time import strftime, gmtime
import math
from StringIO import StringIO
from PIL import Image, ImageFont, ImageDraw, ImageFilter, ImageEnhance, ImageFile
from urlparse import urlparse
import urllib
import json
import commands
import math
from pygame.locals import *

## We're cool with truncated images, since there's an option internet 
## is away. We'll just show these with some gray in it. 
ImageFile.LOAD_TRUNCATED_IMAGES = True

## Time to display any given image, in seconds
IMAGE_PAUSE = 25

## Time needed to wait after start, in case wifi is slower in connecting then we are
START_PAUSE = 30

## Set up the piscreen for pygame
os.environ['SDL_VIDEODRIVER'] = 'fbcon'
os.environ["SDL_FBDEV"] = "/dev/fb1"
w = 480
h = 320
black = 0, 0, 0
screenSize=(w,h)

weather_api=""

## If not told better, assume we are in the Netherlands, the center of the world
if not 'TZ' in os.environ:
	os.environ['TZ'] = ':Europe/Amsterdam'; time.tzset()

## Cachedir for graph files, directory will be created if needed
cacheDir = "/tmp/graphcache"

# Return true if both image and screen are the same size
def matchSize(image, screen):
    width, height = image.size
    return width == screen[0] and  height == screen[1]

## Fancy resize
## - Expand canvas to match the height/width ratio
## - Fill black borders with a blurred image 
## - Add clock and date
## - Resize down to requested size
def resizeImage(image, height, width):
    ## First, get correct ratio
    correct = height / width
    
    ## Then get current ratio
    current = image.size[1] / image.size[0]
    
    ## Image is of different ratio, so we need to resize
    if(current <> correct):

	## ..either wider or higher
        if(current < correct):
            newImage = Image.new(image.mode, (image.size[0],((image.size[0] * height) / width)))
        elif current > correct:
            newImage = Image.new(image.mode, (((image.size[1] * width) / height), image.size[1]))
	
	## To prevent black bars, we pull a blurred image over the screen 
	bgImage = image.copy()
	bgImage = bgImage.resize(newImage.size)
	bgImage = bgImage.filter(ImageFilter.GaussianBlur(radius=20))
	enhancer = ImageEnhance.Brightness(bgImage)
	bgImage = enhancer.enhance(0.5)
	newImage.paste(bgImage)

	## Now copy original image back into this full size image in a good location
        x1 = int(math.floor((newImage.size[0] - image.size[0]) / 2))
        y1 = int(math.floor((newImage.size[1] - image.size[1]) / 2))
        newImage.paste(image, (x1, y1, x1 +  image.size[0], y1 +  image.size[1]))

	## Done!
	image = newImage

    ## ...also, actually resize
    image = image.resize((width, height), Image.ANTIALIAS)
	  
    return image

def drawTimeDateOnImage(timage):
    ## Draw time on image Type some text on image
    font = ImageFont.truetype("/root/graphbum/ironman.ttf", 48)
    draw = ImageDraw.Draw(timage, 'RGBA')
    draw.rectangle((6,185,115, 314),fill=(0,0,0,100))
    draw.text((10, 235),strftime("%d / %m"),(255,255,255, 110),font=font)
    draw.text((10, 275),strftime("%H : %M"),font=font, fill=(255,255,255, 110))

    tinyfont = ImageFont.truetype("/root/graphbum/ironman.ttf", 10)
    draw.text((430, 310),ip,(255,255,255, 110),font=tinyfont)

    return timage


def drawWeatherOnImage(image):
	url = "http://api.openweathermap.org/data/2.5/forecast?q=rijswijk,netherlands&units=metric&lang=nl&cnt=2&APPID=" + weather_api
	jsonraw = None
	while(jsonraw == None):
		try:
			jsonraw =  urllib.urlopen(url).read()
	        except Exception as e:
        		print("Got exception trying for weather info, will attempt again in 10 seconds")
			print(e)
        	        time.sleep(10)
	result = json.loads(jsonraw)  # result is now a dict
	icon0URL = 'http://openweathermap.org/img/w/' + result['list'][0]['weather'][0]['icon'] + '.png'
	icon1URL = 'http://openweathermap.org/img/w/' + result['list'][1]['weather'][0]['icon'] + '.png'
	print('http://www.algarexperience.com/static/images/weather/' + result['list'][0]['weather'][0]['icon'] + '.png')

	icon0Image = fetchOrCache(icon0URL)
	icon1Image = fetchOrCache(icon1URL)
	image.paste(icon0Image, (5,190, 5 + icon0Image.size[0], 190 + icon0Image.size[1]), icon0Image)
	image.paste(icon1Image, (12 + icon0Image.size[0],190, 12 + icon0Image.size[0] + icon1Image.size[0], 190+icon1Image.size[1]), icon1Image)
	return image;

def getCachedFileName(imgUrl):
       urlParsed = urlparse(imgUrl)
       baseFile = os.path.basename(urlParsed.path)
       return cacheDir + "/" + baseFile


def cache(image, filename):
     cachedFile = getCachedFileName(filename)
     image.save(cachedFile)
    
def fetchOrCache(imgUrl, setTransparent = False):
    cacheFile = getCachedFileName(imgUrl);
    ## If a cached file does not exist, create it by opening the facebook image URL 
    if(not os.path.isfile(cacheFile)):
	imageStream = None
	times = 0;
	while((imageStream is None) and times < 5):
		times = times + 1
		try:
		        imageStream = urllib.urlopen(imgUrl)
		except:
			print("Could not connect to " + imgUrl)
			time.sleep(10)
	if times >= 5:
		return None;
        image = Image.open(StringIO(imageStream.read()))
    else:
        image = Image.open(cacheFile)
    cache(image, imgUrl)
    return image;

def blitScreen(surface):
        screen.blit(surface, (0,0))
        pygame.display.flip()
        pygame.time.delay(20)

def showImageOnScreen(fbPicture):
    source = fbPicture['source']
    image = fetchOrCache(source)

    if image is None:
	time.sleep(IMAGE_PAUSE)
	return

    if(not matchSize(image, screenSize)):
        image = resizeImage(image, h, w)
        cache(image, os.path.basename(source))

    image = drawTimeDateOnImage(image)
    image = drawWeatherOnImage(image)

    mode = image.mode
    size = image.size
    data = image.tostring()

    ## Convert the image to a pygame compatible string
    surface = pygame.image.fromstring(data, size, mode)
    
    ## Image fading. First slow, fast at later stages
    i = 1
    while(i < 255):
        i = i + math.ceil(i / 10)
        surface.set_alpha(i)
	blitScreen(surface)
    surface.set_alpha(255)
    blitScreen(surface)

    ## Linger in the beauty of our product
    pygame.time.wait(1000 * IMAGE_PAUSE)


def fetchPosts(fbUser):
	posts = None
	while posts == None:
        	try:
                	posts = graph.get_connections(fbUser, 'photos')
	        except:
        	        print("Got exception trying for facebook connection, will attempt again in 10 seconds")
	                print(e)
        	        time.sleep(10)
	return posts

## Program starts here!
ip = ""
if len(sys.argv) >= 2:
	## Added a waittime since my RPI wifi was slow to start
	if sys.argv[1] == '--wait':
		while(ip == ""):
			## My IP please..
			ip = commands.getoutput("/bin/hostname -I")
			if(ip == ""):
				print("Could not get IP, trying again..")
				time.sleep(5)

    
app_secret = ''
app_id = ''

# You'll need an access token here to do anything.  You can get a temporary one
# here: https://developers.facebook.com/tools/explorer/

# Genereer een graphbum user token op die explorer URL
# Daarna, vul die in achter deze URL

token = ""


## My user id

graph = facebook.GraphAPI(token)
pat = False
while True and not pat:
	try:
		pat = graph.get_object('115724255153018')['id']
	except Error:
		print("Failed to connect.. Trying again in some..")	
		time.sleep(10)
		
print(pat)
posts = graph.get_connections('115724255153018', 'photos')

## Init pygame screen and stuff
pygame.init()
pygame.mouse.set_visible(False)
screen = pygame.display.set_mode(screenSize)

if not os.path.isdir(cacheDir):
    os.makedirs(cacheDir)

posts = fetchPosts('115724255153018')
# Wrap this block in a while loop so we can keep paginating requests until
# finished.
while True:
    try:
        # Perform some action on each post in the collection we receive from
        # Facebook.
        [showImageOnScreen(fbPicture=fbPicture) for fbPicture in posts['data']]
        # Attempt to make a request to the next page of data, if it exists.
        posts = requests.get(posts['paging']['next']).json()
    except KeyError:
        # When hell has no more pages the dead shall walk the earth
        posts = fetchPosts('115724255153018')

