class Counter:
  def __init__(self, zibrato):
    self.zibrato = zibrato

  def __call__(self, name, increment):
    return self.zibrato.send('testing|counter')
