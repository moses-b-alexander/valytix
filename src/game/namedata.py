
overlay = [ "LEFT_1", "LEFT_2", "LEFT_3", "LEFT_4", "LEFT_5", "RIGHT_1", "RIGHT_2", "RIGHT_3", "RIGHT_4", "RIGHT_5" ]

agent_list = [
  "ASTRA", "BREACH", "BRIMSTONE", "CHAMBER", "CYPHER", "JETT", "KAYO", "KILLJOY", "OMEN", 
  "PHOENIX", "RAZE", "REYNA", "SAGE", "SKYE", "SOVA", "VIPER", "YORU", 
  ]

roles = {
  "DUELIST": [ "JETT", "PHOENIX", "RAZE", "REYNA", "YORU", ], 
  "CONTROLLER": [ "ASTRA", "BRIMSTONE", "OMEN", "VIPER", ], 
  "INITIATOR": [ "BREACH", "KAYO", "SKYE", "SOVA", ], 
  "SENTINEL": [ "CHAMBER", "CYPHER", "KILLJOY", "SAGE", ], 
}

pistol_list = [ "CLASSIC", "FRENZY", "GHOST", "SHERIFF", "SHORTY" ]
eco_list = [ "BUCKY", "MARSHAL", "STINGER", "SPECTRE", "BULLDOG", "JUDGE", "GUARDIAN", "ARES" ]
rifle_list = [ "VANDAL", "PHANTOM", "ODIN", "OPERATOR" ]
weapon_list = pistol_list + eco_list + rifle_list

abil_list = [
  "AFTERSHOCK", "BLADE_STORM", "BLAST_PACK", "BLAZE", 
  "BOOM_BOT", "FRAGMENT", "HOT_HANDS", "HUNTERS_FURY", "INCENDIARY", 
  "NANOSWARM", "NULLCMD", "NULLCMD_RES", "ORBITAL_STRIKE", 
  "PAINT_SHELLS", "RESURRECTION", "RUN_IT_BACK", "SHOCK_BOLT", 
  "SHOWSTOPPER", "SNAKE_BITE", "TRAILBLAZER", "TRAPWIRE", 
  "TURRET", 
]

misc_list = [ "SPIKE_DET", ] #NULLCMD?

feed_list = weapon_list + abil_list + misc_list

MAP_CODES = {
  1: "ASCENT", 
  2: "SPLIT", 
  3: "HAVEN", 
  4: "BIND", 
  5: "ICEBOX", 
  6: "BREEZE", 
  7: "FRACTURE", 

}

map_list = list(MAP_CODES.values())

ZONE_CODES = {
  "A": "1", 
  "B": "2", 
  "C": "3", 
  "D": "4", 
  "M": "5", 
  "DEF": "6", 
  "ATK": "7", 
}
