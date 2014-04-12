import matplotlib.pyplot as plt
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
import io
import binascii
import urllib

import datetime

import datetime
import os.path

dataDir = "data"

def getPhoto(day):
  fileName = os.path.join(dataDir, day) +"-photo.jpg"
  if not os.path.isfile(fileName):
    content = urllib.urlopen("http://map1.vis.earthdata.nasa.gov/wmts-geo/MODIS_Terra_CorrectedReflectance_TrueColor/default/" + day + "/EPSG4326_250m/1/0/0.jpg")
    with open(fileName, "wb") as f:
      f.write(content.read())
    return content
  else:
    with open(fileName, "rb") as f:
      content = f.read()
      return content


def getCloud(day):
  fileName = os.path.join(dataDir, day) +"-cloud.jpg"
  if not os.path.isfile(fileName):
    content = urllib.urlopen("http://map1.vis.earthdata.nasa.gov/wmts-geo/MODIS_Terra_Cloud_Top_Temp_Day/default/" + day + "/EPSG4326_2km/1/0/0.png")
    with open(fileName, "wb") as f:
      f.write(content.read())
    return content
  else:
    with open(fileName, "rb") as f:
      content = f.read()
      return content

# Saves the images
def getImageData(nrDays, startDay):
  days = [(startDay + datetime.timedelta(days=x)).strftime("%Y-%m-%d") for x in xrange(nrDays)]
  return map(getPhoto, days), map(getCloud, days)


date = datetime.datetime.today()

getImageData(10, date)