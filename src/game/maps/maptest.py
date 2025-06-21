import cv2
import numpy as np
import os
import random

from game.map import *

datadir = os.path.dirname(os.getcwd()) + "/data/"

def maptest(m, public=True, sites=False, aa=0):
  src = datadir + f"maptest_{m}.mp4" if aa == 0 else datadir + f"maptest_{m}1.mp4"
  cap = cv2.VideoCapture(src)
  mm = Map(m)
  shift_x = 0
  shift_y = 0
  if not public:  mm.applyshift()
  x = list(mm.all.values()) if not sites else list(mm.sites.values())
  x1 = []
  c = [(0,255,0), (0,0,255), (0,255,255), (255,0,255), (255,255,0), (255,0,0), (255,255,200), (200,200,255), (200,255,200), (200,255,255), (255,200,255), (255,200,200)]

  for i in x:
    c1 = c[x.index(i) % len(c)]
    tmp = [j[0:2] for j in i]
    x1.append((tmp, c1))
    tmp = []

  while cap.isOpened():
    ret, frame = cap.read()
    imgg = frame
    if ret:
      for ii in x1:
        xx = np.array(ii[0])
        imgg = cv2.polylines(imgg, np.int32([xx]), True, ii[1], 2)
      cv2.imshow('img', imgg)
      cv2.waitKey(1)
    else:  break
  cap.release()
  cv2.destroyAllWindows()

def getcoords(m, aa=0):
  def clicker(event, x, y, flags, params):
    if event == cv2.EVENT_LBUTTONDOWN:  print(x, y)
  src = datadir + f"maptest_{m}.mp4" if aa == 0 else datadir + f"maptest_{m}1.mp4"
  cap = cv2.VideoCapture(src)
  x = 0
  if x == 0:  ret, frame = cap.read(); x = 1
  imgg = frame
  cv2.imshow('img', imgg)
  cv2.setMouseCallback('img', clicker)
  cv2.waitKey(0)
  cap.release(); cv2.destroyAllWindows()



    # VISUAL AID BOUNDING BOXES FOR SCANNING
    # imgg = cv2.rectangle(imgg, (25, 25), (415, 425), (0, 255, 255), 2)
    # imgg = cv2.rectangle(imgg, (925, 140), (1080, 170), (0, 255, 255), 2)
    # imgg = cv2.rectangle(imgg, (0, 540), (50, 1030), (0, 0, 255), 2)
    # imgg = cv2.rectangle(imgg, (1870, 540), (1920, 1030), (0, 0, 255), 2)
    # imgg = cv2.rectangle(imgg, (905, 80), (1020, 140), (0, 0, 255), 2)
    # imgg = cv2.rectangle(imgg, (790, 5), (1125, 73), (0, 0, 255), 2)
    # imgg = cv2.rectangle(imgg, (790, 20), (880, 80), (0, 0, 255), 2)
    # imgg = cv2.rectangle(imgg, (880, 20), (1034, 80), (255, 0, 0), 2)
    # imgg = cv2.rectangle(imgg, (1034, 20), (1124, 80), (255, 0, 255), 2)
    # imgg = cv2.rectangle(imgg, (230, 540), (450, 1060), (0, 0, 255), 2)
    # imgg = cv2.rectangle(imgg, (1470, 540), (1690, 1060), (0, 0, 255), 2)
    # imgg = cv2.rectangle(imgg, (530, 970), (1210, 1060), (0, 255, 0), 2)
    # imgg = cv2.rectangle(imgg, (795, 20), (1125, 80), (0, 255, 0), 2)
    
    
    # imgg = cv2.rectangle(imgg, (125, 540), (455, 644), (0, 255, 0), 2)
    # imgg = cv2.rectangle(imgg, (1465, 540), (1795, 644), (0, 255, 0), 2)
    # imgg = cv2.rectangle(imgg, (125, 644), (455, 748), (0, 255, 0), 2)
    # imgg = cv2.rectangle(imgg, (1465, 644), (1795, 748), (0, 255, 0), 2)
    # imgg = cv2.rectangle(imgg, (125, 748), (455, 852), (0, 255, 0), 2)
    # imgg = cv2.rectangle(imgg, (1465, 748), (1795, 852), (0, 255, 0), 2)
    # imgg = cv2.rectangle(imgg, (125, 852), (455, 956), (0, 255, 0), 2)
    # imgg = cv2.rectangle(imgg, (1465, 852), (1795, 956), (0, 255, 0), 2)
    # imgg = cv2.rectangle(imgg, (125, 956), (455, 1060), (0, 255, 0), 2)
    # imgg = cv2.rectangle(imgg, (1465, 956), (1795, 1060), (0, 255, 0), 2)
    
    # imgg = cv2.rectangle(imgg, (0, 540), (125, 644), (0, 255, 0), 2)
    # imgg = cv2.rectangle(imgg, (1795, 540), (1920, 644), (0, 255, 0), 2)
    # imgg = cv2.rectangle(imgg, (0, 644), (125, 748), (0, 255, 0), 2)
    # imgg = cv2.rectangle(imgg, (1795, 644), (1920, 748), (0, 255, 0), 2)
    # imgg = cv2.rectangle(imgg, (0, 748), (125, 852), (0, 255, 0), 2)
    # imgg = cv2.rectangle(imgg, (1795, 748), (1920, 852), (0, 255, 0), 2)
    # imgg = cv2.rectangle(imgg, (0, 852), (125, 956), (0, 255, 0), 2)
    # imgg = cv2.rectangle(imgg, (1795, 852), (1920, 956), (0, 255, 0), 2)
    # imgg = cv2.rectangle(imgg, (0, 956), (125, 1060), (0, 255, 0), 2)
    # imgg = cv2.rectangle(imgg, (1795, 956), (1920, 1060), (0, 255, 0), 2)
    
    # draw map gridlines for agent initialization
    # imgg = cv2.rectangle(imgg, (25, 25), (25, 425), (0, 255, 255), 2)
    # imgg = cv2.rectangle(imgg, (105, 25), (105, 425), (100, 255, 0), 2)
    # imgg = cv2.rectangle(imgg, (185, 25), (185, 425), (100, 255, 0), 2)
    # imgg = cv2.rectangle(imgg, (225, 25), (225, 425), (0, 0, 255), 2)
    # imgg = cv2.rectangle(imgg, (265, 25), (265, 425), (100, 255, 0), 2)
    # imgg = cv2.rectangle(imgg, (345, 25), (345, 425), (100, 255, 0), 2)
    # imgg = cv2.rectangle(imgg, (425, 25), (425, 425), (0, 255, 255), 2)
    # imgg = cv2.rectangle(imgg, (25, 25), (425, 25), (0, 255, 255), 2)
    # imgg = cv2.rectangle(imgg, (25, 105), (425, 105), (255, 100, 0), 2)
    # imgg = cv2.rectangle(imgg, (25, 185), (425, 185), (255, 100, 0), 2)
    # imgg = cv2.rectangle(imgg, (25, 225), (425, 225), (0, 0, 255), 2)
    # imgg = cv2.rectangle(imgg, (25, 265), (425, 265), (255, 100, 0), 2)
    # imgg = cv2.rectangle(imgg, (25, 345), (425, 345), (255, 100, 0), 2)
    # imgg = cv2.rectangle(imgg, (25, 425), (425, 425), (0, 255, 255), 2)