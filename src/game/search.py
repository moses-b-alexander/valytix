from collections import defaultdict
from decimal import Decimal
from math import ceil, floor, sqrt

from game.funcs import *
from game.getdata import *
from game.map import *
from game.namedata import *
from game.minimap import FPAC, PPM_PUB, PPM_PRIV


mindist = 5

def search(hits, key, ret_loc=False, verif=0):
  c = 0
  q = []
  ret = []
  rett = []
  if hits:
    for j in hits:
      if j is not None and len(j) > 0:
        t = j['TemplateName'].str.fullmatch(key)
        if t.any() and len(t) > 0:
          c += 1
          # print(t)
          for n in range(len(t)):
            if t.iloc[n]:  q.append(n)
          if c > verif and ret_loc:
            for jj in q:  rett.append([j.iloc[jj]['BBox'][0], j.iloc[jj]['BBox'][1], j.iloc[jj]['Score']])
            if len(rett) > 0:
              rettt = sorted(rett, key=lambda k: [k[2], k[0], k[1]])
              kk = []
              for iii in rettt:
                for jjj in range(len(rett)):
                  if iii[0] == rett[jjj][0] and iii[1] == rett[jjj][1]:  kk.append([rett[jjj][0], rett[jjj][1]])
              ret = list(reversed(kk))
              # print(ret)
              return ret
            if len(rett) == 0:  return [[-1, -1]]
          if c > verif and not ret_loc:  return True
  if ret_loc:  return [[-1, -1]]
  return False

def filter_frames(fltr, ags):
  pass

def get_side(x): # subset of x -> x[s:e]
  l = 0
  r = 0
  for i in x:
    if search(i, "SIDE_LEFT"):  l += 1
    if search(i, "SIDE_RIGHT"):  r += 1
  if l > r:  return "L"
  if r > l:  return "R"
  return "N"

def get_loc_at(ri, ags, f, pa="", last=False):
  llast = []
  if pa:
    for i in list(ags[pa]["POSITION"].values()):
      ix = (list(ags[pa]["POSITION"].values())).index(i)
      for j in i:
        if j["FRAME"] == f:  return j["LOC"]
        if last and j["FRAME"] <= ri[ix+1]["KEYPOINTS"]["END"]:  llast = j["LOC"]
    return [] if not last else llast
  else:  return [ { "PLAYER": kk, "LOC": get_loc_at(ri, ags, f, kk) } for kk in ags.keys() ]

def search_abils(t, s, jj):
  x0 = None
  x1 = None
  x2 = None
  x3 = None
  u = {}
  v1 = []
  w = []
  xx = [None, None, None, None]
  astra = False
  aa = -1
  uf = False
  bnd = [[-1, -1]]
  emptystatus = {"STATUS": {}, "FRAME": jj}
  for ii in range(1, 6):
    if search(t, f"ASTRA_ABIL_{ii}_{s}"):  aa = ii; aa = ii; aa = ii; astra = True
  if search(t, f"ASTRA_ABIL_VERIF_{s}") and not aany(xx):  aa = 0; aa = 0; aa = 0; astra = True

  if astra:  xx[0] = 5 - aa; xx[1] = 5 - aa; xx[2] = 5 - aa
  #   astarsg = []
  #   astarsr = []
  #   for astar in search(t, "ASTRA_STAR_GREEN", ret_loc=True):
  #     if astar[0] > 0 and astar[1] > 0:  astarsg.append(astar)
  #   for astar in search(t, "ASTRA_STAR_RED", ret_loc=True):
  #     if astar[0] > 0 and astar[1] > 0:  astarsr.append(astar)
  #   print(astarsg, astarsr)

  if not astra:
    if search(t, f"ABIL_0_{s}"):  x0 = search(t, f"ABIL_0_{s}", ret_loc=True)
    if search(t, f"ABIL_1_{s}"):  x1 = search(t, f"ABIL_1_{s}", ret_loc=True)
    if search(t, f"ABIL_2_{s}"):  x2 = search(t, f"ABIL_2_{s}", ret_loc=True)
    if search(t, f"ABIL_3_{s}"):  x3 = search(t, f"ABIL_3_{s}", ret_loc=True)
    if search(t, f"ABIL_0_1_{s}"):  x0 = search(t, f"ABIL_0_1_{s}", ret_loc=True)
    if search(t, f"ABIL_0_2_{s}"):  x0 = search(t, f"ABIL_0_2_{s}", ret_loc=True)
    if search(t, f"ABIL_0_3_{s}"):  x0 = search(t, f"ABIL_0_3_{s}", ret_loc=True)
    if search(t, f"ABIL_1_1_{s}"):  x1 = search(t, f"ABIL_1_1_{s}", ret_loc=True)
    if search(t, f"ABIL_1_2_{s}"):  x1 = search(t, f"ABIL_1_2_{s}", ret_loc=True)
    if search(t, f"ABIL_1_3_{s}"):  x1 = search(t, f"ABIL_1_3_{s}", ret_loc=True)
    if search(t, f"ABIL_2_2_{s}"):  x2 = search(t, f"ABIL_2_2_{s}", ret_loc=True)
    if search(t, f"ABIL_2_3_{s}"):  x2 = search(t, f"ABIL_2_3_{s}", ret_loc=True)
    if search(t, f"ABIL_3_3_{s}"):  x3 = search(t, f"ABIL_3_3_{s}", ret_loc=True)

    for i in weapon_list:
      if search(t, f"{i}_{s}"):  bnd = search(t, f"{i}_{s}", ret_loc=True)
    cc = [x0, x1, x2, x3]
    for i in cc:
      if i:
        for j in i:
          if j:
            v1.append(j)
            w.append(cc.index(i))
    xxs = [xx1[0] for xx1 in v1]
    if bnd[0][0] != -1 and len(xxs) > 0:
      if s[0] == "L":  vvv = [bb for bb in v1 if bb[0] < bnd[0][0] and bb[0] > sum(xxs)/len(xxs) - 5]
      if s[0] == "R":  vvv = [bb for bb in v1 if bb[0] > bnd[0][0] and bb[0] < sum(xxs)/len(xxs) + 20]
    else:  return emptystatus

    vv = sorted(vvv, key=lambda k: [k[1], k[0]])
    ww = list(map(lambda s,f: (s, f), v1, w))
    for i in range(len(ww)):
      for j in range(len(vv)):
        if ww[i][0][0] == vv[j][0] and ww[i][0][1] == vv[j][1]:  xx[j] = ww[i][1]
  for p2 in range(6, 9):
    for p1 in range(8):
      if search(t, f"ULT_GREEN_{p1}_{p2}_{s}"):  xx[3] = (p1, p2); uf = True
      if search(t, f"ULT_RED_{p1}_{p2}_{s}"):  xx[3] = (p1, p2); uf = True
  if not uf:
    for aa in agent_list:
      if search(t, f"{aa}_ULT_GREEN_{s}") or search(t, f"{aa}_ULT_RED_{s}"):  xx[3] = (10, 10)
  u = { "UTIL1": xx[0], "UTIL2": xx[1], "ABIL": xx[2], "ULT": xx[3] }
  if not astra and aany(xx):  return { "STATUS": u, "FRAME": jj }
  if astra and aall(xx[:3]):  return { "STATUS": u, "FRAME": jj }
  if astra and not aall(xx[:3]):  return emptystatus
  if not astra and not aany(xx):  return emptystatus

def search_wps(t, s, jj):
  xx = []
  for i in weapon_list:
    if search(t, f"{i}_{s}"):  xx.append(i)
  return {"STATUS": xx, "FRAME": jj}

def search_spike_held(t, s, jj):
  if search(t, f"SPIKE_HELD_{s}"):  return jj

def search_feed(t, sd, ac, jj): # handle phoenix and kayo ult cases
  k = []
  d = []
  a = []
  w = []
  mk = []
  f = []

  if sd == "L":
    for aa in agent_list:
      if search(t, f"{aa}_FEED_LEFT_GREEN"):  k.append((aa, "R", search(t, f"{aa}_FEED_LEFT_GREEN", ret_loc=True)))
      if search(t, f"{aa}_FEED_LEFT_RED"):  k.append((aa, "L", search(t, f"{aa}_FEED_LEFT_RED", ret_loc=True)))
      if search(t, f"{aa}_FEED_RIGHT_GREEN"):  d.append((aa, "R", search(t, f"{aa}_FEED_RIGHT_GREEN", ret_loc=True)))
      if search(t, f"{aa}_FEED_RIGHT_RED"):  d.append((aa, "L", search(t, f"{aa}_FEED_RIGHT_RED", ret_loc=True)))
      if search(t, f"{aa}_FEED_ASSIST"):  a.append((aa, search(t, f"{aa}_FEED_ASSIST", ret_loc=True)))
    for wp in feed_list:
      if search(t, f"{wp}_FEED_GREEN"):  w.append((wp, "R", search(t, f"HEADSHOT_FEED_GREEN", ret_loc=True), search(t, f"WALLBANG_FEED_GREEN", ret_loc=True), search(t, f"NULLCMD_FEED_GREEN", ret_loc=True), search(t, f"RUN_IT_BACK_FEED_GREEN", ret_loc=True), search(t, f"RESURRECTION_FEED_GREEN", ret_loc=True), search(t, f"{wp}_FEED_GREEN", ret_loc=True)))
      if search(t, f"{wp}_FEED_RED"):  w.append((wp, "L", search(t, f"HEADSHOT_FEED_RED", ret_loc=True), search(t, f"WALLBANG_FEED_RED", ret_loc=True), search(t, f"NULLCMD_FEED_RED", ret_loc=True), search(t, f"RUN_IT_BACK_FEED_RED", ret_loc=True), search(t, f"RESURRECTION_FEED_RED", ret_loc=True), search(t, f"{wp}_FEED_RED", ret_loc=True)))

  if sd == "R":
    for aa in agent_list:
      if search(t, f"{aa}_FEED_LEFT_GREEN"):  k.append((aa, "L", search(t, f"{aa}_FEED_LEFT_GREEN", ret_loc=True)))
      if search(t, f"{aa}_FEED_LEFT_RED"):  k.append((aa, "R", search(t, f"{aa}_FEED_LEFT_RED", ret_loc=True)))
      if search(t, f"{aa}_FEED_RIGHT_GREEN"):  d.append((aa, "L", search(t, f"{aa}_FEED_RIGHT_GREEN", ret_loc=True)))
      if search(t, f"{aa}_FEED_RIGHT_RED"):  d.append((aa, "R", search(t, f"{aa}_FEED_RIGHT_RED", ret_loc=True)))
      if search(t, f"{aa}_FEED_ASSIST"):  a.append((aa, search(t, f"{aa}_FEED_ASSIST", ret_loc=True)))
    for wp in feed_list:
      if search(t, f"{wp}_FEED_GREEN"):  w.append((wp, "L", search(t, f"HEADSHOT_FEED_GREEN", ret_loc=True), search(t, f"WALLBANG_FEED_GREEN", ret_loc=True), search(t, f"NULLCMD_FEED_GREEN", ret_loc=True), search(t, f"RUN_IT_BACK_FEED_GREEN", ret_loc=True), search(t, f"RESURRECTION_FEED_GREEN", ret_loc=True), search(t, f"{wp}_FEED_GREEN", ret_loc=True)))
      if search(t, f"{wp}_FEED_RED"):  w.append((wp, "R", search(t, f"HEADSHOT_FEED_RED", ret_loc=True), search(t, f"WALLBANG_FEED_RED", ret_loc=True), search(t, f"NULLCMD_FEED_RED", ret_loc=True), search(t, f"RUN_IT_BACK_FEED_RED", ret_loc=True), search(t, f"RESURRECTION_FEED_RED", ret_loc=True), search(t, f"{wp}_FEED_RED", ret_loc=True)))

  k1 = []
  d1 = []
  mkk = []
  www = []
  aaa = []
  for kx in k:
    for ki in range(len(kx[2])):
      k1.append((kx[0], kx[1], kx[2][ki]))
  for dx in d:
    for di in range(len(dx[2])):
      d1.append((dx[0], dx[1], dx[2][di]))
  for wx in w:
    for wi in range(len(wx[7])):
      www.append((wx[0], wx[1], wx[2], wx[3], wx[4], wx[5], wx[6], wx[7][wi]))
  for ax in a:
    for ai in range(len(ax[1])):
      aaa.append((ax[0], ax[1][ai]))
  for mmm in mk:
    for mi in range(len(mmm[2])):
      mkk.append((mmm[0], mmm[1], mmm[2][mi]))
  k1 = sorted(k1, key=lambda kk: kk[2][1])
  d1 = sorted(d1, key=lambda kk: kk[2][1])
  www = sorted(www, key=lambda kk: kk[-1][1])
  aaa = sorted(aaa, key=lambda kk: kk[1][1])

  if len(k1) > 0 and len(k1) == len(d1): # len(k1) == len(www)
    for i in range(len(k1)):
      tmp = {"K": None, "D": None, "W": www[i][0], "A": [], "HS": False, "WB": False, "ABILITY": False, "SPIKE_DET": False}
      for w1 in www:
        for whs in w1[2]:
          if whs[1] > 0 and whs[1] > k1[i][2][1] and whs[1] < k1[i][2][1] + 20:  tmp["HS"] = True
        for wwb in w1[3]:
          if wwb[1] > 0 and wwb[1] > k1[i][2][1] and wwb[1] < k1[i][2][1] + 20:  tmp["WB"] = True
        # for wku in w1[4]: # TODO fix kayo ult recognition
        #   if wku[1] > 0 and wku[1] > k1[i][2][1] and wku[1] < k1[i][2][1] + 20 and www[i][0] != "NULLCMD":  tmp["KAYO_ULT_DOWN"] = True
        #   elif wku[1] > 0 and wku[1] > k1[i][2][1] and wku[1] < k1[i][2][1] + 20 and www[i][0] == "NULLCMD":  tmp["KAYO_ULT_RES"] = True
        for wpu in w1[5]:
          if wpu[1] > 0 and wpu[1] > k1[i][2][1] and wpu[1] < k1[i][2][1] + 20 and www[i][0] == "RUN_IT_BACK":  tmp["PHOENIX_ULT"] = True
        for wsu in w1[6]:
          if wsu[1] > 0 and wsu[1] > k1[i][2][1] and wsu[1] < k1[i][2][1] + 20 and www[i][0] == "RESURRECTION":  tmp["SAGE_ULT"] = True

      if www[i][0] in abil_list and not (tmp.get("KAYO_ULT_DOWN") or tmp.get("KAYO_ULT_RES") or tmp.get("PHOENIX_ULT") or tmp.get("SAGE_ULT")):
        tmp["ABILITY"] = True
      if www[i][0] == "SPIKE_DET":  tmp["SPIKE_DET"] = True
      for a1 in aaa:
        if i == 0 and a1[1][1] <= k1[i][2][1]:  tmp["A"].append(search_ac(a1[0], flip_side(d1[i][1]), ac))
        if i > 0 and a1[1][1] <= k1[i][2][1] and a1[1][1] > k1[i-1][2][1]:  tmp["A"].append(search_ac(a1[0], flip_side(d1[i][1]), ac))

      ksd = search_ac(k1[i][0], k1[i][1], ac)
      dsd = search_ac(d1[i][0], d1[i][1], ac)
      tmp["K"] = ksd; tmp["D"] = dsd
      if tmp["K"] and tmp["D"]:  f.append(tmp)
  return (f, jj)

def search_health(t, sd, s, jj):
  x = []
  y = []
  shield = -1
  for ii in range(10):
    if s[0] != sd and search(t, f"GREEN_{ii}_{s}"):  x.append((ii, search(t, f"GREEN_{ii}_{s}", ret_loc=True)))
    if s[0] == sd and search(t, f"RED_{ii}_{s}"):  x.append((ii, search(t, f"RED_{ii}_{s}", ret_loc=True)))
  for ii in [25, 50]:
    if s[0] != sd and search(t, f"GREEN_{ii}_{s}"):  shield = ii
    if s[0] == sd and search(t, f"RED_{ii}_{s}"):  shield = ii
  if shield < 0:  shield = 0
  for i in x:
    for j in i[1]:
      y.append((i[0], j))
  y = sorted(y, key=lambda k: k[1][0])
  hh = [d[0] for d in y]
  health = int(''.join(map(str, hh))) if len(hh) > 0 and len(hh) < 4 else 15
  return { "HEALTH": health, "SHIELD": shield, "FRAME": jj }

def collect_kdetc(feed, ri, ags):
  tt = []
  xx = []
  for i in range(max(list(ri.keys()))):
    opener = -1
    ct = 0
    if "PLANTED" in ri[i+1]["KEYPOINTS"]:  ri[i+1]["PLANTED"] = ri[i+1]["KEYPOINTS"]["PLANTED"]
    for kk in ags.keys():
      for kk1 in ags[kk].keys():
        if not ags[kk][kk1].get(i + 1):  ags[kk][kk1][i+1] = []

    for fd in feed[i+1]:
      # print(fd)
      if not fd["FEED_EVENT"].get("KAYO_ULT_DOWN") and not fd["FEED_EVENT"].get("KAYO_ULT_RES") and not fd["FEED_EVENT"].get("PHOENIX_ULT") and not fd["FEED_EVENT"].get("SAGE_ULT"):
        ct += 1
        ags[fd["FEED_EVENT"]["K"]]["KILLS"][i+1].append(fd["FRAME"])
        ags[fd["FEED_EVENT"]["D"]]["DEATHS"][i+1].append(fd["FRAME"])
        if ct == 1:
          ags[fd["FEED_EVENT"]["K"]]["OPENING_KILLS"][i+1].append(fd["FRAME"])
          ags[fd["FEED_EVENT"]["D"]]["OPENING_DEATHS"][i+1].append(fd["FRAME"])
          opener = fd["FRAME"]
        if fd["FEED_EVENT"]["HS"]:  ags[fd["FEED_EVENT"]["K"]]["HEADSHOTS"][i+1].append(fd["FRAME"])
        if fd["FEED_EVENT"]["WB"]:  ags[fd["FEED_EVENT"]["K"]]["WALLBANGS"][i+1].append(fd["FRAME"])
        if fd["FEED_EVENT"]["ABILITY"]:  ags[fd["FEED_EVENT"]["K"]]["UTIL_KILLS"][i+1].append(fd["FRAME"])
        if fd["FEED_EVENT"]["SPIKE_DET"]:  ags[fd["FEED_EVENT"]["D"]]["SPIKE_DEATHS"][i+1].append(fd["FRAME"])
        for assist in fd["FEED_EVENT"]["A"]:
          if assist and ags.get(assist):  ags[assist]["ASSISTS"][i+1].append(fd["FRAME"])
      if fd["FEED_EVENT"].get("KAYO_ULT_RES") or fd["FEED_EVENT"].get("SAGE_ULT"):
        ags[fd["FEED_EVENT"]["K"]]["REVIVES"][i+1].append(fd["FRAME"])
      if fd["FEED_EVENT"].get("PHOENIX_ULT"):
        ags[fd["FEED_EVENT"]["D"]]["REVIVES"][i+1].append(fd["FRAME"])

    hundred = {}
    for kk in ags.keys():
      if len(ags[kk]["KILLS"][i+1]) == 0:  ags[kk]["IDLES"][i+1].append(ri[i+1]["KEYPOINTS"]["END"])
      if len(ags[kk]["DEATHS"][i+1]) == 0:  ags[kk]["SURVIVES"][i+1].append(ri[i+1]["KEYPOINTS"]["END"])
      for kil in ags[kk]["KILLS"][i+1]:  tt.append((kk, "K", kil))
      for dth in ags[kk]["DEATHS"][i+1]:  tt.append((kk, "D", dth))
      for rev in ags[kk]["REVIVES"][i+1]:  tt.append((kk, "R", rev))

      alv = dthtrk(i + 1, kk, ri, ags)
      hundred[kk] = -1
      for hfrm in ags[kk]["HEALTH"][i+1]:
        if hundred[kk] == -1 and hfrm["HEALTH"] == 100 and hfrm["FRAME"] in alv:  hundred[kk] = hfrm["FRAME"]
        if ((0 <= hundred[kk] and hundred[kk] <= hfrm["FRAME"]) or (hundred[kk] == -1)) and (hfrm["FRAME"] in alv):  hfrm["HEALTH"] = 100
        if hfrm["FRAME"] not in alv:  hfrm["HEALTH"] = 0

    tt = sorted(tt, key=lambda k: k[2])
    for tt1 in range(len(tt)):
      for tt2 in range(len(tt)):
        if tt[tt1][2] == tt[tt2][2] and tt[tt1][1] == "K" and tt[tt2][1] == "D" and tt[tt1][0][0] != tt[tt2][0][0] and (tt[tt1][0], tt[tt2][0], tt[tt1][2]) not in xx:
          xx.append((tt[tt1][0], tt[tt2][0], tt[tt1][2]))
    xx = sorted(xx, key=lambda k: k[2])
    for xi in range(len(xx) - 1):
      if xx[xi][0] == xx[xi+1][1] and in_frame_radius(xx[xi][2], x=xx[xi+1][2], n=3*FPAC):
        ags[xx[xi][1]]["TRADES"][i+1].append(xx[xi][2])
        if opener == xx[xi][2]:  ags[xx[xi][1]]["OPENING_TRADES"][i+1].append(fd["FRAME"])
    tt = []
    xx = []

def populate(a, ac, ll, mm, ri, ags, hh=False):
  hh = False
  x = None; y = None; z = None
  if len(ac[a]) == 1:  z = ac[a][0]
  if len(ac[a]) == 2:  x = ac[a][0]; y = ac[a][1]

  l = []
  tt = []
  for i in range(len(ri)):
    for j in get_by_index(ll, i + 1):
      for k in j[0]:  tt.append((k, j[1], j[2]))
    l.append(tt)
    tt = []

  t = []
  u = []
  v = []
  w = []
  err = 0

  for i in range(len(ri)):
    for j in range(len(l[i])):

      if len(ac[a]) == 1:
        alv3 = dthtrk(i+1, ac[a][0], ri, ags)
        cur_coord = l[i][j][0]
        cur_frm = l[i][j][1]
        cur_loc = in_loc(cur_coord, mm)
        fdiff = -1
        if len(t) > 0:  fdiff = cur_frm - t[-1]["FRAME"]
        if hh:  pass
        elif len(t) == 0 and z[0] != ri[i+1]["ATK_SIDE"] and cur_frm in alv3:
          t.append({ "LOC": cur_loc, "COORD": cur_coord, "FRAME": cur_frm })
        elif len(t) == 0 and z[0] == ri[i+1]["ATK_SIDE"] and cur_frm in alv3:
          t.append({ "LOC": cur_loc, "COORD": cur_coord, "FRAME": cur_frm })
        elif len(t) > 0 and cur_frm in alv3 and fdiff > 0 and dist(t[-1]["COORD"], cur_coord) < mindist * abs(cur_frm - t[-1]["FRAME"]):
          t.append({ "LOC": cur_loc, "COORD": cur_coord, "FRAME": cur_frm })
        # else:  print("problem1", t[-1], cur_loc, cur_coord, cur_frm, ac[a][0], i+1, "\n"); err += 1

      if len(ac[a]) == 2:
        alv1 = dthtrk(i+1, ac[a][0], ri, ags)
        alv2 = dthtrk(i+1, ac[a][1], ri, ags)
        cur_coord = l[i][j][0]
        cur_frm = l[i][j][1]
        cur_loc = in_loc(cur_coord, mm)
        fdiff1 = -1
        fdiff2 = -1
        if len(u) > 0:  fdiff1 = cur_frm - u[-1]["FRAME"]
        if len(v) > 0:  fdiff2 = cur_frm - v[-1]["FRAME"]
        if hh:  pass
        elif len(u) == 0 and x[0] != ri[i+1]["ATK_SIDE"] and cur_frm in alv1 and cur_coord[1] < MM_YH:
          u.append({ "LOC": cur_loc, "COORD": cur_coord, "FRAME": cur_frm })
        elif len(v) == 0 and y[0] != ri[i+1]["ATK_SIDE"] and cur_frm in alv2 and cur_coord[1] < MM_YH:
          v.append({ "LOC": cur_loc, "COORD": cur_coord, "FRAME": cur_frm })
        elif len(u) == 0 and x[0] == ri[i+1]["ATK_SIDE"] and cur_frm in alv1 and cur_coord[1] > MM_YH:
          u.append({ "LOC": cur_loc, "COORD": cur_coord, "FRAME": cur_frm })
        elif len(v) == 0 and y[0] == ri[i+1]["ATK_SIDE"] and cur_frm in alv2 and cur_coord[1] > MM_YH:
          v.append({ "LOC": cur_loc, "COORD": cur_coord, "FRAME": cur_frm })
        elif len(u) > 0 and cur_frm in alv1 and fdiff1 > 0 and dist(u[-1]["COORD"], cur_coord) < mindist * abs(cur_frm - u[-1]["FRAME"]):
          u.append({ "LOC": cur_loc, "COORD": cur_coord, "FRAME": cur_frm })
        elif len(v) > 0 and cur_frm in alv2 and fdiff2 > 0 and dist(v[-1]["COORD"], cur_coord) < mindist * abs(cur_frm - v[-1]["FRAME"]):
          v.append({ "LOC": cur_loc, "COORD": cur_coord, "FRAME": cur_frm })
        elif len(u) > 0 and len(v) > 0: # handle sage ult case, yoru tp case, phoenix ult case, omen tp case, etc
          if hh:  pass
          elif fdiff1 == 0 and fdiff2 == 0:  w.append({ "LOC": cur_loc, "COORD": cur_coord, "FRAME": cur_frm })
          elif cur_frm not in alv1 and cur_frm not in alv2:  w.append({ "LOC": cur_loc, "COORD": cur_coord, "FRAME": cur_frm })
          elif fdiff1 == 0:  v.append({ "LOC": cur_loc, "COORD": cur_coord, "FRAME": cur_frm })
          elif fdiff2 == 0:  u.append({ "LOC": cur_loc, "COORD": cur_coord, "FRAME": cur_frm })
          elif cur_frm not in alv1:  v.append({ "LOC": cur_loc, "COORD": cur_coord, "FRAME": cur_frm })
          elif cur_frm not in alv2:  u.append({ "LOC": cur_loc, "COORD": cur_coord, "FRAME": cur_frm })
          else:
            du = abs(dist(u[-1]["COORD"], cur_coord) - (mindist * abs(cur_frm - u[-1]["FRAME"])))
            dv = abs(dist(v[-1]["COORD"], cur_coord) - (mindist * abs(cur_frm - v[-1]["FRAME"])))
            if hh:  pass
            elif du < dv:  u.append({ "LOC": cur_loc, "COORD": cur_coord, "FRAME": cur_frm })
            elif dv < du:  v.append({ "LOC": cur_loc, "COORD": cur_coord, "FRAME": cur_frm })
            # else: print("problem2", u[-1], v[-1], cur_loc, cur_coord, cur_frm, ac[a][0], ac[a][1], i+1, "\n"); err += 1

    if t == []:  t.append({ "LOC": "NONE", "COORD": [-1, -1], "FRAME": ri[i+1]["KEYPOINTS"]["START"] })
    if u == []:  u.append({ "LOC": "NONE", "COORD": [-1, -1], "FRAME": ri[i+1]["KEYPOINTS"]["START"] })
    if v == []:  v.append({ "LOC": "NONE", "COORD": [-1, -1], "FRAME": ri[i+1]["KEYPOINTS"]["START"] })

    if len(ac[a]) == 1:  ags[ac[a][0]]["POSITION"][i+1] = t
    if len(ac[a]) == 2:
      if ri[i+1]["ATK_SIDE"] == x[0]:
        ags[ac[a][0]]["POSITION"][i+1] = u
        ags[ac[a][1]]["POSITION"][i+1] = v
      if ri[i+1]["ATK_SIDE"] == y[0]:
        ags[ac[a][1]]["POSITION"][i+1] = u
        ags[ac[a][0]]["POSITION"][i+1] = v
    t = []
    u = []
    v = []
    w = []
  # print(ags, err)

def fillin(pa, ri, ags, mm):
  agss = {}
  for i in range(max(list(ri.keys()))):
    alv = dthtrk(i + 1, pa, ri, ags)
    fill = [ { "LOC": "", "COORD": ags[pa]["POSITION"][i+1][0]["COORD"], "FRAME": jff } for jff in range(ri[i+1]["KEYPOINTS"]["START"], ags[pa]["POSITION"][i+1][0]["FRAME"]) ]
    for j in range(len(ags[pa]["POSITION"][i+1]) - 1):
      l0 = ags[pa]["POSITION"][i+1][j]["LOC"]
      l1 = ags[pa]["POSITION"][i+1][j+1]["LOC"]
      x0 = ags[pa]["POSITION"][i+1][j]["COORD"][0]
      x1 = ags[pa]["POSITION"][i+1][j+1]["COORD"][0]
      y0 = ags[pa]["POSITION"][i+1][j]["COORD"][1]
      y1 = ags[pa]["POSITION"][i+1][j+1]["COORD"][1]
      f0 = ags[pa]["POSITION"][i+1][j]["FRAME"]
      f1 = ags[pa]["POSITION"][i+1][j+1]["FRAME"]
      x = (x1 - x0) / (f1 - f0)
      y = (y1 - y0) / (f1 - f0)
      c = 0

      for ff in range(f0, f1):
        if ff in alv:
          tmp = [int(x0 + c * x), int(y0 + c * y)]
          cur_loc = in_loc(tmp, mm)
          fill.append({ "LOC": cur_loc, "COORD": tmp, "FRAME": ff })
          c += 1

    if len(ags[pa]["POSITION"][i+1]) > 1:
      last = alv[-1] + 1
      for ff in range(f1, last):
        if ff in alv:  fill.append({ "LOC": l1, "COORD": [x1, y1], "FRAME": ff })
    agss[i+1] = fill
  return agss

def feed_process(fdl):
  fdtrk = defaultdict(list)
  fdfd = []
  for ii in fdl:
    kk = ii[0]["K"]
    dd = ii[0]["D"]
    ww = ii[0]["W"]
    hh = ii[0]["HS"]
    tmpp = f"_K_{kk}_D_{dd}_W_{ww}"
    fdtrk[tmpp].append(ii[1])

  for i, j in fdtrk.items():
    if len(j) > 2:
      k1 = i.find("_K_")
      d1 = i.find("_D_")
      w1 = i.find("_W_")
      jj = j[-2]
      for f in fdl:
        if f[1] == jj and i[k1+3:d1] == f[0]["K"] and i[d1+3:w1] == f[0]["D"]:  fdfd.append({ "FEED_EVENT": f[0], "FRAME": f[1] - len(j) + 1 })
  return fdfd

def collect_util(pa, rr, ri, ags): # TODO fix astra + kj + cypher + reyna + yoru + etc
  uttt = []
  pla = False
  dfs = False
  maxrd = max(list(ri.keys()))

  for ii, jj in ags[pa]["UTIL"].items():
    ags[pa]["ACTIONS"][ii] = []
    utt = []
    cc = -100
    ee = -100
    st = [-10, -10, -10, (-10, 10)]
    ult = False
    us = False
    for ev, frev in ri[ii]["KEYPOINTS"].items():
      if ev == "PLANTED":  cc = frev
      if ev == "END":  ee = frev
    tmpp = [(kk["STATUS"]["UTIL1"], kk["STATUS"]["UTIL2"], kk["STATUS"]["ABIL"], kk["STATUS"]["ULT"], kk["FRAME"]) for kk in jj if not isemptydict(kk["STATUS"])]
    # print(tmpp)
    for kfrm in ags[pa]["KILLS"][ii]:  utt.append(("KILL", get_loc_at(ri, ags, kfrm, pa, last=True), kfrm))
    for dfrm in ags[pa]["DEATHS"][ii]:  utt.append(("DEATH", get_loc_at(ri, ags, dfrm, pa, last=True), dfrm))
    for afrm in ags[pa]["ASSISTS"][ii]:  utt.append(("ASSIST", get_loc_at(ri, ags, afrm, pa, last=True), afrm))
    for rfrm in ags[pa]["REVIVES"][ii]:  utt.append(("REVIVE", get_loc_at(ri, ags, rfrm, pa, last=True), rfrm))

    alv = dthtrk(ii, pa, ri, ags) # handle revives
    for tt in tmpp:
      for uu in range(3):
        if tt[uu] is not None and tt[4] in alv:
          if st[uu] == -10:  st[uu] = tt[uu]
          if st[uu] != -10 and tt[uu] > st[uu]:
            for nn in range(tt[uu] - st[uu]):
              if uu == 0:  utt.append(("UTIL1+1", get_loc_at(ri, ags, tt[4], pa), tt[4])); st[uu] = tt[uu]
              if uu == 1:  utt.append(("UTIL2+1", get_loc_at(ri, ags, tt[4], pa), tt[4])); st[uu] = tt[uu]
              if uu == 2:  utt.append(("ABIL+1", get_loc_at(ri, ags, tt[4], pa), tt[4])); ags[pa]["ABIL_REGAINED"][ii].append(tt[4]); st[uu] = tt[uu]
          if st[uu] != -10 and tt[uu] < st[uu]:
            for nn in range(st[uu] - tt[uu]):
              if uu == 0:  utt.append(("UTIL1", get_loc_at(ri, ags, tt[4], pa), tt[4])); ags[pa]["UTIL1_USAGE"][ii].append(tt[4]); st[uu] = tt[uu]
              if uu == 1:  utt.append(("UTIL2", get_loc_at(ri, ags, tt[4], pa), tt[4])); ags[pa]["UTIL2_USAGE"][ii].append(tt[4]); st[uu] = tt[uu]
              if uu == 2:  utt.append(("ABIL", get_loc_at(ri, ags, tt[4], pa), tt[4])); ags[pa]["ABIL_USAGE"][ii].append(tt[4]); st[uu] = tt[uu]
      if tt[3] is not None and tt[4] in alv:
        if st[3][0] == -10:  st[3] = tt[3]
        if not pla and tt[4] == cc and tt[4] - 2 in ags[pa]["SPIKE_HELD"][ii]:
          utt.append(("PLANT", get_loc_at(ri, ags, tt[4], pa, last=True), tt[4]))
          ags[pa]["PLANTS"][ii].append(tt[4])
          st[3] = tt[3]
          pla = True
        # if not dfs and cc > 0 and tt[4] >= ee and pa[0] != ri[ii]["ATK_SIDE"] and rr[ii][0] != ri[ii]["ATK_SIDE"]: # TODO track defuses
        #   utt.append(("DEFUSE", get_loc_at(ri, ags, tt[4], pa), tt[4]))
        #   ags[pa]["DEFUSES"][ii].append(tt[4])
        #   st[3] = tt[3]
        #   dfs = True
        if not ult and (tt[3][0] == 0 and st[3][0] == 10):
          utt.append(("ULT", get_loc_at(ri, ags, tt[4], pa), tt[4]))
          ags[pa]["ULT_USAGE"][ii].append(tt[4])
          st[3] = tt[3]
          ult = True
        if not ult and (tt[3][0] == 10 and tt[4] >= ee and ii < maxrd and get_util_status(-1, ags, pa, ii + 1, first=True)["STATUS"].get("ULT") != 10):
          utt.append(("ULT", get_loc_at(ri, ags, tt[4], pa), tt[4]))
          ags[pa]["ULT_USAGE"][ii].append(tt[4])
          st[3] = tt[3]
          ult = True
        if not ult and (tt[3][0] == 10 and tt[4] >= ee and (ii == maxrd or ii == 12 or ii == 24)):
          utt.append(("ULT", get_loc_at(ri, ags, tt[4], pa), tt[4]))
          ags[pa]["ULT_USAGE"][ii].append(tt[4])
          st[3] = tt[3]
          ult = True
        if not us and (tt[3][0] == 10 and tt[4] >= ee and ii < maxrd and get_util_status(-1, ii + 1, pa, ri, ags, first=True)["STATUS"].get("ULT") == 10):
          ags[pa]["ULT_SAVED"][ii].append(tt[4])
          st[3] = tt[3]
          us = True
        if not ult and (tt[3][0] == 10 and tt[4] < ee and ii < maxrd and get_util_status(-1, ii + 1, pa, ri, ags, first=True)["STATUS"].get("ULT") != 10):
          utt.append(("ULT", get_loc_at(ri, ags, tt[4], pa), tt[4]))
          ags[pa]["ULT_USAGE"][ii].append(tt[4])
          ags[pa]["ULT_DEATHS"][ii].append(tt[4])
          st[3] = tt[3]
          ult = True
        if not ult and (tt[3][0] == 10 and tt[4] < ee and (ii == maxrd or ii == 12 or ii == 24)):
          utt.append(("ULT", get_loc_at(ri, ags, tt[4], pa), tt[4]))
          ags[pa]["ULT_USAGE"][ii].append(tt[4])
          ags[pa]["ULT_DEATHS"][ii].append(tt[4])
          st[3] = tt[3]
          ult = True
    utt = sorted(utt, key=lambda k: k[2])
    uttt.append(utt)

  rd = 0
  for uu in uttt:
    # print(uu, rd, pa)
    rd += 1
    for uuu in uu:
      ags[pa]["ACTIONS"][rd].append({ "ACTION_TYPE": uuu[0], "LOC": uuu[1], "FRAME": uuu[2] })

def store_events(ri, ags):
  tmp = []
  x = []
  for i in range(max(list(ri.keys()))):
    for kk in ags.keys():  tmp.append((ags[kk]["ACTIONS"][i+1], kk))
    for ii in tmp:
      for jj in ii[0]:
        x.append((ii[1], jj["ACTION_TYPE"], jj["LOC"], jj["FRAME"]))
    x = sorted(x, key=lambda k: [k[3], k[0]])
    ri[i+1]["EVENTS"] = [ { "PLAYER": iii[0], "EVENT_TYPE": iii[1], "LOC": iii[2], "FRAME": iii[3] } for iii in x ]
    tmp = []
    x = []

def fuse(s, m, te, pe, ge, f):
  a = []
  ss = []
  ff = []
  b = []
  c = defaultdict(list)
  for i in [s, m, te, pe, ge, f]:
    for j in i:
      if j in s:  a.append(("START", j))
      if j in m:  a.append(("MIDGAME", j))
      if j in te:  a.append(("ENDGAME", j))
      if j in pe:  a.append(("SITE_TAKEN", j))
      if j in ge:  a.append(("PLANTED", j))
      if j in f:  a.append(("END", j))
  for i in a:  b.append(i[1])
  aaa = sorted(a, key=lambda t: t[1])
  for i in range(len(a)):
    if aaa[i][1] in s:  ss.append(i)
    if aaa[i][1] in f:  ff.append(i)
  cc = defaultdict(list)
  sss = [ss[0]]
  for i in ss:
    for j in range(len(ff) - 1):
      if i < ff[j+1] and i > ff[j]:  cc[ff[j]].append(i)
  for i, j in cc.items():
    if len(j) >= 1:  sss.append(j[0])
  for i in range(len(sss)):  c[i+1] = (aaa[sss[i]:ff[i]+1])
  return c

def in_adj_atk(p, mm, all=False):
  y = in_loc(p, mm)
  x = []
  xx = []
  for l in mm.atk_locs:  x.append(adjs(l, mm))
  t = list(set(flatten(x)))
  t1 = [i for i in t if i not in mm.atk_locs]
  tt = [i for i in t1 if i not in list(mm.sites.keys())]
  if all:  return tt
  for i in y:
    if i in tt:  xx.append(i)
  return xx

def in_adj_def(p, mm, all=False):
  y = in_loc(p, mm)
  x = []
  xx = []
  for l in mm.def_locs:  x.append(adjs(l, mm))
  t = list(set(flatten(x)))
  t1 = [i for i in t if i not in mm.def_locs]
  tt = [i for i in t1 if i not in list(mm.sites.keys())]
  if all:  return tt
  for i in y:
    if i in tt:  xx.append(i)
  return xx

def in_atk(p, mm):
  y = []
  for i in mm.atk_locs:
    if in_loc(p, mm, i):  y.append(i)
  return y

def in_def(p, mm):
  y = []
  for i in mm.def_locs:
    if in_loc(p, mm, i):  y.append(i)
  return y

def in_n(p, mm):
  y = []
  for i in mm.n_locs:
    if in_loc(p, mm, i):  y.append(i)
  return y

def in_sites(p, mm):
  y = []
  for i in mm.sites:
    if in_loc(p, mm, i):  y.append(i)
  return y

def in_spawns(p, mm):
  y = []
  for i in mm.atk_spawns:
    if in_loc(p, mm, i):  y.append(i)
  for i in mm.def_spawns:
    if in_loc(p, mm, i):  y.append(i)
  return y

def in_a(p, mm):
  y = []
  for i in mm.a:
    if in_loc(p, mm, i):  y.append(i)
  return y

def in_b(p, mm):
  y = []
  for i in mm.b:
    if in_loc(p, mm, i):  y.append(i)
  return y

def in_m(p, mm):
  y = []
  for i in mm.m:
    if in_loc(p, mm, i):  y.append(i)
  return y

def in_c(p, mm):
  y = []
  for i in mm.c:
    if in_loc(p, mm, i):  y.append(i)
  return y

def in_d(p, mm):
  y = []
  for i in mm.d:
    if in_loc(p, mm, i):  y.append(i)
  return y

def frame_diffs(l):
  x = []
  for i in range(len(l) - 1):  x.append(l[i + 1][1] - l[i][1])
  return x

def search_in_loc_type(p, mm, atk_loc=False, def_loc=False, adj=[]):
  y = in_loc(p, mm) if type(p) != str else p
  if atk_loc:  return in_atk(p, mm)
  if def_loc:  return in_def(p, mm)
  if adj:
    x = []
    for i in y:
      if i in adj:  x.append(i)
    return x
  return y

def loc_in(cur, chk):
  for i in cur:
    if i in chk:  return True
  return False

def resolve_adj(locs, adjs):
  return list(set(flatten([adjs[l] for l in locs])))

def parse_filter(s, ags):
  return True

def measure_aggs(ri, ags):
  for i in range(max(list(ri.keys()))):
    for kk in ags.keys():

      ags[kk]["KILL_COUNT"][i+1] = len(ags[kk]["KILLS"][i+1])
      ags[kk]["DEATH_COUNT"][i+1] = len(ags[kk]["DEATHS"][i+1])
      ags[kk]["SURVIVE_COUNT"][i+1] = len(ags[kk]["SURVIVES"][i+1])
      ags[kk]["IDLE_COUNT"][i+1] = len(ags[kk]["IDLES"][i+1])
      kilc = ags[kk]["KILL_COUNT"][i+1] if ags[kk]["KILL_COUNT"][i+1] > 0 else 1
      dthc = ags[kk]["DEATH_COUNT"][i+1] if ags[kk]["DEATH_COUNT"][i+1] > 0 else 1
      srvc = ags[kk]["SURVIVE_COUNT"][i+1] if ags[kk]["SURVIVE_COUNT"][i+1] > 0 else 1
      idlc = ags[kk]["IDLE_COUNT"][i+1] if ags[kk]["IDLE_COUNT"][i+1] > 0 else 1
      ags[kk]["ASSIST_COUNT"][i+1] = len(ags[kk]["ASSISTS"][i+1])
      ags[kk]["REVIVE_COUNT"][i+1] = len(ags[kk]["REVIVES"][i+1])
      ags[kk]["TRADE_COUNT"][i+1] = len(ags[kk]["TRADES"][i+1])
      ags[kk]["HEADSHOT_COUNT"][i+1] = len(ags[kk]["HEADSHOTS"][i+1])
      ags[kk]["WALLBANG_COUNT"][i+1] = len(ags[kk]["WALLBANGS"][i+1])
      ags[kk]["UTIL_KILL_COUNT"][i+1] = len(ags[kk]["UTIL_KILLS"][i+1])
      ags[kk]["SPIKE_DEATH_COUNT"][i+1] = len(ags[kk]["SPIKE_DEATHS"][i+1])
      ags[kk]["%_HEADSHOTS"][i+1] = ags[kk]["HEADSHOT_COUNT"][i+1] / kilc
      ags[kk]["%_WALLBANGS"][i+1] = ags[kk]["WALLBANG_COUNT"][i+1] / kilc
      ags[kk]["%_UTIL_KILLS"][i+1] = ags[kk]["UTIL_KILL_COUNT"][i+1] / kilc
      ags[kk]["%_SPIKE_DEATHS"][i+1] = ags[kk]["SPIKE_DEATH_COUNT"][i+1] / dthc
      ags[kk]["PREV_K/D"][i+1] = ags[kk]["K/D"][i] if i > 0 else 0
      ags[kk]["K/D"][i+1] = ags[kk]["KILL_COUNT"][i+1] / dthc
      ags[kk]["PREV_D/K"][i+1] = ags[kk]["D/K"][i] if i > 0 else 0
      ags[kk]["D/K"][i+1] = ags[kk]["DEATH_COUNT"][i+1] / kilc
      ags[kk]["PREV_S/I"][i+1] = ags[kk]["S/I"][i] if i > 0 else 0
      ags[kk]["S/I"][i+1] = ags[kk]["SURVIVE_COUNT"][i+1] / idlc
      ags[kk]["PREV_I/S"][i+1] = ags[kk]["I/S"][i] if i > 0 else 0
      ags[kk]["I/S"][i+1] = ags[kk]["IDLE_COUNT"][i+1] / srvc
      ags[kk]["PREV_T/D"][i+1] = ags[kk]["T/D"][i] if i > 0 else 0
      ags[kk]["T/D"][i+1] = ags[kk]["TRADE_COUNT"][i+1] / dthc
      ags[kk]["PREV_ATR/I"][i+1] = ags[kk]["ATR/I"][i] if i > 0 else 0
      ags[kk]["ATR/I"][i+1] = (ags[kk]["ASSIST_COUNT"][i+1] + ags[kk]["TRADE_COUNT"][i+1] + ags[kk]["REVIVE_COUNT"][i+1]) / idlc
      ags[kk]["TIME"][i+1] = (ri[i+1]["KEYPOINTS"]["END"] - ri[i+1]["KEYPOINTS"]["START"] + 1) / FPAC
      ags[kk]["%_TIME"][i+1] = 1.0
      alvtime = len(dthtrk(i + 1, kk, ri, ags))
      ags[kk]["TIME_ALIVE"][i+1] = alvtime / FPAC
      ags[kk]["%_TIME_ALIVE"][i+1] = ags[kk]["TIME_ALIVE"][i+1] / ags[kk]["TIME"][i+1]
      ags[kk]["TIME_DEAD"][i+1] = ((ri[i+1]["KEYPOINTS"]["END"] - ri[i+1]["KEYPOINTS"]["START"] + 1) - alvtime) / FPAC
      ags[kk]["%_TIME_DEAD"][i+1] = ags[kk]["TIME_DEAD"][i+1] / ags[kk]["TIME"][i+1]
      ags[kk]["PLANT_COUNT"][i+1] = len(ags[kk]["PLANTS"][i+1])
      ags[kk]["DEFUSE_COUNT"][i+1] = len(ags[kk]["DEFUSES"][i+1])
      ags[kk]["UTIL1_USAGE_COUNT"][i+1] = len(ags[kk]["UTIL1_USAGE"][i+1])
      ags[kk]["UTIL2_USAGE_COUNT"][i+1] = len(ags[kk]["UTIL2_USAGE"][i+1])
      ags[kk]["ABIL_USAGE_COUNT"][i+1] = len(ags[kk]["ABIL_USAGE"][i+1])
      ags[kk]["ABIL_REGAINED_COUNT"][i+1] = len(ags[kk]["ABIL_REGAINED"][i+1])
      ags[kk]["ULT_USAGE_COUNT"][i+1] = len(ags[kk]["ULT_USAGE"][i+1])
      ags[kk]["ULT_SAVED_COUNT"][i+1] = len(ags[kk]["ULT_SAVED"][i+1])
      ags[kk]["ULT_DEATH_COUNT"][i+1] = len(ags[kk]["ULT_DEATHS"][i+1])
      ags[kk]["UTIL1_SAVED_COUNT"][i+1] = 0 if ags[kk]["SURVIVE_COUNT"][i+1] == 0 else get_util_status(-1, i + 1, kk, ri, ags, last=True)["STATUS"]["UTIL1"]
      ags[kk]["UTIL2_SAVED_COUNT"][i+1] = 0 if ags[kk]["SURVIVE_COUNT"][i+1] == 0 else get_util_status(-1, i + 1, kk, ri, ags, last=True)["STATUS"]["UTIL2"]
      ags[kk]["ABIL_SAVED_COUNT"][i+1] = 0 if ags[kk]["SURVIVE_COUNT"][i+1] == 0 else get_util_status(-1, i + 1, kk, ri, ags, last=True)["STATUS"]["ABIL"]
      ags[kk]["UTIL1_DIED_WITH_COUNT"][i+1] = 0 if ags[kk]["SURVIVE_COUNT"][i+1] != 0 else get_util_status(-1, i + 1, kk, ri, ags, last=True)["STATUS"]["UTIL1"]
      ags[kk]["UTIL2_DIED_WITH_COUNT"][i+1] = 0 if ags[kk]["SURVIVE_COUNT"][i+1] != 0 else get_util_status(-1, i + 1, kk, ri, ags, last=True)["STATUS"]["UTIL2"]
      ags[kk]["ABIL_DIED_WITH_COUNT"][i+1] = 0 if ags[kk]["SURVIVE_COUNT"][i+1] != 0 else get_util_status(-1, i + 1, kk, ri, ags, last=True)["STATUS"]["ABIL"]
      ags[kk]["PREV_KATRP/D"][i+1] = ags[kk]["KATRP/D"][i] if i > 0 else 0
      ags[kk]["KATRP/D"][i+1] = (ags[kk]["KILL_COUNT"][i+1] + ags[kk]["ASSIST_COUNT"][i+1] + ags[kk]["TRADE_COUNT"][i+1] + ags[kk]["REVIVE_COUNT"][i+1] + ags[kk]["PLANT_COUNT"][i+1]) / (dthc)
      ags[kk]["PROGRESSION_COUNT"][i+1] = len(ags[kk]["PROGRESSIONS"][i+1])
      ags[kk]["HOLD_COUNT"][i+1] = len(ags[kk]["HOLDS"][i+1])
      ags[kk]["EXECUTION_COUNT"][i+1] = len(ags[kk]["EXECUTIONS"][i+1])
      ags[kk]["SWITCH_COUNT"][i+1] = len(ags[kk]["SWITCHS"][i+1])
      ags[kk]["ROTATION_COUNT"][i+1] = len(ags[kk]["ROTATIONS"][i+1])
      ags[kk]["PINCER_COUNT"][i+1] = len(ags[kk]["PINCERS"][i+1])
      ags[kk]["FLANK_COUNT"][i+1] = len(ags[kk]["FLANKS"][i+1])
      ags[kk]["COVER_COUNT"][i+1] = len(ags[kk]["COVERS"][i+1])

      measure_distance(i + 1, kk, ri, ags)
      measure_per_stat(i + 1, kk, ri, ags)

def measure_distance(rd, pa, ri, ags):
  ppm = PPM_PUB if ri[rd]["PUBLIC"] else PPM_PRIV
  z, zx, zy, cz, czx, czy, vz, al, am, mov, stl = ([], [], [], [], [], [], [], [], [], [], [])
  ddx = 0
  ddy = 0
  tx = 0
  ty = 0
  st = 0
  if rd in ags[pa]["POSITION"].keys() and len(ags[pa]["POSITION"][rd]) > 0:
    tx = ags[pa]["POSITION"][rd][0]["COORD"][0]
    ty = ags[pa]["POSITION"][rd][0]["COORD"][1]
    st = ags[pa]["POSITION"][rd][0]["FRAME"]
  else:
    ags[pa]["DISTANCE"][rd] = -1
    ags[pa]["CUM_DISTANCE"][rd] = -1
    ags[pa]["VELOCITY"][rd] = -1
    ags[pa]["TOTAL_DISTANCE"][rd] = -1
    ags[pa]["TOTAL_HORIZ_DISTANCE"][rd] = -1
    ags[pa]["TOTAL_VERT_DISTANCE"][rd] = -1
    ags[pa]["TOTAL_DISTANCE/TIME"][rd] = -1
    ags[pa]["TOTAL_HORIZ_DISTANCE/TIME"][rd] = -1
    ags[pa]["TOTAL_VERT_DISTANCE/TIME"][rd] = -1
    ags[pa]["TOTAL_VELOCITY"][rd] = -1
    ags[pa]["TOTAL_HORIZ_VELOCITY"][rd] = -1
    ags[pa]["TOTAL_VERT_VELOCITY"][rd] = -1
    ags[pa]["%_DISTANCE"][rd] = -1
    ags[pa]["%_HORIZ_DISTANCE"][rd] = -1
    ags[pa]["%_VERT_DISTANCE"][rd] = -1
    ags[pa]["AVG_LOC"][rd] = -1
    ags[pa]["AVG_MOMENTUM"][rd] = -1
    ags[pa]["TIME_MOVING"][rd] = -1
    ags[pa]["TIME_STATIONARY"][rd] = -1
    ags[pa]["%_TIME_MOVING"][rd] = -1
    ags[pa]["%_TIME_STATIONARY"][rd] = -1
    ags[pa]["TOTAL_AVG_LOC"][rd] = [-1, -1]
    ags[pa]["TOTAL_AVG_LOC_COORD_X"][rd] = -1
    ags[pa]["TOTAL_AVG_LOC_COORD_Y"][rd] = -1
    ags[pa]["TOTAL_AVG_MOMENTUM"][rd] = [-1, -1]
    ags[pa]["TOTAL_AVG_MOMENTUM_COORD_X"][rd] = -1
    ags[pa]["TOTAL_AVG_MOMENTUM_COORD_Y"][rd] = -1
    return None
  stl.append(st)

  for ii in range(len(ags[pa]["POSITION"][rd]) - 1):
    denom = (ags[pa]["POSITION"][rd][ii+1]["FRAME"] - st) / FPAC
    dx = abs(ags[pa]["POSITION"][rd][ii+1]["COORD"][0] - ags[pa]["POSITION"][rd][ii]["COORD"][0]) / ppm
    dy = abs(ags[pa]["POSITION"][rd][ii+1]["COORD"][1] - ags[pa]["POSITION"][rd][ii]["COORD"][1]) / ppm
    ddx += dx
    ddy += dy
    z.append({ "dX": dx, "dY": dy, "FRAME": ags[pa]["POSITION"][rd][ii+1]["FRAME"] })
    cz.append({ "dX": ddx, "dY": ddy, "FRAME": ags[pa]["POSITION"][rd][ii+1]["FRAME"] })
    vz.append({ "vX": (ddx / denom), "vY": (ddy / denom), "FRAME": ags[pa]["POSITION"][rd][ii+1]["FRAME"] })
    if dx <= 1 and dy <= 1:  stl.append(ags[pa]["POSITION"][rd][ii+1]["FRAME"])
    else:  mov.append(ags[pa]["POSITION"][rd][ii+1]["FRAME"])
    tx += ags[pa]["POSITION"][rd][ii+1]["COORD"][0]
    ty += ags[pa]["POSITION"][rd][ii+1]["COORD"][1]
    al.append({ "X_AVG": (tx / denom), "Y_AVG": (ty / denom), "FRAME": ags[pa]["POSITION"][rd][ii+1]["FRAME"] })
    am.append({ 
      "X_MOMENTUM": (tx / denom) + (ddx / denom), "Y_MOMENTUM": (ty / denom) + (ddy / denom), "FRAME": ags[pa]["POSITION"][rd][ii+1]["FRAME"] })

  ags[pa]["DISTANCE"][rd] = z
  ags[pa]["CUM_DISTANCE"][rd] = cz
  ags[pa]["VELOCITY"][rd] = vz
  ags[pa]["TOTAL_DISTANCE"][rd] = sqrt((ddx**2) + (ddy**2))
  ags[pa]["TOTAL_HORIZ_DISTANCE"][rd] = ddx
  ags[pa]["TOTAL_VERT_DISTANCE"][rd] = ddy
  ags[pa]["TOTAL_DISTANCE/TIME"][rd] = ags[pa]["TOTAL_DISTANCE"][rd] / ags[pa]["TIME"][rd]
  ags[pa]["TOTAL_HORIZ_DISTANCE/TIME"][rd] = ags[pa]["TOTAL_HORIZ_DISTANCE"][rd] / ags[pa]["TIME"][rd]
  ags[pa]["TOTAL_VERT_DISTANCE/TIME"][rd] = ags[pa]["TOTAL_VERT_DISTANCE"][rd] / ags[pa]["TIME"][rd]
  ags[pa]["TOTAL_VELOCITY"][rd] = ags[pa]["TOTAL_DISTANCE"][rd] / ags[pa]["TIME_ALIVE"][rd]
  ags[pa]["TOTAL_HORIZ_VELOCITY"][rd] = ags[pa]["TOTAL_HORIZ_DISTANCE"][rd] / ags[pa]["TIME_ALIVE"][rd]
  ags[pa]["TOTAL_VERT_VELOCITY"][rd] = ags[pa]["TOTAL_VERT_DISTANCE"][rd] / ags[pa]["TIME_ALIVE"][rd]
  ags[pa]["%_DISTANCE"][rd] = (ags[pa]["TOTAL_DISTANCE"][rd]) / ((sqrt((MM_XD**2) + (MM_YD**2))) / ppm)
  ags[pa]["%_HORIZ_DISTANCE"][rd] = (ags[pa]["TOTAL_HORIZ_DISTANCE"][rd]) / (MM_XD / ppm)
  ags[pa]["%_VERT_DISTANCE"][rd] = (ags[pa]["TOTAL_VERT_DISTANCE"][rd]) / (MM_YD / ppm)
  ags[pa]["AVG_LOC"][rd] = al
  ags[pa]["AVG_MOMENTUM"][rd] = am
  ttx = tx / ags[pa]["TIME_ALIVE"][rd]
  tty = ty / ags[pa]["TIME_ALIVE"][rd]
  ags[pa]["TIME_MOVING"][rd] = len(mov) / FPAC
  ags[pa]["TIME_STATIONARY"][rd] = len(stl) / FPAC
  ags[pa]["%_TIME_MOVING"][rd] = ags[pa]["TIME_MOVING"][rd] / ags[pa]["TIME_ALIVE"][rd]
  ags[pa]["%_TIME_STATIONARY"][rd] = ags[pa]["TIME_STATIONARY"][rd] / ags[pa]["TIME_ALIVE"][rd]
  ags[pa]["TOTAL_AVG_LOC"][rd] = [ttx, tty]
  ags[pa]["TOTAL_AVG_LOC_COORD_X"][rd] = ttx
  ags[pa]["TOTAL_AVG_LOC_COORD_Y"][rd] = tty
  ags[pa]["TOTAL_AVG_MOMENTUM"][rd] = [ttx + ags[pa]["TOTAL_HORIZ_VELOCITY"][rd], tty + ags[pa]["TOTAL_VERT_VELOCITY"][rd]]
  ags[pa]["TOTAL_AVG_MOMENTUM_COORD_X"][rd] = ttx + ags[pa]["TOTAL_HORIZ_VELOCITY"][rd]
  ags[pa]["TOTAL_AVG_MOMENTUM_COORD_Y"][rd] = tty + ags[pa]["TOTAL_VERT_VELOCITY"][rd]

def measure_per_stat(rd, pa, ri, ags):
  keylist = [
    "KILL_COUNT", "DEATH_COUNT", "ASSIST_COUNT", "SURVIVE_COUNT", "IDLE_COUNT", "TRADE_COUNT", 
    "REVIVE_COUNT", "PLANT_COUNT", "DEFUSE_COUNT", 
    "HEADSHOT_COUNT", "WALLBANG_COUNT", "UTIL_KILL_COUNT", "SPIKE_DEATH_COUNT", 
    "UTIL1_USAGE_COUNT", "UTIL1_SAVED_COUNT", "UTIL1_DIED_WITH_COUNT", 
    "UTIL2_USAGE_COUNT", "UTIL2_SAVED_COUNT", "UTIL2_DIED_WITH_COUNT", 
    "ABIL_USAGE_COUNT", "ABIL_REGAINED_COUNT", "ABIL_SAVED_COUNT", "ABIL_DIED_WITH_COUNT", 
    "ULT_USAGE_COUNT", "ULT_SAVED_COUNT", "ULT_DEATH_COUNT", 
    # "PROGRESSION_COUNT", "HOLD_COUNT", "EXECUTION_COUNT", "SWITCH_COUNT", "ROTATION_COUNT", "PINCER_COUNT", "FLANK_COUNT"
    ]

  for k1 in keylist:
    if ags[pa][k1][rd]:
      ags[pa][f"{k1}/TOTAL_DISTANCE"][rd] = ags[pa][k1][rd] / ags[pa]["TOTAL_DISTANCE"][rd] if ags[pa]["TOTAL_DISTANCE"][rd] > 0 else ags[pa][k1][rd]
      ags[pa][f"{k1}/TOTAL_VELOCITY"][rd] = ags[pa][k1][rd] / ags[pa]["TOTAL_VELOCITY"][rd] if ags[pa]["TOTAL_VELOCITY"][rd] > 0 else ags[pa][k1][rd]
      ags[pa][f"{k1}/TIME"][rd] = ags[pa][k1][rd] / ags[pa]["TIME"][rd] if ags[pa]["TIME"][rd] > 0 else ags[pa][k1][rd]
      ags[pa][f"{k1}/TIME_ALIVE"][rd] = ags[pa][k1][rd] / ags[pa]["TIME_ALIVE"][rd] if ags[pa]["TIME_ALIVE"][rd] > 0 else ags[pa][k1][rd]
    else:
      ags[pa][f"{k1}/TOTAL_DISTANCE"][rd] = 0
      ags[pa][f"{k1}/TOTAL_VELOCITY"][rd] = 0
      ags[pa][f"{k1}/TIME"][rd] = 0
      ags[pa][f"{k1}/TIME_ALIVE"][rd] = 0

  keylist = keylist[6:]
  keylist.extend(["TOTAL_DISTANCE", "TOTAL_VELOCITY", "TIME", "TIME_ALIVE"])
  for k1 in keylist:
    if ags[pa][k1][rd]:
      if ags[pa].get(f"{k1}/KILL_COUNT"):  ags[pa][f"{k1}/KILL_COUNT"][rd] = ags[pa][k1][rd] / ags[pa]["KILL_COUNT"][rd] if ags[pa]["KILL_COUNT"][rd] > 0 else ags[pa][k1][rd]
      if ags[pa].get(f"{k1}/DEATH_COUNT"):  ags[pa][f"{k1}/DEATH_COUNT"][rd] = ags[pa][k1][rd] / ags[pa]["DEATH_COUNT"][rd] if ags[pa]["DEATH_COUNT"][rd] > 0 else ags[pa][k1][rd]
      ags[pa][f"{k1}/ASSIST_COUNT"][rd] = ags[pa][k1][rd] / ags[pa]["ASSIST_COUNT"][rd] if ags[pa]["ASSIST_COUNT"][rd] > 0 else ags[pa][k1][rd]
      ags[pa][f"{k1}/SURVIVE_COUNT"][rd] = ags[pa][k1][rd] / ags[pa]["SURVIVE_COUNT"][rd] if ags[pa]["SURVIVE_COUNT"][rd] > 0 else ags[pa][k1][rd]
      ags[pa][f"{k1}/IDLE_COUNT"][rd] = ags[pa][k1][rd] / ags[pa]["IDLE_COUNT"][rd] if ags[pa]["IDLE_COUNT"][rd] > 0 else ags[pa][k1][rd]
      ags[pa][f"{k1}/TRADE_COUNT"][rd] = ags[pa][k1][rd] / ags[pa]["TRADE_COUNT"][rd] if ags[pa]["TRADE_COUNT"][rd] > 0 else ags[pa][k1][rd]
    else:
      if ags[pa].get(f"{k1}/KILL_COUNT"):  ags[pa][f"{k1}/KILL_COUNT"][rd] = 0
      if ags[pa].get(f"{k1}/DEATH_COUNT"):  ags[pa][f"{k1}/DEATH_COUNT"][rd] = 0
      ags[pa][f"{k1}/ASSIST_COUNT"][rd] = 0
      ags[pa][f"{k1}/SURVIVE_COUNT"][rd] = 0
      ags[pa][f"{k1}/IDLE_COUNT"][rd] = 0
      ags[pa][f"{k1}/TRADE_COUNT"][rd] = 0

  ags[pa]["KILL_COUNT/ASSIST_COUNT"][rd] = ags[pa]["KILL_COUNT"][rd] / ags[pa]["ASSIST_COUNT"][rd] if ags[pa]["ASSIST_COUNT"][rd] > 0 else ags[pa]["KILL_COUNT"][rd]
  ags[pa]["KILL_COUNT/SURVIVE_COUNT"][rd] = ags[pa]["KILL_COUNT"][rd] / ags[pa]["SURVIVE_COUNT"][rd] if ags[pa]["SURVIVE_COUNT"][rd] > 0 else ags[pa]["KILL_COUNT"][rd]
  ags[pa]["KILL_COUNT/IDLE_COUNT"][rd] = ags[pa]["KILL_COUNT"][rd] / ags[pa]["IDLE_COUNT"][rd] if ags[pa]["IDLE_COUNT"][rd] > 0 else ags[pa]["KILL_COUNT"][rd]
  ags[pa]["KILL_COUNT/TRADE_COUNT"][rd] = ags[pa]["KILL_COUNT"][rd] / ags[pa]["TRADE_COUNT"][rd] if ags[pa]["TRADE_COUNT"][rd] > 0 else ags[pa]["KILL_COUNT"][rd]

  ags[pa]["DEATH_COUNT/ASSIST_COUNT"][rd] = ags[pa]["DEATH_COUNT"][rd] / ags[pa]["ASSIST_COUNT"][rd] if ags[pa]["ASSIST_COUNT"][rd] > 0 else ags[pa]["DEATH_COUNT"][rd]
  ags[pa]["DEATH_COUNT/SURVIVE_COUNT"][rd] = ags[pa]["DEATH_COUNT"][rd] / ags[pa]["SURVIVE_COUNT"][rd] if ags[pa]["SURVIVE_COUNT"][rd] > 0 else ags[pa]["DEATH_COUNT"][rd]
  ags[pa]["DEATH_COUNT/IDLE_COUNT"][rd] = ags[pa]["DEATH_COUNT"][rd] / ags[pa]["IDLE_COUNT"][rd] if ags[pa]["IDLE_COUNT"][rd] > 0 else ags[pa]["DEATH_COUNT"][rd]
  ags[pa]["DEATH_COUNT/TRADE_COUNT"][rd] = ags[pa]["DEATH_COUNT"][rd] / ags[pa]["TRADE_COUNT"][rd] if ags[pa]["TRADE_COUNT"][rd] > 0 else ags[pa]["DEATH_COUNT"][rd]

  ags[pa]["ASSIST_COUNT/KILL_COUNT"][rd] = ags[pa]["ASSIST_COUNT"][rd] / ags[pa]["KILL_COUNT"][rd] if ags[pa]["KILL_COUNT"][rd] > 0 else ags[pa]["ASSIST_COUNT"][rd]
  ags[pa]["ASSIST_COUNT/DEATH_COUNT"][rd] = ags[pa]["ASSIST_COUNT"][rd] / ags[pa]["DEATH_COUNT"][rd] if ags[pa]["DEATH_COUNT"][rd] > 0 else ags[pa]["ASSIST_COUNT"][rd]
  ags[pa]["ASSIST_COUNT/SURVIVE_COUNT"][rd] = ags[pa]["ASSIST_COUNT"][rd] / ags[pa]["SURVIVE_COUNT"][rd] if ags[pa]["SURVIVE_COUNT"][rd] > 0 else ags[pa]["ASSIST_COUNT"][rd]
  ags[pa]["ASSIST_COUNT/IDLE_COUNT"][rd] = ags[pa]["ASSIST_COUNT"][rd] / ags[pa]["IDLE_COUNT"][rd] if ags[pa]["IDLE_COUNT"][rd] > 0 else ags[pa]["ASSIST_COUNT"][rd]
  ags[pa]["ASSIST_COUNT/TRADE_COUNT"][rd] = ags[pa]["ASSIST_COUNT"][rd] / ags[pa]["TRADE_COUNT"][rd] if ags[pa]["TRADE_COUNT"][rd] > 0 else ags[pa]["ASSIST_COUNT"][rd]

  ags[pa]["SURVIVE_COUNT/KILL_COUNT"][rd] = ags[pa]["SURVIVE_COUNT"][rd] / ags[pa]["KILL_COUNT"][rd] if ags[pa]["KILL_COUNT"][rd] > 0 else ags[pa]["SURVIVE_COUNT"][rd]
  ags[pa]["SURVIVE_COUNT/DEATH_COUNT"][rd] = ags[pa]["SURVIVE_COUNT"][rd] / ags[pa]["DEATH_COUNT"][rd] if ags[pa]["DEATH_COUNT"][rd] > 0 else ags[pa]["SURVIVE_COUNT"][rd]
  ags[pa]["SURVIVE_COUNT/ASSIST_COUNT"][rd] = ags[pa]["SURVIVE_COUNT"][rd] / ags[pa]["ASSIST_COUNT"][rd] if ags[pa]["ASSIST_COUNT"][rd] > 0 else ags[pa]["SURVIVE_COUNT"][rd]
  ags[pa]["SURVIVE_COUNT/TRADE_COUNT"][rd] = ags[pa]["SURVIVE_COUNT"][rd] / ags[pa]["TRADE_COUNT"][rd] if ags[pa]["TRADE_COUNT"][rd] > 0 else ags[pa]["SURVIVE_COUNT"][rd]

  ags[pa]["IDLE_COUNT/KILL_COUNT"][rd] = ags[pa]["IDLE_COUNT"][rd] / ags[pa]["KILL_COUNT"][rd] if ags[pa]["KILL_COUNT"][rd] > 0 else ags[pa]["IDLE_COUNT"][rd]
  ags[pa]["IDLE_COUNT/DEATH_COUNT"][rd] = ags[pa]["IDLE_COUNT"][rd] / ags[pa]["DEATH_COUNT"][rd] if ags[pa]["DEATH_COUNT"][rd] > 0 else ags[pa]["IDLE_COUNT"][rd]
  ags[pa]["IDLE_COUNT/ASSIST_COUNT"][rd] = ags[pa]["IDLE_COUNT"][rd] / ags[pa]["ASSIST_COUNT"][rd] if ags[pa]["ASSIST_COUNT"][rd] > 0 else ags[pa]["IDLE_COUNT"][rd]
  ags[pa]["IDLE_COUNT/TRADE_COUNT"][rd] = ags[pa]["IDLE_COUNT"][rd] / ags[pa]["TRADE_COUNT"][rd] if ags[pa]["TRADE_COUNT"][rd] > 0 else ags[pa]["IDLE_COUNT"][rd]

  ags[pa]["TRADE_COUNT/KILL_COUNT"][rd] = ags[pa]["TRADE_COUNT"][rd] / ags[pa]["KILL_COUNT"][rd] if ags[pa]["KILL_COUNT"][rd] > 0 else ags[pa]["TRADE_COUNT"][rd]
  ags[pa]["TRADE_COUNT/ASSIST_COUNT"][rd] = ags[pa]["TRADE_COUNT"][rd] / ags[pa]["ASSIST_COUNT"][rd] if ags[pa]["ASSIST_COUNT"][rd] > 0 else ags[pa]["TRADE_COUNT"][rd]
  ags[pa]["TRADE_COUNT/SURVIVE_COUNT"][rd] = ags[pa]["TRADE_COUNT"][rd] / ags[pa]["SURVIVE_COUNT"][rd] if ags[pa]["SURVIVE_COUNT"][rd] > 0 else ags[pa]["TRADE_COUNT"][rd]
  ags[pa]["TRADE_COUNT/IDLE_COUNT"][rd] = ags[pa]["TRADE_COUNT"][rd] / ags[pa]["IDLE_COUNT"][rd] if ags[pa]["IDLE_COUNT"][rd] > 0 else ags[pa]["TRADE_COUNT"][rd]
