from collections import defaultdict
import numpy as np

from game.funcs import *
from game.namedata import *


def ags_get_rd(rd, ags, pa=None):
  x = {}
  y = {}
  for i, j in ags.items():
    if pa is None:
      y[i] = ags_get_rd(rd, ags, pa=i)
    if pa == i:
      for i1, j1 in j.items():
        for i2, j2 in j1.items():
          if i2 == rd:
            x[i1] = j2
      return x
  return y

def rd_get_all(key, rd, ags, sd="N"):
  if sd == "N":  sd = "LR"
  return [ ags[kk][key][rd] for kk in ags.keys() if kk[0] in sd ]

def rd_get_sum(key, rd, ags, sd="N"):
  return sum(rd_get_all(key, rd, ags, sd=sd))

def rd_get_avg(key, rd, ags, sd="N"):
  return (rd_get_sum(key, rd, ags, sd=sd)) / 5

def ags_get_all(key, pa, ags):
  return [ i for i in ags[pa][key].values() ]

def ags_get_sum(key, pa, ags):
  x = ags_get_all(key, pa, ags)
  if len(x) == 0 or type(x[0]) == dict:  return None
  return sum(x)

def ags_get_avg(key, pa, ags):
  return (ags_get_sum(key, pa, ags)) / (max(list(ags[pa][key].keys())))

def ags_get_wps(rd, ags, pa="", sd="N"):
  c = {}
  if sd == "N":  sd = "LR"
  if pa == "":
    for kk in ags.keys():
      if kk[0] in sd:
        c[kk] = list(set([ i["STATUS"][0] for i in ags[kk]["WEAPON"][rd] if len(i["STATUS"]) > 0 ]))
  return c

def ags_classify_wps(rd, ags, start=False, end=False):
  if start == end:  start = True; end = False
  ix = 0 if start else -1
  def wps(x):
    if x in pistol_list:  return "PISTOL"
    if x in eco_list:  return "ECO"
    if x in rifle_list:  return "RIFLE"
  c = {}
  x = ags_get_wps(rd, ags)
  for kk in x.keys():
    c[kk] = wps(x[kk][ix])
  return c

def ags_measure_dmg(rd, ags, end):
  c = {}
  for kk in ags.keys():
    dt = []
    for hh in range(len(ags[kk]["HEALTH"][rd]) - 1):
      if ags[kk]["HEALTH"][rd][hh+1]["FRAME"] <= end:
        diff = ags[kk]["HEALTH"][rd][hh+1]["HEALTH"] - ags[kk]["HEALTH"][rd][hh]["HEALTH"]
        if diff != 0:  dt.append({ "HEALTH": diff, "FRAME": ags[kk]["HEALTH"][rd][hh+1]["FRAME"] })
    c[kk] = dt
  return c

def ags_measure_total_dmg(rd, ags, end):
  c = {}
  dmg = ags_measure_dmg(rd, ags, end)
  for kk in dmg.keys():
    dt, rg = (0, 0)
    for di in dmg[kk]:
      t = di["HEALTH"]
      if t < 0:  dt += (t * -1)
      if t > 0:  rg += t
    c[kk] = { "TAKEN": dt, "REGAINED": rg }
  return c

def intype(p, m):
  x = in_loc(p, m)
  print(x)

def has_spike(f, ags):
  pass

def get_agent(pa, ags):
  return (ags[pa]["AGENT"][1], pa[0])

def get_loc(f, ags):
  pass

def get_locs(rd, ags):
  pass

def get_first_loc(rd, ags):
  pass

def get_last_loc(rd, ags):
  pass

def get_util_status(f, rd, pa, ri, ags, first=None, last=None):
  lst = { "STATUS": {"UTIL1": 0, "UTIL2": 0, "ABIL": 0, "ULT": (0, 10)}, "FRAME": -1 }
  alv = dthtrk(rd, pa, ri, ags)
  end = ri[rd]["KEYPOINTS"]["END"]
  for i in ags[pa]["UTIL"][rd]:
    if i is not None and i.get("FRAME") == f and f in alv and i.get("FRAME") <= end:  return i
    if i is not None and first and not isemptydict(i["STATUS"])and i.get("FRAME") in alv and i.get("FRAME") <= end:  return i
    if i is not None and last and not isemptydict(i["STATUS"]) and i.get("FRAME") in alv and i.get("FRAME") <= end:  lst = i
  return lst

def get_all_util_status(rd, ags):
  pass

def get_first_util_status(rd, ags):
  pass

def get_last_util_status(rd, ags):
  pass

def get_events(rd, ags):
  pass

def get_spike_events(rd, ags):
  pass

def get_kd_events(rd, ags):
  pass

def get_util_events(rd, ags):
  pass

