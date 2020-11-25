import random
import logging

logging.basicConfig()
LOG = logging.getLogger(__name__)
LOG.setLevel(logging.INFO)

class DiceRoller():
  def __init__(self):
    random.seed()

  def roll_d(self, size):
    return random.randint(1,int(size))

  def roll_string(self, raw_string):
    LOG.debug(raw_string)
    dice_string = "".join(raw_string.split())
    terms = dice_string.split('+')
    result = 0
    for term in terms:
      factors = term.split('d')
      LOG.debug(factors)
      if len(factors) == 1:
        result += int(factors[0])
      elif len(factors) == 2:
        multiplier, die_size = factors
        if len(multiplier) == 0:
          multiplier = 1
        for _ in range(int(multiplier)):
          result += self.roll_d(die_size)
    LOG.info(f'Rolled {dice_string} and got {result}')
    return result

  def roll_move(self, mod):
    return self.roll_string(f'2d6 + {mod}')

if __name__ == '__main__':
  roller = DiceRoller()

  print(roller.roll_string("2d6 + 100"))
