# action class

class Action:
  # what is an action
  def __init__(self, typ, src, dst):
    self.typ = typ
    self.src = src
    self.dst = dst

  def exe(self):
    pass