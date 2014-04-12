import matplotlib.pyplot as plt
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
import io
import binascii
import urllib

import numpy as np
import datetime
import os.path

def dayDeltaBack(day, delta):
  return (day + datetime.timedelta(days=delta)).strftime("%Y-%m-%d")

dataDir = "data"

def getPhoto(day):
  fileName = os.path.join(dataDir, day) +"-photo.jpg"
  if not os.path.isfile(fileName):
    content = urllib.urlopen("http://map1.vis.earthdata.nasa.gov/wmts-geo/MODIS_Terra_CorrectedReflectance_TrueColor/default/" + day + "/EPSG4326_250m/1/0/0.jpg").read()
    with open(fileName, "wb") as f:
      f.write(content)

  return Image.open(fileName)

def getCloud(day):
  fileName = os.path.join(dataDir, day) +"-cloud.png"
  if not os.path.isfile(fileName):
    content = urllib.urlopen("http://map1.vis.earthdata.nasa.gov/wmts-geo/MODIS_Terra_Cloud_Top_Temp_Day/default/" + day + "/EPSG4326_2km/1/0/0.png").read()
    with open(fileName, "wb") as f:
      f.write(content)

  return Image.open(fileName)

def getNoData(day):
  fileName = os.path.join(dataDir, day) +"-nodata.png"
  if not os.path.isfile(fileName):
    content = urllib.urlopen("http://map1.vis.earthdata.nasa.gov/wmts-geo/MODIS_Terra_Data_No_Data/default/" + day + "/EPSG4326_250m/1/0/0.png").read()
    with open(fileName, "wb") as f:
      f.write(content)

  return Image.open(fileName)


# Saves the images
def getImageData(startDay, nrDays):
  days = [dayDeltaBack(startDay, x) for x in xrange(nrDays)]
  return map(getPhoto, days), map(getCloud, days), map(getNoData, days)

def growMask(mask, up, left):
  maskBuffer = np.array(mask)

  res = np.roll(maskBuffer,  up, axis=0) # down
  res[:up,:] = 0
  maskBuffer |= res

  res = np.roll(maskBuffer, -up, axis=0) # up
  res[-up:,:] = 0
  maskBuffer |= res


  res = np.roll(maskBuffer,  left, axis=1) # right
  res[:, :left] = 0
  maskBuffer |= res

  res = np.roll(maskBuffer, -left, axis=1) # left
  res[:, -left:] = 0
  maskBuffer |= res

  return maskBuffer

# date = datetime.datetime.today() - 100
date = datetime.datetime(year=2013, month=01, day=01)
getImageData(date, 10)

# The maximum number of days used to get the cloud free images
maxDays = 10 # TODO: change to 100

# get all the data at once
photos, clouds, noDatas = getImageData(date, maxDays)

workingBuffer = np.zeros(shape=(512, 512, 3), dtype=np.uint8)

for i in xrange(maxDays):
  print i
  photo = photos[i]
  cloud = clouds[i]
  noData = noDatas[i]

  rgb = np.asarray(photo.convert('RGB'))
  a = np.asarray(cloud.convert('RGBA').split()[3]) # 0 -> transparent, 0xff -> cloud

  # TODO: once the bug in PIL is fixed, use RGBA and transparent instead of black
  # https://mail.python.org/pipermail/image-sig/2011-February/006693.html
  # noDataMask = np.asarray(noData.convert('RGBA').split()[3]) # 0 -> transparent, 0xff -> noData

  noDataMask = (np.asarray(noData.convert('RGB').split()[0]) != 0) * 0xff # 0 -> transparent, 0xff -> noData

  # Due to difference in resolution in the cloud image and the mask and photo images
  # we need to increase the size of the masks by 2 pixels in each direction
  # We do this by replicating the mask to the left and right and create a slightly
  # bigger mask

  # print a
  gapMask = growMask(noDataMask, 40, 0) ^ noDataMask  # 0xff -> gap pixels
  # print gapMask.shape
  # print type(gapMask[0,0])
  bla = gapMask.astype(np.uint8)
  xx = np.array([bla]*3).T
  print xx.shape
  print type(xx[0,0,0])
  # print "xx.tobytes"
  # print xx.tobytes
  # Image.fromarray(xx).save('gap.jpg')
  Image.fromarray(np.uint8(xx*255)).save('gap.jpg')

  workingBuffer = np.where(((a | noDataMask | gapMask) == 0)[:, :, np.newaxis], rgb, workingBuffer)
  print workingBuffer.shape
  print type(workingBuffer[0,0,0])

  # save output
  fileName = "output/output-"+dayDeltaBack(date, i) + ".jpg"
  Image.fromarray(workingBuffer).save(fileName)
