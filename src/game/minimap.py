import cv2
import itertools
from MTM import matchTemplates, drawBoxesOnRGB
import os
from threading import Thread
from time import sleep
import numpy as np

from game.map import *

iconsdir = os.getcwd() + "/icons/"
abilsdir = os.getcwd() + "/icons/abils/"
agentsdir = os.getcwd() + "/icons/agents/"
scoresdir = os.getcwd() + "/icons/scores/"
ultsdir = os.getcwd() + "/icons/ults/"
weapsdir = os.getcwd() + "/icons/weaps/"

FPAC = 1
PPM_PUB = 2.5
PPM_PRIV = 2.5 # TODO verify later
CORES = 1
SCREEN_WIDTH, SCREEN_HEIGHT = 1920, 1080

def get_frame(src, n):
  cap = cv2.VideoCapture(src)
  d = f"{os.path.dirname(os.path.dirname(src))}/temp/"
  os.mkdir(d)
  cap.set(cv2.CAP_PROP_POS_MSEC, (n * 1000 / FPAC))
  ret, frame = cap.read()
  p = f"{d}{os.path.basename(src)[:-4]}_{n}.png"
  cv2.imwrite(p, frame)
  img = cv2.imread(p)
  os.remove(p)
  os.rmdir(d)
  return img

def get_surr_coords(c, r=1):
  x, s, e = [], r * -1, r + 1
  for i in range(s, e):
    for j in range(s, e):
      x.append([ c[0] + i, c[1] + j ])
  return x

def get_all_surr_coords(c):
  x = []
  y = []
  for i in c:
    x.append(get_surr_coords(i, r=5))
  for ii in x:
    for jj in ii:
      y.append(jj)
  return list(j for j,_ in itertools.groupby(y))

def get_minimap_coords(minimap_frame):
  minimap_coords = []
  lower1, upper1 = np.array([126, 126, 126], dtype="uint8"), np.array([128, 128, 128], dtype="uint8")
  lower2, upper2 = np.array([133, 161, 163], dtype="uint8"), np.array([139, 165, 167], dtype="uint8")
  mask_gray, mask_site = cv2.inRange(minimap_frame, lower1, upper1), cv2.inRange(minimap_frame, lower2, upper2)
  mask = (255*(mask_gray + mask_site)).clip(0, 255).astype("uint8")
  kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3,3))
  opening = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=1)
  contours, _ = cv2.findContours(opening, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
  for ccnt in contours:
    ccnt_area = cv2.contourArea(ccnt)
    for i in ccnt:
      if i[0][0] < SCREEN_WIDTH / 4 and i[0][1] < SCREEN_HEIGHT / 2:  minimap_coords.append([i[0][0], i[0][1]])
  ret = get_all_surr_coords(minimap_coords)
  # print(ret, type(ret[0][0]))
  return ret

def minimap_tracking(data, public, teamleft="", teamright=""):

  abcd = "mm_" # ""
  t_astra = cv2.imread(agentsdir + abcd + "astra.png")
  t_breach = cv2.imread(agentsdir + abcd + "breach.png")
  t_brimstone = cv2.imread(agentsdir + abcd + "brimstone.png")
  t_cypher = cv2.imread(agentsdir + abcd + "cypher.png")
  t_jett = cv2.imread(agentsdir + abcd + "jett.png")
  t_kayo = cv2.imread(agentsdir + abcd + "kayo.png")
  t_killjoy = cv2.imread(agentsdir + abcd + "killjoy.png")
  t_omen = cv2.imread(agentsdir + abcd + "omen.png")
  t_phoenix = cv2.imread(agentsdir + abcd + "phoenix.png")
  t_raze = cv2.imread(agentsdir + abcd + "raze.png")
  t_reyna = cv2.imread(agentsdir + abcd + "reyna.png")
  t_sage = cv2.imread(agentsdir + abcd + "sage.png")
  t_skye = cv2.imread(agentsdir + abcd + "skye.png")
  t_sova = cv2.imread(agentsdir + abcd + "sova.png")
  t_viper = cv2.imread(agentsdir + abcd + "viper.png")
  t_yoru = cv2.imread(agentsdir + abcd + "yoru.png")

  ts_astra = cv2.imread(agentsdir + "astra_with_spike.png")
  ts_breach = cv2.imread(agentsdir + "breach_with_spike.png")
  ts_brimstone = cv2.imread(agentsdir + "brimstone_with_spike.png")
  ts_cypher = cv2.imread(agentsdir + "cypher_with_spike.png")
  ts_jett = cv2.imread(agentsdir + "jett_with_spike.png")
  ts_kayo = cv2.imread(agentsdir + "kayo_with_spike.png")
  ts_killjoy = cv2.imread(agentsdir + "killjoy_with_spike.png")
  ts_omen = cv2.imread(agentsdir + "omen_with_spike.png")
  ts_phoenix = cv2.imread(agentsdir + "phoenix_with_spike.png")
  ts_raze = cv2.imread(agentsdir + "raze_with_spike.png")
  ts_reyna = cv2.imread(agentsdir + "reyna_with_spike.png")
  ts_sage = cv2.imread(agentsdir + "sage_with_spike.png")
  ts_skye = cv2.imread(agentsdir + "skye_with_spike.png")
  ts_sova = cv2.imread(agentsdir + "sova_with_spike.png")
  ts_viper = cv2.imread(agentsdir + "viper_with_spike.png")
  ts_yoru = cv2.imread(agentsdir + "yoru_with_spike.png")

  til_astra = cv2.imread(agentsdir + "astra_init_left.png")
  til_breach = cv2.imread(agentsdir + "breach_init_left.png")
  til_brimstone = cv2.imread(agentsdir + "brimstone_init_left.png")
  til_cypher = cv2.imread(agentsdir + "cypher_init_left.png")
  til_jett = cv2.imread(agentsdir + "jett_init_left.png")
  til_kayo = cv2.imread(agentsdir + "kayo_init_left.png")
  til_killjoy = cv2.imread(agentsdir + "killjoy_init_left.png")
  til_omen = cv2.imread(agentsdir + "omen_init_left.png")
  til_phoenix = cv2.imread(agentsdir + "phoenix_init_left.png")
  til_raze = cv2.imread(agentsdir + "raze_init_left.png")
  til_reyna = cv2.imread(agentsdir + "reyna_init_left.png")
  til_sage = cv2.imread(agentsdir + "sage_init_left.png")
  til_skye = cv2.imread(agentsdir + "skye_init_left.png")
  til_sova = cv2.imread(agentsdir + "sova_init_left.png")
  til_viper = cv2.imread(agentsdir + "viper_init_left.png")
  til_yoru = cv2.imread(agentsdir + "yoru_init_left.png")

  tir_astra = cv2.imread(agentsdir + "astra_init_right.png")
  tir_breach = cv2.imread(agentsdir + "breach_init_right.png")
  tir_brimstone = cv2.imread(agentsdir + "brimstone_init_right.png")
  tir_cypher = cv2.imread(agentsdir + "cypher_init_right.png")
  tir_jett = cv2.imread(agentsdir + "jett_init_right.png")
  tir_kayo = cv2.imread(agentsdir + "kayo_init_right.png")
  tir_killjoy = cv2.imread(agentsdir + "killjoy_init_right.png")
  tir_omen = cv2.imread(agentsdir + "omen_init_right.png")
  tir_phoenix = cv2.imread(agentsdir + "phoenix_init_right.png")
  tir_raze = cv2.imread(agentsdir + "raze_init_right.png")
  tir_reyna = cv2.imread(agentsdir + "reyna_init_right.png")
  tir_sage = cv2.imread(agentsdir + "sage_init_right.png")
  tir_skye = cv2.imread(agentsdir + "skye_init_right.png")
  tir_sova = cv2.imread(agentsdir + "sova_init_right.png")
  tir_viper = cv2.imread(agentsdir + "viper_init_right.png")
  tir_yoru = cv2.imread(agentsdir + "yoru_init_right.png")

  privtil_astra = cv2.imread(agentsdir + "astra_priv_init_left.png")
  privtil_breach = cv2.imread(agentsdir + "breach_priv_init_left.png")
  privtil_brimstone = cv2.imread(agentsdir + "brimstone_priv_init_left.png")
  privtil_cypher = cv2.imread(agentsdir + "cypher_priv_init_left.png")
  privtil_jett = cv2.imread(agentsdir + "jett_priv_init_left.png")
  privtil_kayo = cv2.imread(agentsdir + "kayo_priv_init_left.png")
  privtil_killjoy = cv2.imread(agentsdir + "killjoy_priv_init_left.png")
  privtil_omen = cv2.imread(agentsdir + "omen_priv_init_left.png")
  privtil_phoenix = cv2.imread(agentsdir + "phoenix_priv_init_left.png")
  privtil_raze = cv2.imread(agentsdir + "raze_priv_init_left.png")
  privtil_reyna = cv2.imread(agentsdir + "reyna_priv_init_left.png")
  privtil_sage = cv2.imread(agentsdir + "sage_priv_init_left.png")
  privtil_skye = cv2.imread(agentsdir + "skye_priv_init_left.png")
  privtil_sova = cv2.imread(agentsdir + "sova_priv_init_left.png")
  privtil_viper = cv2.imread(agentsdir + "viper_priv_init_left.png")
  privtil_yoru = cv2.imread(agentsdir + "yoru_priv_init_left.png")

  privtir_astra = cv2.imread(agentsdir + "astra_priv_init_right.png")
  privtir_breach = cv2.imread(agentsdir + "breach_priv_init_right.png")
  privtir_brimstone = cv2.imread(agentsdir + "brimstone_priv_init_right.png")
  privtir_cypher = cv2.imread(agentsdir + "cypher_priv_init_right.png")
  privtir_jett = cv2.imread(agentsdir + "jett_priv_init_right.png")
  privtir_kayo = cv2.imread(agentsdir + "kayo_priv_init_right.png")
  privtir_killjoy = cv2.imread(agentsdir + "killjoy_priv_init_right.png")
  privtir_omen = cv2.imread(agentsdir + "omen_priv_init_right.png")
  privtir_phoenix = cv2.imread(agentsdir + "phoenix_priv_init_right.png")
  privtir_raze = cv2.imread(agentsdir + "raze_priv_init_right.png")
  privtir_reyna = cv2.imread(agentsdir + "reyna_priv_init_right.png")
  privtir_sage = cv2.imread(agentsdir + "sage_priv_init_right.png")
  privtir_skye = cv2.imread(agentsdir + "skye_priv_init_right.png")
  privtir_sova = cv2.imread(agentsdir + "sova_priv_init_right.png")
  privtir_viper = cv2.imread(agentsdir + "viper_priv_init_right.png")
  privtir_yoru = cv2.imread(agentsdir + "yoru_priv_init_right.png")

  flg_astra = cv2.imread(agentsdir + "astra_left_green.png")
  flg_breach = cv2.imread(agentsdir + "breach_left_green.png")
  flg_brimstone = cv2.imread(agentsdir + "brimstone_left_green.png")
  flg_cypher = cv2.imread(agentsdir + "cypher_left_green.png")
  flg_jett = cv2.imread(agentsdir + "jett_left_green.png")
  flg_kayo = cv2.imread(agentsdir + "kayo_left_green.png")
  flg_killjoy = cv2.imread(agentsdir + "killjoy_left_green.png")
  flg_omen = cv2.imread(agentsdir + "omen_left_green.png")
  flg_phoenix = cv2.imread(agentsdir + "phoenix_left_green.png")
  flg_raze = cv2.imread(agentsdir + "raze_left_green.png")
  flg_reyna = cv2.imread(agentsdir + "reyna_left_green.png")
  flg_sage = cv2.imread(agentsdir + "sage_left_green.png")
  flg_skye = cv2.imread(agentsdir + "skye_left_green.png")
  flg_sova = cv2.imread(agentsdir + "sova_left_green.png")
  flg_viper = cv2.imread(agentsdir + "viper_left_green.png")
  flg_yoru = cv2.imread(agentsdir + "yoru_left_green.png")

  flr_astra = cv2.imread(agentsdir + "astra_left_red.png")
  flr_breach = cv2.imread(agentsdir + "breach_left_red.png")
  flr_brimstone = cv2.imread(agentsdir + "brimstone_left_red.png")
  flr_cypher = cv2.imread(agentsdir + "cypher_left_red.png")
  flr_jett = cv2.imread(agentsdir + "jett_left_red.png")
  flr_kayo = cv2.imread(agentsdir + "kayo_left_red.png")
  flr_killjoy = cv2.imread(agentsdir + "killjoy_left_red.png")
  flr_omen = cv2.imread(agentsdir + "omen_left_red.png")
  flr_phoenix = cv2.imread(agentsdir + "phoenix_left_red.png")
  flr_raze = cv2.imread(agentsdir + "raze_left_red.png")
  flr_reyna = cv2.imread(agentsdir + "reyna_left_red.png")
  flr_sage = cv2.imread(agentsdir + "sage_left_red.png")
  flr_skye = cv2.imread(agentsdir + "skye_left_red.png")
  flr_sova = cv2.imread(agentsdir + "sova_left_red.png")
  flr_viper = cv2.imread(agentsdir + "viper_left_red.png")
  flr_yoru = cv2.imread(agentsdir + "yoru_left_red.png")

  frg_astra = cv2.imread(agentsdir + "astra_right_green.png")
  frg_breach = cv2.imread(agentsdir + "breach_right_green.png")
  frg_brimstone = cv2.imread(agentsdir + "brimstone_right_green.png")
  frg_cypher = cv2.imread(agentsdir + "cypher_right_green.png")
  frg_jett = cv2.imread(agentsdir + "jett_right_green.png")
  frg_kayo = cv2.imread(agentsdir + "kayo_right_green.png")
  frg_killjoy = cv2.imread(agentsdir + "killjoy_right_green.png")
  frg_omen = cv2.imread(agentsdir + "omen_right_green.png")
  frg_phoenix = cv2.imread(agentsdir + "phoenix_right_green.png")
  frg_raze = cv2.imread(agentsdir + "raze_right_green.png")
  frg_reyna = cv2.imread(agentsdir + "reyna_right_green.png")
  frg_sage = cv2.imread(agentsdir + "sage_right_green.png")
  frg_skye = cv2.imread(agentsdir + "skye_right_green.png")
  frg_sova = cv2.imread(agentsdir + "sova_right_green.png")
  frg_viper = cv2.imread(agentsdir + "viper_right_green.png")
  frg_yoru = cv2.imread(agentsdir + "yoru_right_green.png")

  frr_astra = cv2.imread(agentsdir + "astra_right_red.png")
  frr_breach = cv2.imread(agentsdir + "breach_right_red.png")
  frr_brimstone = cv2.imread(agentsdir + "brimstone_right_red.png")
  frr_cypher = cv2.imread(agentsdir + "cypher_right_red.png")
  frr_jett = cv2.imread(agentsdir + "jett_right_red.png")
  frr_kayo = cv2.imread(agentsdir + "kayo_right_red.png")
  frr_killjoy = cv2.imread(agentsdir + "killjoy_right_red.png")
  frr_omen = cv2.imread(agentsdir + "omen_right_red.png")
  frr_phoenix = cv2.imread(agentsdir + "phoenix_right_red.png")
  frr_raze = cv2.imread(agentsdir + "raze_right_red.png")
  frr_reyna = cv2.imread(agentsdir + "reyna_right_red.png")
  frr_sage = cv2.imread(agentsdir + "sage_right_red.png")
  frr_skye = cv2.imread(agentsdir + "skye_right_red.png")
  frr_sova = cv2.imread(agentsdir + "sova_right_red.png")
  frr_viper = cv2.imread(agentsdir + "viper_right_red.png")
  frr_yoru = cv2.imread(agentsdir + "yoru_right_red.png")

  fa_astra = cv2.imread(agentsdir + "astra_feed_assist.png")
  fa_breach = cv2.imread(agentsdir + "breach_feed_assist.png")
  fa_brimstone = cv2.imread(agentsdir + "brimstone_feed_assist.png")
  fa_cypher = cv2.imread(agentsdir + "cypher_feed_assist.png")
  fa_jett = cv2.imread(agentsdir + "jett_feed_assist.png")
  fa_kayo = cv2.imread(agentsdir + "kayo_feed_assist.png")
  fa_killjoy = cv2.imread(agentsdir + "killjoy_feed_assist.png")
  fa_omen = cv2.imread(agentsdir + "omen_feed_assist.png")
  fa_phoenix = cv2.imread(agentsdir + "phoenix_feed_assist.png")
  fa_raze = cv2.imread(agentsdir + "raze_feed_assist.png")
  fa_reyna = cv2.imread(agentsdir + "reyna_feed_assist.png")
  fa_sage = cv2.imread(agentsdir + "sage_feed_assist.png")
  fa_skye = cv2.imread(agentsdir + "skye_feed_assist.png")
  fa_sova = cv2.imread(agentsdir + "sova_feed_assist.png")
  fa_viper = cv2.imread(agentsdir + "viper_feed_assist.png")
  fa_yoru = cv2.imread(agentsdir + "yoru_feed_assist.png")

  tgu_astra = cv2.imread(ultsdir + "astra_ult_green.png")
  tgu_breach = cv2.imread(ultsdir + "breach_ult_green.png")
  tgu_brimstone = cv2.imread(ultsdir + "brimstone_ult_green.png")
  tgu_cypher = cv2.imread(ultsdir + "cypher_ult_green.png")
  tgu_jett = cv2.imread(ultsdir + "jett_ult_green.png")
  tgu_kayo = cv2.imread(ultsdir + "kayo_ult_green.png")
  tgu_killjoy = cv2.imread(ultsdir + "killjoy_ult_green.png")
  tgu_omen = cv2.imread(ultsdir + "omen_ult_green.png")
  tgu_phoenix = cv2.imread(ultsdir + "phoenix_ult_green.png")
  tgu_raze = cv2.imread(ultsdir + "raze_ult_green.png")
  tgu_reyna = cv2.imread(ultsdir + "reyna_ult_green.png")
  tgu_sage = cv2.imread(ultsdir + "sage_ult_green.png")
  tgu_skye = cv2.imread(ultsdir + "skye_ult_green.png")
  tgu_sova = cv2.imread(ultsdir + "sova_ult_green.png")
  tgu_viper = cv2.imread(ultsdir + "viper_ult_green.png")
  tgu_yoru = cv2.imread(ultsdir + "yoru_ult_green.png")

  tru_astra = cv2.imread(ultsdir + "astra_ult_red.png")
  tru_breach = cv2.imread(ultsdir + "breach_ult_red.png")
  tru_brimstone = cv2.imread(ultsdir + "brimstone_ult_red.png")
  tru_cypher = cv2.imread(ultsdir + "cypher_ult_red.png")
  tru_jett = cv2.imread(ultsdir + "jett_ult_red.png")
  tru_kayo = cv2.imread(ultsdir + "kayo_ult_red.png")
  tru_killjoy = cv2.imread(ultsdir + "killjoy_ult_red.png")
  tru_omen = cv2.imread(ultsdir + "omen_ult_red.png")
  tru_phoenix = cv2.imread(ultsdir + "phoenix_ult_red.png")
  tru_raze = cv2.imread(ultsdir + "raze_ult_red.png")
  tru_reyna = cv2.imread(ultsdir + "reyna_ult_red.png")
  tru_sage = cv2.imread(ultsdir + "sage_ult_red.png")
  tru_skye = cv2.imread(ultsdir + "skye_ult_red.png")
  tru_sova = cv2.imread(ultsdir + "sova_ult_red.png")
  tru_viper = cv2.imread(ultsdir + "viper_ult_red.png")
  tru_yoru = cv2.imread(ultsdir + "yoru_ult_red.png")

  ult_red_0_6 = cv2.imread(ultsdir + "ult_0_6.png")
  ult_red_0_7 = cv2.imread(ultsdir + "ult_0_7.png")
  ult_red_0_8 = cv2.imread(ultsdir + "ult_0_8.png")
  ult_red_1_6 = cv2.imread(ultsdir + "ult_red_1_6.png")
  ult_red_1_7 = cv2.imread(ultsdir + "ult_red_1_7.png")
  ult_red_1_8 = cv2.imread(ultsdir + "ult_red_1_8.png")
  ult_red_2_6 = cv2.imread(ultsdir + "ult_red_2_6.png")
  ult_red_2_7 = cv2.imread(ultsdir + "ult_red_2_7.png")
  ult_red_2_8 = cv2.imread(ultsdir + "ult_red_2_8.png")
  ult_red_3_6 = cv2.imread(ultsdir + "ult_red_3_6.png")
  ult_red_3_7 = cv2.imread(ultsdir + "ult_red_3_7.png")
  ult_red_3_8 = cv2.imread(ultsdir + "ult_red_3_8.png")
  ult_red_4_6 = cv2.imread(ultsdir + "ult_red_4_6.png")
  ult_red_4_7 = cv2.imread(ultsdir + "ult_red_4_7.png")
  ult_red_4_8 = cv2.imread(ultsdir + "ult_red_4_8.png")
  ult_red_5_6 = cv2.imread(ultsdir + "ult_red_5_6.png")
  ult_red_5_7 = cv2.imread(ultsdir + "ult_red_5_7.png")
  ult_red_5_8 = cv2.imread(ultsdir + "ult_red_5_8.png")
  ult_red_6_7 = cv2.imread(ultsdir + "ult_red_6_7.png")
  ult_red_6_8 = cv2.imread(ultsdir + "ult_red_6_8.png")
  ult_red_7_8 = cv2.imread(ultsdir + "ult_red_7_8.png")

  ult_green_0_6 = cv2.imread(ultsdir + "ult_0_6.png")
  ult_green_0_7 = cv2.imread(ultsdir + "ult_0_7.png")
  ult_green_0_8 = cv2.imread(ultsdir + "ult_0_8.png")
  ult_green_1_6 = cv2.imread(ultsdir + "ult_green_1_6.png")
  ult_green_1_7 = cv2.imread(ultsdir + "ult_green_1_7.png")
  ult_green_1_8 = cv2.imread(ultsdir + "ult_green_1_8.png")
  ult_green_2_6 = cv2.imread(ultsdir + "ult_green_2_6.png")
  ult_green_2_7 = cv2.imread(ultsdir + "ult_green_2_7.png")
  ult_green_2_8 = cv2.imread(ultsdir + "ult_green_2_8.png")
  ult_green_3_6 = cv2.imread(ultsdir + "ult_green_3_6.png")
  ult_green_3_7 = cv2.imread(ultsdir + "ult_green_3_7.png")
  ult_green_3_8 = cv2.imread(ultsdir + "ult_green_3_8.png")
  ult_green_4_6 = cv2.imread(ultsdir + "ult_green_4_6.png")
  ult_green_4_7 = cv2.imread(ultsdir + "ult_green_4_7.png")
  ult_green_4_8 = cv2.imread(ultsdir + "ult_green_4_8.png")
  ult_green_5_6 = cv2.imread(ultsdir + "ult_green_5_6.png")
  ult_green_5_7 = cv2.imread(ultsdir + "ult_green_5_7.png")
  ult_green_5_8 = cv2.imread(ultsdir + "ult_green_5_8.png")
  ult_green_6_7 = cv2.imread(ultsdir + "ult_green_6_7.png")
  ult_green_6_8 = cv2.imread(ultsdir + "ult_green_6_8.png")
  ult_green_7_8 = cv2.imread(ultsdir + "ult_green_7_8.png")

  abil_0 = cv2.imread(abilsdir + "abil_0.png")
  abil_1 = cv2.imread(abilsdir + "abil_1.png")
  abil_2 = cv2.imread(abilsdir + "abil_2.png")
  abil_3 = cv2.imread(abilsdir + "abil_3.png")

  astra_abil_verif = cv2.imread(abilsdir + "astra_abil_verif.png")
  astra_abil_1 = cv2.imread(abilsdir + "astra_abil_1.png")
  astra_abil_2 = cv2.imread(abilsdir + "astra_abil_2.png")
  astra_abil_3 = cv2.imread(abilsdir + "astra_abil_3.png")
  astra_abil_4 = cv2.imread(abilsdir + "astra_abil_4.png")
  astra_abil_5 = cv2.imread(abilsdir + "astra_abil_5.png")
  astra_star_green = cv2.imread(iconsdir + "astra_star_green.png")
  astra_star_red = cv2.imread(iconsdir + "astra_star_red.png")

  a_site = cv2.imread(iconsdir + "a.png")
  b_site = cv2.imread(iconsdir + "b.png")
  b_site_2 = cv2.imread(iconsdir + "b_2.png")
  c_site = cv2.imread(iconsdir + "c.png")

  spike = cv2.imread(iconsdir + "spike.png")
  spike_held = cv2.imread(iconsdir + "spike_held.png")
  spike_planting = cv2.imread(iconsdir + "spike_planting.png")
  spike_planted = cv2.imread(iconsdir + "spike_planted.png")
  spike_planted_text = cv2.imread(iconsdir + "spike_planted_text.png")
  spike_defusing = cv2.imread(iconsdir + "spike_defusing.png")
  spike_carrier_down = cv2.imread(iconsdir + "spike_carrier_down.png")
  spike_planter_down = cv2.imread(iconsdir + "spike_planter_down.png")

  spike_planted_op_pub = cv2.imread(iconsdir + "spike_planted_op_pub.png")
  spike_planted_op_priv = cv2.imread(iconsdir + "spike_planted_op_priv.png")

  side_atk_left = cv2.imread(iconsdir + "side_left.png")
  side_atk_right = cv2.imread(iconsdir + "side_right.png")

  round_start_pub = cv2.imread(iconsdir + "round_start_pub.png")
  round_start_priv = cv2.imread(iconsdir + "round_start_priv.png")
  round_start2_pub = cv2.imread(iconsdir + "round_start2_pub.png")
  round_start2_priv = cv2.imread(iconsdir + "round_start2_priv.png")
  round_start3_pub = cv2.imread(iconsdir + "round_start3_pub.png")
  round_start3_priv = cv2.imread(iconsdir + "round_start3_priv.png")
  round_midgame_pub = cv2.imread(iconsdir + "round_midgame_pub.png")
  round_midgame_priv = cv2.imread(iconsdir + "round_midgame_priv.png")
  round_endgame_pub = cv2.imread(iconsdir + "round_endgame_pub.png")
  round_endgame_priv = cv2.imread(iconsdir + "round_endgame_priv.png")

  classic_left = cv2.imread(weapsdir + "classic_left.png")
  frenzy_left = cv2.imread(weapsdir + "frenzy_left.png")
  ghost_left = cv2.imread(weapsdir + "ghost_left.png")
  sheriff_left = cv2.imread(weapsdir + "sheriff_left.png")
  shorty_left = cv2.imread(weapsdir + "shorty_left.png")
  bucky_left = cv2.imread(weapsdir + "bucky_left_temp.png") # TODO find bucky left overlay image
  marshal_left = cv2.imread(weapsdir + "marshal_left.png")
  stinger_left = cv2.imread(weapsdir + "stinger_left.png")
  spectre_left = cv2.imread(weapsdir + "spectre_left.png")
  bulldog_left = cv2.imread(weapsdir + "bulldog_left.png")
  judge_left = cv2.imread(weapsdir + "judge_left.png")
  guardian_left = cv2.imread(weapsdir + "guardian_left.png")
  vandal_left = cv2.imread(weapsdir + "vandal_left.png")
  phantom_left = cv2.imread(weapsdir + "phantom_left.png")
  operator_left = cv2.imread(weapsdir + "operator_left.png")
  ares_left = cv2.imread(weapsdir + "ares_left.png")
  odin_left = cv2.imread(weapsdir + "odin_left.png")

  classic_right = cv2.imread(weapsdir + "classic_right.png")
  frenzy_right = cv2.imread(weapsdir + "frenzy_right.png")
  ghost_right = cv2.imread(weapsdir + "ghost_right.png")
  sheriff_right = cv2.imread(weapsdir + "sheriff_right.png")
  shorty_right = cv2.imread(weapsdir + "shorty_right.png")
  bucky_right = cv2.imread(weapsdir + "bucky_right.png")
  marshal_right = cv2.imread(weapsdir + "marshal_right.png")
  stinger_right = cv2.imread(weapsdir + "stinger_right.png")
  spectre_right = cv2.imread(weapsdir + "spectre_right.png")
  bulldog_right = cv2.imread(weapsdir + "bulldog_right.png")
  judge_right = cv2.imread(weapsdir + "judge_right.png")
  guardian_right = cv2.imread(weapsdir + "guardian_right.png")
  vandal_right = cv2.imread(weapsdir + "vandal_right.png")
  phantom_right = cv2.imread(weapsdir + "phantom_right.png")
  operator_right = cv2.imread(weapsdir + "operator_right.png")
  ares_right = cv2.imread(weapsdir + "ares_right.png")
  odin_right = cv2.imread(weapsdir + "odin_right.png")

  classic_green = cv2.imread(weapsdir + "green_classic.png")
  frenzy_green = cv2.imread(weapsdir + "green_frenzy.png")
  ghost_green = cv2.imread(weapsdir + "green_ghost.png")
  sheriff_green = cv2.imread(weapsdir + "green_sheriff.png")
  shorty_green = cv2.imread(weapsdir + "green_shorty.png")
  bucky_green = cv2.imread(weapsdir + "green_bucky.png")
  marshal_green = cv2.imread(weapsdir + "green_marshal.png")
  stinger_green = cv2.imread(weapsdir + "green_stinger.png")
  spectre_green = cv2.imread(weapsdir + "green_spectre.png")
  bulldog_green = cv2.imread(weapsdir + "green_bulldog.png")
  judge_green = cv2.imread(weapsdir + "green_judge.png")
  guardian_green = cv2.imread(weapsdir + "green_guardian.png")
  vandal_green = cv2.imread(weapsdir + "green_vandal.png")
  phantom_green = cv2.imread(weapsdir + "green_phantom.png")
  operator_green = cv2.imread(weapsdir + "green_operator.png")
  ares_green = cv2.imread(weapsdir + "green_ares.png")
  odin_green = cv2.imread(weapsdir + "green_odin.png")

  classic_red = cv2.imread(weapsdir + "red_classic.png")
  frenzy_red = cv2.imread(weapsdir + "red_frenzy.png")
  ghost_red = cv2.imread(weapsdir + "red_ghost.png")
  sheriff_red = cv2.imread(weapsdir + "red_sheriff.png")
  shorty_red = cv2.imread(weapsdir + "red_shorty.png")
  bucky_red = cv2.imread(weapsdir + "red_bucky.png")
  marshal_red = cv2.imread(weapsdir + "red_marshal.png")
  stinger_red = cv2.imread(weapsdir + "red_stinger.png")
  spectre_red = cv2.imread(weapsdir + "red_spectre.png")
  bulldog_red = cv2.imread(weapsdir + "red_bulldog.png")
  judge_red = cv2.imread(weapsdir + "red_judge.png")
  guardian_red = cv2.imread(weapsdir + "red_guardian.png")
  vandal_red = cv2.imread(weapsdir + "red_vandal.png")
  phantom_red = cv2.imread(weapsdir + "red_phantom.png")
  operator_red = cv2.imread(weapsdir + "red_operator.png")
  ares_red = cv2.imread(weapsdir + "red_ares.png")
  odin_red = cv2.imread(weapsdir + "red_odin.png")

  green_aftershock = cv2.imread(abilsdir + "green_aftershock.png")
  green_blade_storm = cv2.imread(abilsdir + "green_blade_storm.png")
  green_blast_pack = cv2.imread(abilsdir + "green_blast_pack.png")
  green_blaze = cv2.imread(abilsdir + "green_blaze.png")
  green_boom_bot = cv2.imread(abilsdir + "green_boom_bot.png")
  green_fragment = cv2.imread(abilsdir + "green_fragment.png")
  green_hot_hands = cv2.imread(abilsdir + "green_hot_hands.png")
  green_hunters_fury = cv2.imread(abilsdir + "green_hunters_fury.png")
  green_incendiary = cv2.imread(abilsdir + "green_incendiary.png")
  green_nanoswarm = cv2.imread(abilsdir + "green_nanoswarm.png")
  green_nullcmd = cv2.imread(abilsdir + "green_nullcmd.png")
  green_nullcmd_res = cv2.imread(abilsdir + "green_nullcmd_res.png")
  green_orbital_strike = cv2.imread(abilsdir + "green_orbital_strike.png")
  green_paint_shells = cv2.imread(abilsdir + "green_paint_shells.png")
  green_resurrection = cv2.imread(abilsdir + "green_resurrection.png")
  green_run_it_back = cv2.imread(abilsdir + "green_run_it_back.png")
  green_shock_bolt = cv2.imread(abilsdir + "green_shock_bolt.png")
  green_showstopper = cv2.imread(abilsdir + "green_showstopper.png")
  green_snake_bite = cv2.imread(abilsdir + "green_snake_bite.png")
  green_trailblazer = cv2.imread(abilsdir + "green_trailblazer.png")
  green_trapwire = cv2.imread(abilsdir + "green_trapwire.png")
  green_turret = cv2.imread(abilsdir + "green_turret.png")

  red_aftershock = cv2.imread(abilsdir + "red_aftershock.png")
  red_blade_storm = cv2.imread(abilsdir + "red_blade_storm.png")
  red_blast_pack = cv2.imread(abilsdir + "red_blast_pack.png")
  red_blaze = cv2.imread(abilsdir + "red_blaze.png")
  red_boom_bot = cv2.imread(abilsdir + "red_boom_bot.png")
  red_fragment = cv2.imread(abilsdir + "red_fragment.png")
  red_hot_hands = cv2.imread(abilsdir + "red_hot_hands.png")
  red_hunters_fury = cv2.imread(abilsdir + "red_hunters_fury.png")
  red_incendiary = cv2.imread(abilsdir + "red_incendiary.png")
  red_nanoswarm = cv2.imread(abilsdir + "red_nanoswarm.png")
  red_nullcmd = cv2.imread(abilsdir + "red_nullcmd.png")
  red_nullcmd_res = cv2.imread(abilsdir + "red_nullcmd_res.png")
  red_orbital_strike = cv2.imread(abilsdir + "red_orbital_strike.png")
  red_paint_shells = cv2.imread(abilsdir + "red_paint_shells.png")
  red_resurrection = cv2.imread(abilsdir + "red_resurrection.png")
  red_run_it_back = cv2.imread(abilsdir + "red_run_it_back.png")
  red_shock_bolt = cv2.imread(abilsdir + "red_shock_bolt.png")
  red_showstopper = cv2.imread(abilsdir + "red_showstopper.png")
  red_snake_bite = cv2.imread(abilsdir + "red_snake_bite.png")
  red_trailblazer = cv2.imread(abilsdir + "red_trailblazer.png")
  red_trapwire = cv2.imread(abilsdir + "red_trapwire.png")
  red_turret = cv2.imread(abilsdir + "red_turret.png")

  headshot_green = cv2.imread(iconsdir + "green_headshot.png")
  spike_det_green = cv2.imread(iconsdir + "green_spike_det.png")
  wallbang_green = cv2.imread(iconsdir + "green_wallbang.png")

  headshot_red = cv2.imread(iconsdir + "red_headshot.png")
  spike_det_red = cv2.imread(iconsdir + "red_spike_det.png")
  wallbang_red = cv2.imread(iconsdir + "red_wallbang.png")

  health_green_0 = cv2.imread(scoresdir + "green_0.png")
  health_green_1 = cv2.imread(scoresdir + "green_1.png")
  health_green_2 = cv2.imread(scoresdir + "green_2.png")
  health_green_3 = cv2.imread(scoresdir + "green_3.png")
  health_green_4 = cv2.imread(scoresdir + "green_4.png")
  health_green_5 = cv2.imread(scoresdir + "green_5.png")
  health_green_6 = cv2.imread(scoresdir + "green_6.png")
  health_green_7 = cv2.imread(scoresdir + "green_7.png")
  health_green_8 = cv2.imread(scoresdir + "green_8.png")
  health_green_9 = cv2.imread(scoresdir + "green_9.png")
  health_green_25 = cv2.imread(scoresdir + "green_25.png")
  health_green_50 = cv2.imread(scoresdir + "green_50.png")

  health_red_0 = cv2.imread(scoresdir + "red_0.png")
  health_red_1 = cv2.imread(scoresdir + "red_1.png")
  health_red_2 = cv2.imread(scoresdir + "red_2.png")
  health_red_3 = cv2.imread(scoresdir + "red_3.png")
  health_red_4 = cv2.imread(scoresdir + "red_4.png")
  health_red_5 = cv2.imread(scoresdir + "red_5.png")
  health_red_6 = cv2.imread(scoresdir + "red_6.png")
  health_red_7 = cv2.imread(scoresdir + "red_7.png")
  health_red_8 = cv2.imread(scoresdir + "red_8.png")
  health_red_9 = cv2.imread(scoresdir + "red_9.png")
  health_red_25 = cv2.imread(scoresdir + "red_25.png")
  health_red_50 = cv2.imread(scoresdir + "red_50.png")

  health_blue_0 = cv2.imread(scoresdir + "blue_0.png")
  health_blue_1 = cv2.imread(scoresdir + "blue_1.png")
  health_blue_2 = cv2.imread(scoresdir + "blue_2.png")
  health_blue_3 = cv2.imread(scoresdir + "blue_3.png")
  health_blue_4 = cv2.imread(scoresdir + "blue_4.png")
  health_blue_5 = cv2.imread(scoresdir + "blue_5.png")
  health_blue_6 = cv2.imread(scoresdir + "blue_6.png")
  health_blue_7 = cv2.imread(scoresdir + "blue_7.png")
  health_blue_8 = cv2.imread(scoresdir + "blue_8.png")
  health_blue_9 = cv2.imread(scoresdir + "blue_9.png")
  health_blue_25 = cv2.imread(scoresdir + "blue_25.png")
  health_blue_50 = cv2.imread(scoresdir + "blue_50.png")

  score_0_pub = cv2.imread(scoresdir + "score_0_pub.png")
  score_1_pub = cv2.imread(scoresdir + "score_1_pub.png")
  score_2_pub = cv2.imread(scoresdir + "score_2_pub.png")
  score_3_pub = cv2.imread(scoresdir + "score_3_pub.png")
  score_4_pub = cv2.imread(scoresdir + "score_4_pub.png")
  score_5_pub = cv2.imread(scoresdir + "score_5_pub.png")
  score_6_pub = cv2.imread(scoresdir + "score_6_pub.png")
  score_7_pub = cv2.imread(scoresdir + "score_7_pub.png")
  score_8_pub = cv2.imread(scoresdir + "score_8_pub.png")
  score_9_pub = cv2.imread(scoresdir + "score_9_pub.png")
  score_10_pub = cv2.imread(scoresdir + "score_10_pub.png")
  score_11_pub = cv2.imread(scoresdir + "score_11_pub.png")
  score_12_pub = cv2.imread(scoresdir + "score_12_pub.png")
  score_13_pub = cv2.imread(scoresdir + "score_13_pub.png")
  score_14_pub = cv2.imread(scoresdir + "score_14_pub.png")
  score_15_pub = cv2.imread(scoresdir + "score_15_pub.png")
  score_16_pub = cv2.imread(scoresdir + "score_16_pub.png")
  score_17_pub = cv2.imread(scoresdir + "score_17_pub.png")
  score_18_pub = cv2.imread(scoresdir + "score_18_pub.png")
  score_19_pub = cv2.imread(scoresdir + "score_19_pub.png")
  score_20_pub = cv2.imread(scoresdir + "score_20_pub.png")

  score_0_priv = cv2.imread(scoresdir + "score_0_priv.png")
  score_1_priv = cv2.imread(scoresdir + "score_1_priv.png")
  score_2_priv = cv2.imread(scoresdir + "score_2_priv.png")
  score_3_priv = cv2.imread(scoresdir + "score_3_priv.png")
  score_4_priv = cv2.imread(scoresdir + "score_4_priv.png")
  score_5_priv = cv2.imread(scoresdir + "score_5_priv.png")
  score_6_priv = cv2.imread(scoresdir + "score_6_priv.png")
  score_7_priv = cv2.imread(scoresdir + "score_7_priv.png")
  score_8_priv = cv2.imread(scoresdir + "score_8_priv.png")
  score_9_priv = cv2.imread(scoresdir + "score_9_priv.png")
  score_10_priv = cv2.imread(scoresdir + "score_10_priv.png")
  score_11_priv = cv2.imread(scoresdir + "score_11_priv.png")
  score_12_priv = cv2.imread(scoresdir + "score_12_priv.png")
  score_13_priv = cv2.imread(scoresdir + "score_13_priv.png")
  score_14_priv = cv2.imread(scoresdir + "score_14_priv.png")
  score_15_priv = cv2.imread(scoresdir + "score_15_priv.png")
  score_16_priv = cv2.imread(scoresdir + "score_16_priv.png")
  score_17_priv = cv2.imread(scoresdir + "score_17_priv.png")
  score_18_priv = cv2.imread(scoresdir + "score_18_priv.png")
  score_19_priv = cv2.imread(scoresdir + "score_19_priv.png")
  score_20_priv = cv2.imread(scoresdir + "score_20_priv.png")

  minimap_templates = [
    ("A_SITE", a_site), ("B_SITE", b_site), ("B_SITE", b_site_2), ("C_SITE", c_site), ("SPIKE", spike), 
    ("ASTRA_STAR_GREEN", astra_star_green), ("ASTRA_STAR_RED", astra_star_red), 

    ("ASTRA", t_astra), ("BREACH", t_breach), ("BRIMSTONE", t_brimstone), 
    ("CYPHER", t_cypher), 
    ("JETT", t_jett), ("KAYO", t_kayo), ("KILLJOY", t_killjoy), ("OMEN", t_omen), 
    ("PHOENIX", t_phoenix), ("RAZE", t_raze), ("REYNA", t_reyna), ("SAGE", t_sage), 
    ("SKYE", t_skye), ("SOVA", t_sova), ("VIPER", t_viper), ("YORU", t_yoru), 

    ("ASTRA_WITH_SPIKE", ts_astra), ("BREACH_WITH_SPIKE", ts_breach), ("BRIMSTONE_WITH_SPIKE", ts_brimstone), 
    ("CYPHER_WITH_SPIKE", ts_cypher), ("JETT_WITH_SPIKE", ts_jett), ("KAYO_WITH_SPIKE", ts_kayo), ("KILLJOY_WITH_SPIKE", ts_killjoy), 
    ("OMEN_WITH_SPIKE", ts_omen), ("PHOENIX_WITH_SPIKE", ts_phoenix), ("RAZE_WITH_SPIKE", ts_raze), ("REYNA_WITH_SPIKE", ts_reyna), 
    ("SAGE_WITH_SPIKE", ts_sage), ("SKYE_WITH_SPIKE", ts_skye), ("SOVA_WITH_SPIKE", ts_sova), ("VIPER_WITH_SPIKE", ts_viper), 
    ("YORU_WITH_SPIKE", ts_yoru), 


    # ("TEST", test)
    ]

  op_templates_pub_mid = [
    ("ROUND_START", round_start_pub), ("ROUND_START", round_start2_pub), ("ROUND_START", round_start3_pub), 
    ("ROUND_MIDGAME", round_midgame_pub), ("ROUND_ENDGAME", round_endgame_pub), 
    ]

  op_templates_pub_left = [
    ("SCORE_LEFT_0", score_0_pub), ("SCORE_LEFT_1", score_1_pub), ("SCORE_LEFT_2", score_2_pub), ("SCORE_LEFT_3", score_3_pub), ("SCORE_LEFT_4", score_4_pub), 
    ("SCORE_LEFT_5", score_5_pub), ("SCORE_LEFT_6", score_6_pub), ("SCORE_LEFT_7", score_7_pub), ("SCORE_LEFT_8", score_8_pub), ("SCORE_LEFT_9", score_9_pub), 
    ("SCORE_LEFT_10", score_10_pub), ("SCORE_LEFT_11", score_11_pub), ("SCORE_LEFT_12", score_12_pub), ("SCORE_LEFT_13", score_13_pub), 
    ("SCORE_LEFT_14", score_14_pub), ("SCORE_LEFT_15", score_15_pub), ("SCORE_LEFT_16", score_16_pub), ("SCORE_LEFT_17", score_17_pub), 
    ("SCORE_LEFT_18", score_18_pub), ("SCORE_LEFT_19", score_19_pub), ("SCORE_LEFT_20", score_20_pub), 
    ]

  op_templates_pub_right = [
    ("SCORE_RIGHT_0", score_0_pub), ("SCORE_RIGHT_1", score_1_pub), ("SCORE_RIGHT_2", score_2_pub), ("SCORE_RIGHT_3", score_3_pub), ("SCORE_RIGHT_4", score_4_pub),
    ("SCORE_RIGHT_5", score_5_pub), ("SCORE_RIGHT_6", score_6_pub), ("SCORE_RIGHT_7", score_7_pub), ("SCORE_RIGHT_8", score_8_pub), ("SCORE_RIGHT_9", score_9_pub), 
    ("SCORE_RIGHT_10", score_10_pub), ("SCORE_RIGHT_11", score_11_pub), ("SCORE_RIGHT_12", score_12_pub), ("SCORE_RIGHT_13", score_13_pub), 
    ("SCORE_RIGHT_14", score_14_pub), ("SCORE_RIGHT_15", score_15_pub), ("SCORE_RIGHT_16", score_16_pub), ("SCORE_RIGHT_17", score_17_pub), 
    ("SCORE_RIGHT_18", score_18_pub), ("SCORE_RIGHT_19", score_19_pub), ("SCORE_RIGHT_20", score_20_pub), 
    ]

  op_templates_priv_mid = [
    ("ROUND_START", round_start_priv), ("ROUND_START", round_start2_priv), ("ROUND_START", round_start3_priv), 
    ("ROUND_MIDGAME", round_midgame_priv), ("ROUND_ENDGAME", round_endgame_priv), 
    
    ]

  op_templates_priv_left = [
    ("SCORE_LEFT_0", score_0_priv), ("SCORE_LEFT_1", score_1_priv), ("SCORE_LEFT_2", score_2_priv), ("SCORE_LEFT_3", score_3_priv), ("SCORE_LEFT_4", score_4_priv),
    ("SCORE_LEFT_5", score_5_priv), ("SCORE_LEFT_6", score_6_priv), ("SCORE_LEFT_7", score_7_priv), ("SCORE_LEFT_8", score_8_priv), ("SCORE_LEFT_9", score_9_priv), 
    ("SCORE_LEFT_10", score_10_priv), ("SCORE_LEFT_11", score_11_priv), ("SCORE_LEFT_12", score_12_priv), ("SCORE_LEFT_13", score_13_priv), 
    ("SCORE_LEFT_14", score_14_priv), ("SCORE_LEFT_15", score_15_priv), ("SCORE_LEFT_16", score_16_priv), ("SCORE_LEFT_17", score_17_priv),
    ("SCORE_LEFT_18", score_18_priv), ("SCORE_LEFT_19", score_19_priv), ("SCORE_LEFT_20", score_20_priv), 

    # ("ASTRA_INIT_LEFT", privtil_astra), ("BREACH_INIT_LEFT", privtil_breach), ("BRIMSTONE_INIT_LEFT", privtil_brimstone), 
    # ("CYPHER_INIT_LEFT", privtil_cypher),("JETT_INIT_LEFT", privtil_jett), ("KAYO_INIT_LEFT", privtil_kayo), 
    # ("KILLJOY_INIT_LEFT", privtil_killjoy), ("OMEN_INIT_LEFT", privtil_omen), ("PHOENIX_INIT_LEFT", privtil_phoenix), 
    # ("RAZE_INIT_LEFT", privtil_raze), ("REYNA_INIT_LEFT", privtil_reyna), ("SAGE_INIT_LEFT", privtil_sage), 
    # ("SKYE_INIT_LEFT", privtil_skye), ("SOVA_INIT_LEFT", privtil_sova), ("VIPER_INIT_LEFT", privtil_viper), 
    # ("YORU_INIT_LEFT", privtil_yoru), 

    ]

  op_templates_priv_right = [
    ("SCORE_RIGHT_0", score_0_priv), ("SCORE_RIGHT_1", score_1_priv), ("SCORE_RIGHT_2", score_2_priv), ("SCORE_RIGHT_3", score_3_priv), ("SCORE_RIGHT_4", score_4_priv),
    ("SCORE_RIGHT_5", score_5_priv), ("SCORE_RIGHT_6", score_6_priv), ("SCORE_RIGHT_7", score_7_priv), ("SCORE_RIGHT_8", score_8_priv), ("SCORE_RIGHT_9", score_9_priv), 
    ("SCORE_RIGHT_10", score_10_priv), ("SCORE_RIGHT_11", score_11_priv), ("SCORE_RIGHT_12", score_12_priv), ("SCORE_RIGHT_13", score_13_priv), 
    ("SCORE_RIGHT_14", score_14_priv), ("SCORE_RIGHT_15", score_15_priv), ("SCORE_RIGHT_16", score_16_priv), ("SCORE_RIGHT_17", score_17_priv),
    ("SCORE_RIGHT_18", score_18_priv), ("SCORE_RIGHT_19", score_19_priv), ("SCORE_RIGHT_20", score_20_priv),

    # ("ASTRA_INIT_RIGHT", privtir_astra), ("BREACH_INIT_RIGHT", privtir_breach), ("BRIMSTONE_INIT_RIGHT", privtir_brimstone), 
    # ("CYPHER_INIT_RIGHT", privtir_cypher),("JETT_INIT_RIGHT", privtir_jett), ("KAYO_INIT_RIGHT", privtir_kayo), 
    # ("KILLJOY_INIT_RIGHT", privtir_killjoy), ("OMEN_INIT_RIGHT", privtir_omen), ("PHOENIX_INIT_RIGHT", privtir_phoenix), 
    # ("RAZE_INIT_RIGHT", privtir_raze), ("REYNA_INIT_RIGHT", privtir_reyna), ("SAGE_INIT_RIGHT", privtir_sage), 
    # ("SKYE_INIT_RIGHT", privtir_skye), ("SOVA_INIT_RIGHT", privtir_sova), ("VIPER_INIT_RIGHT", privtir_viper), 
    # ("YORU_INIT_RIGHT", privtir_yoru), 

    ]

  side_templates = [
    ("SIDE_LEFT", side_atk_left), ("SIDE_RIGHT", side_atk_right), 
    ("SPIKE_PLANTED", spike_planted_op_pub), ("SPIKE_PLANTED", spike_planted_op_priv), 
    ]

  spike_templates = [
    ("SPIKE_PLANTING", spike_planting), ("SPIKE_DEFUSING", spike_defusing), 
    # ("SPIKE_CARRIER_DOWN", spike_carrier_down), ("SPIKE_PLANTER_DOWN", spike_planter_down), ("SPIKE_PLANTED", spike_planted), 

    ]

  ult_templates_left_1 = [
    ("ASTRA_INIT_LEFT_1", til_astra), ("BREACH_INIT_LEFT_1", til_breach), ("BRIMSTONE_INIT_LEFT_1", til_brimstone), 
    ("CYPHER_INIT_LEFT_1", til_cypher),("JETT_INIT_LEFT_1", til_jett), ("KAYO_INIT_LEFT_1", til_kayo), 
    ("KILLJOY_INIT_LEFT_1", til_killjoy), ("OMEN_INIT_LEFT_1", til_omen), ("PHOENIX_INIT_LEFT_1", til_phoenix), 
    ("RAZE_INIT_LEFT_1", til_raze), ("REYNA_INIT_LEFT_1", til_reyna), ("SAGE_INIT_LEFT_1", til_sage), 
    ("SKYE_INIT_LEFT_1", til_skye), ("SOVA_INIT_LEFT_1", til_sova), ("VIPER_INIT_LEFT_1", til_viper), 
    ("YORU_INIT_LEFT_1", til_yoru), 

    ("ASTRA_ULT_GREEN_LEFT_1", tgu_astra), ("BREACH_ULT_GREEN_LEFT_1", tgu_breach), ("BRIMSTONE_ULT_GREEN_LEFT_1", tgu_brimstone), 
    ("CYPHER_ULT_GREEN_LEFT_1", tgu_cypher), ("JETT_ULT_GREEN_LEFT_1", tgu_jett), ("KAYO_ULT_GREEN_LEFT_1", tgu_kayo), 
    ("KILLJOY_ULT_GREEN_LEFT_1", tgu_killjoy), ("OMEN_ULT_GREEN_LEFT_1", tgu_omen), ("PHOENIX_ULT_GREEN_LEFT_1", tgu_phoenix), 
    ("RAZE_ULT_GREEN_LEFT_1", tgu_raze), ("REYNA_ULT_GREEN_LEFT_1", tgu_reyna), ("SAGE_ULT_GREEN_LEFT_1", tgu_sage), 
    ("SKYE_ULT_GREEN_LEFT_1", tgu_skye), ("SOVA_ULT_GREEN_LEFT_1", tgu_sova), ("VIPER_ULT_GREEN_LEFT_1", tgu_viper), 
    ("YORU_ULT_GREEN_LEFT_1", tgu_yoru), 

    ("ASTRA_ULT_RED_LEFT_1", tru_astra), ("BREACH_ULT_RED_LEFT_1", tru_breach), ("BRIMSTONE_ULT_RED_LEFT_1", tru_brimstone), 
    ("CYPHER_ULT_RED_LEFT_1", tru_cypher), ("JETT_ULT_RED_LEFT_1", tru_jett), ("KAYO_ULT_RED_LEFT_1", tru_kayo), 
    ("KILLJOY_ULT_RED_LEFT_1", tru_killjoy), ("OMEN_ULT_RED_LEFT_1", tru_omen), ("PHOENIX_ULT_RED_LEFT_1", tru_phoenix), 
    ("RAZE_ULT_RED_LEFT_1", tru_raze), ("REYNA_ULT_RED_LEFT_1", tru_reyna), ("SAGE_ULT_RED_LEFT_1", tru_sage), 
    ("SKYE_ULT_RED_LEFT_1", tru_skye), ("SOVA_ULT_RED_LEFT_1", tru_sova), ("VIPER_ULT_RED_LEFT_1", tru_viper), 
    ("YORU_ULT_RED_LEFT_1", tru_yoru), 

    ("ULT_RED_0_6_LEFT_1", ult_red_0_6), ("ULT_RED_0_7_LEFT_1", ult_red_0_7), ("ULT_RED_0_8_LEFT_1", ult_red_0_8), 
    ("ULT_RED_1_6_LEFT_1", ult_red_1_6), ("ULT_RED_1_7_LEFT_1", ult_red_1_7), ("ULT_RED_1_8_LEFT_1", ult_red_1_8), 
    ("ULT_RED_2_6_LEFT_1", ult_red_2_6), ("ULT_RED_2_7_LEFT_1", ult_red_2_7), ("ULT_RED_2_8_LEFT_1", ult_red_2_8), 
    ("ULT_RED_3_6_LEFT_1", ult_red_3_6), ("ULT_RED_3_7_LEFT_1", ult_red_3_7), ("ULT_RED_3_8_LEFT_1", ult_red_3_8), 
    ("ULT_RED_4_6_LEFT_1", ult_red_4_6), ("ULT_RED_4_7_LEFT_1", ult_red_4_7), ("ULT_RED_4_8_LEFT_1", ult_red_4_8), 
    ("ULT_RED_5_6_LEFT_1", ult_red_5_6), ("ULT_RED_5_7_LEFT_1", ult_red_5_7), ("ULT_RED_5_8_LEFT_1", ult_red_5_8), 
    ("ULT_RED_6_7_LEFT_1", ult_red_6_7), ("ULT_RED_6_8_LEFT_1", ult_red_6_8), ("ULT_RED_7_8_LEFT_1", ult_red_7_8), 

    ("ULT_GREEN_0_6_LEFT_1", ult_green_0_6), ("ULT_GREEN_0_7_LEFT_1", ult_green_0_7), ("ULT_GREEN_0_8_LEFT_1", ult_green_0_8), 
    ("ULT_GREEN_1_6_LEFT_1", ult_green_1_6), ("ULT_GREEN_1_7_LEFT_1", ult_green_1_7), ("ULT_GREEN_1_8_LEFT_1", ult_green_1_8), 
    ("ULT_GREEN_2_6_LEFT_1", ult_green_2_6), ("ULT_GREEN_2_7_LEFT_1", ult_green_2_7), ("ULT_GREEN_2_8_LEFT_1", ult_green_2_8), 
    ("ULT_GREEN_3_6_LEFT_1", ult_green_3_6), ("ULT_GREEN_3_7_LEFT_1", ult_green_3_7), ("ULT_GREEN_3_8_LEFT_1", ult_green_3_8), 
    ("ULT_GREEN_4_6_LEFT_1", ult_green_4_6), ("ULT_GREEN_4_7_LEFT_1", ult_green_4_7), ("ULT_GREEN_4_8_LEFT_1", ult_green_4_8), 
    ("ULT_GREEN_5_6_LEFT_1", ult_green_5_6), ("ULT_GREEN_5_7_LEFT_1", ult_green_5_7), ("ULT_GREEN_5_8_LEFT_1", ult_green_5_8), 
    ("ULT_GREEN_6_7_LEFT_1", ult_green_6_7), ("ULT_GREEN_6_8_LEFT_1", ult_green_6_8), ("ULT_GREEN_7_8_LEFT_1", ult_green_7_8), 

    ]

  ult_templates_right_1 = [
    ("ASTRA_INIT_RIGHT_1", tir_astra), ("BREACH_INIT_RIGHT_1", tir_breach), ("BRIMSTONE_INIT_RIGHT_1", tir_brimstone), 
    ("CYPHER_INIT_RIGHT_1", tir_cypher), ("JETT_INIT_RIGHT_1", tir_jett), ("KAYO_INIT_RIGHT_1", tir_kayo), 
    ("KILLJOY_INIT_RIGHT_1", tir_killjoy), ("OMEN_INIT_RIGHT_1", tir_omen), ("PHOENIX_INIT_RIGHT_1", tir_phoenix), 
    ("RAZE_INIT_RIGHT_1", tir_raze), ("REYNA_INIT_RIGHT_1", tir_reyna), ("SAGE_INIT_RIGHT_1", tir_sage), 
    ("SKYE_INIT_RIGHT_1", tir_skye), ("SOVA_INIT_RIGHT_1", tir_sova), ("VIPER_INIT_RIGHT_1", tir_viper), 
    ("YORU_INIT_RIGHT_1", tir_yoru), 

    ("ASTRA_ULT_GREEN_RIGHT_1", tgu_astra), ("BREACH_ULT_GREEN_RIGHT_1", tgu_breach), ("BRIMSTONE_ULT_GREEN_RIGHT_1", tgu_brimstone), 
    ("CYPHER_ULT_GREEN_RIGHT_1", tgu_cypher), ("JETT_ULT_GREEN_RIGHT_1", tgu_jett), ("KAYO_ULT_GREEN_RIGHT_1", tgu_kayo), 
    ("KILLJOY_ULT_GREEN_RIGHT_1", tgu_killjoy), ("OMEN_ULT_GREEN_RIGHT_1", tgu_omen), ("PHOENIX_ULT_GREEN_RIGHT_1", tgu_phoenix), 
    ("RAZE_ULT_GREEN_RIGHT_1", tgu_raze), ("REYNA_ULT_GREEN_RIGHT_1", tgu_reyna), ("SAGE_ULT_GREEN_RIGHT_1", tgu_sage), 
    ("SKYE_ULT_GREEN_RIGHT_1", tgu_skye), ("SOVA_ULT_GREEN_RIGHT_1", tgu_sova), ("VIPER_ULT_GREEN_RIGHT_1", tgu_viper), 
    ("YORU_ULT_GREEN_RIGHT_1", tgu_yoru), 

    ("ASTRA_ULT_RED_RIGHT_1", tru_astra), ("BREACH_ULT_RED_RIGHT_1", tru_breach), ("BRIMSTONE_ULT_RED_RIGHT_1", tru_brimstone), 
    ("CYPHER_ULT_RED_RIGHT_1", tru_cypher), ("JETT_ULT_RED_RIGHT_1", tru_jett), ("KAYO_ULT_RED_RIGHT_1", tru_kayo), 
    ("KILLJOY_ULT_RED_RIGHT_1", tru_killjoy), ("OMEN_ULT_RED_RIGHT_1", tru_omen), ("PHOENIX_ULT_RED_RIGHT_1", tru_phoenix), 
    ("RAZE_ULT_RED_RIGHT_1", tru_raze), ("REYNA_ULT_RED_RIGHT_1", tru_reyna), ("SAGE_ULT_RED_RIGHT_1", tru_sage), 
    ("SKYE_ULT_RED_RIGHT_1", tru_skye), ("SOVA_ULT_RED_RIGHT_1", tru_sova), ("VIPER_ULT_RED_RIGHT_1", tru_viper), 
    ("YORU_ULT_RED_RIGHT_1", tru_yoru), 

    ("ULT_RED_0_6_RIGHT_1", ult_red_0_6), ("ULT_RED_0_7_RIGHT_1", ult_red_0_7), ("ULT_RED_0_8_RIGHT_1", ult_red_0_8), 
    ("ULT_RED_1_6_RIGHT_1", ult_red_1_6), ("ULT_RED_1_7_RIGHT_1", ult_red_1_7), ("ULT_RED_1_8_RIGHT_1", ult_red_1_8), 
    ("ULT_RED_2_6_RIGHT_1", ult_red_2_6), ("ULT_RED_2_7_RIGHT_1", ult_red_2_7), ("ULT_RED_2_8_RIGHT_1", ult_red_2_8), 
    ("ULT_RED_3_6_RIGHT_1", ult_red_3_6), ("ULT_RED_3_7_RIGHT_1", ult_red_3_7), ("ULT_RED_3_8_RIGHT_1", ult_red_3_8), 
    ("ULT_RED_4_6_RIGHT_1", ult_red_4_6), ("ULT_RED_4_7_RIGHT_1", ult_red_4_7), ("ULT_RED_4_8_RIGHT_1", ult_red_4_8), 
    ("ULT_RED_5_6_RIGHT_1", ult_red_5_6), ("ULT_RED_5_7_RIGHT_1", ult_red_5_7), ("ULT_RED_5_8_RIGHT_1", ult_red_5_8), 
    ("ULT_RED_6_7_RIGHT_1", ult_red_6_7), ("ULT_RED_6_8_RIGHT_1", ult_red_6_8), ("ULT_RED_7_8_RIGHT_1", ult_red_7_8), 

    ("ULT_GREEN_0_6_RIGHT_1", ult_green_0_6), ("ULT_GREEN_0_7_RIGHT_1", ult_green_0_7), ("ULT_GREEN_0_8_RIGHT_1", ult_green_0_8), 
    ("ULT_GREEN_1_6_RIGHT_1", ult_green_1_6), ("ULT_GREEN_1_7_RIGHT_1", ult_green_1_7), ("ULT_GREEN_1_8_RIGHT_1", ult_green_1_8), 
    ("ULT_GREEN_2_6_RIGHT_1", ult_green_2_6), ("ULT_GREEN_2_7_RIGHT_1", ult_green_2_7), ("ULT_GREEN_2_8_RIGHT_1", ult_green_2_8), 
    ("ULT_GREEN_3_6_RIGHT_1", ult_green_3_6), ("ULT_GREEN_3_7_RIGHT_1", ult_green_3_7), ("ULT_GREEN_3_8_RIGHT_1", ult_green_3_8), 
    ("ULT_GREEN_4_6_RIGHT_1", ult_green_4_6), ("ULT_GREEN_4_7_RIGHT_1", ult_green_4_7), ("ULT_GREEN_4_8_RIGHT_1", ult_green_4_8), 
    ("ULT_GREEN_5_6_RIGHT_1", ult_green_5_6), ("ULT_GREEN_5_7_RIGHT_1", ult_green_5_7), ("ULT_GREEN_5_8_RIGHT_1", ult_green_5_8), 
    ("ULT_GREEN_6_7_RIGHT_1", ult_green_6_7), ("ULT_GREEN_6_8_RIGHT_1", ult_green_6_8), ("ULT_GREEN_7_8_RIGHT_1", ult_green_7_8), 

    ]

  abil_templates_left_1 = [
    ("ABIL_0_LEFT_1", abil_0), ("ABIL_1_LEFT_1", abil_1), ("ABIL_2_LEFT_1", abil_2), ("ABIL_3_LEFT_1", abil_3), 

    ("ASTRA_ABIL_VERIF_LEFT_1", astra_abil_verif), ("ASTRA_ABIL_1_LEFT_1", astra_abil_1), ("ASTRA_ABIL_2_LEFT_1", astra_abil_2), 
    ("ASTRA_ABIL_3_LEFT_1", astra_abil_3), ("ASTRA_ABIL_4_LEFT_1", astra_abil_4), ("ASTRA_ABIL_5_LEFT_1", astra_abil_5), 

    ("SPIKE_HELD_LEFT_1", spike_held), 

    ("GREEN_0_LEFT_1", health_green_0), ("GREEN_1_LEFT_1", health_green_1), ("GREEN_2_LEFT_1", health_green_2), 
    ("GREEN_3_LEFT_1", health_green_3), ("GREEN_4_LEFT_1", health_green_4), ("GREEN_5_LEFT_1", health_green_5), 
    ("GREEN_6_LEFT_1", health_green_6), ("GREEN_7_LEFT_1", health_green_7), ("GREEN_8_LEFT_1", health_green_8), 
    ("GREEN_9_LEFT_1", health_green_9), ("GREEN_25_LEFT_1", health_green_25), ("GREEN_50_LEFT_1", health_green_50), 

    ("RED_0_LEFT_1", health_red_0), ("RED_1_LEFT_1", health_red_1), ("RED_2_LEFT_1", health_red_2), 
    ("RED_3_LEFT_1", health_red_3), ("RED_4_LEFT_1", health_red_4), ("RED_5_LEFT_1", health_red_5), 
    ("RED_6_LEFT_1", health_red_6), ("RED_7_LEFT_1", health_red_7), ("RED_8_LEFT_1", health_red_8), 
    ("RED_9_LEFT_1", health_red_9), ("RED_25_LEFT_1", health_red_25), ("RED_50_LEFT_1", health_red_50), 

    ("CLASSIC_LEFT_1", classic_left), ("FRENZY_LEFT_1", frenzy_left), ("GHOST_LEFT_1", ghost_left), 
    ("SHERIFF_LEFT_1", sheriff_left), ("SHORTY_LEFT_1", shorty_left), ("MARSHAL_LEFT_1", marshal_left), 
    ("STINGER_LEFT_1", stinger_left), ("SPECTRE_LEFT_1", spectre_left), ("BULLDOG_LEFT_1", bulldog_left), 
    ("JUDGE_LEFT_1", judge_left), ("GUARDIAN_LEFT_1", guardian_left), ("VANDAL_LEFT_1", vandal_left), 
    ("PHANTOM_LEFT_1", phantom_left), ("OPERATOR_LEFT_1", operator_left), ("ODIN_LEFT_1", odin_left), 
    ("ARES_LEFT_1", ares_left), ("BUCKY_LEFT_1", bucky_left)

    ]

  abil_templates_right_1 = [
    ("ABIL_0_RIGHT_1", abil_0), ("ABIL_1_RIGHT_1", abil_1), ("ABIL_2_RIGHT_1", abil_2), ("ABIL_3_RIGHT_1", abil_3), 

    ("ASTRA_ABIL_VERIF_RIGHT_1", astra_abil_verif), ("ASTRA_ABIL_1_RIGHT_1", astra_abil_1), ("ASTRA_ABIL_2_RIGHT_1", astra_abil_2), 
    ("ASTRA_ABIL_3_RIGHT_1", astra_abil_3), ("ASTRA_ABIL_4_RIGHT_1", astra_abil_4), ("ASTRA_ABIL_5_RIGHT_1", astra_abil_5), 

    ("SPIKE_HELD_RIGHT_1", spike_held), 

    ("GREEN_0_RIGHT_1", health_green_0), ("GREEN_1_RIGHT_1", health_green_1), ("GREEN_2_RIGHT_1", health_green_2), 
    ("GREEN_3_RIGHT_1", health_green_3), ("GREEN_4_RIGHT_1", health_green_4), ("GREEN_5_RIGHT_1", health_green_5), 
    ("GREEN_6_RIGHT_1", health_green_6), ("GREEN_7_RIGHT_1", health_green_7), ("GREEN_8_RIGHT_1", health_green_8), 
    ("GREEN_9_RIGHT_1", health_green_9), ("GREEN_25_RIGHT_1", health_green_25), ("GREEN_50_RIGHT_1", health_green_50), 

    ("RED_0_RIGHT_1", health_red_0), ("RED_1_RIGHT_1", health_red_1), ("RED_2_RIGHT_1", health_red_2), 
    ("RED_3_RIGHT_1", health_red_3), ("RED_4_RIGHT_1", health_red_4), ("RED_5_RIGHT_1", health_red_5), 
    ("RED_6_RIGHT_1", health_red_6), ("RED_7_RIGHT_1", health_red_7), ("RED_8_RIGHT_1", health_red_8), 
    ("RED_9_RIGHT_1", health_red_9), ("RED_25_RIGHT_1", health_red_25), ("RED_50_RIGHT_1", health_red_50), 

    ("CLASSIC_RIGHT_1", classic_right), ("FRENZY_RIGHT_1", frenzy_right), ("GHOST_RIGHT_1", ghost_right), 
    ("SHERIFF_RIGHT_1", sheriff_right), ("SHORTY_RIGHT_1", shorty_right), ("MARSHAL_RIGHT_1", marshal_right), 
    ("STINGER_RIGHT_1", stinger_right), ("SPECTRE_RIGHT_1", spectre_right), ("BULLDOG_RIGHT_1", bulldog_right), 
    ("JUDGE_RIGHT_1", judge_right), ("GUARDIAN_RIGHT_1", guardian_right), ("VANDAL_RIGHT_1", vandal_right), 
    ("PHANTOM_RIGHT_1", phantom_right), ("OPERATOR_RIGHT_1", operator_right), ("ODIN_RIGHT_1", odin_right), 
    ("ARES_RIGHT_1", ares_right), ("BUCKY_RIGHT_1", bucky_right)

    ]

  ult_templates_left_2 = [
    ("ASTRA_INIT_LEFT_2", til_astra), ("BREACH_INIT_LEFT_2", til_breach), ("BRIMSTONE_INIT_LEFT_2", til_brimstone), 
    ("CYPHER_INIT_LEFT_2", til_cypher),("JETT_INIT_LEFT_2", til_jett), ("KAYO_INIT_LEFT_2", til_kayo), 
    ("KILLJOY_INIT_LEFT_2", til_killjoy), ("OMEN_INIT_LEFT_2", til_omen), ("PHOENIX_INIT_LEFT_2", til_phoenix), 
    ("RAZE_INIT_LEFT_2", til_raze), ("REYNA_INIT_LEFT_2", til_reyna), ("SAGE_INIT_LEFT_2", til_sage), 
    ("SKYE_INIT_LEFT_2", til_skye), ("SOVA_INIT_LEFT_2", til_sova), ("VIPER_INIT_LEFT_2", til_viper), 
    ("YORU_INIT_LEFT_2", til_yoru), 

    ("ASTRA_ULT_GREEN_LEFT_2", tgu_astra), ("BREACH_ULT_GREEN_LEFT_2", tgu_breach), ("BRIMSTONE_ULT_GREEN_LEFT_2", tgu_brimstone), 
    ("CYPHER_ULT_GREEN_LEFT_2", tgu_cypher), ("JETT_ULT_GREEN_LEFT_2", tgu_jett), ("KAYO_ULT_GREEN_LEFT_2", tgu_kayo), 
    ("KILLJOY_ULT_GREEN_LEFT_2", tgu_killjoy), ("OMEN_ULT_GREEN_LEFT_2", tgu_omen), ("PHOENIX_ULT_GREEN_LEFT_2", tgu_phoenix), 
    ("RAZE_ULT_GREEN_LEFT_2", tgu_raze), ("REYNA_ULT_GREEN_LEFT_2", tgu_reyna), ("SAGE_ULT_GREEN_LEFT_2", tgu_sage), 
    ("SKYE_ULT_GREEN_LEFT_2", tgu_skye), ("SOVA_ULT_GREEN_LEFT_2", tgu_sova), ("VIPER_ULT_GREEN_LEFT_2", tgu_viper), 
    ("YORU_ULT_GREEN_LEFT_2", tgu_yoru), 

    ("ASTRA_ULT_RED_LEFT_2", tru_astra), ("BREACH_ULT_RED_LEFT_2", tru_breach), ("BRIMSTONE_ULT_RED_LEFT_2", tru_brimstone), 
    ("CYPHER_ULT_RED_LEFT_2", tru_cypher), ("JETT_ULT_RED_LEFT_2", tru_jett), ("KAYO_ULT_RED_LEFT_2", tru_kayo), 
    ("KILLJOY_ULT_RED_LEFT_2", tru_killjoy), ("OMEN_ULT_RED_LEFT_2", tru_omen), ("PHOENIX_ULT_RED_LEFT_2", tru_phoenix), 
    ("RAZE_ULT_RED_LEFT_2", tru_raze), ("REYNA_ULT_RED_LEFT_2", tru_reyna), ("SAGE_ULT_RED_LEFT_2", tru_sage), 
    ("SKYE_ULT_RED_LEFT_2", tru_skye), ("SOVA_ULT_RED_LEFT_2", tru_sova), ("VIPER_ULT_RED_LEFT_2", tru_viper), 
    ("YORU_ULT_RED_LEFT_2", tru_yoru), 

    ("ULT_RED_0_6_LEFT_2", ult_red_0_6), ("ULT_RED_0_7_LEFT_2", ult_red_0_7), ("ULT_RED_0_8_LEFT_2", ult_red_0_8), 
    ("ULT_RED_1_6_LEFT_2", ult_red_1_6), ("ULT_RED_1_7_LEFT_2", ult_red_1_7), ("ULT_RED_1_8_LEFT_2", ult_red_1_8), 
    ("ULT_RED_2_6_LEFT_2", ult_red_2_6), ("ULT_RED_2_7_LEFT_2", ult_red_2_7), ("ULT_RED_2_8_LEFT_2", ult_red_2_8), 
    ("ULT_RED_3_6_LEFT_2", ult_red_3_6), ("ULT_RED_3_7_LEFT_2", ult_red_3_7), ("ULT_RED_3_8_LEFT_2", ult_red_3_8), 
    ("ULT_RED_4_6_LEFT_2", ult_red_4_6), ("ULT_RED_4_7_LEFT_2", ult_red_4_7), ("ULT_RED_4_8_LEFT_2", ult_red_4_8), 
    ("ULT_RED_5_6_LEFT_2", ult_red_5_6), ("ULT_RED_5_7_LEFT_2", ult_red_5_7), ("ULT_RED_5_8_LEFT_2", ult_red_5_8), 
    ("ULT_RED_6_7_LEFT_2", ult_red_6_7), ("ULT_RED_6_8_LEFT_2", ult_red_6_8), ("ULT_RED_7_8_LEFT_2", ult_red_7_8), 

    ("ULT_GREEN_0_6_LEFT_2", ult_green_0_6), ("ULT_GREEN_0_7_LEFT_2", ult_green_0_7), ("ULT_GREEN_0_8_LEFT_2", ult_green_0_8), 
    ("ULT_GREEN_1_6_LEFT_2", ult_green_1_6), ("ULT_GREEN_1_7_LEFT_2", ult_green_1_7), ("ULT_GREEN_1_8_LEFT_2", ult_green_1_8), 
    ("ULT_GREEN_2_6_LEFT_2", ult_green_2_6), ("ULT_GREEN_2_7_LEFT_2", ult_green_2_7), ("ULT_GREEN_2_8_LEFT_2", ult_green_2_8), 
    ("ULT_GREEN_3_6_LEFT_2", ult_green_3_6), ("ULT_GREEN_3_7_LEFT_2", ult_green_3_7), ("ULT_GREEN_3_8_LEFT_2", ult_green_3_8), 
    ("ULT_GREEN_4_6_LEFT_2", ult_green_4_6), ("ULT_GREEN_4_7_LEFT_2", ult_green_4_7), ("ULT_GREEN_4_8_LEFT_2", ult_green_4_8), 
    ("ULT_GREEN_5_6_LEFT_2", ult_green_5_6), ("ULT_GREEN_5_7_LEFT_2", ult_green_5_7), ("ULT_GREEN_5_8_LEFT_2", ult_green_5_8), 
    ("ULT_GREEN_6_7_LEFT_2", ult_green_6_7), ("ULT_GREEN_6_8_LEFT_2", ult_green_6_8), ("ULT_GREEN_7_8_LEFT_2", ult_green_7_8), 

    ]

  ult_templates_right_2 = [
    ("ASTRA_INIT_RIGHT_2", tir_astra), ("BREACH_INIT_RIGHT_2", tir_breach), ("BRIMSTONE_INIT_RIGHT_2", tir_brimstone), 
    ("CYPHER_INIT_RIGHT_2", tir_cypher), ("JETT_INIT_RIGHT_2", tir_jett), ("KAYO_INIT_RIGHT_2", tir_kayo), 
    ("KILLJOY_INIT_RIGHT_2", tir_killjoy), ("OMEN_INIT_RIGHT_2", tir_omen), ("PHOENIX_INIT_RIGHT_2", tir_phoenix), 
    ("RAZE_INIT_RIGHT_2", tir_raze), ("REYNA_INIT_RIGHT_2", tir_reyna), ("SAGE_INIT_RIGHT_2", tir_sage), 
    ("SKYE_INIT_RIGHT_2", tir_skye), ("SOVA_INIT_RIGHT_2", tir_sova), ("VIPER_INIT_RIGHT_2", tir_viper), 
    ("YORU_INIT_RIGHT_2", tir_yoru), 

    ("ASTRA_ULT_GREEN_RIGHT_2", tgu_astra), ("BREACH_ULT_GREEN_RIGHT_2", tgu_breach), ("BRIMSTONE_ULT_GREEN_RIGHT_2", tgu_brimstone), 
    ("CYPHER_ULT_GREEN_RIGHT_2", tgu_cypher), ("JETT_ULT_GREEN_RIGHT_2", tgu_jett), ("KAYO_ULT_GREEN_RIGHT_2", tgu_kayo), 
    ("KILLJOY_ULT_GREEN_RIGHT_2", tgu_killjoy), ("OMEN_ULT_GREEN_RIGHT_2", tgu_omen), ("PHOENIX_ULT_GREEN_RIGHT_2", tgu_phoenix), 
    ("RAZE_ULT_GREEN_RIGHT_2", tgu_raze), ("REYNA_ULT_GREEN_RIGHT_2", tgu_reyna), ("SAGE_ULT_GREEN_RIGHT_2", tgu_sage), 
    ("SKYE_ULT_GREEN_RIGHT_2", tgu_skye), ("SOVA_ULT_GREEN_RIGHT_2", tgu_sova), ("VIPER_ULT_GREEN_RIGHT_2", tgu_viper), 
    ("YORU_ULT_GREEN_RIGHT_2", tgu_yoru), 

    ("ASTRA_ULT_RED_RIGHT_2", tru_astra), ("BREACH_ULT_RED_RIGHT_2", tru_breach), ("BRIMSTONE_ULT_RED_RIGHT_2", tru_brimstone), 
    ("CYPHER_ULT_RED_RIGHT_2", tru_cypher), ("JETT_ULT_RED_RIGHT_2", tru_jett), ("KAYO_ULT_RED_RIGHT_2", tru_kayo), 
    ("KILLJOY_ULT_RED_RIGHT_2", tru_killjoy), ("OMEN_ULT_RED_RIGHT_2", tru_omen), ("PHOENIX_ULT_RED_RIGHT_2", tru_phoenix), 
    ("RAZE_ULT_RED_RIGHT_2", tru_raze), ("REYNA_ULT_RED_RIGHT_2", tru_reyna), ("SAGE_ULT_RED_RIGHT_2", tru_sage), 
    ("SKYE_ULT_RED_RIGHT_2", tru_skye), ("SOVA_ULT_RED_RIGHT_2", tru_sova), ("VIPER_ULT_RED_RIGHT_2", tru_viper), 
    ("YORU_ULT_RED_RIGHT_2", tru_yoru), 

    ("ULT_RED_0_6_RIGHT_2", ult_red_0_6), ("ULT_RED_0_7_RIGHT_2", ult_red_0_7), ("ULT_RED_0_8_RIGHT_2", ult_red_0_8), 
    ("ULT_RED_1_6_RIGHT_2", ult_red_1_6), ("ULT_RED_1_7_RIGHT_2", ult_red_1_7), ("ULT_RED_1_8_RIGHT_2", ult_red_1_8), 
    ("ULT_RED_2_6_RIGHT_2", ult_red_2_6), ("ULT_RED_2_7_RIGHT_2", ult_red_2_7), ("ULT_RED_2_8_RIGHT_2", ult_red_2_8), 
    ("ULT_RED_3_6_RIGHT_2", ult_red_3_6), ("ULT_RED_3_7_RIGHT_2", ult_red_3_7), ("ULT_RED_3_8_RIGHT_2", ult_red_3_8), 
    ("ULT_RED_4_6_RIGHT_2", ult_red_4_6), ("ULT_RED_4_7_RIGHT_2", ult_red_4_7), ("ULT_RED_4_8_RIGHT_2", ult_red_4_8), 
    ("ULT_RED_5_6_RIGHT_2", ult_red_5_6), ("ULT_RED_5_7_RIGHT_2", ult_red_5_7), ("ULT_RED_5_8_RIGHT_2", ult_red_5_8), 
    ("ULT_RED_6_7_RIGHT_2", ult_red_6_7), ("ULT_RED_6_8_RIGHT_2", ult_red_6_8), ("ULT_RED_7_8_RIGHT_2", ult_red_7_8), 

    ("ULT_GREEN_0_6_RIGHT_2", ult_green_0_6), ("ULT_GREEN_0_7_RIGHT_2", ult_green_0_7), ("ULT_GREEN_0_8_RIGHT_2", ult_green_0_8), 
    ("ULT_GREEN_1_6_RIGHT_2", ult_green_1_6), ("ULT_GREEN_1_7_RIGHT_2", ult_green_1_7), ("ULT_GREEN_1_8_RIGHT_2", ult_green_1_8), 
    ("ULT_GREEN_2_6_RIGHT_2", ult_green_2_6), ("ULT_GREEN_2_7_RIGHT_2", ult_green_2_7), ("ULT_GREEN_2_8_RIGHT_2", ult_green_2_8), 
    ("ULT_GREEN_3_6_RIGHT_2", ult_green_3_6), ("ULT_GREEN_3_7_RIGHT_2", ult_green_3_7), ("ULT_GREEN_3_8_RIGHT_2", ult_green_3_8), 
    ("ULT_GREEN_4_6_RIGHT_2", ult_green_4_6), ("ULT_GREEN_4_7_RIGHT_2", ult_green_4_7), ("ULT_GREEN_4_8_RIGHT_2", ult_green_4_8), 
    ("ULT_GREEN_5_6_RIGHT_2", ult_green_5_6), ("ULT_GREEN_5_7_RIGHT_2", ult_green_5_7), ("ULT_GREEN_5_8_RIGHT_2", ult_green_5_8), 
    ("ULT_GREEN_6_7_RIGHT_2", ult_green_6_7), ("ULT_GREEN_6_8_RIGHT_2", ult_green_6_8), ("ULT_GREEN_7_8_RIGHT_2", ult_green_7_8), 

    ]

  abil_templates_left_2 = [
    ("ABIL_0_LEFT_2", abil_0), ("ABIL_1_LEFT_2", abil_1), ("ABIL_2_LEFT_2", abil_2), ("ABIL_3_LEFT_2", abil_3), 

    ("ASTRA_ABIL_VERIF_LEFT_2", astra_abil_verif), ("ASTRA_ABIL_1_LEFT_2", astra_abil_1), ("ASTRA_ABIL_2_LEFT_2", astra_abil_2), 
    ("ASTRA_ABIL_3_LEFT_2", astra_abil_3), ("ASTRA_ABIL_4_LEFT_2", astra_abil_4), ("ASTRA_ABIL_5_LEFT_2", astra_abil_5), 

    ("SPIKE_HELD_LEFT_2", spike_held), 

    ("GREEN_0_LEFT_2", health_green_0), ("GREEN_1_LEFT_2", health_green_1), ("GREEN_2_LEFT_2", health_green_2), 
    ("GREEN_3_LEFT_2", health_green_3), ("GREEN_4_LEFT_2", health_green_4), ("GREEN_5_LEFT_2", health_green_5), 
    ("GREEN_6_LEFT_2", health_green_6), ("GREEN_7_LEFT_2", health_green_7), ("GREEN_8_LEFT_2", health_green_8), 
    ("GREEN_9_LEFT_2", health_green_9), ("GREEN_25_LEFT_2", health_green_25), ("GREEN_50_LEFT_2", health_green_50), 

    ("RED_0_LEFT_2", health_red_0), ("RED_1_LEFT_2", health_red_1), ("RED_2_LEFT_2", health_red_2), 
    ("RED_3_LEFT_2", health_red_3), ("RED_4_LEFT_2", health_red_4), ("RED_5_LEFT_2", health_red_5), 
    ("RED_6_LEFT_2", health_red_6), ("RED_7_LEFT_2", health_red_7), ("RED_8_LEFT_2", health_red_8), 
    ("RED_9_LEFT_2", health_red_9), ("RED_25_LEFT_2", health_red_25), ("RED_50_LEFT_2", health_red_50), 

    ("CLASSIC_LEFT_2", classic_left), ("FRENZY_LEFT_2", frenzy_left), ("GHOST_LEFT_2", ghost_left), 
    ("SHERIFF_LEFT_2", sheriff_left), ("SHORTY_LEFT_2", shorty_left), ("MARSHAL_LEFT_2", marshal_left), 
    ("STINGER_LEFT_2", stinger_left), ("SPECTRE_LEFT_2", spectre_left), ("BULLDOG_LEFT_2", bulldog_left), 
    ("JUDGE_LEFT_2", judge_left), ("GUARDIAN_LEFT_2", guardian_left), ("VANDAL_LEFT_2", vandal_left), 
    ("PHANTOM_LEFT_2", phantom_left), ("OPERATOR_LEFT_2", operator_left), ("ODIN_LEFT_2", odin_left), 
    ("ARES_LEFT_2", ares_left), ("BUCKY_LEFT_2", bucky_left)

    ]

  abil_templates_right_2 = [
    ("ABIL_0_RIGHT_2", abil_0), ("ABIL_1_RIGHT_2", abil_1), ("ABIL_2_RIGHT_2", abil_2), ("ABIL_3_RIGHT_2", abil_3), 

    ("ASTRA_ABIL_VERIF_RIGHT_2", astra_abil_verif), ("ASTRA_ABIL_1_RIGHT_2", astra_abil_1), ("ASTRA_ABIL_2_RIGHT_2", astra_abil_2), 
    ("ASTRA_ABIL_3_RIGHT_2", astra_abil_3), ("ASTRA_ABIL_4_RIGHT_2", astra_abil_4), ("ASTRA_ABIL_5_RIGHT_2", astra_abil_5), 

    ("SPIKE_HELD_RIGHT_2", spike_held), 

    ("GREEN_0_RIGHT_2", health_green_0), ("GREEN_1_RIGHT_2", health_green_1), ("GREEN_2_RIGHT_2", health_green_2), 
    ("GREEN_3_RIGHT_2", health_green_3), ("GREEN_4_RIGHT_2", health_green_4), ("GREEN_5_RIGHT_2", health_green_5), 
    ("GREEN_6_RIGHT_2", health_green_6), ("GREEN_7_RIGHT_2", health_green_7), ("GREEN_8_RIGHT_2", health_green_8), 
    ("GREEN_9_RIGHT_2", health_green_9), ("GREEN_25_RIGHT_2", health_green_25), ("GREEN_50_RIGHT_2", health_green_50), 

    ("RED_0_RIGHT_2", health_red_0), ("RED_1_RIGHT_2", health_red_1), ("RED_2_RIGHT_2", health_red_2), 
    ("RED_3_RIGHT_2", health_red_3), ("RED_4_RIGHT_2", health_red_4), ("RED_5_RIGHT_2", health_red_5), 
    ("RED_6_RIGHT_2", health_red_6), ("RED_7_RIGHT_2", health_red_7), ("RED_8_RIGHT_2", health_red_8), 
    ("RED_9_RIGHT_2", health_red_9), ("RED_25_RIGHT_2", health_red_25), ("RED_50_RIGHT_2", health_red_50), 

    ("CLASSIC_RIGHT_2", classic_right), ("FRENZY_RIGHT_2", frenzy_right), ("GHOST_RIGHT_2", ghost_right), 
    ("SHERIFF_RIGHT_2", sheriff_right), ("SHORTY_RIGHT_2", shorty_right), ("MARSHAL_RIGHT_2", marshal_right), 
    ("STINGER_RIGHT_2", stinger_right), ("SPECTRE_RIGHT_2", spectre_right), ("BULLDOG_RIGHT_2", bulldog_right), 
    ("JUDGE_RIGHT_2", judge_right), ("GUARDIAN_RIGHT_2", guardian_right), ("VANDAL_RIGHT_2", vandal_right), 
    ("PHANTOM_RIGHT_2", phantom_right), ("OPERATOR_RIGHT_2", operator_right), ("ODIN_RIGHT_2", odin_right), 
    ("ARES_RIGHT_2", ares_right), ("BUCKY_RIGHT_2", bucky_right)

    ]

  ult_templates_left_3 = [
    ("ASTRA_INIT_LEFT_3", til_astra), ("BREACH_INIT_LEFT_3", til_breach), ("BRIMSTONE_INIT_LEFT_3", til_brimstone), 
    ("CYPHER_INIT_LEFT_3", til_cypher),("JETT_INIT_LEFT_3", til_jett), ("KAYO_INIT_LEFT_3", til_kayo), 
    ("KILLJOY_INIT_LEFT_3", til_killjoy), ("OMEN_INIT_LEFT_3", til_omen), ("PHOENIX_INIT_LEFT_3", til_phoenix), 
    ("RAZE_INIT_LEFT_3", til_raze), ("REYNA_INIT_LEFT_3", til_reyna), ("SAGE_INIT_LEFT_3", til_sage), 
    ("SKYE_INIT_LEFT_3", til_skye), ("SOVA_INIT_LEFT_3", til_sova), ("VIPER_INIT_LEFT_3", til_viper), 
    ("YORU_INIT_LEFT_3", til_yoru), 

    ("ASTRA_ULT_GREEN_LEFT_3", tgu_astra), ("BREACH_ULT_GREEN_LEFT_3", tgu_breach), ("BRIMSTONE_ULT_GREEN_LEFT_3", tgu_brimstone), 
    ("CYPHER_ULT_GREEN_LEFT_3", tgu_cypher), ("JETT_ULT_GREEN_LEFT_3", tgu_jett), ("KAYO_ULT_GREEN_LEFT_3", tgu_kayo), 
    ("KILLJOY_ULT_GREEN_LEFT_3", tgu_killjoy), ("OMEN_ULT_GREEN_LEFT_3", tgu_omen), ("PHOENIX_ULT_GREEN_LEFT_3", tgu_phoenix), 
    ("RAZE_ULT_GREEN_LEFT_3", tgu_raze), ("REYNA_ULT_GREEN_LEFT_3", tgu_reyna), ("SAGE_ULT_GREEN_LEFT_3", tgu_sage), 
    ("SKYE_ULT_GREEN_LEFT_3", tgu_skye), ("SOVA_ULT_GREEN_LEFT_3", tgu_sova), ("VIPER_ULT_GREEN_LEFT_3", tgu_viper), 
    ("YORU_ULT_GREEN_LEFT_3", tgu_yoru), 

    ("ASTRA_ULT_RED_LEFT_3", tru_astra), ("BREACH_ULT_RED_LEFT_3", tru_breach), ("BRIMSTONE_ULT_RED_LEFT_3", tru_brimstone), 
    ("CYPHER_ULT_RED_LEFT_3", tru_cypher), ("JETT_ULT_RED_LEFT_3", tru_jett), ("KAYO_ULT_RED_LEFT_3", tru_kayo), 
    ("KILLJOY_ULT_RED_LEFT_3", tru_killjoy), ("OMEN_ULT_RED_LEFT_3", tru_omen), ("PHOENIX_ULT_RED_LEFT_3", tru_phoenix), 
    ("RAZE_ULT_RED_LEFT_3", tru_raze), ("REYNA_ULT_RED_LEFT_3", tru_reyna), ("SAGE_ULT_RED_LEFT_3", tru_sage), 
    ("SKYE_ULT_RED_LEFT_3", tru_skye), ("SOVA_ULT_RED_LEFT_3", tru_sova), ("VIPER_ULT_RED_LEFT_3", tru_viper), 
    ("YORU_ULT_RED_LEFT_3", tru_yoru), 

    ("ULT_RED_0_6_LEFT_3", ult_red_0_6), ("ULT_RED_0_7_LEFT_3", ult_red_0_7), ("ULT_RED_0_8_LEFT_3", ult_red_0_8), 
    ("ULT_RED_1_6_LEFT_3", ult_red_1_6), ("ULT_RED_1_7_LEFT_3", ult_red_1_7), ("ULT_RED_1_8_LEFT_3", ult_red_1_8), 
    ("ULT_RED_2_6_LEFT_3", ult_red_2_6), ("ULT_RED_2_7_LEFT_3", ult_red_2_7), ("ULT_RED_2_8_LEFT_3", ult_red_2_8), 
    ("ULT_RED_3_6_LEFT_3", ult_red_3_6), ("ULT_RED_3_7_LEFT_3", ult_red_3_7), ("ULT_RED_3_8_LEFT_3", ult_red_3_8), 
    ("ULT_RED_4_6_LEFT_3", ult_red_4_6), ("ULT_RED_4_7_LEFT_3", ult_red_4_7), ("ULT_RED_4_8_LEFT_3", ult_red_4_8), 
    ("ULT_RED_5_6_LEFT_3", ult_red_5_6), ("ULT_RED_5_7_LEFT_3", ult_red_5_7), ("ULT_RED_5_8_LEFT_3", ult_red_5_8), 
    ("ULT_RED_6_7_LEFT_3", ult_red_6_7), ("ULT_RED_6_8_LEFT_3", ult_red_6_8), ("ULT_RED_7_8_LEFT_3", ult_red_7_8), 

    ("ULT_GREEN_0_6_LEFT_3", ult_green_0_6), ("ULT_GREEN_0_7_LEFT_3", ult_green_0_7), ("ULT_GREEN_0_8_LEFT_3", ult_green_0_8), 
    ("ULT_GREEN_1_6_LEFT_3", ult_green_1_6), ("ULT_GREEN_1_7_LEFT_3", ult_green_1_7), ("ULT_GREEN_1_8_LEFT_3", ult_green_1_8), 
    ("ULT_GREEN_2_6_LEFT_3", ult_green_2_6), ("ULT_GREEN_2_7_LEFT_3", ult_green_2_7), ("ULT_GREEN_2_8_LEFT_3", ult_green_2_8), 
    ("ULT_GREEN_3_6_LEFT_3", ult_green_3_6), ("ULT_GREEN_3_7_LEFT_3", ult_green_3_7), ("ULT_GREEN_3_8_LEFT_3", ult_green_3_8), 
    ("ULT_GREEN_4_6_LEFT_3", ult_green_4_6), ("ULT_GREEN_4_7_LEFT_3", ult_green_4_7), ("ULT_GREEN_4_8_LEFT_3", ult_green_4_8), 
    ("ULT_GREEN_5_6_LEFT_3", ult_green_5_6), ("ULT_GREEN_5_7_LEFT_3", ult_green_5_7), ("ULT_GREEN_5_8_LEFT_3", ult_green_5_8), 
    ("ULT_GREEN_6_7_LEFT_3", ult_green_6_7), ("ULT_GREEN_6_8_LEFT_3", ult_green_6_8), ("ULT_GREEN_7_8_LEFT_3", ult_green_7_8), 

    ]

  ult_templates_right_3 = [
    ("ASTRA_INIT_RIGHT_3", tir_astra), ("BREACH_INIT_RIGHT_3", tir_breach), ("BRIMSTONE_INIT_RIGHT_3", tir_brimstone), 
    ("CYPHER_INIT_RIGHT_3", tir_cypher), ("JETT_INIT_RIGHT_3", tir_jett), ("KAYO_INIT_RIGHT_3", tir_kayo), 
    ("KILLJOY_INIT_RIGHT_3", tir_killjoy), ("OMEN_INIT_RIGHT_3", tir_omen), ("PHOENIX_INIT_RIGHT_3", tir_phoenix), 
    ("RAZE_INIT_RIGHT_3", tir_raze), ("REYNA_INIT_RIGHT_3", tir_reyna), ("SAGE_INIT_RIGHT_3", tir_sage), 
    ("SKYE_INIT_RIGHT_3", tir_skye), ("SOVA_INIT_RIGHT_3", tir_sova), ("VIPER_INIT_RIGHT_3", tir_viper), 
    ("YORU_INIT_RIGHT_3", tir_yoru), 

    ("ASTRA_ULT_GREEN_RIGHT_3", tgu_astra), ("BREACH_ULT_GREEN_RIGHT_3", tgu_breach), ("BRIMSTONE_ULT_GREEN_RIGHT_3", tgu_brimstone), 
    ("CYPHER_ULT_GREEN_RIGHT_3", tgu_cypher), ("JETT_ULT_GREEN_RIGHT_3", tgu_jett), ("KAYO_ULT_GREEN_RIGHT_3", tgu_kayo), 
    ("KILLJOY_ULT_GREEN_RIGHT_3", tgu_killjoy), ("OMEN_ULT_GREEN_RIGHT_3", tgu_omen), ("PHOENIX_ULT_GREEN_RIGHT_3", tgu_phoenix), 
    ("RAZE_ULT_GREEN_RIGHT_3", tgu_raze), ("REYNA_ULT_GREEN_RIGHT_3", tgu_reyna), ("SAGE_ULT_GREEN_RIGHT_3", tgu_sage), 
    ("SKYE_ULT_GREEN_RIGHT_3", tgu_skye), ("SOVA_ULT_GREEN_RIGHT_3", tgu_sova), ("VIPER_ULT_GREEN_RIGHT_3", tgu_viper), 
    ("YORU_ULT_GREEN_RIGHT_3", tgu_yoru), 

    ("ASTRA_ULT_RED_RIGHT_3", tru_astra), ("BREACH_ULT_RED_RIGHT_3", tru_breach), ("BRIMSTONE_ULT_RED_RIGHT_3", tru_brimstone), 
    ("CYPHER_ULT_RED_RIGHT_3", tru_cypher), ("JETT_ULT_RED_RIGHT_3", tru_jett), ("KAYO_ULT_RED_RIGHT_3", tru_kayo), 
    ("KILLJOY_ULT_RED_RIGHT_3", tru_killjoy), ("OMEN_ULT_RED_RIGHT_3", tru_omen), ("PHOENIX_ULT_RED_RIGHT_3", tru_phoenix), 
    ("RAZE_ULT_RED_RIGHT_3", tru_raze), ("REYNA_ULT_RED_RIGHT_3", tru_reyna), ("SAGE_ULT_RED_RIGHT_3", tru_sage), 
    ("SKYE_ULT_RED_RIGHT_3", tru_skye), ("SOVA_ULT_RED_RIGHT_3", tru_sova), ("VIPER_ULT_RED_RIGHT_3", tru_viper), 
    ("YORU_ULT_RED_RIGHT_3", tru_yoru), 

    ("ULT_RED_0_6_RIGHT_3", ult_red_0_6), ("ULT_RED_0_7_RIGHT_3", ult_red_0_7), ("ULT_RED_0_8_RIGHT_3", ult_red_0_8), 
    ("ULT_RED_1_6_RIGHT_3", ult_red_1_6), ("ULT_RED_1_7_RIGHT_3", ult_red_1_7), ("ULT_RED_1_8_RIGHT_3", ult_red_1_8), 
    ("ULT_RED_2_6_RIGHT_3", ult_red_2_6), ("ULT_RED_2_7_RIGHT_3", ult_red_2_7), ("ULT_RED_2_8_RIGHT_3", ult_red_2_8), 
    ("ULT_RED_3_6_RIGHT_3", ult_red_3_6), ("ULT_RED_3_7_RIGHT_3", ult_red_3_7), ("ULT_RED_3_8_RIGHT_3", ult_red_3_8), 
    ("ULT_RED_4_6_RIGHT_3", ult_red_4_6), ("ULT_RED_4_7_RIGHT_3", ult_red_4_7), ("ULT_RED_4_8_RIGHT_3", ult_red_4_8), 
    ("ULT_RED_5_6_RIGHT_3", ult_red_5_6), ("ULT_RED_5_7_RIGHT_3", ult_red_5_7), ("ULT_RED_5_8_RIGHT_3", ult_red_5_8), 
    ("ULT_RED_6_7_RIGHT_3", ult_red_6_7), ("ULT_RED_6_8_RIGHT_3", ult_red_6_8), ("ULT_RED_7_8_RIGHT_3", ult_red_7_8), 

    ("ULT_GREEN_0_6_RIGHT_3", ult_green_0_6), ("ULT_GREEN_0_7_RIGHT_3", ult_green_0_7), ("ULT_GREEN_0_8_RIGHT_3", ult_green_0_8), 
    ("ULT_GREEN_1_6_RIGHT_3", ult_green_1_6), ("ULT_GREEN_1_7_RIGHT_3", ult_green_1_7), ("ULT_GREEN_1_8_RIGHT_3", ult_green_1_8), 
    ("ULT_GREEN_2_6_RIGHT_3", ult_green_2_6), ("ULT_GREEN_2_7_RIGHT_3", ult_green_2_7), ("ULT_GREEN_2_8_RIGHT_3", ult_green_2_8), 
    ("ULT_GREEN_3_6_RIGHT_3", ult_green_3_6), ("ULT_GREEN_3_7_RIGHT_3", ult_green_3_7), ("ULT_GREEN_3_8_RIGHT_3", ult_green_3_8), 
    ("ULT_GREEN_4_6_RIGHT_3", ult_green_4_6), ("ULT_GREEN_4_7_RIGHT_3", ult_green_4_7), ("ULT_GREEN_4_8_RIGHT_3", ult_green_4_8), 
    ("ULT_GREEN_5_6_RIGHT_3", ult_green_5_6), ("ULT_GREEN_5_7_RIGHT_3", ult_green_5_7), ("ULT_GREEN_5_8_RIGHT_3", ult_green_5_8), 
    ("ULT_GREEN_6_7_RIGHT_3", ult_green_6_7), ("ULT_GREEN_6_8_RIGHT_3", ult_green_6_8), ("ULT_GREEN_7_8_RIGHT_3", ult_green_7_8), 

    ]

  abil_templates_left_3 = [
    ("ABIL_0_LEFT_3", abil_0), ("ABIL_1_LEFT_3", abil_1), ("ABIL_2_LEFT_3", abil_2), ("ABIL_3_LEFT_3", abil_3), 

    ("ASTRA_ABIL_VERIF_LEFT_3", astra_abil_verif), ("ASTRA_ABIL_1_LEFT_3", astra_abil_1), ("ASTRA_ABIL_2_LEFT_3", astra_abil_2), 
    ("ASTRA_ABIL_3_LEFT_3", astra_abil_3), ("ASTRA_ABIL_4_LEFT_3", astra_abil_4), ("ASTRA_ABIL_5_LEFT_3", astra_abil_5), 

    ("SPIKE_HELD_LEFT_3", spike_held), 

    ("GREEN_0_LEFT_3", health_green_0), ("GREEN_1_LEFT_3", health_green_1), ("GREEN_2_LEFT_3", health_green_2), 
    ("GREEN_3_LEFT_3", health_green_3), ("GREEN_4_LEFT_3", health_green_4), ("GREEN_5_LEFT_3", health_green_5), 
    ("GREEN_6_LEFT_3", health_green_6), ("GREEN_7_LEFT_3", health_green_7), ("GREEN_8_LEFT_3", health_green_8), 
    ("GREEN_9_LEFT_3", health_green_9), ("GREEN_25_LEFT_3", health_green_25), ("GREEN_50_LEFT_3", health_green_50), 

    ("RED_0_LEFT_3", health_red_0), ("RED_1_LEFT_3", health_red_1), ("RED_2_LEFT_3", health_red_2), 
    ("RED_3_LEFT_3", health_red_3), ("RED_4_LEFT_3", health_red_4), ("RED_5_LEFT_3", health_red_5), 
    ("RED_6_LEFT_3", health_red_6), ("RED_7_LEFT_3", health_red_7), ("RED_8_LEFT_3", health_red_8), 
    ("RED_9_LEFT_3", health_red_9), ("RED_25_LEFT_3", health_red_25), ("RED_50_LEFT_3", health_red_50), 

    ("CLASSIC_LEFT_3", classic_left), ("FRENZY_LEFT_3", frenzy_left), ("GHOST_LEFT_3", ghost_left), 
    ("SHERIFF_LEFT_3", sheriff_left), ("SHORTY_LEFT_3", shorty_left), ("MARSHAL_LEFT_3", marshal_left), 
    ("STINGER_LEFT_3", stinger_left), ("SPECTRE_LEFT_3", spectre_left), ("BULLDOG_LEFT_3", bulldog_left), 
    ("JUDGE_LEFT_3", judge_left), ("GUARDIAN_LEFT_3", guardian_left), ("VANDAL_LEFT_3", vandal_left), 
    ("PHANTOM_LEFT_3", phantom_left), ("OPERATOR_LEFT_3", operator_left), ("ODIN_LEFT_3", odin_left), 
    ("ARES_LEFT_3", ares_left), ("BUCKY_LEFT_3", bucky_left)

    ]

  abil_templates_right_3 = [
    ("ABIL_0_RIGHT_3", abil_0), ("ABIL_1_RIGHT_3", abil_1), ("ABIL_2_RIGHT_3", abil_2), ("ABIL_3_RIGHT_3", abil_3), 

    ("ASTRA_ABIL_VERIF_RIGHT_3", astra_abil_verif), ("ASTRA_ABIL_1_RIGHT_3", astra_abil_1), ("ASTRA_ABIL_2_RIGHT_3", astra_abil_2), 
    ("ASTRA_ABIL_3_RIGHT_3", astra_abil_3), ("ASTRA_ABIL_4_RIGHT_3", astra_abil_4), ("ASTRA_ABIL_5_RIGHT_3", astra_abil_5), 

    ("SPIKE_HELD_RIGHT_3", spike_held), 

    ("GREEN_0_RIGHT_3", health_green_0), ("GREEN_1_RIGHT_3", health_green_1), ("GREEN_2_RIGHT_3", health_green_2), 
    ("GREEN_3_RIGHT_3", health_green_3), ("GREEN_4_RIGHT_3", health_green_4), ("GREEN_5_RIGHT_3", health_green_5), 
    ("GREEN_6_RIGHT_3", health_green_6), ("GREEN_7_RIGHT_3", health_green_7), ("GREEN_8_RIGHT_3", health_green_8), 
    ("GREEN_9_RIGHT_3", health_green_9), ("GREEN_25_RIGHT_3", health_green_25), ("GREEN_50_RIGHT_3", health_green_50), 

    ("RED_0_RIGHT_3", health_red_0), ("RED_1_RIGHT_3", health_red_1), ("RED_2_RIGHT_3", health_red_2), 
    ("RED_3_RIGHT_3", health_red_3), ("RED_4_RIGHT_3", health_red_4), ("RED_5_RIGHT_3", health_red_5), 
    ("RED_6_RIGHT_3", health_red_6), ("RED_7_RIGHT_3", health_red_7), ("RED_8_RIGHT_3", health_red_8), 
    ("RED_9_RIGHT_3", health_red_9), ("RED_25_RIGHT_3", health_red_25), ("RED_50_RIGHT_3", health_red_50), 

    ("CLASSIC_RIGHT_3", classic_right), ("FRENZY_RIGHT_3", frenzy_right), ("GHOST_RIGHT_3", ghost_right), 
    ("SHERIFF_RIGHT_3", sheriff_right), ("SHORTY_RIGHT_3", shorty_right), ("MARSHAL_RIGHT_3", marshal_right), 
    ("STINGER_RIGHT_3", stinger_right), ("SPECTRE_RIGHT_3", spectre_right), ("BULLDOG_RIGHT_3", bulldog_right), 
    ("JUDGE_RIGHT_3", judge_right), ("GUARDIAN_RIGHT_3", guardian_right), ("VANDAL_RIGHT_3", vandal_right), 
    ("PHANTOM_RIGHT_3", phantom_right), ("OPERATOR_RIGHT_3", operator_right), ("ODIN_RIGHT_3", odin_right), 
    ("ARES_RIGHT_3", ares_right), ("BUCKY_RIGHT_3", bucky_right)

    ]

  ult_templates_left_4 = [
    ("ASTRA_INIT_LEFT_4", til_astra), ("BREACH_INIT_LEFT_4", til_breach), ("BRIMSTONE_INIT_LEFT_4", til_brimstone), 
    ("CYPHER_INIT_LEFT_4", til_cypher),("JETT_INIT_LEFT_4", til_jett), ("KAYO_INIT_LEFT_4", til_kayo), 
    ("KILLJOY_INIT_LEFT_4", til_killjoy), ("OMEN_INIT_LEFT_4", til_omen), ("PHOENIX_INIT_LEFT_4", til_phoenix), 
    ("RAZE_INIT_LEFT_4", til_raze), ("REYNA_INIT_LEFT_4", til_reyna), ("SAGE_INIT_LEFT_4", til_sage), 
    ("SKYE_INIT_LEFT_4", til_skye), ("SOVA_INIT_LEFT_4", til_sova), ("VIPER_INIT_LEFT_4", til_viper), 
    ("YORU_INIT_LEFT_4", til_yoru), 

    ("ASTRA_ULT_GREEN_LEFT_4", tgu_astra), ("BREACH_ULT_GREEN_LEFT_4", tgu_breach), ("BRIMSTONE_ULT_GREEN_LEFT_4", tgu_brimstone), 
    ("CYPHER_ULT_GREEN_LEFT_4", tgu_cypher), ("JETT_ULT_GREEN_LEFT_4", tgu_jett), ("KAYO_ULT_GREEN_LEFT_4", tgu_kayo), 
    ("KILLJOY_ULT_GREEN_LEFT_4", tgu_killjoy), ("OMEN_ULT_GREEN_LEFT_4", tgu_omen), ("PHOENIX_ULT_GREEN_LEFT_4", tgu_phoenix), 
    ("RAZE_ULT_GREEN_LEFT_4", tgu_raze), ("REYNA_ULT_GREEN_LEFT_4", tgu_reyna), ("SAGE_ULT_GREEN_LEFT_4", tgu_sage), 
    ("SKYE_ULT_GREEN_LEFT_4", tgu_skye), ("SOVA_ULT_GREEN_LEFT_4", tgu_sova), ("VIPER_ULT_GREEN_LEFT_4", tgu_viper), 
    ("YORU_ULT_GREEN_LEFT_4", tgu_yoru), 

    ("ASTRA_ULT_RED_LEFT_4", tru_astra), ("BREACH_ULT_RED_LEFT_4", tru_breach), ("BRIMSTONE_ULT_RED_LEFT_4", tru_brimstone), 
    ("CYPHER_ULT_RED_LEFT_4", tru_cypher), ("JETT_ULT_RED_LEFT_4", tru_jett), ("KAYO_ULT_RED_LEFT_4", tru_kayo), 
    ("KILLJOY_ULT_RED_LEFT_4", tru_killjoy), ("OMEN_ULT_RED_LEFT_4", tru_omen), ("PHOENIX_ULT_RED_LEFT_4", tru_phoenix), 
    ("RAZE_ULT_RED_LEFT_4", tru_raze), ("REYNA_ULT_RED_LEFT_4", tru_reyna), ("SAGE_ULT_RED_LEFT_4", tru_sage), 
    ("SKYE_ULT_RED_LEFT_4", tru_skye), ("SOVA_ULT_RED_LEFT_4", tru_sova), ("VIPER_ULT_RED_LEFT_4", tru_viper), 
    ("YORU_ULT_RED_LEFT_4", tru_yoru), 

    ("ULT_RED_0_6_LEFT_4", ult_red_0_6), ("ULT_RED_0_7_LEFT_4", ult_red_0_7), ("ULT_RED_0_8_LEFT_4", ult_red_0_8), 
    ("ULT_RED_1_6_LEFT_4", ult_red_1_6), ("ULT_RED_1_7_LEFT_4", ult_red_1_7), ("ULT_RED_1_8_LEFT_4", ult_red_1_8), 
    ("ULT_RED_2_6_LEFT_4", ult_red_2_6), ("ULT_RED_2_7_LEFT_4", ult_red_2_7), ("ULT_RED_2_8_LEFT_4", ult_red_2_8), 
    ("ULT_RED_3_6_LEFT_4", ult_red_3_6), ("ULT_RED_3_7_LEFT_4", ult_red_3_7), ("ULT_RED_3_8_LEFT_4", ult_red_3_8), 
    ("ULT_RED_4_6_LEFT_4", ult_red_4_6), ("ULT_RED_4_7_LEFT_4", ult_red_4_7), ("ULT_RED_4_8_LEFT_4", ult_red_4_8), 
    ("ULT_RED_5_6_LEFT_4", ult_red_5_6), ("ULT_RED_5_7_LEFT_4", ult_red_5_7), ("ULT_RED_5_8_LEFT_4", ult_red_5_8), 
    ("ULT_RED_6_7_LEFT_4", ult_red_6_7), ("ULT_RED_6_8_LEFT_4", ult_red_6_8), ("ULT_RED_7_8_LEFT_4", ult_red_7_8), 

    ("ULT_GREEN_0_6_LEFT_4", ult_green_0_6), ("ULT_GREEN_0_7_LEFT_4", ult_green_0_7), ("ULT_GREEN_0_8_LEFT_4", ult_green_0_8), 
    ("ULT_GREEN_1_6_LEFT_4", ult_green_1_6), ("ULT_GREEN_1_7_LEFT_4", ult_green_1_7), ("ULT_GREEN_1_8_LEFT_4", ult_green_1_8), 
    ("ULT_GREEN_2_6_LEFT_4", ult_green_2_6), ("ULT_GREEN_2_7_LEFT_4", ult_green_2_7), ("ULT_GREEN_2_8_LEFT_4", ult_green_2_8), 
    ("ULT_GREEN_3_6_LEFT_4", ult_green_3_6), ("ULT_GREEN_3_7_LEFT_4", ult_green_3_7), ("ULT_GREEN_3_8_LEFT_4", ult_green_3_8), 
    ("ULT_GREEN_4_6_LEFT_4", ult_green_4_6), ("ULT_GREEN_4_7_LEFT_4", ult_green_4_7), ("ULT_GREEN_4_8_LEFT_4", ult_green_4_8), 
    ("ULT_GREEN_5_6_LEFT_4", ult_green_5_6), ("ULT_GREEN_5_7_LEFT_4", ult_green_5_7), ("ULT_GREEN_5_8_LEFT_4", ult_green_5_8), 
    ("ULT_GREEN_6_7_LEFT_4", ult_green_6_7), ("ULT_GREEN_6_8_LEFT_4", ult_green_6_8), ("ULT_GREEN_7_8_LEFT_4", ult_green_7_8), 

    ]

  ult_templates_right_4 = [
    ("ASTRA_INIT_RIGHT_4", tir_astra), ("BREACH_INIT_RIGHT_4", tir_breach), ("BRIMSTONE_INIT_RIGHT_4", tir_brimstone), 
    ("CYPHER_INIT_RIGHT_4", tir_cypher), ("JETT_INIT_RIGHT_4", tir_jett), ("KAYO_INIT_RIGHT_4", tir_kayo), 
    ("KILLJOY_INIT_RIGHT_4", tir_killjoy), ("OMEN_INIT_RIGHT_4", tir_omen), ("PHOENIX_INIT_RIGHT_4", tir_phoenix), 
    ("RAZE_INIT_RIGHT_4", tir_raze), ("REYNA_INIT_RIGHT_4", tir_reyna), ("SAGE_INIT_RIGHT_4", tir_sage), 
    ("SKYE_INIT_RIGHT_4", tir_skye), ("SOVA_INIT_RIGHT_4", tir_sova), ("VIPER_INIT_RIGHT_4", tir_viper), 
    ("YORU_INIT_RIGHT_4", tir_yoru), 

    ("ASTRA_ULT_GREEN_RIGHT_4", tgu_astra), ("BREACH_ULT_GREEN_RIGHT_4", tgu_breach), ("BRIMSTONE_ULT_GREEN_RIGHT_4", tgu_brimstone), 
    ("CYPHER_ULT_GREEN_RIGHT_4", tgu_cypher), ("JETT_ULT_GREEN_RIGHT_4", tgu_jett), ("KAYO_ULT_GREEN_RIGHT_4", tgu_kayo), 
    ("KILLJOY_ULT_GREEN_RIGHT_4", tgu_killjoy), ("OMEN_ULT_GREEN_RIGHT_4", tgu_omen), ("PHOENIX_ULT_GREEN_RIGHT_4", tgu_phoenix), 
    ("RAZE_ULT_GREEN_RIGHT_4", tgu_raze), ("REYNA_ULT_GREEN_RIGHT_4", tgu_reyna), ("SAGE_ULT_GREEN_RIGHT_4", tgu_sage), 
    ("SKYE_ULT_GREEN_RIGHT_4", tgu_skye), ("SOVA_ULT_GREEN_RIGHT_4", tgu_sova), ("VIPER_ULT_GREEN_RIGHT_4", tgu_viper), 
    ("YORU_ULT_GREEN_RIGHT_4", tgu_yoru), 

    ("ASTRA_ULT_RED_RIGHT_4", tru_astra), ("BREACH_ULT_RED_RIGHT_4", tru_breach), ("BRIMSTONE_ULT_RED_RIGHT_4", tru_brimstone), 
    ("CYPHER_ULT_RED_RIGHT_4", tru_cypher), ("JETT_ULT_RED_RIGHT_4", tru_jett), ("KAYO_ULT_RED_RIGHT_4", tru_kayo), 
    ("KILLJOY_ULT_RED_RIGHT_4", tru_killjoy), ("OMEN_ULT_RED_RIGHT_4", tru_omen), ("PHOENIX_ULT_RED_RIGHT_4", tru_phoenix), 
    ("RAZE_ULT_RED_RIGHT_4", tru_raze), ("REYNA_ULT_RED_RIGHT_4", tru_reyna), ("SAGE_ULT_RED_RIGHT_4", tru_sage), 
    ("SKYE_ULT_RED_RIGHT_4", tru_skye), ("SOVA_ULT_RED_RIGHT_4", tru_sova), ("VIPER_ULT_RED_RIGHT_4", tru_viper), 
    ("YORU_ULT_RED_RIGHT_4", tru_yoru), 

    ("ULT_RED_0_6_RIGHT_4", ult_red_0_6), ("ULT_RED_0_7_RIGHT_4", ult_red_0_7), ("ULT_RED_0_8_RIGHT_4", ult_red_0_8), 
    ("ULT_RED_1_6_RIGHT_4", ult_red_1_6), ("ULT_RED_1_7_RIGHT_4", ult_red_1_7), ("ULT_RED_1_8_RIGHT_4", ult_red_1_8), 
    ("ULT_RED_2_6_RIGHT_4", ult_red_2_6), ("ULT_RED_2_7_RIGHT_4", ult_red_2_7), ("ULT_RED_2_8_RIGHT_4", ult_red_2_8), 
    ("ULT_RED_3_6_RIGHT_4", ult_red_3_6), ("ULT_RED_3_7_RIGHT_4", ult_red_3_7), ("ULT_RED_3_8_RIGHT_4", ult_red_3_8), 
    ("ULT_RED_4_6_RIGHT_4", ult_red_4_6), ("ULT_RED_4_7_RIGHT_4", ult_red_4_7), ("ULT_RED_4_8_RIGHT_4", ult_red_4_8), 
    ("ULT_RED_5_6_RIGHT_4", ult_red_5_6), ("ULT_RED_5_7_RIGHT_4", ult_red_5_7), ("ULT_RED_5_8_RIGHT_4", ult_red_5_8), 
    ("ULT_RED_6_7_RIGHT_4", ult_red_6_7), ("ULT_RED_6_8_RIGHT_4", ult_red_6_8), ("ULT_RED_7_8_RIGHT_4", ult_red_7_8), 

    ("ULT_GREEN_0_6_RIGHT_4", ult_green_0_6), ("ULT_GREEN_0_7_RIGHT_4", ult_green_0_7), ("ULT_GREEN_0_8_RIGHT_4", ult_green_0_8), 
    ("ULT_GREEN_1_6_RIGHT_4", ult_green_1_6), ("ULT_GREEN_1_7_RIGHT_4", ult_green_1_7), ("ULT_GREEN_1_8_RIGHT_4", ult_green_1_8), 
    ("ULT_GREEN_2_6_RIGHT_4", ult_green_2_6), ("ULT_GREEN_2_7_RIGHT_4", ult_green_2_7), ("ULT_GREEN_2_8_RIGHT_4", ult_green_2_8), 
    ("ULT_GREEN_3_6_RIGHT_4", ult_green_3_6), ("ULT_GREEN_3_7_RIGHT_4", ult_green_3_7), ("ULT_GREEN_3_8_RIGHT_4", ult_green_3_8), 
    ("ULT_GREEN_4_6_RIGHT_4", ult_green_4_6), ("ULT_GREEN_4_7_RIGHT_4", ult_green_4_7), ("ULT_GREEN_4_8_RIGHT_4", ult_green_4_8), 
    ("ULT_GREEN_5_6_RIGHT_4", ult_green_5_6), ("ULT_GREEN_5_7_RIGHT_4", ult_green_5_7), ("ULT_GREEN_5_8_RIGHT_4", ult_green_5_8), 
    ("ULT_GREEN_6_7_RIGHT_4", ult_green_6_7), ("ULT_GREEN_6_8_RIGHT_4", ult_green_6_8), ("ULT_GREEN_7_8_RIGHT_4", ult_green_7_8), 

    ]

  abil_templates_left_4 = [
    ("ABIL_0_LEFT_4", abil_0), ("ABIL_1_LEFT_4", abil_1), ("ABIL_2_LEFT_4", abil_2), ("ABIL_3_LEFT_4", abil_3), 

    ("ASTRA_ABIL_VERIF_LEFT_4", astra_abil_verif), ("ASTRA_ABIL_1_LEFT_4", astra_abil_1), ("ASTRA_ABIL_2_LEFT_4", astra_abil_2), 
    ("ASTRA_ABIL_3_LEFT_4", astra_abil_3), ("ASTRA_ABIL_4_LEFT_4", astra_abil_4), ("ASTRA_ABIL_5_LEFT_4", astra_abil_5), 

    ("SPIKE_HELD_LEFT_4", spike_held), 

    ("GREEN_0_LEFT_4", health_green_0), ("GREEN_1_LEFT_4", health_green_1), ("GREEN_2_LEFT_4", health_green_2), 
    ("GREEN_3_LEFT_4", health_green_3), ("GREEN_4_LEFT_4", health_green_4), ("GREEN_5_LEFT_4", health_green_5), 
    ("GREEN_6_LEFT_4", health_green_6), ("GREEN_7_LEFT_4", health_green_7), ("GREEN_8_LEFT_4", health_green_8), 
    ("GREEN_9_LEFT_4", health_green_9), ("GREEN_25_LEFT_4", health_green_25), ("GREEN_50_LEFT_4", health_green_50), 

    ("RED_0_LEFT_4", health_red_0), ("RED_1_LEFT_4", health_red_1), ("RED_2_LEFT_4", health_red_2), 
    ("RED_3_LEFT_4", health_red_3), ("RED_4_LEFT_4", health_red_4), ("RED_5_LEFT_4", health_red_5), 
    ("RED_6_LEFT_4", health_red_6), ("RED_7_LEFT_4", health_red_7), ("RED_8_LEFT_4", health_red_8), 
    ("RED_9_LEFT_4", health_red_9), ("RED_25_LEFT_4", health_red_25), ("RED_50_LEFT_4", health_red_50), 

    ("CLASSIC_LEFT_4", classic_left), ("FRENZY_LEFT_4", frenzy_left), ("GHOST_LEFT_4", ghost_left), 
    ("SHERIFF_LEFT_4", sheriff_left), ("SHORTY_LEFT_4", shorty_left), ("MARSHAL_LEFT_4", marshal_left), 
    ("STINGER_LEFT_4", stinger_left), ("SPECTRE_LEFT_4", spectre_left), ("BULLDOG_LEFT_4", bulldog_left), 
    ("JUDGE_LEFT_4", judge_left), ("GUARDIAN_LEFT_4", guardian_left), ("VANDAL_LEFT_4", vandal_left), 
    ("PHANTOM_LEFT_4", phantom_left), ("OPERATOR_LEFT_4", operator_left), ("ODIN_LEFT_4", odin_left), 
    ("ARES_LEFT_4", ares_left), ("BUCKY_LEFT_4", bucky_left)

    ]

  abil_templates_right_4 = [
    ("ABIL_0_RIGHT_4", abil_0), ("ABIL_1_RIGHT_4", abil_1), ("ABIL_2_RIGHT_4", abil_2), ("ABIL_3_RIGHT_4", abil_3), 

    ("ASTRA_ABIL_VERIF_RIGHT_4", astra_abil_verif), ("ASTRA_ABIL_1_RIGHT_4", astra_abil_1), ("ASTRA_ABIL_2_RIGHT_4", astra_abil_2), 
    ("ASTRA_ABIL_3_RIGHT_4", astra_abil_3), ("ASTRA_ABIL_4_RIGHT_4", astra_abil_4), ("ASTRA_ABIL_5_RIGHT_4", astra_abil_5), 

    ("SPIKE_HELD_RIGHT_4", spike_held), 

    ("GREEN_0_RIGHT_4", health_green_0), ("GREEN_1_RIGHT_4", health_green_1), ("GREEN_2_RIGHT_4", health_green_2), 
    ("GREEN_3_RIGHT_4", health_green_3), ("GREEN_4_RIGHT_4", health_green_4), ("GREEN_5_RIGHT_4", health_green_5), 
    ("GREEN_6_RIGHT_4", health_green_6), ("GREEN_7_RIGHT_4", health_green_7), ("GREEN_8_RIGHT_4", health_green_8), 
    ("GREEN_9_RIGHT_4", health_green_9), ("GREEN_25_RIGHT_4", health_green_25), ("GREEN_50_RIGHT_4", health_green_50), 

    ("RED_0_RIGHT_4", health_red_0), ("RED_1_RIGHT_4", health_red_1), ("RED_2_RIGHT_4", health_red_2), 
    ("RED_3_RIGHT_4", health_red_3), ("RED_4_RIGHT_4", health_red_4), ("RED_5_RIGHT_4", health_red_5), 
    ("RED_6_RIGHT_4", health_red_6), ("RED_7_RIGHT_4", health_red_7), ("RED_8_RIGHT_4", health_red_8), 
    ("RED_9_RIGHT_4", health_red_9), ("RED_25_RIGHT_4", health_red_25), ("RED_50_RIGHT_4", health_red_50), 

    ("CLASSIC_RIGHT_4", classic_right), ("FRENZY_RIGHT_4", frenzy_right), ("GHOST_RIGHT_4", ghost_right), 
    ("SHERIFF_RIGHT_4", sheriff_right), ("SHORTY_RIGHT_4", shorty_right), ("MARSHAL_RIGHT_4", marshal_right), 
    ("STINGER_RIGHT_4", stinger_right), ("SPECTRE_RIGHT_4", spectre_right), ("BULLDOG_RIGHT_4", bulldog_right), 
    ("JUDGE_RIGHT_4", judge_right), ("GUARDIAN_RIGHT_4", guardian_right), ("VANDAL_RIGHT_4", vandal_right), 
    ("PHANTOM_RIGHT_4", phantom_right), ("OPERATOR_RIGHT_4", operator_right), ("ODIN_RIGHT_4", odin_right), 
    ("ARES_RIGHT_4", ares_right), ("BUCKY_RIGHT_4", bucky_right)

    ]

  ult_templates_left_5 = [
    ("ASTRA_INIT_LEFT_5", til_astra), ("BREACH_INIT_LEFT_5", til_breach), ("BRIMSTONE_INIT_LEFT_5", til_brimstone), 
    ("CYPHER_INIT_LEFT_5", til_cypher),("JETT_INIT_LEFT_5", til_jett), ("KAYO_INIT_LEFT_5", til_kayo), 
    ("KILLJOY_INIT_LEFT_5", til_killjoy), ("OMEN_INIT_LEFT_5", til_omen), ("PHOENIX_INIT_LEFT_5", til_phoenix), 
    ("RAZE_INIT_LEFT_5", til_raze), ("REYNA_INIT_LEFT_5", til_reyna), ("SAGE_INIT_LEFT_5", til_sage), 
    ("SKYE_INIT_LEFT_5", til_skye), ("SOVA_INIT_LEFT_5", til_sova), ("VIPER_INIT_LEFT_5", til_viper), 
    ("YORU_INIT_LEFT_5", til_yoru), 

    ("ASTRA_ULT_GREEN_LEFT_5", tgu_astra), ("BREACH_ULT_GREEN_LEFT_5", tgu_breach), ("BRIMSTONE_ULT_GREEN_LEFT_5", tgu_brimstone), 
    ("CYPHER_ULT_GREEN_LEFT_5", tgu_cypher), ("JETT_ULT_GREEN_LEFT_5", tgu_jett), ("KAYO_ULT_GREEN_LEFT_5", tgu_kayo), 
    ("KILLJOY_ULT_GREEN_LEFT_5", tgu_killjoy), ("OMEN_ULT_GREEN_LEFT_5", tgu_omen), ("PHOENIX_ULT_GREEN_LEFT_5", tgu_phoenix), 
    ("RAZE_ULT_GREEN_LEFT_5", tgu_raze), ("REYNA_ULT_GREEN_LEFT_5", tgu_reyna), ("SAGE_ULT_GREEN_LEFT_5", tgu_sage), 
    ("SKYE_ULT_GREEN_LEFT_5", tgu_skye), ("SOVA_ULT_GREEN_LEFT_5", tgu_sova), ("VIPER_ULT_GREEN_LEFT_5", tgu_viper), 
    ("YORU_ULT_GREEN_LEFT_5", tgu_yoru), 

    ("ASTRA_ULT_RED_LEFT_5", tru_astra), ("BREACH_ULT_RED_LEFT_5", tru_breach), ("BRIMSTONE_ULT_RED_LEFT_5", tru_brimstone), 
    ("CYPHER_ULT_RED_LEFT_5", tru_cypher), ("JETT_ULT_RED_LEFT_5", tru_jett), ("KAYO_ULT_RED_LEFT_5", tru_kayo), 
    ("KILLJOY_ULT_RED_LEFT_5", tru_killjoy), ("OMEN_ULT_RED_LEFT_5", tru_omen), ("PHOENIX_ULT_RED_LEFT_5", tru_phoenix), 
    ("RAZE_ULT_RED_LEFT_5", tru_raze), ("REYNA_ULT_RED_LEFT_5", tru_reyna), ("SAGE_ULT_RED_LEFT_5", tru_sage), 
    ("SKYE_ULT_RED_LEFT_5", tru_skye), ("SOVA_ULT_RED_LEFT_5", tru_sova), ("VIPER_ULT_RED_LEFT_5", tru_viper), 
    ("YORU_ULT_RED_LEFT_5", tru_yoru), 

    ("ULT_RED_0_6_LEFT_5", ult_red_0_6), ("ULT_RED_0_7_LEFT_5", ult_red_0_7), ("ULT_RED_0_8_LEFT_5", ult_red_0_8), 
    ("ULT_RED_1_6_LEFT_5", ult_red_1_6), ("ULT_RED_1_7_LEFT_5", ult_red_1_7), ("ULT_RED_1_8_LEFT_5", ult_red_1_8), 
    ("ULT_RED_2_6_LEFT_5", ult_red_2_6), ("ULT_RED_2_7_LEFT_5", ult_red_2_7), ("ULT_RED_2_8_LEFT_5", ult_red_2_8), 
    ("ULT_RED_3_6_LEFT_5", ult_red_3_6), ("ULT_RED_3_7_LEFT_5", ult_red_3_7), ("ULT_RED_3_8_LEFT_5", ult_red_3_8), 
    ("ULT_RED_4_6_LEFT_5", ult_red_4_6), ("ULT_RED_4_7_LEFT_5", ult_red_4_7), ("ULT_RED_4_8_LEFT_5", ult_red_4_8), 
    ("ULT_RED_5_6_LEFT_5", ult_red_5_6), ("ULT_RED_5_7_LEFT_5", ult_red_5_7), ("ULT_RED_5_8_LEFT_5", ult_red_5_8), 
    ("ULT_RED_6_7_LEFT_5", ult_red_6_7), ("ULT_RED_6_8_LEFT_5", ult_red_6_8), ("ULT_RED_7_8_LEFT_5", ult_red_7_8), 

    ("ULT_GREEN_0_6_LEFT_5", ult_green_0_6), ("ULT_GREEN_0_7_LEFT_5", ult_green_0_7), ("ULT_GREEN_0_8_LEFT_5", ult_green_0_8), 
    ("ULT_GREEN_1_6_LEFT_5", ult_green_1_6), ("ULT_GREEN_1_7_LEFT_5", ult_green_1_7), ("ULT_GREEN_1_8_LEFT_5", ult_green_1_8), 
    ("ULT_GREEN_2_6_LEFT_5", ult_green_2_6), ("ULT_GREEN_2_7_LEFT_5", ult_green_2_7), ("ULT_GREEN_2_8_LEFT_5", ult_green_2_8), 
    ("ULT_GREEN_3_6_LEFT_5", ult_green_3_6), ("ULT_GREEN_3_7_LEFT_5", ult_green_3_7), ("ULT_GREEN_3_8_LEFT_5", ult_green_3_8), 
    ("ULT_GREEN_4_6_LEFT_5", ult_green_4_6), ("ULT_GREEN_4_7_LEFT_5", ult_green_4_7), ("ULT_GREEN_4_8_LEFT_5", ult_green_4_8), 
    ("ULT_GREEN_5_6_LEFT_5", ult_green_5_6), ("ULT_GREEN_5_7_LEFT_5", ult_green_5_7), ("ULT_GREEN_5_8_LEFT_5", ult_green_5_8), 
    ("ULT_GREEN_6_7_LEFT_5", ult_green_6_7), ("ULT_GREEN_6_8_LEFT_5", ult_green_6_8), ("ULT_GREEN_7_8_LEFT_5", ult_green_7_8), 

    ]

  ult_templates_right_5 = [
    ("ASTRA_INIT_RIGHT_5", tir_astra), ("BREACH_INIT_RIGHT_5", tir_breach), ("BRIMSTONE_INIT_RIGHT_5", tir_brimstone), 
    ("CYPHER_INIT_RIGHT_5", tir_cypher), ("JETT_INIT_RIGHT_5", tir_jett), ("KAYO_INIT_RIGHT_5", tir_kayo), 
    ("KILLJOY_INIT_RIGHT_5", tir_killjoy), ("OMEN_INIT_RIGHT_5", tir_omen), ("PHOENIX_INIT_RIGHT_5", tir_phoenix), 
    ("RAZE_INIT_RIGHT_5", tir_raze), ("REYNA_INIT_RIGHT_5", tir_reyna), ("SAGE_INIT_RIGHT_5", tir_sage), 
    ("SKYE_INIT_RIGHT_5", tir_skye), ("SOVA_INIT_RIGHT_5", tir_sova), ("VIPER_INIT_RIGHT_5", tir_viper), 
    ("YORU_INIT_RIGHT_5", tir_yoru), 

    ("ASTRA_ULT_GREEN_RIGHT_5", tgu_astra), ("BREACH_ULT_GREEN_RIGHT_5", tgu_breach), ("BRIMSTONE_ULT_GREEN_RIGHT_5", tgu_brimstone), 
    ("CYPHER_ULT_GREEN_RIGHT_5", tgu_cypher), ("JETT_ULT_GREEN_RIGHT_5", tgu_jett), ("KAYO_ULT_GREEN_RIGHT_5", tgu_kayo), 
    ("KILLJOY_ULT_GREEN_RIGHT_5", tgu_killjoy), ("OMEN_ULT_GREEN_RIGHT_5", tgu_omen), ("PHOENIX_ULT_GREEN_RIGHT_5", tgu_phoenix), 
    ("RAZE_ULT_GREEN_RIGHT_5", tgu_raze), ("REYNA_ULT_GREEN_RIGHT_5", tgu_reyna), ("SAGE_ULT_GREEN_RIGHT_5", tgu_sage), 
    ("SKYE_ULT_GREEN_RIGHT_5", tgu_skye), ("SOVA_ULT_GREEN_RIGHT_5", tgu_sova), ("VIPER_ULT_GREEN_RIGHT_5", tgu_viper), 
    ("YORU_ULT_GREEN_RIGHT_5", tgu_yoru), 

    ("ASTRA_ULT_RED_RIGHT_5", tru_astra), ("BREACH_ULT_RED_RIGHT_5", tru_breach), ("BRIMSTONE_ULT_RED_RIGHT_5", tru_brimstone), 
    ("CYPHER_ULT_RED_RIGHT_5", tru_cypher), ("JETT_ULT_RED_RIGHT_5", tru_jett), ("KAYO_ULT_RED_RIGHT_5", tru_kayo), 
    ("KILLJOY_ULT_RED_RIGHT_5", tru_killjoy), ("OMEN_ULT_RED_RIGHT_5", tru_omen), ("PHOENIX_ULT_RED_RIGHT_5", tru_phoenix), 
    ("RAZE_ULT_RED_RIGHT_5", tru_raze), ("REYNA_ULT_RED_RIGHT_5", tru_reyna), ("SAGE_ULT_RED_RIGHT_5", tru_sage), 
    ("SKYE_ULT_RED_RIGHT_5", tru_skye), ("SOVA_ULT_RED_RIGHT_5", tru_sova), ("VIPER_ULT_RED_RIGHT_5", tru_viper), 
    ("YORU_ULT_RED_RIGHT_5", tru_yoru), 

    ("ULT_RED_0_6_RIGHT_5", ult_red_0_6), ("ULT_RED_0_7_RIGHT_5", ult_red_0_7), ("ULT_RED_0_8_RIGHT_5", ult_red_0_8), 
    ("ULT_RED_1_6_RIGHT_5", ult_red_1_6), ("ULT_RED_1_7_RIGHT_5", ult_red_1_7), ("ULT_RED_1_8_RIGHT_5", ult_red_1_8), 
    ("ULT_RED_2_6_RIGHT_5", ult_red_2_6), ("ULT_RED_2_7_RIGHT_5", ult_red_2_7), ("ULT_RED_2_8_RIGHT_5", ult_red_2_8), 
    ("ULT_RED_3_6_RIGHT_5", ult_red_3_6), ("ULT_RED_3_7_RIGHT_5", ult_red_3_7), ("ULT_RED_3_8_RIGHT_5", ult_red_3_8), 
    ("ULT_RED_4_6_RIGHT_5", ult_red_4_6), ("ULT_RED_4_7_RIGHT_5", ult_red_4_7), ("ULT_RED_4_8_RIGHT_5", ult_red_4_8), 
    ("ULT_RED_5_6_RIGHT_5", ult_red_5_6), ("ULT_RED_5_7_RIGHT_5", ult_red_5_7), ("ULT_RED_5_8_RIGHT_5", ult_red_5_8), 
    ("ULT_RED_6_7_RIGHT_5", ult_red_6_7), ("ULT_RED_6_8_RIGHT_5", ult_red_6_8), ("ULT_RED_7_8_RIGHT_5", ult_red_7_8), 

    ("ULT_GREEN_0_6_RIGHT_5", ult_green_0_6), ("ULT_GREEN_0_7_RIGHT_5", ult_green_0_7), ("ULT_GREEN_0_8_RIGHT_5", ult_green_0_8), 
    ("ULT_GREEN_1_6_RIGHT_5", ult_green_1_6), ("ULT_GREEN_1_7_RIGHT_5", ult_green_1_7), ("ULT_GREEN_1_8_RIGHT_5", ult_green_1_8), 
    ("ULT_GREEN_2_6_RIGHT_5", ult_green_2_6), ("ULT_GREEN_2_7_RIGHT_5", ult_green_2_7), ("ULT_GREEN_2_8_RIGHT_5", ult_green_2_8), 
    ("ULT_GREEN_3_6_RIGHT_5", ult_green_3_6), ("ULT_GREEN_3_7_RIGHT_5", ult_green_3_7), ("ULT_GREEN_3_8_RIGHT_5", ult_green_3_8), 
    ("ULT_GREEN_4_6_RIGHT_5", ult_green_4_6), ("ULT_GREEN_4_7_RIGHT_5", ult_green_4_7), ("ULT_GREEN_4_8_RIGHT_5", ult_green_4_8), 
    ("ULT_GREEN_5_6_RIGHT_5", ult_green_5_6), ("ULT_GREEN_5_7_RIGHT_5", ult_green_5_7), ("ULT_GREEN_5_8_RIGHT_5", ult_green_5_8), 
    ("ULT_GREEN_6_7_RIGHT_5", ult_green_6_7), ("ULT_GREEN_6_8_RIGHT_5", ult_green_6_8), ("ULT_GREEN_7_8_RIGHT_5", ult_green_7_8), 

    ]

  abil_templates_left_5 = [
    ("ABIL_0_LEFT_5", abil_0), ("ABIL_1_LEFT_5", abil_1), ("ABIL_2_LEFT_5", abil_2), ("ABIL_3_LEFT_5", abil_3), 

    ("ASTRA_ABIL_VERIF_LEFT_5", astra_abil_verif), ("ASTRA_ABIL_1_LEFT_5", astra_abil_1), ("ASTRA_ABIL_2_LEFT_5", astra_abil_2), 
    ("ASTRA_ABIL_3_LEFT_5", astra_abil_3), ("ASTRA_ABIL_4_LEFT_5", astra_abil_4), ("ASTRA_ABIL_5_LEFT_5", astra_abil_5), 

    ("SPIKE_HELD_LEFT_5", spike_held), 

    ("GREEN_0_LEFT_5", health_green_0), ("GREEN_1_LEFT_5", health_green_1), ("GREEN_2_LEFT_5", health_green_2), 
    ("GREEN_3_LEFT_5", health_green_3), ("GREEN_4_LEFT_5", health_green_4), ("GREEN_5_LEFT_5", health_green_5), 
    ("GREEN_6_LEFT_5", health_green_6), ("GREEN_7_LEFT_5", health_green_7), ("GREEN_8_LEFT_5", health_green_8), 
    ("GREEN_9_LEFT_5", health_green_9), ("GREEN_25_LEFT_5", health_green_25), ("GREEN_50_LEFT_5", health_green_50), 

    ("RED_0_LEFT_5", health_red_0), ("RED_1_LEFT_5", health_red_1), ("RED_2_LEFT_5", health_red_2), 
    ("RED_3_LEFT_5", health_red_3), ("RED_4_LEFT_5", health_red_4), ("RED_5_LEFT_5", health_red_5), 
    ("RED_6_LEFT_5", health_red_6), ("RED_7_LEFT_5", health_red_7), ("RED_8_LEFT_5", health_red_8), 
    ("RED_9_LEFT_5", health_red_9), ("RED_25_LEFT_5", health_red_25), ("RED_50_LEFT_5", health_red_50), 

    ("CLASSIC_LEFT_5", classic_left), ("FRENZY_LEFT_5", frenzy_left), ("GHOST_LEFT_5", ghost_left), 
    ("SHERIFF_LEFT_5", sheriff_left), ("SHORTY_LEFT_5", shorty_left), ("MARSHAL_LEFT_5", marshal_left), 
    ("STINGER_LEFT_5", stinger_left), ("SPECTRE_LEFT_5", spectre_left), ("BULLDOG_LEFT_5", bulldog_left), 
    ("JUDGE_LEFT_5", judge_left), ("GUARDIAN_LEFT_5", guardian_left), ("VANDAL_LEFT_5", vandal_left), 
    ("PHANTOM_LEFT_5", phantom_left), ("OPERATOR_LEFT_5", operator_left), ("ODIN_LEFT_5", odin_left), 
    ("ARES_LEFT_5", ares_left), ("BUCKY_LEFT_5", bucky_left)

    ]

  abil_templates_right_5 = [
    ("ABIL_0_RIGHT_5", abil_0), ("ABIL_1_RIGHT_5", abil_1), ("ABIL_2_RIGHT_5", abil_2), ("ABIL_3_RIGHT_5", abil_3), 

    ("ASTRA_ABIL_VERIF_RIGHT_5", astra_abil_verif), ("ASTRA_ABIL_1_RIGHT_5", astra_abil_1), ("ASTRA_ABIL_2_RIGHT_5", astra_abil_2), 
    ("ASTRA_ABIL_3_RIGHT_5", astra_abil_3), ("ASTRA_ABIL_4_RIGHT_5", astra_abil_4), ("ASTRA_ABIL_5_RIGHT_5", astra_abil_5), 

    ("SPIKE_HELD_RIGHT_5", spike_held), 

    ("GREEN_0_RIGHT_5", health_green_0), ("GREEN_1_RIGHT_5", health_green_1), ("GREEN_2_RIGHT_5", health_green_2), 
    ("GREEN_3_RIGHT_5", health_green_3), ("GREEN_4_RIGHT_5", health_green_4), ("GREEN_5_RIGHT_5", health_green_5), 
    ("GREEN_6_RIGHT_5", health_green_6), ("GREEN_7_RIGHT_5", health_green_7), ("GREEN_8_RIGHT_5", health_green_8), 
    ("GREEN_9_RIGHT_5", health_green_9), ("GREEN_25_RIGHT_5", health_green_25), ("GREEN_50_RIGHT_5", health_green_50), 

    ("RED_0_RIGHT_5", health_red_0), ("RED_1_RIGHT_5", health_red_1), ("RED_2_RIGHT_5", health_red_2), 
    ("RED_3_RIGHT_5", health_red_3), ("RED_4_RIGHT_5", health_red_4), ("RED_5_RIGHT_5", health_red_5), 
    ("RED_6_RIGHT_5", health_red_6), ("RED_7_RIGHT_5", health_red_7), ("RED_8_RIGHT_5", health_red_8), 
    ("RED_9_RIGHT_5", health_red_9), ("RED_25_RIGHT_5", health_red_25), ("RED_50_RIGHT_5", health_red_50), 

    ("CLASSIC_RIGHT_5", classic_right), ("FRENZY_RIGHT_5", frenzy_right), ("GHOST_RIGHT_5", ghost_right), 
    ("SHERIFF_RIGHT_5", sheriff_right), ("SHORTY_RIGHT_5", shorty_right), ("MARSHAL_RIGHT_5", marshal_right), 
    ("STINGER_RIGHT_5", stinger_right), ("SPECTRE_RIGHT_5", spectre_right), ("BULLDOG_RIGHT_5", bulldog_right), 
    ("JUDGE_RIGHT_5", judge_right), ("GUARDIAN_RIGHT_5", guardian_right), ("VANDAL_RIGHT_5", vandal_right), 
    ("PHANTOM_RIGHT_5", phantom_right), ("OPERATOR_RIGHT_5", operator_right), ("ODIN_RIGHT_5", odin_right), 
    ("ARES_RIGHT_5", ares_right), ("BUCKY_RIGHT_5", bucky_right)

    ]

  abil_templates_bottom = [

    ]

  feed_templates = [

    ("ASTRA_FEED_LEFT_GREEN", flg_astra), ("BREACH_FEED_LEFT_GREEN", flg_breach), ("BRIMSTONE_FEED_LEFT_GREEN", flg_brimstone), 
    ("CYPHER_FEED_LEFT_GREEN", flg_cypher), ("JETT_FEED_LEFT_GREEN", flg_jett), ("KAYO_FEED_LEFT_GREEN", flg_kayo), 
    ("KILLJOY_FEED_LEFT_GREEN", flg_killjoy), ("OMEN_FEED_LEFT_GREEN", flg_omen), ("PHOENIX_FEED_LEFT_GREEN", flg_phoenix), 
    ("RAZE_FEED_LEFT_GREEN", flg_raze), ("REYNA_FEED_LEFT_GREEN", flg_reyna), ("SAGE_FEED_LEFT_GREEN", flg_sage), 
    ("SKYE_FEED_LEFT_GREEN", flg_skye), ("SOVA_FEED_LEFT_GREEN", flg_sova), ("VIPER_FEED_LEFT_GREEN", flg_viper), 
    ("YORU_FEED_LEFT_GREEN", flg_yoru), 

    ("ASTRA_FEED_LEFT_RED", flr_astra), ("BREACH_FEED_LEFT_RED", flr_breach), ("BRIMSTONE_FEED_LEFT_RED", flr_brimstone), 
    ("CYPHER_FEED_LEFT_RED", flr_cypher), ("JETT_FEED_LEFT_RED", flr_jett), ("KAYO_FEED_LEFT_RED", flr_kayo), 
    ("KILLJOY_FEED_LEFT_RED", flr_killjoy), ("OMEN_FEED_LEFT_RED", flr_omen), ("PHOENIX_FEED_LEFT_RED", flr_phoenix), 
    ("RAZE_FEED_LEFT_RED", flr_raze), ("REYNA_FEED_LEFT_RED", flr_reyna), ("SAGE_FEED_LEFT_RED", flr_sage), 
    ("SKYE_FEED_LEFT_RED", flr_skye), ("SOVA_FEED_LEFT_RED", flr_sova), ("VIPER_FEED_LEFT_RED", flr_viper), 
    ("YORU_FEED_LEFT_RED", flr_yoru), 

    ("ASTRA_FEED_RIGHT_GREEN", frg_astra), ("BREACH_FEED_RIGHT_GREEN", frg_breach), ("BRIMSTONE_FEED_RIGHT_GREEN", frg_brimstone), 
    ("CYPHER_FEED_RIGHT_GREEN", frg_cypher), ("JETT_FEED_RIGHT_GREEN", frg_jett), ("KAYO_FEED_RIGHT_GREEN", frg_kayo), 
    ("KILLJOY_FEED_RIGHT_GREEN", frg_killjoy), ("OMEN_FEED_RIGHT_GREEN", frg_omen), ("PHOENIX_FEED_RIGHT_GREEN", frg_phoenix), 
    ("RAZE_FEED_RIGHT_GREEN", frg_raze), ("REYNA_FEED_RIGHT_GREEN", frg_reyna), ("SAGE_FEED_RIGHT_GREEN", frg_sage), 
    ("SKYE_FEED_RIGHT_GREEN", frg_skye), ("SOVA_FEED_RIGHT_GREEN", frg_sova), ("VIPER_FEED_RIGHT_GREEN", frg_viper), 
    ("YORU_FEED_RIGHT_GREEN", frg_yoru), 

    ("ASTRA_FEED_RIGHT_RED", frr_astra), ("BREACH_FEED_RIGHT_RED", frr_breach), ("BRIMSTONE_FEED_RIGHT_RED", frr_brimstone), 
    ("CYPHER_FEED_RIGHT_RED", frr_cypher), ("JETT_FEED_RIGHT_RED", frr_jett), ("KAYO_FEED_RIGHT_RED", frr_kayo), 
    ("KILLJOY_FEED_RIGHT_RED", frr_killjoy), ("OMEN_FEED_RIGHT_RED", frr_omen), ("PHOENIX_FEED_RIGHT_RED", frr_phoenix), 
    ("RAZE_FEED_RIGHT_RED", frr_raze), ("REYNA_FEED_RIGHT_RED", frr_reyna), ("SAGE_FEED_RIGHT_RED", frr_sage), 
    ("SKYE_FEED_RIGHT_RED", frr_skye), ("SOVA_FEED_RIGHT_RED", frr_sova), ("VIPER_FEED_RIGHT_RED", frr_viper), 
    ("YORU_FEED_RIGHT_RED", frr_yoru), 

    ("ASTRA_FEED_ASSIST", fa_astra), ("BREACH_FEED_ASSIST", fa_breach), ("BRIMSTONE_FEED_ASSIST", fa_brimstone), 
    ("CYPHER_FEED_ASSIST", fa_cypher), ("JETT_FEED_ASSIST", fa_jett), ("KAYO_FEED_ASSIST", fa_kayo), 
    ("KILLJOY_FEED_ASSIST", fa_killjoy), ("OMEN_FEED_ASSIST", fa_omen), ("PHOENIX_FEED_ASSIST", fa_phoenix), 
    ("RAZE_FEED_ASSIST", fa_raze), ("REYNA_FEED_ASSIST", fa_reyna), ("SAGE_FEED_ASSIST", fa_sage), 
    ("SKYE_FEED_ASSIST", fa_skye), ("SOVA_FEED_ASSIST", fa_sova), ("VIPER_FEED_ASSIST", fa_viper), 
    ("YORU_FEED_ASSIST", fa_yoru), 

    ("HEADSHOT_FEED_GREEN", headshot_green), ("SPIKE_DET_FEED_GREEN", spike_det_green), ("WALLBANG_FEED_GREEN", wallbang_green), 

    ("HEADSHOT_FEED_RED", headshot_red), ("SPIKE_DET_FEED_RED", spike_det_red), ("WALLBANG_FEED_RED", wallbang_red), 

    ("CLASSIC_FEED_GREEN", classic_green), ("FRENZY_FEED_GREEN", frenzy_green), ("GHOST_FEED_GREEN", ghost_green), 
    ("SHERIFF_FEED_GREEN", sheriff_green), ("SHORTY_FEED_GREEN", shorty_green), ("MARSHAL_FEED_GREEN", marshal_green), 
    ("STINGER_FEED_GREEN", stinger_green), ("SPECTRE_FEED_GREEN", spectre_green), ("BULLDOG_FEED_GREEN", bulldog_green), 
    ("JUDGE_FEED_GREEN", judge_green), ("GUARDIAN_FEED_GREEN", guardian_green), ("VANDAL_FEED_GREEN", vandal_green), 
    ("PHANTOM_FEED_GREEN", phantom_green), ("OPERATOR_FEED_GREEN", operator_green), ("ODIN_FEED_GREEN", odin_green), 
    ("ARES_FEED_GREEN", ares_green), ("BUCKY_FEED_GREEN", bucky_green), 

    ("CLASSIC_FEED_RED", classic_red), ("FRENZY_FEED_RED", frenzy_red), ("GHOST_FEED_RED", ghost_red), 
    ("SHERIFF_FEED_RED", sheriff_red), ("SHORTY_FEED_RED", shorty_red), ("MARSHAL_FEED_RED", marshal_red), 
    ("STINGER_FEED_RED", stinger_red), ("SPECTRE_FEED_RED", spectre_red), ("BULLDOG_FEED_RED", bulldog_red), 
    ("JUDGE_FEED_RED", judge_red), ("GUARDIAN_FEED_RED", guardian_red), ("VANDAL_FEED_RED", vandal_red), 
    ("PHANTOM_FEED_RED", phantom_red), ("OPERATOR_FEED_RED", operator_red), ("ODIN_FEED_RED", odin_red), 
    ("ARES_FEED_RED", ares_red), ("BUCKY_FEED_RED", bucky_red), 

    ("AFTERSHOCK_FEED_GREEN", green_aftershock), ("BLADE_STORM_FEED_GREEN", green_blade_storm), 
    ("BLAST_PACK_FEED_GREEN", green_blast_pack), ("BLAZE_FEED_GREEN", green_blaze), 
    ("BOOM_BOT_FEED_GREEN", green_boom_bot), ("FRAGMENT_FEED_GREEN", green_fragment), 
    ("HOT_HANDS_FEED_GREEN", green_hot_hands), ("HUNTERS_FURY_FEED_GREEN", green_hunters_fury), 
    ("INCENDIARY_FEED_GREEN", green_incendiary), ("NANOSWARM_FEED_GREEN", green_nanoswarm), 
    ("NULLCMD_FEED_GREEN", green_nullcmd), ("NULLCMD_RES_FEED_GREEN", green_nullcmd_res), 
    ("ORBITAL_STRIKE_FEED_GREEN", green_orbital_strike), ("PAINT_SHELLS_FEED_GREEN", green_paint_shells), 
    ("RESURRECTION_FEED_GREEN", green_resurrection), ("RUN_IT_BACK_FEED_GREEN", green_run_it_back), 
    ("SHOCK_BOLT_FEED_GREEN", green_shock_bolt), ("SHOWSTOPPER_FEED_GREEN", green_showstopper), 
    ("SNAKE_BITE_FEED_GREEN", green_snake_bite), ("TRAILBLAZER_FEED_GREEN", green_trailblazer), 
    ("TRAPWIRE_FEED_GREEN", green_trapwire), ("TURRET_FEED_GREEN", green_turret), 

    ("AFTERSHOCK_FEED_RED", red_aftershock), ("BLADE_STORM_FEED_RED", red_blade_storm), 
    ("BLAST_PACK_FEED_RED", red_blast_pack), ("BLAZE_FEED_RED", red_blaze), 
    ("BOOM_BOT_FEED_RED", red_boom_bot), ("FRAGMENT_FEED_RED", red_fragment), 
    ("HOT_HANDS_FEED_RED", red_hot_hands), ("HUNTERS_FURY_FEED_RED", red_hunters_fury), 
    ("INCENDIARY_FEED_RED", red_incendiary), ("NANOSWARM_FEED_RED", red_nanoswarm), 
    ("NULLCMD_FEED_RED", red_nullcmd), ("NULLCMD_RES_FEED_RED", red_nullcmd_res), 
    ("ORBITAL_STRIKE_FEED_RED", red_orbital_strike), ("PAINT_SHELLS_FEED_RED", red_paint_shells), 
    ("RESURRECTION_FEED_RED", red_resurrection), ("RUN_IT_BACK_FEED_RED", red_run_it_back), 
    ("SHOCK_BOLT_FEED_RED", red_shock_bolt), ("SHOWSTOPPER_FEED_RED", red_showstopper), 
    ("SNAKE_BITE_FEED_RED", red_snake_bite), ("TRAILBLAZER_FEED_RED", red_trailblazer), 
    ("TRAPWIRE_FEED_RED", red_trapwire), ("TURRET_FEED_RED", red_turret), 

    ]

  sleep(1.0)

  x = scan(data, public, minimap_templates, side_templates, spike_templates, 
      op_templates_pub_mid, op_templates_pub_left, op_templates_pub_right, 
      op_templates_priv_mid, op_templates_priv_left, op_templates_priv_right, 
      ult_templates_left_1, ult_templates_right_1, ult_templates_left_2, ult_templates_right_2, 
      ult_templates_left_3, ult_templates_right_3, ult_templates_left_4, ult_templates_right_4, 
      ult_templates_left_5, ult_templates_right_5, abil_templates_left_1, abil_templates_right_1, 
      abil_templates_left_2, abil_templates_right_2, abil_templates_left_3, abil_templates_right_3, 
      abil_templates_left_4, abil_templates_right_4, abil_templates_left_5, abil_templates_right_5, 
      abil_templates_bottom, feed_templates)
  return x

def scan_minimap(frame, minimap_templates):
  if frame is None:  return []
  minimap_hits = matchTemplates(minimap_templates, frame, method=cv2.TM_CCOEFF_NORMED, N_object=float("inf"), score_threshold=0.75, maxOverlap=0.75, searchBox=(MM_XL, MM_YT, (MM_XR - MM_XL), (MM_YB - MM_YT)))
  return [minimap_hits]

def scan_overlay(frame, public, 
  ult_templates_left_1, ult_templates_right_1, ult_templates_left_2, ult_templates_right_2, 
  ult_templates_left_3, ult_templates_right_3, ult_templates_left_4, ult_templates_right_4, 
  ult_templates_left_5, ult_templates_right_5, abil_templates_left_1, abil_templates_right_1, 
  abil_templates_left_2, abil_templates_right_2, abil_templates_left_3, abil_templates_right_3, 
  abil_templates_left_4, abil_templates_right_4, abil_templates_left_5, abil_templates_right_5, 
  abil_templates_bottom):

  if frame is None:  return []

  ult_hits_left_1 = None
  ult_hits_right_1 = None
  abil_hits_left_1 = None
  abil_hits_right_1 = None
  ult_hits_left_2 = None
  ult_hits_right_2 = None
  abil_hits_left_2 = None
  abil_hits_right_2 = None
  ult_hits_left_3 = None
  ult_hits_right_3 = None
  abil_hits_left_3 = None
  abil_hits_right_3 = None
  ult_hits_left_4 = None
  ult_hits_right_4 = None
  abil_hits_left_4 = None
  abil_hits_right_4 = None
  ult_hits_left_5 = None
  ult_hits_right_5 = None
  abil_hits_left_5 = None
  abil_hits_right_5 = None
  abil_hits_bottom = None

  if public:

    ult_hits_left_1 = matchTemplates(ult_templates_left_1, frame, method=cv2.TM_CCOEFF_NORMED, N_object=float("inf"), score_threshold=0.85, maxOverlap=0.1, searchBox=(0, 540, 125, 104))
    ult_hits_right_1 = matchTemplates(ult_templates_right_1, frame, method=cv2.TM_CCOEFF_NORMED, N_object=float("inf"), score_threshold=0.85, maxOverlap=0.1, searchBox=(1795, 540, 125, 104))
    abil_hits_left_1 = matchTemplates(abil_templates_left_1, frame, method=cv2.TM_CCOEFF_NORMED, N_object=float("inf"), score_threshold=0.8, maxOverlap=0.01, searchBox=(125, 540, 330, 104))
    abil_hits_right_1 = matchTemplates(abil_templates_right_1, frame, method=cv2.TM_CCOEFF_NORMED, N_object=float("inf"), score_threshold=0.8, maxOverlap=0.01, searchBox=(1465, 540, 330, 104))

    ult_hits_left_2 = matchTemplates(ult_templates_left_2, frame, method=cv2.TM_CCOEFF_NORMED, N_object=float("inf"), score_threshold=0.85, maxOverlap=0.1, searchBox=(0, 644, 125, 104))
    ult_hits_right_2 = matchTemplates(ult_templates_right_2, frame, method=cv2.TM_CCOEFF_NORMED, N_object=float("inf"), score_threshold=0.85, maxOverlap=0.1, searchBox=(1795, 644, 125, 104))
    abil_hits_left_2 = matchTemplates(abil_templates_left_2, frame, method=cv2.TM_CCOEFF_NORMED, N_object=float("inf"), score_threshold=0.8, maxOverlap=0.01, searchBox=(125, 644, 330, 104))
    abil_hits_right_2 = matchTemplates(abil_templates_right_2, frame, method=cv2.TM_CCOEFF_NORMED, N_object=float("inf"), score_threshold=0.8, maxOverlap=0.01, searchBox=(1465, 644, 330, 104))

    ult_hits_left_3 = matchTemplates(ult_templates_left_3, frame, method=cv2.TM_CCOEFF_NORMED, N_object=float("inf"), score_threshold=0.85, maxOverlap=0.1, searchBox=(0, 748, 125, 104))
    ult_hits_right_3 = matchTemplates(ult_templates_right_3, frame, method=cv2.TM_CCOEFF_NORMED, N_object=float("inf"), score_threshold=0.85, maxOverlap=0.1, searchBox=(1795, 748, 125, 104))
    abil_hits_left_3 = matchTemplates(abil_templates_left_3, frame, method=cv2.TM_CCOEFF_NORMED, N_object=float("inf"), score_threshold=0.8, maxOverlap=0.01, searchBox=(125, 748, 330, 104))
    abil_hits_right_3 = matchTemplates(abil_templates_right_3, frame, method=cv2.TM_CCOEFF_NORMED, N_object=float("inf"), score_threshold=0.8, maxOverlap=0.01, searchBox=(1465, 748, 330, 104))

    ult_hits_left_4 = matchTemplates(ult_templates_left_4, frame, method=cv2.TM_CCOEFF_NORMED, N_object=float("inf"), score_threshold=0.85, maxOverlap=0.1, searchBox=(0, 852, 125, 104))
    ult_hits_right_4 = matchTemplates(ult_templates_right_4, frame, method=cv2.TM_CCOEFF_NORMED, N_object=float("inf"), score_threshold=0.85, maxOverlap=0.1, searchBox=(1795, 852, 125, 104))
    abil_hits_left_4 = matchTemplates(abil_templates_left_4, frame, method=cv2.TM_CCOEFF_NORMED, N_object=float("inf"), score_threshold=0.8, maxOverlap=0.01, searchBox=(125, 852, 330, 104))
    abil_hits_right_4 = matchTemplates(abil_templates_right_4, frame, method=cv2.TM_CCOEFF_NORMED, N_object=float("inf"), score_threshold=0.8, maxOverlap=0.01, searchBox=(1465, 852, 330, 104))

    ult_hits_left_5 = matchTemplates(ult_templates_left_5, frame, method=cv2.TM_CCOEFF_NORMED, N_object=float("inf"), score_threshold=0.85, maxOverlap=0.1, searchBox=(0, 956, 125, 104))
    ult_hits_right_5 = matchTemplates(ult_templates_right_5, frame, method=cv2.TM_CCOEFF_NORMED, N_object=float("inf"), score_threshold=0.85, maxOverlap=0.1, searchBox=(1795, 956, 125, 104))
    abil_hits_left_5 = matchTemplates(abil_templates_left_5, frame, method=cv2.TM_CCOEFF_NORMED, N_object=float("inf"), score_threshold=0.8, maxOverlap=0.01, searchBox=(125, 956, 330, 104))
    abil_hits_right_5 = matchTemplates(abil_templates_right_5, frame, method=cv2.TM_CCOEFF_NORMED, N_object=float("inf"), score_threshold=0.8, maxOverlap=0.01, searchBox=(1465, 956, 330, 104))

  if not public:
    abil_hits_bottom = matchTemplates(abil_templates_bottom, frame, method=cv2.TM_CCOEFF_NORMED, N_object=float("inf"), score_threshold=0.9, maxOverlap=0.01, searchBox=(530, 970, 680, 90))

  return [
    ult_hits_left_1, ult_hits_right_1, ult_hits_left_2, ult_hits_right_2, 
    ult_hits_left_3, ult_hits_right_3, ult_hits_left_4, ult_hits_right_4, 
    ult_hits_left_5, ult_hits_right_5, abil_hits_left_1, abil_hits_right_1, 
    abil_hits_left_2, abil_hits_right_2, abil_hits_left_3, abil_hits_right_3, 
    abil_hits_left_4, abil_hits_right_4, abil_hits_left_5, abil_hits_right_5, 
    abil_hits_bottom ]

def scan_status(frame, public, side_templates, spike_templates, 
  op_templates_pub_mid, op_templates_pub_left, op_templates_pub_right, 
  op_templates_priv_mid, op_templates_priv_left, op_templates_priv_right):

  if frame is None:  return []

  side_hits = None
  spike_hits = None
  op_hits_mid = None
  op_hits_left = None
  op_hits_right = None
  spike_hits = matchTemplates(spike_templates, frame, method=cv2.TM_CCOEFF_NORMED, N_object=float("inf"), score_threshold=0.8, maxOverlap=0.01, searchBox=(925, 140, 155, 30))

  if public:
    side_hits = matchTemplates(side_templates, frame, method=cv2.TM_CCOEFF_NORMED, N_object=float("inf"), score_threshold=0.8, maxOverlap=0.1, searchBox=(905, 0, 115, 140))
    op_hits_mid = matchTemplates(op_templates_pub_mid, frame, method=cv2.TM_CCOEFF_NORMED, N_object=float("inf"), score_threshold=0.9, maxOverlap=0.1, searchBox=(880, 0, 154, 75))
    op_hits_left = matchTemplates(op_templates_pub_left, frame, method=cv2.TM_CCOEFF_NORMED, N_object=float("inf"), score_threshold=0.85, maxOverlap=0.55, searchBox=(780, 0, 100, 75))
    op_hits_right = matchTemplates(op_templates_pub_right, frame, method=cv2.TM_CCOEFF_NORMED, N_object=float("inf"), score_threshold=0.85, maxOverlap=0.55, searchBox=(1034, 0, 100, 75))

  if not public:
    side_hits = matchTemplates(side_templates, frame, method=cv2.TM_CCOEFF_NORMED, N_object=float("inf"), score_threshold=0.8, maxOverlap=0.1, searchBox=(880, 20, 154, 60))
    op_hits_mid = matchTemplates(op_templates_priv_mid, frame, method=cv2.TM_CCOEFF_NORMED, N_object=float("inf"), score_threshold=0.9, maxOverlap=0.1, searchBox=(880, 20, 154, 60))
    op_hits_left = matchTemplates(op_templates_priv_left, frame, method=cv2.TM_CCOEFF_NORMED, N_object=float("inf"), score_threshold=0.8, maxOverlap=0.1, searchBox=(400, 20, 480, 60))
    op_hits_right = matchTemplates(op_templates_priv_right, frame, method=cv2.TM_CCOEFF_NORMED, N_object=float("inf"), score_threshold=0.8, maxOverlap=0.1, searchBox=(1034, 20, 480, 60))

  return [side_hits, spike_hits, op_hits_mid, op_hits_left, op_hits_right]

def scan_feed(frame, feed_templates):
  feed_hits = None
  feed_hits = matchTemplates(feed_templates, frame, method=cv2.TM_CCOEFF_NORMED, N_object=float("inf"), score_threshold=0.81, maxOverlap=0.01, searchBox=(1350, 20, 570, 300))
  return [feed_hits]

def scan(src, public, minimap_templates, side_templates, spike_templates, 
  op_templates_pub_mid, op_templates_pub_left, op_templates_pub_right, 
  op_templates_priv_mid, op_templates_priv_left, op_templates_priv_right, 
  ult_templates_left_1, ult_templates_right_1, ult_templates_left_2, 
  ult_templates_right_2, ult_templates_left_3, ult_templates_right_3, 
  ult_templates_left_4, ult_templates_right_4, ult_templates_left_5, 
  ult_templates_right_5, abil_templates_left_1, abil_templates_right_1, 
  abil_templates_left_2, abil_templates_right_2, abil_templates_left_3, 
  abil_templates_right_3, abil_templates_left_4, abil_templates_right_4, 
  abil_templates_left_5, abil_templates_right_5, abil_templates_bottom, 
  feed_templates):

  hits = []
  cap = cv2.VideoCapture(src)
  count = 0
  d = f"{os.path.dirname(os.path.dirname(src))}/temp/"
  os.mkdir(d)
  num_frames = int((cap.get(cv2.CAP_PROP_FRAME_COUNT) / cap.get(cv2.CAP_PROP_FPS)) / FPAC) + 1
  while count < num_frames:
    cap.set(cv2.CAP_PROP_POS_MSEC, (count * 1000 / FPAC))
    ret, frame = cap.read()
    p = f"{d}{os.path.basename(src)[:-4]}_{count+1}.png"
    cv2.imwrite(p, frame)
    img = cv2.imread(p)
    # verif = verify(img)
    # while not verif:
    #   cv2.imwrite(p, frame)
    #   img = cv2.imread(p)
    #   verif = verify(img)
    count += 1

    tmp = []
    x1 = scan_minimap(img, minimap_templates)
    x2 = scan_overlay(img, public, 
      ult_templates_left_1, ult_templates_right_1, ult_templates_left_2, ult_templates_right_2, 
      ult_templates_left_3, ult_templates_right_3, ult_templates_left_4, ult_templates_right_4, 
      ult_templates_left_5, ult_templates_right_5, abil_templates_left_1, abil_templates_right_1, 
      abil_templates_left_2, abil_templates_right_2, abil_templates_left_3, abil_templates_right_3, 
      abil_templates_left_4, abil_templates_right_4, abil_templates_left_5, abil_templates_right_5, 
      abil_templates_bottom)
    x3 = scan_status(img, public, side_templates, spike_templates, 
      op_templates_pub_mid, op_templates_pub_left, op_templates_pub_right, 
      op_templates_priv_mid, op_templates_priv_left, op_templates_priv_right)
    x4 = scan_feed(img, feed_templates)

    for i in [x1, x2, x3, x4]:
      for j in i:
        tmp.append(j)
    os.remove(p)
    tmpp = tuple(tmp)
    hits.append(tmpp)
  os.rmdir(d)
  return hits
