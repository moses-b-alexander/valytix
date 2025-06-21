from collections import defaultdict
from enum import Enum
import os
import time
import uuid

from game.funcs import *
from game.map import *
from game.namedata import *
from game.search import *
from game.minimap import *


class Game:
  def __init__(self, filename, mapname="", public=False, teamleft="", teamright="", log=False, dbg=False, xshift=0, yshift=0):
    # left is team that has left side on overlay in game, right """"" right
    self.filename = filename
    self.mapname = mapname
    self.public = public
    self.teamleft = teamleft
    self.teamright = teamright
    self.dbg = dbg
    self.log = log

    self.x = None
    self.frames = {}
    self.agents = {}
    self.agent_names = []

    self.round_info = {}
    self.round_results = defaultdict(list)
    self.results = None
    self.game_score_left = 0
    self.game_score_right = 0
    self.round_score_left = 0
    self.round_score_right = 0

    self.rs = []
    self.rm = []
    self.rte = []
    self.rpe = []
    self.rge = []
    self.rf = []
    self.ac = {}
    self.map_obj = Map(self.mapname)

    if not self.public:
      self.teamleft = "ALLIES"
      self.teamright = "ENEMIES"
    if self.log:
      self.f = open(os.path.dirname(os.getcwd()) + f"/output/vx_{(uuid.uuid4()).hex}.txt", "w")


  def run(self):
    t1 = time.perf_counter()
    self.x = minimap_tracking(self.filename, self.public, self.teamleft, self.teamright)
    t2 = time.perf_counter()
    print(f"\n\nvideo processing time is {t2 - t1:0.5f} seconds\n\n")
    rs_splits = []
    rm_splits = []
    rte_splits = []
    rpe_splits = []
    rge_splits = []
    rf_splits = []
    agent_trk = defaultdict(list)
    feed = defaultdict(list)
    round_info = {}
    if self.dbg:
      for iii in range(len(self.x)):
        self.f.write("\n\nframe # --- " + str(iii) + "\n\n"); self.f.write(str(self.x[iii]))

    for i in range(len(self.x)):
      if search(self.x[i], "ROUND_START"):  rs_splits.append(i)
      if search(self.x[i], "ROUND_MIDGAME"):  rm_splits.append(i)
      if search(self.x[i], "ROUND_ENDGAME"):  rte_splits.append(i)
      if search(self.x[i], "SPIKE_PLANTED"):  rge_splits.append(i)
      if search(self.x[i], f"SCORE_LEFT_{self.round_score_left + 1}"):
        rf_splits.append(i)
        self.round_score_left += 1
        self.round_results[self.round_score_left + self.round_score_right] = ("L", self.round_score_left, self.round_score_right)
      if search(self.x[i], f"SCORE_RIGHT_{self.round_score_right + 1}"):
        rf_splits.append(i)
        self.round_score_right += 1
        self.round_results[self.round_score_left + self.round_score_right] = ("R", self.round_score_left, self.round_score_right)
      if self.round_score_left == 12 and self.round_score_right == 12:
        if search(self.x[i], f"SCORE_LEFT_{self.round_score_left + 1}"):
          rf_splits.append(i)
          self.round_score_left += 1
          self.round_results[self.round_score_left + self.round_score_right] = ("L", self.round_score_left, self.round_score_right)
        if search(self.x[i], f"SCORE_RIGHT_{self.round_score_right + 1}"):
          rf_splits.append(i)
          self.round_score_right += 1
          self.round_results[self.round_score_left + self.round_score_right] = ("R", self.round_score_left, self.round_score_right)
        if self.round_score_left - self.round_score_right > 1:
          self.game_score_left += 1
          # LEFT WINS OVERTIME
        if self.round_score_right - self.round_score_left > 1:
          self.game_score_right += 1
          # RIGHT WINS OVERTIME
      if self.round_score_left == 13 and self.round_score_right < 12:
        self.game_score_left += 1
        # LEFT WINS GAME
      if self.round_score_right == 13 and self.round_score_left < 12:
        self.game_score_right += 1
        # RIGHT WINS GAME
      else:  pass

    # print(rs_splits)
    # print()
    # print(rf_splits)
    self.rs = get_splits(rs_splits) # round start frames
    self.rm = get_splits(rm_splits) # round midgame frames
    self.rte = get_splits(rte_splits) # round endgame frames
    self.rpe = get_splits(rpe_splits) # atk takes site frames
    self.rge = get_splits(rge_splits) # round planted frames
    self.rf = get_splits(rf_splits) # round finish frames
    def makerounds(s, f):
      cc = defaultdict(list)
      sss = [s[0]]
      for i in s:
        for j in range(len(f) - 1):
          if i < f[j+1] and i > f[j]:  cc[f[j]].append(i)
      for i, j in cc.items():
        if len(j) >= 1:  sss.append(j[0])
      return (list(map(lambda ss,ff: (ss, ff), sss, f)))
    self.rbs = makerounds(self.rs, self.rf)
    names = defaultdict(list)

    for ii in range(self.rbs[0][0], self.rbs[0][1]):
      if ii == self.rbs[0][1] - 2:
        minimap_frame = get_frame(self.filename, ii)
        get_minimap_coords(minimap_frame)
      for a in agent_list:
        for o in overlay:
          if search(self.x[ii], f"{a}_INIT_{o}"):
            self.agents[o] = { 
              "AGENT": {}, "ROLE": {}, "SUBROLE": {}, "ACTIONS": {}, 
              "POSITION": {}, "UTIL": {}, "WEAPON": {}, "HEALTH": {}, 
              "DISTANCE": {}, "CUM_DISTANCE": {}, "VELOCITY": {}, "AVG_LOC": {}, "AVG_MOMENTUM": {}, "HEALTH_VARIATION": {}, "SPIKE_HELD": {}, 

              "KILLS": {}, "DEATHS": {}, "ASSISTS": {}, "SURVIVES": {}, "IDLES": {}, "TRADES": {}, "REVIVES": {}, "PLANTS": {}, "DEFUSES": {}, 
              "HEADSHOTS": {}, "WALLBANGS": {}, "UTIL_KILLS": {}, "SPIKE_DEATHS": {}, "OPENING_KILLS": {}, "OPENING_DEATHS": {}, 
              "OPENING_TRADES": {}, "STARTING_ECONOMY": {}, "ENDING_ECONOMY": {}, 

              "UTIL1_USAGE": {}, "UTIL2_USAGE": {}, "ABIL_USAGE": {}, "ABIL_REGAINED": {}, "ULT_USAGE": {}, "ULT_SAVED": {}, "ULT_DEATHS": {}, 
              "UTIL_ASSISTS": {}, "UTIL_WASTE": {}, "UTIL_STALL": {}, "UTIL_EXPANSION": {}, "UTIL_INFO": {}, "UTIL_TRADES": {}, 
              "ULT_ASSISTS": {}, "ULT_STALL": {}, "ULT_EXPANSION": {}, "ULT_INFO": {}, "ULT_TRADES": {}, 

              "PROGRESSIONS": {}, "HOLDS": {}, "EXECUTIONS": {}, "SWITCHS": {}, "ROTATIONS": {}, "PINCERS": {}, "FLANKS": {}, "COVERS": {}, 

              "PREV_K/D": {}, "K/D": {}, "PREV_D/K": {}, "D/K": {}, "PREV_S/I": {}, "S/I": {}, "PREV_I/S": {}, "I/S": {}, 
              "PREV_T/D": {}, "T/D": {}, "PREV_ATR/I": {}, "ATR/I": {}, "PREV_KATRP/D": {}, "KATRP/D": {}, 

              "KILL_COUNT": {}, "DEATH_COUNT": {}, "ASSIST_COUNT": {}, "SURVIVE_COUNT": {}, "IDLE_COUNT": {}, 
              "TRADE_COUNT": {}, "REVIVE_COUNT": {}, "PLANT_COUNT": {}, "DEFUSE_COUNT": {}, 
              "HEADSHOT_COUNT": {}, "WALLBANG_COUNT": {}, "UTIL_KILL_COUNT": {}, "SPIKE_DEATH_COUNT": {}, 
              "%_HEADSHOTS": {}, "%_WALLBANGS": {}, "%_UTIL_KILLS": {}, "%_SPIKE_DEATHS": {}, 

              "UTIL1_USAGE_COUNT": {}, "UTIL1_SAVED_COUNT": {}, "UTIL1_DIED_WITH_COUNT": {}, 
              "UTIL2_USAGE_COUNT": {}, "UTIL2_SAVED_COUNT": {}, "UTIL2_DIED_WITH_COUNT": {}, 
              "ABIL_USAGE_COUNT": {}, "ABIL_REGAINED_COUNT": {}, "ABIL_SAVED_COUNT": {}, "ABIL_DIED_WITH_COUNT": {}, 
              "ULT_USAGE_COUNT": {}, "ULT_DEATH_COUNT": {}, "ULT_SAVED_COUNT": {}, 

              "PROGRESSION_COUNT": {}, "HOLD_COUNT": {}, "EXECUTION_COUNT": {}, "SWITCH_COUNT": {}, "ROTATION_COUNT": {}, 
              "PINCER_COUNT": {}, "FLANK_COUNT": {}, "COVER_COUNT": {}, 

              "TOTAL_DAMAGE_TAKEN": {}, "TOTAL_HEALTH_REGAINED": {}, 

              "KILL_COUNT/TOTAL_DISTANCE": {}, "DEATH_COUNT/TOTAL_DISTANCE": {}, "ASSIST_COUNT/TOTAL_DISTANCE": {}, 
              "SURVIVE_COUNT/TOTAL_DISTANCE": {}, "IDLE_COUNT/TOTAL_DISTANCE": {}, 
              "TRADE_COUNT/TOTAL_DISTANCE": {}, "REVIVE_COUNT/TOTAL_DISTANCE": {}, 
              "PLANT_COUNT/TOTAL_DISTANCE": {}, "DEFUSE_COUNT/TOTAL_DISTANCE": {}, 
              "HEADSHOT_COUNT/TOTAL_DISTANCE": {}, "WALLBANG_COUNT/TOTAL_DISTANCE": {}, "UTIL_KILL_COUNT/TOTAL_DISTANCE": {}, 
              "SPIKE_DEATH_COUNT/TOTAL_DISTANCE": {}, 
              "KILL_COUNT/TOTAL_VELOCITY": {}, "DEATH_COUNT/TOTAL_VELOCITY": {}, "ASSIST_COUNT/TOTAL_VELOCITY": {}, 
              "SURVIVE_COUNT/TOTAL_VELOCITY": {}, "IDLE_COUNT/TOTAL_VELOCITY": {}, 
              "TRADE_COUNT/TOTAL_VELOCITY": {}, "REVIVE_COUNT/TOTAL_VELOCITY": {}, 
              "PLANT_COUNT/TOTAL_VELOCITY": {}, "DEFUSE_COUNT/TOTAL_VELOCITY": {}, 
              "HEADSHOT_COUNT/TOTAL_VELOCITY": {}, "WALLBANG_COUNT/TOTAL_VELOCITY": {}, "UTIL_KILL_COUNT/TOTAL_VELOCITY": {}, 
              "SPIKE_DEATH_COUNT/TOTAL_VELOCITY": {}, 
              "KILL_COUNT/TIME": {}, "DEATH_COUNT/TIME": {}, "ASSIST_COUNT/TIME": {}, "SURVIVE_COUNT/TIME": {}, "IDLE_COUNT/TIME": {}, 
              "TRADE_COUNT/TIME": {}, "REVIVE_COUNT/TIME": {}, "PLANT_COUNT/TIME": {}, "DEFUSE_COUNT/TIME": {}, 
              "HEADSHOT_COUNT/TIME": {}, "WALLBANG_COUNT/TIME": {}, "UTIL_KILL_COUNT/TIME": {}, "SPIKE_DEATH_COUNT/TIME": {}, 
              "KILL_COUNT/TIME_ALIVE": {}, "DEATH_COUNT/TIME_ALIVE": {}, "ASSIST_COUNT/TIME_ALIVE": {}, "SURVIVE_COUNT/TIME_ALIVE": {}, 
              "IDLE_COUNT/TIME_ALIVE": {}, "TRADE_COUNT/TIME_ALIVE": {}, "REVIVE_COUNT/TIME_ALIVE": {}, "PLANT_COUNT/TIME_ALIVE": {}, 
              "DEFUSE_COUNT/TIME_ALIVE": {}, "HEADSHOT_COUNT/TIME_ALIVE": {}, "WALLBANG_COUNT/TIME_ALIVE": {}, 
              "UTIL_KILL_COUNT/TIME_ALIVE": {}, "SPIKE_DEATH_COUNT/TIME_ALIVE": {}, 
              "ASSIST_COUNT/KILL_COUNT": {}, "SURVIVE_COUNT/KILL_COUNT": {}, "IDLE_COUNT/KILL_COUNT": {}, "TRADE_COUNT/KILL_COUNT": {}, 
              "REVIVE_COUNT/KILL_COUNT": {}, "PLANT_COUNT/KILL_COUNT": {}, "DEFUSE_COUNT/KILL_COUNT": {}, "SPIKE_DEATH_COUNT/KILL_COUNT": {}, 
              "ASSIST_COUNT/DEATH_COUNT": {}, "SURVIVE_COUNT/DEATH_COUNT": {}, "IDLE_COUNT/DEATH_COUNT": {}, 
              "REVIVE_COUNT/DEATH_COUNT": {}, "PLANT_COUNT/DEATH_COUNT": {}, "DEFUSE_COUNT/DEATH_COUNT": {}, "HEADSHOT_COUNT/DEATH_COUNT": {}, 
              "WALLBANG_COUNT/DEATH_COUNT": {}, "UTIL_KILL_COUNT/DEATH_COUNT": {}, 
              "KILL_COUNT/ASSIST_COUNT": {}, "DEATH_COUNT/ASSIST_COUNT": {}, "SURVIVE_COUNT/ASSIST_COUNT": {}, "IDLE_COUNT/ASSIST_COUNT": {}, 
              "TRADE_COUNT/ASSIST_COUNT": {}, "REVIVE_COUNT/ASSIST_COUNT": {}, "PLANT_COUNT/ASSIST_COUNT": {}, "DEFUSE_COUNT/ASSIST_COUNT": {}, 
              "HEADSHOT_COUNT/ASSIST_COUNT": {}, "WALLBANG_COUNT/ASSIST_COUNT": {}, "UTIL_KILL_COUNT/ASSIST_COUNT": {}, 
              "SPIKE_DEATH_COUNT/ASSIST_COUNT": {}, 
              "KILL_COUNT/SURVIVE_COUNT": {}, "DEATH_COUNT/SURVIVE_COUNT": {}, "ASSIST_COUNT/SURVIVE_COUNT": {}, 
              "TRADE_COUNT/SURVIVE_COUNT": {}, "REVIVE_COUNT/SURVIVE_COUNT": {}, "PLANT_COUNT/SURVIVE_COUNT": {}, 
              "DEFUSE_COUNT/SURVIVE_COUNT": {}, "HEADSHOT_COUNT/SURVIVE_COUNT": {}, "WALLBANG_COUNT/SURVIVE_COUNT": {}, 
              "UTIL_KILL_COUNT/SURVIVE_COUNT": {}, "SPIKE_DEATH_COUNT/SURVIVE_COUNT": {}, 
              "KILL_COUNT/IDLE_COUNT": {}, "DEATH_COUNT/IDLE_COUNT": {}, "ASSIST_COUNT/IDLE_COUNT": {}, 
              "TRADE_COUNT/IDLE_COUNT": {}, "REVIVE_COUNT/IDLE_COUNT": {}, "PLANT_COUNT/IDLE_COUNT": {}, 
              "DEFUSE_COUNT/IDLE_COUNT": {}, "HEADSHOT_COUNT/IDLE_COUNT": {}, "WALLBANG_COUNT/IDLE_COUNT": {}, 
              "UTIL_KILL_COUNT/IDLE_COUNT": {}, "SPIKE_DEATH_COUNT/IDLE_COUNT": {}, 
              "KILL_COUNT/TRADE_COUNT": {}, "DEATH_COUNT/TRADE_COUNT": {}, "ASSIST_COUNT/TRADE_COUNT": {}, "SURVIVE_COUNT/TRADE_COUNT": {}, 
              "IDLE_COUNT/TRADE_COUNT": {}, "REVIVE_COUNT/TRADE_COUNT": {}, "PLANT_COUNT/TRADE_COUNT": {}, "DEFUSE_COUNT/TRADE_COUNT": {}, 
              "HEADSHOT_COUNT/TRADE_COUNT": {}, "WALLBANG_COUNT/TRADE_COUNT": {}, "UTIL_KILL_COUNT/TRADE_COUNT": {}, 
              "SPIKE_DEATH_COUNT/TRADE_COUNT": {}, 

              "UTIL1_USAGE_COUNT/TOTAL_DISTANCE": {}, "UTIL1_USAGE_COUNT/TOTAL_VELOCITY": {}, "UTIL1_USAGE_COUNT/TIME": {}, 
              "UTIL1_USAGE_COUNT/TIME_ALIVE": {}, "UTIL1_USAGE_COUNT/KILL_COUNT": {}, "UTIL1_USAGE_COUNT/DEATH_COUNT": {}, 
              "UTIL1_USAGE_COUNT/ASSIST_COUNT": {}, "UTIL1_USAGE_COUNT/SURVIVE_COUNT": {}, "UTIL1_USAGE_COUNT/IDLE_COUNT": {}, 
              "UTIL1_USAGE_COUNT/TRADE_COUNT": {}, "UTIL1_SAVED_COUNT/TOTAL_DISTANCE": {}, 
              "UTIL1_SAVED_COUNT/TOTAL_VELOCITY": {}, "UTIL1_SAVED_COUNT/TIME": {}, 
              "UTIL1_SAVED_COUNT/TIME_ALIVE": {}, "UTIL1_SAVED_COUNT/KILL_COUNT": {}, "UTIL1_SAVED_COUNT/DEATH_COUNT": {}, 
              "UTIL1_SAVED_COUNT/ASSIST_COUNT": {}, "UTIL1_SAVED_COUNT/SURVIVE_COUNT": {}, "UTIL1_SAVED_COUNT/IDLE_COUNT": {}, 
              "UTIL1_SAVED_COUNT/TRADE_COUNT": {}, "UTIL1_DIED_WITH_COUNT/TOTAL_DISTANCE": {}, 
              "UTIL1_DIED_WITH_COUNT/TOTAL_VELOCITY": {}, "UTIL1_DIED_WITH_COUNT/TIME": {}, 
              "UTIL1_DIED_WITH_COUNT/TIME_ALIVE": {}, "UTIL1_DIED_WITH_COUNT/KILL_COUNT": {}, "UTIL1_DIED_WITH_COUNT/DEATH_COUNT": {}, 
              "UTIL1_DIED_WITH_COUNT/ASSIST_COUNT": {}, "UTIL1_DIED_WITH_COUNT/SURVIVE_COUNT": {}, "UTIL1_DIED_WITH_COUNT/IDLE_COUNT": {}, 
              "UTIL1_DIED_WITH_COUNT/TRADE_COUNT": {}, "UTIL2_USAGE_COUNT/TOTAL_DISTANCE": {}, 
              "UTIL2_USAGE_COUNT/TOTAL_VELOCITY": {}, "UTIL2_USAGE_COUNT/TIME": {}, 
              "UTIL2_USAGE_COUNT/TIME_ALIVE": {}, "UTIL2_USAGE_COUNT/KILL_COUNT": {}, "UTIL2_USAGE_COUNT/DEATH_COUNT": {}, 
              "UTIL2_USAGE_COUNT/ASSIST_COUNT": {}, "UTIL2_USAGE_COUNT/SURVIVE_COUNT": {}, "UTIL2_USAGE_COUNT/IDLE_COUNT": {}, 
              "UTIL2_USAGE_COUNT/TRADE_COUNT": {}, "UTIL2_SAVED_COUNT/TOTAL_DISTANCE": {}, 
              "UTIL2_SAVED_COUNT/TOTAL_VELOCITY": {}, "UTIL2_SAVED_COUNT/TIME": {}, 
              "UTIL2_SAVED_COUNT/TIME_ALIVE": {}, "UTIL2_SAVED_COUNT/KILL_COUNT": {}, "UTIL2_SAVED_COUNT/DEATH_COUNT": {}, 
              "UTIL2_SAVED_COUNT/ASSIST_COUNT": {}, "UTIL2_SAVED_COUNT/SURVIVE_COUNT": {}, "UTIL2_SAVED_COUNT/IDLE_COUNT": {}, 
              "UTIL2_SAVED_COUNT/TRADE_COUNT": {}, "UTIL2_DIED_WITH_COUNT/TOTAL_DISTANCE": {}, 
              "UTIL2_DIED_WITH_COUNT/TOTAL_VELOCITY": {}, "UTIL2_DIED_WITH_COUNT/TIME": {}, 
              "UTIL2_DIED_WITH_COUNT/TIME_ALIVE": {}, "UTIL2_DIED_WITH_COUNT/KILL_COUNT": {}, "UTIL2_DIED_WITH_COUNT/DEATH_COUNT": {}, 
              "UTIL2_DIED_WITH_COUNT/ASSIST_COUNT": {}, "UTIL2_DIED_WITH_COUNT/SURVIVE_COUNT": {}, "UTIL2_DIED_WITH_COUNT/IDLE_COUNT": {}, 
              "UTIL2_DIED_WITH_COUNT/TRADE_COUNT": {}, "ABIL_USAGE_COUNT/TOTAL_DISTANCE": {}, 
              "ABIL_USAGE_COUNT/TOTAL_VELOCITY": {}, "ABIL_USAGE_COUNT/TIME": {}, 
              "ABIL_USAGE_COUNT/TIME_ALIVE": {}, "ABIL_USAGE_COUNT/KILL_COUNT": {}, "ABIL_USAGE_COUNT/DEATH_COUNT": {}, 
              "ABIL_USAGE_COUNT/ASSIST_COUNT": {}, "ABIL_USAGE_COUNT/SURVIVE_COUNT": {}, "ABIL_USAGE_COUNT/IDLE_COUNT": {}, 
              "ABIL_USAGE_COUNT/TRADE_COUNT": {}, "ABIL_REGAINED_COUNT/TOTAL_DISTANCE": {}, 
              "ABIL_REGAINED_COUNT/TOTAL_VELOCITY": {}, "ABIL_REGAINED_COUNT/TIME": {}, 
              "ABIL_REGAINED_COUNT/TIME_ALIVE": {}, "ABIL_REGAINED_COUNT/KILL_COUNT": {}, "ABIL_REGAINED_COUNT/DEATH_COUNT": {}, 
              "ABIL_REGAINED_COUNT/ASSIST_COUNT": {}, "ABIL_REGAINED_COUNT/SURVIVE_COUNT": {}, "ABIL_REGAINED_COUNT/IDLE_COUNT": {}, 
              "ABIL_REGAINED_COUNT/TRADE_COUNT": {}, "ABIL_SAVED_COUNT/TOTAL_DISTANCE": {}, 
              "ABIL_SAVED_COUNT/TOTAL_VELOCITY": {}, "ABIL_SAVED_COUNT/TIME": {}, 
              "ABIL_SAVED_COUNT/TIME_ALIVE": {}, "ABIL_SAVED_COUNT/KILL_COUNT": {}, "ABIL_SAVED_COUNT/DEATH_COUNT": {}, 
              "ABIL_SAVED_COUNT/ASSIST_COUNT": {}, "ABIL_SAVED_COUNT/SURVIVE_COUNT": {}, "ABIL_SAVED_COUNT/IDLE_COUNT": {}, 
              "ABIL_SAVED_COUNT/TRADE_COUNT": {}, "ABIL_DIED_WITH_COUNT/TOTAL_DISTANCE": {}, 
              "ABIL_DIED_WITH_COUNT/TOTAL_VELOCITY": {}, "ABIL_DIED_WITH_COUNT/TIME": {}, 
              "ABIL_DIED_WITH_COUNT/TIME_ALIVE": {}, "ABIL_DIED_WITH_COUNT/KILL_COUNT": {}, "ABIL_DIED_WITH_COUNT/DEATH_COUNT": {}, 
              "ABIL_DIED_WITH_COUNT/ASSIST_COUNT": {}, "ABIL_DIED_WITH_COUNT/SURVIVE_COUNT": {}, "ABIL_DIED_WITH_COUNT/IDLE_COUNT": {}, 
              "ABIL_DIED_WITH_COUNT/TRADE_COUNT": {}, "ULT_USAGE_COUNT/TOTAL_DISTANCE": {}, 
              "ULT_USAGE_COUNT/TOTAL_VELOCITY": {}, "ULT_USAGE_COUNT/TIME": {}, 
              "ULT_USAGE_COUNT/TIME_ALIVE": {}, "ULT_USAGE_COUNT/KILL_COUNT": {}, "ULT_USAGE_COUNT/DEATH_COUNT": {}, 
              "ULT_USAGE_COUNT/ASSIST_COUNT": {}, "ULT_USAGE_COUNT/SURVIVE_COUNT": {}, "ULT_USAGE_COUNT/IDLE_COUNT": {}, 
              "ULT_USAGE_COUNT/TRADE_COUNT": {}, "ULT_SAVED_COUNT/TOTAL_DISTANCE": {}, 
              "ULT_SAVED_COUNT/TOTAL_VELOCITY": {}, "ULT_SAVED_COUNT/TIME": {}, 
              "ULT_SAVED_COUNT/TIME_ALIVE": {}, "ULT_SAVED_COUNT/KILL_COUNT": {}, "ULT_SAVED_COUNT/DEATH_COUNT": {}, 
              "ULT_SAVED_COUNT/ASSIST_COUNT": {}, "ULT_SAVED_COUNT/SURVIVE_COUNT": {}, "ULT_SAVED_COUNT/IDLE_COUNT": {}, 
              "ULT_SAVED_COUNT/TRADE_COUNT": {}, 
              "ULT_DEATH_COUNT/TOTAL_DISTANCE": {}, "ULT_DEATH_COUNT/TOTAL_VELOCITY": {}, "ULT_DEATH_COUNT/TIME": {}, 
              "ULT_DEATH_COUNT/TIME_ALIVE": {}, "ULT_DEATH_COUNT/KILL_COUNT": {}, "ULT_DEATH_COUNT/DEATH_COUNT": {}, 
              "ULT_DEATH_COUNT/ASSIST_COUNT": {}, "ULT_DEATH_COUNT/SURVIVE_COUNT": {}, "ULT_DEATH_COUNT/IDLE_COUNT": {}, 
              "ULT_DEATH_COUNT/TRADE_COUNT": {}, 

              "PROGRESSION_COUNT/TOTAL_DISTANCE": {}, "HOLD_COUNT/TOTAL_DISTANCE": {}, "EXECUTION_COUNT/TOTAL_DISTANCE": {}, 
              "SWITCH_COUNT/TOTAL_DISTANCE": {}, "ROTATION_COUNT/TOTAL_DISTANCE": {}, "PINCER_COUNT/TOTAL_DISTANCE": {}, 
              "FLANK_COUNT/TOTAL_DISTANCE": {}, "COVER_COUNT/TOTAL_DISTANCE": {}, 
              "PROGRESSION_COUNT/TOTAL_VELOCITY": {}, "HOLD_COUNT/TOTAL_VELOCITY": {}, "EXECUTION_COUNT/TOTAL_VELOCITY": {}, 
              "SWITCH_COUNT/TOTAL_VELOCITY": {}, "ROTATION_COUNT/TOTAL_VELOCITY": {}, "PINCER_COUNT/TOTAL_VELOCITY": {}, 
              "FLANK_COUNT/TOTAL_VELOCITY": {}, "COVER_COUNT/TOTAL_VELOCITY": {}, 
              "PROGRESSION_COUNT/TIME": {}, "HOLD_COUNT/TIME": {}, "EXECUTION_COUNT/TIME": {}, "SWITCH_COUNT/TIME": {}, 
              "ROTATION_COUNT/TIME": {}, "PINCER_COUNT/TIME": {}, "FLANK_COUNT/TIME": {}, "COVER_COUNT/TIME": {}, 
              "PROGRESSION_COUNT/TIME_ALIVE": {}, "HOLD_COUNT/TIME_ALIVE": {}, "EXECUTION_COUNT/TIME_ALIVE": {}, "SWITCH_COUNT/TIME_ALIVE": {}, 
              "ROTATION_COUNT/TIME_ALIVE": {}, "PINCER_COUNT/TIME_ALIVE": {}, "FLANK_COUNT/TIME_ALIVE": {}, "COVER_COUNT/TIME_ALIVE": {}, 
              "PROGRESSION_COUNT/KILL_COUNT": {}, "HOLD_COUNT/KILL_COUNT": {}, "EXECUTION_COUNT/KILL_COUNT": {}, "SWITCH_COUNT/KILL_COUNT": {}, 
              "ROTATION_COUNT/KILL_COUNT": {}, "PINCER_COUNT/KILL_COUNT": {}, "FLANK_COUNT/KILL_COUNT": {}, "COVER_COUNT/KILL_COUNT": {}, 
              "PROGRESSION_COUNT/DEATH_COUNT": {}, "HOLD_COUNT/DEATH_COUNT": {}, "EXECUTION_COUNT/DEATH_COUNT": {}, 
              "SWITCH_COUNT/DEATH_COUNT": {}, "ROTATION_COUNT/DEATH_COUNT": {}, "PINCER_COUNT/DEATH_COUNT": {}, "FLANK_COUNT/DEATH_COUNT": {}, 
              "COVER_COUNT/DEATH_COUNT": {}, 
              "PROGRESSION_COUNT/ASSIST_COUNT": {}, "HOLD_COUNT/ASSIST_COUNT": {}, "EXECUTION_COUNT/ASSIST_COUNT": {}, 
              "SWITCH_COUNT/ASSIST_COUNT": {}, "ROTATION_COUNT/ASSIST_COUNT": {}, "PINCER_COUNT/ASSIST_COUNT": {}, 
              "FLANK_COUNT/ASSIST_COUNT": {}, "COVER_COUNT/ASSIST_COUNT": {}, 
              "PROGRESSION_COUNT/SURVIVE_COUNT": {}, "HOLD_COUNT/SURVIVE_COUNT": {}, "EXECUTION_COUNT/SURVIVE_COUNT": {}, 
              "SWITCH_COUNT/SURVIVE_COUNT": {}, "ROTATION_COUNT/SURVIVE_COUNT": {}, "PINCER_COUNT/SURVIVE_COUNT": {}, 
              "FLANK_COUNT/SURVIVE_COUNT": {}, "COVER_COUNT/SURVIVE_COUNT": {}, 
              "PROGRESSION_COUNT/IDLE_COUNT": {}, "HOLD_COUNT/IDLE_COUNT": {}, "EXECUTION_COUNT/IDLE_COUNT": {}, 
              "SWITCH_COUNT/IDLE_COUNT": {}, "ROTATION_COUNT/IDLE_COUNT": {}, "PINCER_COUNT/IDLE_COUNT": {}, 
              "FLANK_COUNT/IDLE_COUNT": {}, "COVER_COUNT/IDLE_COUNT": {}, 
              "PROGRESSION_COUNT/TRADE_COUNT": {}, "HOLD_COUNT/TRADE_COUNT": {}, "EXECUTION_COUNT/TRADE_COUNT": {}, 
              "SWITCH_COUNT/TRADE_COUNT": {}, "ROTATION_COUNT/TRADE_COUNT": {}, "PINCER_COUNT/TRADE_COUNT": {}, 
              "FLANK_COUNT/TRADE_COUNT": {}, "COVER_COUNT/TRADE_COUNT": {}, 

              "TIME": {}, "%_TIME": {}, "TIME_ALIVE": {}, "%_TIME_ALIVE": {}, "TIME_DEAD": {}, "%_TIME_DEAD": {}, 
              "TIME_MOVING": {}, "%_TIME_MOVING": {}, "TIME_STATIONARY": {}, "%_TIME_STATIONARY": {}, 
              
              "TOTAL_AVG_LOC": {}, "TOTAL_AVG_LOC_COORD_X": {}, "TOTAL_AVG_LOC_COORD_Y": {}, 
              "TOTAL_AVG_MOMENTUM": {}, "TOTAL_AVG_MOMENTUM_COORD_X": {}, "TOTAL_AVG_MOMENTUM_COORD_Y": {}, 
              "%_DISTANCE": {}, "TOTAL_DISTANCE": {}, "TOTAL_DISTANCE/TIME": {}, "TOTAL_VELOCITY": {}, 
              "%_HORIZ_DISTANCE": {}, "TOTAL_HORIZ_DISTANCE": {}, "TOTAL_HORIZ_DISTANCE/TIME": {}, "TOTAL_HORIZ_VELOCITY": {}, 
              "%_VERT_DISTANCE": {}, "TOTAL_VERT_DISTANCE": {}, "TOTAL_VERT_DISTANCE/TIME": {}, "TOTAL_VERT_VELOCITY": {}, 

              "TOTAL_DISTANCE/KILL_COUNT": {}, "TOTAL_VELOCITY/KILL_COUNT": {}, "TIME/KILL_COUNT": {}, "TIME_ALIVE/KILL_COUNT": {}, 
              "TOTAL_DISTANCE/DEATH_COUNT": {}, "TOTAL_VELOCITY/DEATH_COUNT": {}, "TIME/DEATH_COUNT": {}, "TIME_ALIVE/DEATH_COUNT": {}, 
              "TOTAL_DISTANCE/ASSIST_COUNT": {}, "TOTAL_VELOCITY/ASSIST_COUNT": {}, "TIME/ASSIST_COUNT": {}, "TIME_ALIVE/ASSIST_COUNT": {}, 
              "TOTAL_DISTANCE/SURVIVE_COUNT": {}, "TOTAL_VELOCITY/SURVIVE_COUNT": {}, "TIME/SURVIVE_COUNT": {}, "TIME_ALIVE/SURVIVE_COUNT": {}, 
              "TOTAL_DISTANCE/IDLE_COUNT": {}, "TOTAL_VELOCITY/IDLE_COUNT": {}, "TIME/IDLE_COUNT": {}, "TIME_ALIVE/IDLE_COUNT": {}, 
              "TOTAL_DISTANCE/TRADE_COUNT": {}, "TOTAL_VELOCITY/TRADE_COUNT": {}, "TIME/TRADE_COUNT": {}, "TIME_ALIVE/TRADE_COUNT": {}, 

              }
            self.agent_names.append(a)
            if len(a) > 0 and a not in names[o]:  names[o].append(a)

    for an in self.agent_names:  self.ac[an] = []
    print(self.ac, names, overlay)
    for o in overlay:
      self.ac[list(set(names[o]))[0]].append(o)
      for rdlen in range(len(self.round_results)):
        self.agents[o]["AGENT"][rdlen+1] = list(set(names[o]))[-1]
        self.agents[o]["ROLE"][rdlen+1] = search_role(self.agents[o]["AGENT"][rdlen+1])
        self.agents[o]["SUBROLE"][rdlen+1] = ""
    self.agent_names = list(set(self.agent_names))
    frames = fuse(self.rs, self.rm, self.rte, self.rpe, self.rge, self.rf)
    for frd in frames.keys():
      self.frames[frd] = {}
      for fri in frames[frd]:
        self.frames[frd][fri[0]] = fri[1]

    for i in self.rbs:
      rdix = self.rbs.index(i) + 1
      rdside = get_side(self.x[i[0]:i[1] + 4])

      self.round_info[rdix] = {
        "PUBLIC": self.public, "MAP": self.mapname, "TEAM_LEFT": self.teamleft, "TEAM_RIGHT": self.teamright, 
        "NUMBER": rdix, "ATK_SIDE": rdside, "KEYPOINTS": self.frames[rdix], "EVENTS": None, "FEED": None, 
        "LEFT_KILL_COUNT": 0, "RIGHT_KILL_COUNT": 0, "LEFT_DEATH_COUNT": 0, "RIGHT_DEATH_COUNT": 0, 
        "LEFT_SURVIVE_COUNT": 0, "RIGHT_SURVIVE_COUNT": 0, "LEFT_IDLE_COUNT": 0, "RIGHT_IDLE_COUNT": 0, 
        "LEFT_ASSIST_COUNT": 0, "RIGHT_ASSIST_COUNT": 0, "LEFT_REVIVE_COUNT": 0, "RIGHT_REVIVE_COUNT": 0, 
        "LEFT_TRADE_COUNT": 0, "RIGHT_TRADE_COUNT": 0,  "LEFT_PLANT_COUNT": 0, "RIGHT_PLANT_COUNT": 0, 
        "LEFT_DEFUSE_COUNT": 0, "RIGHT_DEFUSE_COUNT": 0, 
        "LEFT_K/D": 0, "RIGHT_K/D": 0, "LEFT_S/I": 0, "RIGHT_S/I": 0, 
        "OPENING": "N", "LEFT_UTIL_OPENING": 0, "RIGHT_UTIL_OPENING": 0, 
        "LEFT_UTIL1_COUNT": 0, "RIGHT_UTIL1_COUNT": 0, "LEFT_UTIL2_COUNT": 0, "RIGHT_UTIL2_COUNT": 0, 
        "LEFT_ABIL_COUNT": 0, "RIGHT_ABIL_COUNT": 0, "LEFT_ULT_COUNT": 0, "RIGHT_ULT_COUNT": 0, 
        "LEFT_AVG_DISTANCE": 0, "RIGHT_AVG_DISTANCE": 0, "LEFT_AVG_VELOCITY": 0, "RIGHT_AVG_VELOCITY": 0, 
        "LEFT_AVG_LOC": 0, "RIGHT_AVG_LOC": 0, "LEFT_AVG_MOMENTUM": 0, "RIGHT_AVG_MOMENTUM": 0, 
        "LEFT_AVG_TIME_ALIVE_RATIO": 0, "RIGHT_AVG_TIME_ALIVE_RATIO": 0, "LEFT_AVG_TIME_DEAD_RATIO": 0, "RIGHT_AVG_TIME_DEAD_RATIO": 0, 
        "LEFT_AVG_TIME_MOVING_RATIO": 0, "RIGHT_AVG_TIME_MOVING_RATIO": 0, 
        "LEFT_AVG_TIME_STATIONARY_RATIO": 0, "RIGHT_AVG_TIME_STATIONARY_RATIO": 0, 
        "LEFT_PROGRESSION_COUNT": 0, "RIGHT_PROGRESSION_COUNT": 0, "LEFT_HOLD_COUNT": 0, "RIGHT_HOLD_COUNT": 0, 
        "LEFT_EXECUTION_COUNT": 0, "RIGHT_EXECUTION_COUNT": 0, "LEFT_SWITCH_COUNT": 0, "RIGHT_SWITCH_COUNT": 0, 
        "LEFT_ROTATION_COUNT": 0, "RIGHT_ROTATION_COUNT": 0, "LEFT_PINCER_COUNT": 0, "RIGHT_PINCER_COUNT": 0, 
        "LEFT_FLANK_COUNT": 0, "RIGHT_FLANK_COUNT": 0, "LEFT_COVER_COUNT": 0, "RIGHT_COVER_COUNT": 0, 
        "LEFT_DAMAGE_TAKEN": 0, "RIGHT_DAMAGE_TAKEN": 0, "LEFT_HEALTH_REGAINED": 0, "RIGHT_HEALTH_REGAINED": 0, 
        "LEFT_ECON": None, "RIGHT_ECON": None, # "LEFT_OPENING": None, "RIGHT_OPENING": None, 
        "PLANTED": -1, "DEFUSED": -1, "ATK_WIN": False, "DEF_WIN": False, 
        "LEFT_PLAYER_DIFFERENCE": 0, "LEFT_TRAVEL_DIFFERENCE": 0,  "LEFT_VELOCITY_DIFFERENCE": 0, 
        "LEFT_UTIL1_DIFFERENCE": 0, "LEFT_UTIL2_DIFFERENCE": 0, "LEFT_ABIL_DIFFERENCE": 0, "LEFT_ULT_DIFFERENCE": 0, 
        "LEFT_TOTAL_UTIL_DIFFERENCE": 0, 
        "RIGHT_PLAYER_DIFFERENCE": 0, "RIGHT_TRAVEL_DIFFERENCE": 0,  "RIGHT_VELOCITY_DIFFERENCE": 0, 
        "RIGHT_UTIL1_DIFFERENCE": 0, "RIGHT_UTIL2_DIFFERENCE": 0, "RIGHT_ABIL_DIFFERENCE": 0, "RIGHT_ULT_DIFFERENCE": 0, 
        "RIGHT_TOTAL_UTIL_DIFFERENCE": 0, 
        "LEFT_ALMOST_DECISIVE": False, "LEFT_DECISIVE": False, "RIGHT_ALMOST_DECISIVE": False, "RIGHT_DECISIVE": False, 
        "WINNING": "N", "WINNER": "N", "LEFT_ROUND_DIFFERENCE": 0, "RIGHT_ROUND_DIFFERENCE": 0, 
        "PREVIOUS_RESULT": None, "RESULT": None, 
        "LEFT_1_AGENT": inv_search_ac("LEFT_1", self.ac), "LEFT_2_AGENT": inv_search_ac("LEFT_2", self.ac), 
        "LEFT_3_AGENT": inv_search_ac("LEFT_3", self.ac), "LEFT_4_AGENT": inv_search_ac("LEFT_4", self.ac), 
        "LEFT_5_AGENT": inv_search_ac("LEFT_5", self.ac), "RIGHT_1_AGENT": inv_search_ac("RIGHT_1", self.ac), 
        "RIGHT_2_AGENT": inv_search_ac("RIGHT_2", self.ac), "RIGHT_3_AGENT": inv_search_ac("RIGHT_3", self.ac), 
        "RIGHT_4_AGENT": inv_search_ac("RIGHT_4", self.ac), "RIGHT_5_AGENT": inv_search_ac("RIGHT_5", self.ac), 
        "LEFT_1": None, "LEFT_2": None, "LEFT_3": None, "LEFT_4": None, "LEFT_5": None, 
        "RIGHT_1": None, "RIGHT_2": None, "RIGHT_3": None, "RIGHT_4": None, "RIGHT_5": None, 
        "_A": None, 
        }

      l1u, l2u, l3u, l4u, l5u, r1u, r2u, r3u, r4u, r5u = ([], [], [], [], [], [], [], [], [], [])
      l1w, l2w, l3w, l4w, l5w, r1w, r2w, r3w, r4w, r5w = ([], [], [], [], [], [], [], [], [], [])
      l1h, l2h, l3h, l4h, l5h, r1h, r2h, r3h, r4h, r5h = ([], [], [], [], [], [], [], [], [], [])
      l1sh, l2sh, l3sh, l4sh, l5sh, r1sh, r2sh, r3sh, r4sh, r5sh = ([], [], [], [], [], [], [], [], [], [])
      fdtmp = []
      for j in range(i[0], i[1] + 4):
        fdi = search_feed(self.x[j], rdside, self.ac, j)
        for i in fdi[0]:  fdtmp.append((i, fdi[1]))

        l1u.append(search_abils(self.x[j], "LEFT_1", j)); l2u.append(search_abils(self.x[j], "LEFT_2", j)); l3u.append(search_abils(self.x[j], "LEFT_3", j)); l4u.append(search_abils(self.x[j], "LEFT_4", j)); l5u.append(search_abils(self.x[j], "LEFT_5", j))
        r1u.append(search_abils(self.x[j], "RIGHT_1", j)); r2u.append(search_abils(self.x[j], "RIGHT_2", j)); r3u.append(search_abils(self.x[j], "RIGHT_3", j)); r4u.append(search_abils(self.x[j], "RIGHT_4", j)); r5u.append(search_abils(self.x[j], "RIGHT_5", j))
        l1w.append(search_wps(self.x[j], "LEFT_1", j)); l2w.append(search_wps(self.x[j], "LEFT_2", j)); l3w.append(search_wps(self.x[j], "LEFT_3", j)); l4w.append(search_wps(self.x[j], "LEFT_4", j)); l5w.append(search_wps(self.x[j], "LEFT_5", j))
        r1w.append(search_wps(self.x[j], "RIGHT_1", j)); r2w.append(search_wps(self.x[j], "RIGHT_2", j)); r3w.append(search_wps(self.x[j], "RIGHT_3", j)); r4w.append(search_wps(self.x[j], "RIGHT_4", j)); r5w.append(search_wps(self.x[j], "RIGHT_5", j))
        l1h.append(search_health(self.x[j], rdside, "LEFT_1", j)); l2h.append(search_health(self.x[j], rdside, "LEFT_2", j)); l3h.append(search_health(self.x[j], rdside, "LEFT_3", j)); l4h.append(search_health(self.x[j], rdside, "LEFT_4", j)); l5h.append(search_health(self.x[j], rdside, "LEFT_5", j))
        r1h.append(search_health(self.x[j], rdside, "RIGHT_1", j)); r2h.append(search_health(self.x[j], rdside, "RIGHT_2", j)); r3h.append(search_health(self.x[j], rdside, "RIGHT_3", j)); r4h.append(search_health(self.x[j], rdside, "RIGHT_4", j)); r5h.append(search_health(self.x[j], rdside, "RIGHT_5", j))
        notnullappend(l1sh, search_spike_held(self.x[j], "LEFT_1", j)); notnullappend(l2sh, search_spike_held(self.x[j], "LEFT_2", j)); notnullappend(l3sh, search_spike_held(self.x[j], "LEFT_3", j)); notnullappend(l4sh, search_spike_held(self.x[j], "LEFT_4", j)); notnullappend(l5sh, search_spike_held(self.x[j], "LEFT_5", j))
        notnullappend(r1sh, search_spike_held(self.x[j], "RIGHT_1", j)); notnullappend(r2sh, search_spike_held(self.x[j], "RIGHT_2", j)); notnullappend(r3sh, search_spike_held(self.x[j], "RIGHT_3", j)); notnullappend(r4sh, search_spike_held(self.x[j], "RIGHT_4", j)); notnullappend(r5sh, search_spike_held(self.x[j], "RIGHT_5", j))

        for a in self.agent_names:
          if search(self.x[j], a):  agent_trk[a].append(((search(self.x[j], a, ret_loc=True)), j, rdix))
          if search(self.x[j], a + "_WITH_SPIKE"):  agent_trk[a].append(((search(self.x[j], a + "_WITH_SPIKE", ret_loc=True)), j, rdix))
      feed[rdix] = feed_process(fdtmp)

      self.agents["LEFT_1"]["UTIL"][rdix] = l1u; self.agents["LEFT_2"]["UTIL"][rdix] = l2u; self.agents["LEFT_3"]["UTIL"][rdix] = l3u; self.agents["LEFT_4"]["UTIL"][rdix] = l4u; self.agents["LEFT_5"]["UTIL"][rdix] = l5u
      self.agents["RIGHT_1"]["UTIL"][rdix] = r1u; self.agents["RIGHT_2"]["UTIL"][rdix] = r2u; self.agents["RIGHT_3"]["UTIL"][rdix] = r3u; self.agents["RIGHT_4"]["UTIL"][rdix] = r4u; self.agents["RIGHT_5"]["UTIL"][rdix] = r5u
      self.agents["LEFT_1"]["WEAPON"][rdix] = l1w; self.agents["LEFT_2"]["WEAPON"][rdix] = l2w; self.agents["LEFT_3"]["WEAPON"][rdix] = l3w; self.agents["LEFT_4"]["WEAPON"][rdix] = l4w; self.agents["LEFT_5"]["WEAPON"][rdix] = l5w
      self.agents["RIGHT_1"]["WEAPON"][rdix] = r1w; self.agents["RIGHT_2"]["WEAPON"][rdix] = r2w; self.agents["RIGHT_3"]["WEAPON"][rdix] = r3w; self.agents["RIGHT_4"]["WEAPON"][rdix] = r4w; self.agents["RIGHT_5"]["WEAPON"][rdix] = r5w
      self.agents["LEFT_1"]["HEALTH"][rdix] = l1h; self.agents["LEFT_2"]["HEALTH"][rdix] = l2h; self.agents["LEFT_3"]["HEALTH"][rdix] = l3h; self.agents["LEFT_4"]["HEALTH"][rdix] = l4h; self.agents["LEFT_5"]["HEALTH"][rdix] = l5h
      self.agents["RIGHT_1"]["HEALTH"][rdix] = r1h; self.agents["RIGHT_2"]["HEALTH"][rdix] = r2h; self.agents["RIGHT_3"]["HEALTH"][rdix] = r3h; self.agents["RIGHT_4"]["HEALTH"][rdix] = r4h; self.agents["RIGHT_5"]["HEALTH"][rdix] = r5h
      self.agents["LEFT_1"]["SPIKE_HELD"][rdix] = l1sh; self.agents["LEFT_2"]["SPIKE_HELD"][rdix] = l2sh; self.agents["LEFT_3"]["SPIKE_HELD"][rdix] = l3sh; self.agents["LEFT_4"]["SPIKE_HELD"][rdix] = l4sh; self.agents["LEFT_5"]["SPIKE_HELD"][rdix] = l5sh
      self.agents["RIGHT_1"]["SPIKE_HELD"][rdix] = r1sh; self.agents["RIGHT_2"]["SPIKE_HELD"][rdix] = r2sh; self.agents["RIGHT_3"]["SPIKE_HELD"][rdix] = r3sh; self.agents["RIGHT_4"]["SPIKE_HELD"][rdix] = r4sh; self.agents["RIGHT_5"]["SPIKE_HELD"][rdix] = r5sh

    filled = {}
    wpsrd = {}
    def analyze(feedx, ri, ags, fltr):
      fx = parse_filter(fltr, ags)
      collect_kdetc(feedx, ri, ags)
      for kk in overlay:
        aa = inv_search_ac(kk, self.ac)
        populate(aa, self.ac, agent_trk[aa], self.map_obj, self.round_info, self.agents)
        filled[kk] = fillin(kk, ri, ags, self.map_obj)
        for rdnum in range(1, max(list(self.round_info.keys())) + 1):
          wpss = ags_classify_wps(rdnum, self.agents, start=True)
          wpsrd[rdnum] = wpss
          wpse = ags_classify_wps(rdnum, self.agents, end=True)
          dmgall = ags_measure_dmg(rdnum, self.agents, self.round_info[rdnum]["KEYPOINTS"]["END"])
          dmg = ags_measure_total_dmg(rdnum, self.agents, self.round_info[rdnum]["KEYPOINTS"]["END"])
          ags[kk]["STARTING_ECONOMY"][rdnum] = wpss[kk]
          ags[kk]["ENDING_ECONOMY"][rdnum] = wpse[kk] if ags[kk]["DEATH_COUNT"][rdnum] == 0 else "PISTOL"
          ags[kk]["HEALTH_VARIATION"][rdnum] = dmgall[kk]
          ags[kk]["TOTAL_DAMAGE_TAKEN"][rdnum] = dmg[kk]["TAKEN"]
          ags[kk]["TOTAL_HEALTH_REGAINED"][rdnum] = dmg[kk]["REGAINED"]
      for kk in overlay:
        self.agents[kk]["POSITION"] = filled[kk]
        collect_util(kk, self.round_results, ri, ags)
      store_events(ri, ags)
      measure_aggs(ri, ags)

    fltrx = ""
    analyze(feed, self.round_info, self.agents, fltrx)
    for fif, fjf in feed.items():
      for fkf in fjf:
        fkf["FEED_EVENT"]["K"] = {"PLAYER": fkf["FEED_EVENT"]["K"], "LOC": get_loc_at(self.round_info, self.agents, fkf["FRAME"] - 1, fkf["FEED_EVENT"]["K"], last=True)}
        fkf["FEED_EVENT"]["D"] = {"PLAYER": fkf["FEED_EVENT"]["D"], "LOC": get_loc_at(self.round_info, self.agents, fkf["FRAME"] - 1, fkf["FEED_EVENT"]["D"], last=True)}
        fkf["FEED_EVENT"]["A"] = [{"PLAYER": faa, "LOC": get_loc_at(self.round_info, self.agents, fkf["FRAME"] - 1, faa)} for faa in fkf["FEED_EVENT"]["A"]]
    for rdi in range(len(self.round_info)):  self.round_info[rdi+1]["FEED"] = feed[rdi+1]

    for rdnum in range(1, max(list(self.round_info.keys())) + 1):
      rdtime = self.round_info[rdnum]["KEYPOINTS"]["END"] - self.round_info[rdnum]["KEYPOINTS"]["START"] + 1
      # for ovk in overlay:  self.round_info[rdnum][ovk] = ags_get_rd(rdnum, self.agents, pa=ovk)
      self.round_info[rdnum]["LEFT_KILL_COUNT"] = rd_get_sum("KILL_COUNT", rdnum, self.agents, sd="L")
      self.round_info[rdnum]["RIGHT_KILL_COUNT"] = rd_get_sum("KILL_COUNT", rdnum, self.agents, sd="R")
      self.round_info[rdnum]["LEFT_DEATH_COUNT"] = rd_get_sum("DEATH_COUNT", rdnum, self.agents, sd="L")
      self.round_info[rdnum]["RIGHT_DEATH_COUNT"] = rd_get_sum("DEATH_COUNT", rdnum, self.agents, sd="R")
      self.round_info[rdnum]["LEFT_SURVIVE_COUNT"] = rd_get_sum("SURVIVE_COUNT", rdnum, self.agents, sd="L")
      self.round_info[rdnum]["RIGHT_SURVIVE_COUNT"] = rd_get_sum("SURVIVE_COUNT", rdnum, self.agents, sd="R")
      self.round_info[rdnum]["LEFT_IDLE_COUNT"] = rd_get_sum("IDLE_COUNT", rdnum, self.agents, sd="L")
      self.round_info[rdnum]["RIGHT_IDLE_COUNT"] = rd_get_sum("IDLE_COUNT", rdnum, self.agents, sd="R")
      self.round_info[rdnum]["LEFT_ASSIST_COUNT"] = rd_get_sum("ASSIST_COUNT", rdnum, self.agents, sd="L")
      self.round_info[rdnum]["RIGHT_ASSIST_COUNT"] = rd_get_sum("ASSIST_COUNT", rdnum, self.agents, sd="R")
      self.round_info[rdnum]["LEFT_REVIVE_COUNT"] = rd_get_sum("REVIVE_COUNT", rdnum, self.agents, sd="L")
      self.round_info[rdnum]["RIGHT_REVIVE_COUNT"] = rd_get_sum("REVIVE_COUNT", rdnum, self.agents, sd="R")
      self.round_info[rdnum]["LEFT_TRADE_COUNT"] = rd_get_sum("TRADE_COUNT", rdnum, self.agents, sd="L")
      self.round_info[rdnum]["RIGHT_TRADE_COUNT"] = rd_get_sum("TRADE_COUNT", rdnum, self.agents, sd="R")
      self.round_info[rdnum]["LEFT_PLANT_COUNT"] = rd_get_sum("PLANT_COUNT", rdnum, self.agents, sd="L")
      self.round_info[rdnum]["RIGHT_PLANT_COUNT"] = rd_get_sum("PLANT_COUNT", rdnum, self.agents, sd="R")
      self.round_info[rdnum]["LEFT_DEFUSE_COUNT"] = rd_get_sum("DEFUSE_COUNT", rdnum, self.agents, sd="L")
      self.round_info[rdnum]["RIGHT_DEFUSE_COUNT"] = rd_get_sum("DEFUSE_COUNT", rdnum, self.agents, sd="R")
      self.round_info[rdnum]["LEFT_UTIL1_COUNT"] = rd_get_sum("UTIL1_USAGE_COUNT", rdnum, self.agents, sd="L")
      self.round_info[rdnum]["RIGHT_UTIL1_COUNT"] = rd_get_sum("UTIL1_USAGE_COUNT", rdnum, self.agents, sd="R")
      self.round_info[rdnum]["LEFT_UTIL2_COUNT"] = rd_get_sum("UTIL2_USAGE_COUNT", rdnum, self.agents, sd="L")
      self.round_info[rdnum]["RIGHT_UTIL2_COUNT"] = rd_get_sum("UTIL2_USAGE_COUNT", rdnum, self.agents, sd="R")
      self.round_info[rdnum]["LEFT_ABIL_COUNT"] = rd_get_sum("ABIL_USAGE_COUNT", rdnum, self.agents, sd="L")
      self.round_info[rdnum]["RIGHT_ABIL_COUNT"] = rd_get_sum("ABIL_USAGE_COUNT", rdnum, self.agents, sd="R")
      self.round_info[rdnum]["LEFT_ULT_COUNT"] = rd_get_sum("ULT_USAGE_COUNT", rdnum, self.agents, sd="L")
      self.round_info[rdnum]["RIGHT_ULT_COUNT"] = rd_get_sum("ULT_USAGE_COUNT", rdnum, self.agents, sd="R")
      self.round_info[rdnum]["LEFT_AVG_DISTANCE"] = rd_get_avg("TOTAL_DISTANCE", rdnum, self.agents, sd="L")
      self.round_info[rdnum]["RIGHT_AVG_DISTANCE"] = rd_get_avg("TOTAL_DISTANCE", rdnum, self.agents, sd="R")
      self.round_info[rdnum]["LEFT_AVG_VELOCITY"] = rd_get_avg("TOTAL_VELOCITY", rdnum, self.agents, sd="L")
      self.round_info[rdnum]["RIGHT_AVG_VELOCITY"] = rd_get_avg("TOTAL_VELOCITY", rdnum, self.agents, sd="R")
      self.round_info[rdnum]["LEFT_AVG_LOC"] = \
        in_loc([rd_get_avg("TOTAL_AVG_LOC_COORD_X", rdnum, self.agents, sd="L"), rd_get_avg("TOTAL_AVG_LOC_COORD_Y", rdnum, self.agents, sd="L")], self.map_obj)
      self.round_info[rdnum]["RIGHT_AVG_LOC"] = \
        in_loc([rd_get_avg("TOTAL_AVG_LOC_COORD_X", rdnum, self.agents, sd="R"), rd_get_avg("TOTAL_AVG_LOC_COORD_Y", rdnum, self.agents, sd="R")], self.map_obj)
      self.round_info[rdnum]["LEFT_AVG_MOMENTUM"] = \
        in_loc([rd_get_avg("TOTAL_AVG_MOMENTUM_COORD_X", rdnum, self.agents, sd="L"), rd_get_avg("TOTAL_AVG_MOMENTUM_COORD_Y", rdnum, self.agents, sd="L")], self.map_obj)
      self.round_info[rdnum]["RIGHT_AVG_MOMENTUM"] = \
        in_loc([rd_get_avg("TOTAL_AVG_MOMENTUM_COORD_X", rdnum, self.agents, sd="R"), rd_get_avg("TOTAL_AVG_MOMENTUM_COORD_Y", rdnum, self.agents, sd="R")], self.map_obj)
      self.round_info[rdnum]["LEFT_AVG_TIME_ALIVE_RATIO"] = rd_get_avg("%_TIME_ALIVE", rdnum, self.agents, sd="L")
      self.round_info[rdnum]["RIGHT_AVG_TIME_ALIVE_RATIO"] = rd_get_avg("%_TIME_ALIVE", rdnum, self.agents, sd="R")
      self.round_info[rdnum]["LEFT_AVG_TIME_DEAD_RATIO"] = rd_get_avg("%_TIME_DEAD", rdnum, self.agents, sd="L")
      self.round_info[rdnum]["RIGHT_AVG_TIME_DEAD_RATIO"] = rd_get_avg("%_TIME_DEAD", rdnum, self.agents, sd="R")
      self.round_info[rdnum]["LEFT_AVG_TIME_MOVING_RATIO"] = rd_get_avg("%_TIME_MOVING", rdnum, self.agents, sd="L")
      self.round_info[rdnum]["RIGHT_AVG_TIME_MOVING_RATIO"] = rd_get_avg("%_TIME_MOVING", rdnum, self.agents, sd="R")
      self.round_info[rdnum]["LEFT_AVG_TIME_STATIONARY_RATIO"] = rd_get_avg("%_TIME_STATIONARY", rdnum, self.agents, sd="L")
      self.round_info[rdnum]["RIGHT_AVG_TIME_STATIONARY_RATIO"] = rd_get_avg("%_TIME_STATIONARY", rdnum, self.agents, sd="R")
      self.round_info[rdnum]["LEFT_K/D"] = self.round_info[rdnum]["LEFT_KILL_COUNT"] / (max(self.round_info[rdnum]["LEFT_DEATH_COUNT"], 1))
      self.round_info[rdnum]["RIGHT_K/D"] = self.round_info[rdnum]["RIGHT_KILL_COUNT"] / (max(self.round_info[rdnum]["RIGHT_DEATH_COUNT"], 1))
      self.round_info[rdnum]["LEFT_S/I"] = self.round_info[rdnum]["LEFT_SURVIVE_COUNT"] / (max(self.round_info[rdnum]["LEFT_IDLE_COUNT"], 1))
      self.round_info[rdnum]["RIGHT_S/I"] = self.round_info[rdnum]["RIGHT_SURVIVE_COUNT"] / (max(self.round_info[rdnum]["RIGHT_IDLE_COUNT"], 1))
      self.round_info[rdnum]["LEFT_PROGRESSION_COUNT"] = rd_get_sum("PROGRESSION_COUNT", rdnum, self.agents, sd="L")
      self.round_info[rdnum]["RIGHT_PROGRESSION_COUNT"] = rd_get_sum("PROGRESSION_COUNT", rdnum, self.agents, sd="R")
      self.round_info[rdnum]["LEFT_HOLD_COUNT"] = rd_get_sum("HOLD_COUNT", rdnum, self.agents, sd="L")
      self.round_info[rdnum]["RIGHT_HOLD_COUNT"] = rd_get_sum("HOLD_COUNT", rdnum, self.agents, sd="R")
      self.round_info[rdnum]["LEFT_EXECUTION_COUNT"] = rd_get_sum("EXECUTION_COUNT", rdnum, self.agents, sd="L")
      self.round_info[rdnum]["RIGHT_EXECUTION_COUNT"] = rd_get_sum("EXECUTION_COUNT", rdnum, self.agents, sd="R")
      self.round_info[rdnum]["LEFT_SWITCH_COUNT"] = rd_get_sum("SWITCH_COUNT", rdnum, self.agents, sd="L")
      self.round_info[rdnum]["RIGHT_SWITCH_COUNT"] = rd_get_sum("SWITCH_COUNT", rdnum, self.agents, sd="R")
      self.round_info[rdnum]["LEFT_ROTATION_COUNT"] = rd_get_sum("ROTATION_COUNT", rdnum, self.agents, sd="L")
      self.round_info[rdnum]["RIGHT_ROTATION_COUNT"] = rd_get_sum("ROTATION_COUNT", rdnum, self.agents, sd="R")
      self.round_info[rdnum]["LEFT_PINCER_COUNT"] = rd_get_sum("PINCER_COUNT", rdnum, self.agents, sd="L")
      self.round_info[rdnum]["RIGHT_PINCER_COUNT"] = rd_get_sum("PINCER_COUNT", rdnum, self.agents, sd="R")
      self.round_info[rdnum]["LEFT_FLANK_COUNT"] = rd_get_sum("FLANK_COUNT", rdnum, self.agents, sd="L")
      self.round_info[rdnum]["RIGHT_FLANK_COUNT"] = rd_get_sum("FLANK_COUNT", rdnum, self.agents, sd="R")
      self.round_info[rdnum]["LEFT_COVER_COUNT"] = rd_get_sum("COVER_COUNT", rdnum, self.agents, sd="L")
      self.round_info[rdnum]["RIGHT_COVER_COUNT"] = rd_get_sum("COVER_COUNT", rdnum, self.agents, sd="R")
      lwp, rwp = (defaultdict(list), defaultdict(list))
      tmplwp, tmprwp = (-1, -1)
      tmplname, tmprname = (None, None)
      for kkwp, jjwp in wpsrd[rdnum].items():
        if kkwp[0] == "L":  lwp[jjwp].append(jjwp)
        if kkwp[0] == "R":  rwp[jjwp].append(jjwp)
      for wpname in ["PISTOL", "ECO", "RIFLE"]:
        if len(lwp[wpname]) >= tmplwp:  tmplwp = len(lwp[wpname]); tmplname = wpname
        if len(rwp[wpname]) >= tmprwp:  tmprwp = len(rwp[wpname]); tmprname = wpname
      self.round_info[rdnum]["LEFT_ECON"] = tmplname
      self.round_info[rdnum]["RIGHT_ECON"] = tmprname
      self.round_info[rdnum]["LEFT_DAMAGE_TAKEN"] = rd_get_sum("TOTAL_DAMAGE_TAKEN", rdnum, self.agents, sd="L")
      self.round_info[rdnum]["RIGHT_DAMAGE_TAKEN"] = rd_get_sum("TOTAL_DAMAGE_TAKEN", rdnum, self.agents, sd="R")
      self.round_info[rdnum]["LEFT_HEALTH_REGAINED"] = rd_get_sum("TOTAL_HEALTH_REGAINED", rdnum, self.agents, sd="L")
      self.round_info[rdnum]["RIGHT_HEALTH_REGAINED"] = rd_get_sum("TOTAL_HEALTH_REGAINED", rdnum, self.agents, sd="R")
      if self.round_info[rdnum]["ATK_SIDE"] == self.round_results[rdnum][0]:  self.round_info[rdnum]["ATK_WIN"] = True
      else:  self.round_info[rdnum]["DEF_WIN"] = True
      self.round_info[rdnum]["LEFT_PLAYER_DIFFERENCE"] = self.round_info[rdnum]["LEFT_KILL_COUNT"] - self.round_info[rdnum]["RIGHT_KILL_COUNT"]
      self.round_info[rdnum]["LEFT_TRAVEL_DIFFERENCE"] = (self.round_info[rdnum]["LEFT_AVG_DISTANCE"] - self.round_info[rdnum]["RIGHT_AVG_DISTANCE"]) * 5
      self.round_info[rdnum]["LEFT_VELOCITY_DIFFERENCE"] = (self.round_info[rdnum]["LEFT_AVG_VELOCITY"] - self.round_info[rdnum]["RIGHT_AVG_VELOCITY"]) * 5
      self.round_info[rdnum]["LEFT_UTIL1_DIFFERENCE"] = self.round_info[rdnum]["LEFT_UTIL1_COUNT"] - self.round_info[rdnum]["RIGHT_UTIL1_COUNT"]
      self.round_info[rdnum]["LEFT_UTIL2_DIFFERENCE"] = self.round_info[rdnum]["LEFT_UTIL2_COUNT"] - self.round_info[rdnum]["RIGHT_UTIL2_COUNT"]
      self.round_info[rdnum]["LEFT_ABIL_DIFFERENCE"] = self.round_info[rdnum]["LEFT_ABIL_COUNT"] - self.round_info[rdnum]["RIGHT_ABIL_COUNT"]
      self.round_info[rdnum]["LEFT_ULT_DIFFERENCE"] = self.round_info[rdnum]["LEFT_ULT_COUNT"] - self.round_info[rdnum]["RIGHT_ULT_COUNT"]
      self.round_info[rdnum]["RIGHT_PLAYER_DIFFERENCE"] = self.round_info[rdnum]["RIGHT_KILL_COUNT"] - self.round_info[rdnum]["LEFT_KILL_COUNT"]
      self.round_info[rdnum]["RIGHT_TRAVEL_DIFFERENCE"] = (self.round_info[rdnum]["RIGHT_AVG_DISTANCE"] - self.round_info[rdnum]["LEFT_AVG_DISTANCE"]) * 5
      self.round_info[rdnum]["RIGHT_VELOCITY_DIFFERENCE"] = (self.round_info[rdnum]["RIGHT_AVG_VELOCITY"] - self.round_info[rdnum]["LEFT_AVG_VELOCITY"]) * 5
      self.round_info[rdnum]["RIGHT_UTIL1_DIFFERENCE"] = self.round_info[rdnum]["RIGHT_UTIL1_COUNT"] - self.round_info[rdnum]["LEFT_UTIL1_COUNT"]
      self.round_info[rdnum]["RIGHT_UTIL2_DIFFERENCE"] = self.round_info[rdnum]["RIGHT_UTIL2_COUNT"] - self.round_info[rdnum]["LEFT_UTIL2_COUNT"]
      self.round_info[rdnum]["RIGHT_ABIL_DIFFERENCE"] = self.round_info[rdnum]["RIGHT_ABIL_COUNT"] - self.round_info[rdnum]["LEFT_ABIL_COUNT"]
      self.round_info[rdnum]["RIGHT_ULT_DIFFERENCE"] = self.round_info[rdnum]["RIGHT_ULT_COUNT"] - self.round_info[rdnum]["LEFT_ULT_COUNT"]
      self.round_info[rdnum]["LEFT_TOTAL_UTIL_DIFFERENCE"] = (self.round_info[rdnum]["LEFT_UTIL1_COUNT"] - self.round_info[rdnum]["RIGHT_UTIL1_COUNT"]) + (self.round_info[rdnum]["LEFT_UTIL2_COUNT"] - self.round_info[rdnum]["RIGHT_UTIL2_COUNT"]) + (self.round_info[rdnum]["LEFT_ABIL_COUNT"] - self.round_info[rdnum]["RIGHT_ABIL_COUNT"]) + (self.round_info[rdnum]["LEFT_ULT_COUNT"] - self.round_info[rdnum]["RIGHT_ULT_COUNT"])
      self.round_info[rdnum]["RIGHT_TOTAL_UTIL_DIFFERENCE"] = (self.round_info[rdnum]["RIGHT_UTIL1_COUNT"] - self.round_info[rdnum]["LEFT_UTIL1_COUNT"]) + (self.round_info[rdnum]["RIGHT_UTIL2_COUNT"] - self.round_info[rdnum]["LEFT_UTIL2_COUNT"]) + (self.round_info[rdnum]["RIGHT_ABIL_COUNT"] - self.round_info[rdnum]["LEFT_ABIL_COUNT"]) + (self.round_info[rdnum]["RIGHT_ULT_COUNT"] - self.round_info[rdnum]["LEFT_ULT_COUNT"])
      if self.round_results[rdnum][1] > 9:  self.round_info[rdnum]["LEFT_ALMOST_DECISIVE"] = True
      if self.round_results[rdnum][2] > 9:  self.round_info[rdnum]["RIGHT_ALMOST_DECISIVE"] = True
      if self.round_results[rdnum][1] > 11 or (self.round_results[rdnum][1] > 13 and self.round_results[rdnum][1] - self.round_results[rdnum][2] == 1):  self.round_info[rdnum]["LEFT_DECISIVE"] = True
      if self.round_results[rdnum][2] > 11 or (self.round_results[rdnum][2] > 13 and self.round_results[rdnum][2] - self.round_results[rdnum][1] == 1):  self.round_info[rdnum]["RIGHT_DECISIVE"] = True
      if self.round_results[rdnum][1] > self.round_results[rdnum][2]:  self.round_info[rdnum]["WINNING"] = "L"
      if self.round_results[rdnum][1] < self.round_results[rdnum][2]:  self.round_info[rdnum]["WINNING"] = "R"
      if self.round_results[rdnum][1] == self.round_results[rdnum][2]:  self.round_info[rdnum]["WINNING"] = "N"
      self.round_info[rdnum]["WINNER"] = self.round_results[rdnum][0]
      self.round_info[rdnum]["LEFT_ROUND_DIFFERENCE"] = self.round_results[rdnum][1] - self.round_results[rdnum][2]
      self.round_info[rdnum]["RIGHT_ROUND_DIFFERENCE"] = self.round_results[rdnum][2] - self.round_results[rdnum][1]
      lalv, ralv, ptd, asd, wnr = (self.round_info[rdnum]["LEFT_SURVIVE_COUNT"], self.round_info[rdnum]["RIGHT_SURVIVE_COUNT"], self.round_info[rdnum]["PLANTED"], self.round_info[rdnum]["ATK_SIDE"], self.round_results[rdnum][0])
      if wnr == asd:
        self.round_info[rdnum]["ATK_WIN"] = True
        if wnr == "L" and ralv == 0 and ptd < 0:  self.round_info[rdnum]["RESULT"] = "ATK_ELIM"
        if wnr == "L" and ralv == 0 and ptd > 0:  self.round_info[rdnum]["RESULT"] = "ATK_PLANT_ELIM"
        if wnr == "L" and ralv > 0 and ptd > 0:  self.round_info[rdnum]["RESULT"] = "ATK_DET"
        if wnr == "R" and lalv == 0 and ptd < 0:  self.round_info[rdnum]["RESULT"] = "ATK_ELIM"
        if wnr == "R" and lalv == 0 and ptd > 0:  self.round_info[rdnum]["RESULT"] = "ATK_PLANT_ELIM"
        if wnr == "R" and lalv > 0 and ptd > 0:  self.round_info[rdnum]["RESULT"] = "ATK_DET"
      if wnr == flip_side(asd):
        self.round_info[rdnum]["DEF_WIN"] = True
        if wnr == "L" and ralv == 0 and ptd < 0:  self.round_info[rdnum]["RESULT"] = "DEF_ELIM"
        if wnr == "L" and ralv == 0 and ptd > 0:  self.round_info[rdnum]["RESULT"] = "DEF_PLANT_ELIM"
        if wnr == "L" and ralv > 0 and ptd > 0:  self.round_info[rdnum]["RESULT"] = "DEF_DEFUSE"; self.round_info[rdnum]["DEFUSED"] = self.round_info[rdnum]["KEYPOINTS"]["END"]
        if wnr == "R" and lalv == 0 and ptd < 0:  self.round_info[rdnum]["RESULT"] = "DEF_ELIM"
        if wnr == "R" and lalv == 0 and ptd > 0:  self.round_info[rdnum]["RESULT"] = "DEF_PLANT_ELIM"
        if wnr == "R" and lalv > 0 and ptd > 0:  self.round_info[rdnum]["RESULT"] = "DEF_DEFUSE"; self.round_info[rdnum]["DEFUSED"] = self.round_info[rdnum]["KEYPOINTS"]["END"]
      self.round_info[rdnum]["PREVIOUS_RESULT"] = self.round_info[rdnum-1]["RESULT"] if rdnum > 1 else "NONE"

    tmp = list(self.round_info.values())[-1]
    self.results = {
      "WINNER": tmp["WINNER"], "LOSER": flip_side(tmp["WINNER"]), "LEFT_SCORE": 0, "RIGHT_SCORE": 0, 
      "LEFT_ATK_WIN_COUNT": 0, "RIGHT_ATK_WIN_COUNT": 0, "LEFT_DEF_WIN_COUNT": 0, "RIGHT_DEF_WIN_COUNT": 0, 
      "LEFT_ELIM_WIN_COUNT": 0, "RIGHT_ELIM_WIN_COUNT": 0, 
      "LEFT_PLANT_WIN_RATE": 0, "RIGHT_PLANT_WIN_RATE": 0, "LEFT_DEFUSE_WIN_RATE": 0, "RIGHT_DEFUSE_WIN_RATE": 0, 
      "LEFT_K/D": 0, "RIGHT_K/D": 0, "LEFT_S/I": 0, "RIGHT_S/I": 0, 
      "LEFT_KILL_COUNT": 0, "RIGHT_KILL_COUNT": 0, "LEFT_DEATH_COUNT": 0, "RIGHT_DEATH_COUNT": 0, 
      "LEFT_SURVIVE_COUNT": 0, "RIGHT_SURVIVE_COUNT": 0, "LEFT_IDLE_COUNT": 0, "RIGHT_IDLE_COUNT": 0, 
      "LEFT_ASSIST_COUNT": 0, "RIGHT_ASSIST_COUNT": 0, "LEFT_REVIVE_COUNT": 0, "RIGHT_REVIVE_COUNT": 0, 
      "LEFT_TRADE_COUNT": 0, "RIGHT_TRADE_COUNT": 0, "LEFT_PLANT_COUNT": 0, "RIGHT_PLANT_COUNT": 0, 
      "LEFT_DEFUSE_COUNT": 0, "RIGHT_DEFUSE_COUNT": 0, "LEFT_UTIL1_COUNT": 0, "RIGHT_UTIL1_COUNT": 0, 
      "LEFT_UTIL2_COUNT": 0, "RIGHT_UTIL2_COUNT": 0, "LEFT_ABIL_COUNT": 0, "RIGHT_ABIL_COUNT": 0, 
      "LEFT_ULT_COUNT": 0, "RIGHT_ULT_COUNT": 0, "LEFT_DISTANCE_TRAVELED": 0, "RIGHT_DISTANCE_TRAVELED": 0, 
      "LEFT_VELOCITY": 0, "RIGHT_VELOCITY": 0, "LEFT_%A": 0, "RIGHT_%A": 0, "LEFT_%B": 0, "RIGHT_%B": 0, 
      "LEFT_PROGRESSION_RATE": 0, "RIGHT_PROGRESSION_RATE": 0, "LEFT_HOLD_RATE": 0, "RIGHT_HOLD_RATE": 0, 
      "LEFT_EXECUTION_RATE": 0, "RIGHT_EXECUTION_RATE": 0, "LEFT_SWITCH_RATE": 0, "RIGHT_SWITCH_RATE": 0, 
      "LEFT_ROTATION_RATE": 0, "RIGHT_ROTATION_RATE": 0, "LEFT_PINCER_RATE": 0, "RIGHT_PINCER_RATE": 0, 
      "LEFT_FLANK_RATE": 0, "RIGHT_FLANK_RATE": 0, "LEFT_COVER_RATE": 0, "RIGHT_COVER_RATE": 0, 
      "LEFT_SUBSTITUTIONS": 0, "RIGHT_SUBSTITUTIONS": 0, 
      }
    if self.mapname == "HAVEN":  self.results["LEFT_%C"] = 0; self.results["RIGHT_%C"] = 0
    else:  self.results["LEFT_%M"] = 0; self.results["RIGHT_%M"] = 0

    self.results = {   }
    self.agents = { ovkey: self.agents[ovkey] for ovkey in sorted(list(self.agents.keys())) }
    self.round_info = { rdkey: self.round_info[rdkey] for rdkey in sorted(list(self.round_info.keys())) }

    t3 = time.perf_counter()
    print(f"\n\nanalytics runtime is {t3 - t2:0.5f} seconds\n\n")
    print(f"\n\ntotal runtime is {t3 - t1:0.5f} seconds\n\n")

    if self.log:
      print(self.round_score_left, self.round_score_right)
      print()
      print(self.game_score_left, self.game_score_right)
      print()
      print(self.results)
      print()
      for i, j in self.round_info.items():
        print("\n\nROUND # " + str(i) + " :::\n\n")
        for kk, kj in j.items():
          print(kk + " :: " + str(kj))
        print()
        print()
      # print(str(self.agents))
      self.f.write("\n\n\n\n\n")
      self.f.write(str(self.filename) + "\n")
      self.f.write(str(self.mapname) + "\n")
      self.f.write(str(self.public) + "\n")
      self.f.write(str(self.teamleft) + "\n")
      self.f.write(str(self.teamright) + "\n")
      self.f.write("\n\n\n\n\n")
      self.f.write(str(self.agent_names) + "\n")
      self.f.write("\n\n\n\n\n")
      self.f.write(f"{self.round_score_left} - {self.round_score_right}")
      self.f.write("\n\n\n\n\n")
      self.f.write(f"{self.game_score_left} --- {self.game_score_right}")
      self.f.write("\n\n\n\n\n")
      self.f.write(str(self.ac) + "\n")
      self.f.write("\n\n\n\n\n")
      self.f.write("\n\n\n\n\n")
      self.f.write("\n\n\n\n\n")
      for key in self.agents.keys():  self.f.write(str(key) + "\n\n"); self.f.write(str(self.agents[key]) + "\n\n\n")
      self.f.write("\n\n\n\n\n")
      self.f.write("\n\n\n\n\n")
      self.f.write("\n\n\n\n\n")
      self.f.write(str(self.round_info) + "\n")
      self.f.write("\n\n\n\n\n")
      self.f.write("\n\n\n\n\n")
      self.f.close()

    return { 
      "PUBLIC_VOD": self.public, "MAP": self.mapname, "TEAM_LEFT": self.teamleft, "TEAM_RIGHT": self.teamright, 
      "ROUND_INFO": self.round_info, "PLAYER_INFO": self.agents, "GAME_RESULTS": self.results, 
      }
