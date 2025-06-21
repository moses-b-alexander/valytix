
from game.maps.haven import *

from game.maps.icebox import *

MM_XL = 25
MM_YT = 25
MM_XR = 425
MM_YB = 425
MM_XH = int((MM_XL + MM_XR) / 2)
MM_YH = int((MM_YT + MM_YB) / 2)
MM_XD = MM_XR - MM_XL
MM_YD = MM_YB - MM_YT

def lat(n):
  if n < 0 or n > 1:  return 0
  return int(MM_XL + n*MM_XD)

def lng(n):
  if n < 0 or n > 1:  return 0
  return int(MM_YT + n*MM_YD)

ASCENT_PRIV_SHIFT_X = 0
ASCENT_PRIV_SHIFT_Y = 0

SPLIT_PRIV_SHIFT_X = 0
SPLIT_PRIV_SHIFT_Y = 0

HAVEN_PRIV_SHIFT_X = -21
HAVEN_PRIV_SHIFT_Y = -2

BIND_PRIV_SHIFT_X = 0
BIND_PRIV_SHIFT_Y = 0

ICEBOX_PRIV_SHIFT_X = -19
ICEBOX_PRIV_SHIFT_Y = -2

BREEZE_PRIV_SHIFT_X = 0
BREEZE_PRIV_SHIFT_Y = 0

class Map:
  def __init__(self, name):
    self.sites = None
    self.def_spawns = None
    self.atk_spawns = None
    self.a = None
    self.b = None
    self.c = None
    self.d = None
    self.m = None
    self.all = None
    self.atk_locs = None
    self.def_locs = None
    self.n_locs = []
    self.priv_xshift = 0
    self.priv_yshift = 0
    if name == "":
      self.sites = {}
      self.def_spawns = {}
      self.atk_spawns = {}
      self.a = {}
      self.b = {}
      self.m = {}
      self.all = {}
      self.atk_locs = []
      self.def_locs = []
      self.n_locs = []
      self.priv_xshift = 0
      self.priv_yshift = 0
    elif name == "ASCENT":
      self.sites = ASCENT_SITES
      self.def_spawns = ASCENT_DEF_SPAWNS
      self.atk_spawns = ASCENT_ATK_SPAWNS
      self.a = ASCENT_A
      self.b = ASCENT_B
      self.m = ASCENT_M
      self.all = ASCENT
      self.atk_locs = ASCENT_ATK_LOCS
      self.def_locs = ASCENT_DEF_LOCS
      self.n_locs = [i for i in self.all if i not in self.atk_locs and i not in self.def_locs and i not in self.sites]
      self.priv_xshift = ASCENT_PRIV_SHIFT_X
      self.priv_yshift = ASCENT_PRIV_SHIFT_Y
    elif name == "SPLIT":
      pass
    elif name == "HAVEN":
      self.sites = HAVEN_SITES
      self.def_spawns = HAVEN_DEF_SPAWNS
      self.atk_spawns = HAVEN_ATK_SPAWNS
      self.a = HAVEN_A
      self.b = HAVEN_B
      self.c = HAVEN_C
      self.all = HAVEN
      self.atk_locs = HAVEN_ATK_LOCS
      self.def_locs = HAVEN_DEF_LOCS
      self.n_locs = [i for i in self.all if i not in self.atk_locs and i not in self.def_locs and i not in self.sites]
      self.priv_xshift = HAVEN_PRIV_SHIFT_X
      self.priv_yshift = HAVEN_PRIV_SHIFT_Y
    elif name == "BIND":
      pass
    elif name == "ICEBOX":
      self.sites = ICEBOX_SITES
      self.def_spawns = ICEBOX_DEF_SPAWNS
      self.atk_spawns = ICEBOX_ATK_SPAWNS
      self.a = ICEBOX_A
      self.b = ICEBOX_B
      self.m = ICEBOX_M
      self.all = ICEBOX
      self.atk_locs = ICEBOX_ATK_LOCS
      self.def_locs = ICEBOX_DEF_LOCS
      self.n_locs = [i for i in self.all if i not in self.atk_locs and i not in self.def_locs and i not in self.sites]
      self.priv_xshift = ICEBOX_PRIV_SHIFT_X
      self.priv_yshift = ICEBOX_PRIV_SHIFT_Y
    elif name == "BREEZE":
      pass
    elif name == "FRACTURE":
      pass
    else:
      self.sites = {}
      self.def_spawns = {}
      self.atk_spawns = {}
      self.a = {}
      self.b = {}
      self.m = {}
      self.all = {}
      self.atk_locs = []
      self.def_locs = []
      self.n_locs = []
      self.priv_xshift = 0
      self.priv_yshift = 0

  def applyshift(self, x=0, y=0):
    if x == 0 and y == 0:  x = self.priv_xshift; y = self.priv_yshift
    def f(w, xx, yy):
      for i in w:
        if len(i) > 0:  i[0] += xx; i[1] += yy
      return w
    for i in [self.sites, self.def_spawns, self.atk_spawns, self.a, self.b, self.c, self.d, self.m]:
      if i:
        for j in i.items():  i[j[0]] = f(j[1], x, y)
    if self.c and not self.d and not self.m:  self.all = {**self.sites, **self.def_spawns, **self.atk_spawns, **self.a, **self.b, **self.c}
    if self.m and not self.c and not self.d:  self.all = {**self.sites, **self.def_spawns, **self.atk_spawns, **self.a, **self.b, **self.m}
    # if self.c and self.d and self.m:
    #   self.all = {**self.sites, **self.def_spawns, **self.atk_spawns, **self.a, **self.b, **self.c, **self.d, **self.m}
    # if self.c and not self.d and self.m:
    #   self.all = {**self.sites, **self.def_spawns, **self.atk_spawns, **self.a, **self.b, **self.c, **self.m}
