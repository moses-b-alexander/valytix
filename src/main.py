


import json
import os
import time

from game.game import *
from game.getdata import *
from game.map import *
from game.minimap import *
from game.sheet import *
from game.maps.maptest import *
from game.search import *
from game.test import *


datadir = os.path.dirname(os.getcwd()) + "/data/"


def main():


  game1 = (Game(datadir + "placeholder_mp4.txt", "ICEBOX", public=True, log=True, dbg=False)).run()

  print(game1)


  return None


if __name__ == "__main__":  main()


