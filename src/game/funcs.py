from collections import defaultdict
import numpy as np
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon

from game.namedata import *


def flip_side(x):
  if x == "R":  return "L"
  if x == "L":  return "R"
  else:  return "N"

def dist(a, b):
  return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

def rdist(a, b):
  return sqrt((abs(a[0] - b[0])**2) + (abs(a[1] - b[1])**2))

def chkdist(a, b, n):
  return True if dist(a, b) <= n else False

def aany(l):
  for i in l:
    if i is not None:  return True
  return False

def aall(l):
  for i in l:
    if i is None:  return False
  return True

def isemptydict(d):
  return True if d == {} else False

def notnullappend(l, x):
  if x is not None:  l.append(x)

def in_frame_radius(f, x=0, n=5, ret_all=False):
  if ret_all:  return list(range(f - n, f + n + 1))
  if x:  return True if x >= f - n and x <= f + n else False

def search_ac(n, sd, ac):
  for i, j in ac.items():
    if i == n:
      if j[0][0] == sd:  return j[0]

def inv_search_ac(ov, ac):
  for i, j in ac.items():
    if ov in j:  return i

def search_role(n):
  for i, j in roles.items():
    if n in j:  return i

def get_splits(l, n=0):
  if len(l) == 0:  return l
  d = {l[0]: []}
  x = l[0]
  if n == 0:  y = 30
  if n > 0:  y = 2
  for i in range(len(l) - 1):
    if l[i+1] - l[i] > y:  x = l[i+1]; d[x] = []
    else:  d[x].append(l[i+1])
  if n == 0:  c = [k for k in list(d.keys()) if len(d[k]) >= 0]
  if n == 1:  c = [k for k in list(d.keys()) if len(d[k]) > 4 or (k in l[-5:] and len(d[k]) > 1) or k in l[-1:]]
  if n == 2:  c = [k for k in list(d.keys()) if len(d[k]) >= 0]
  return c

def chk_splits(l):
  for i in range(len(l) - 1):
    if l[i+1] - l[i] > 1:  return False
  return True

def flatten(l):
  y = []
  for i in l:
    for j in i:  y.append(j)
  return y

def get_by_index(l, n):
  return [ i for i in l if i[2] == n ]

def is_adj(s, locs):
  return True if s in locs else False

def dthtrk(rd, pa, ri, ags):
  c = []
  dead = False
  alive1 = [ ( "D", i ) for i in ags[pa]["DEATHS"][rd] ]
  alive2 = [ ( "R", i ) for i in ags[pa]["REVIVES"][rd] ]
  for i in [alive1, alive2]:
    for j in i:
      c.append(j)
  c = sorted(c, key=lambda k: k[1])
  end = c[-1][1] if len(c) > 0 else ri[rd]["KEYPOINTS"]["END"] + 1
  if len(alive1) == 0:  return list(range(ri[rd]["KEYPOINTS"]["START"], ri[rd]["KEYPOINTS"]["END"] + 1))
  alive = []
  for f in range(ri[rd]["KEYPOINTS"]["START"], end):
    if not dead:  alive.append(f)
    for cc in c:
      if f == cc[1] and cc[0] == "D":  dead = True
      if f == cc[1] and cc[0] == "R":  dead = False
  return alive

def in_loc(p, mm, s="", r=3):
  pts = []
  xr = np.arange(p[0] - r - 1, p[0] + r + 1, dtype=int)
  yr = np.arange(p[1] - r - 1, p[1] + r + 1, dtype=int)
  x1, y1 = np.where((xr[:,np.newaxis] - p[0])**2 + (yr - p[1])**2 <= r**2)
  cs = [(x, y) for x, y in zip(xr[x1], yr[y1])]
  for cc in cs:  pts.append(Point([cc[0], cc[1]]))
  x = []
  z = defaultdict(list)
  q = None
  n = []
  mins = []
  if s:  q = [s]
  else:  q = mm.all.keys()
  for c in q:
    for i in mm.all[c]:
      if i:
        x.append([i[0], i[1]])
        z[i[2]].append(i)
    # TODO check len(z) for elevation?
    if s:
      poly = Polygon(x)
      for pt in pts:
        if poly.contains(pt):  return True
      return False
    if not s:
      poly = Polygon(x)
      for pt in pts:
        if poly.contains(pt):  n.append(c)
    x = []
    z = defaultdict(list)
  ns = list(set(n))
  if len(ns) > 0:  return ns
  else:
    nsn = []
    xy = None
    sml = 10000
    for mk in mm.all.keys():
      for mi in mm.all[mk]:
          if mi:
            ddd = dist([mi[0], mi[1]], p)
            if ddd < sml:
              sml = ddd
              xy = [mk]
    return xy
  # return Delaunay(np.array(mm.all[s])).find_simplex(p) >= 0

def adjs(s, mm, rad=10):
  x = []
  z = defaultdict(list)
  for i in mm.all[s]:
    if i:
      x.append([i[0], i[1]])
      z[i[2]].append(i)
  n = [ in_loc(ii, mm, r=rad) for ii in x ]
  nn = list(set(flatten(n)))
  # nn.remove(s)
  return nn

def in_adj(p, mm, s="", r=10):
  x = []
  for l in in_loc(p, mm):  x.append(adjs(l, mm, rad=r))
  t = list(set(flatten(x)))
  if not s:  return t
  return True if s and s in t else False
