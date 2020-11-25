import random
import logging
import re

logging.basicConfig()
LOG = logging.getLogger(__name__)
LOG.setLevel(logging.INFO)

TOKEN_PATTERN = '\d*d\d+|\d+|[+-]'
TOKEN_RE = re.compile(TOKEN_PATTERN)

class DiceRoller():
  def __init__(self):
    random.seed()

  def _roll_d(self, size):
    return random.randint(1,int(size))

  def _d_exp_value(self, d_exp):
    factors = d_exp.split('d')

    if len(factors) == 1:
      # no 'd' means a constant value
      exp_value = int(factors[0])
    elif len(factors) == 2:
      ndice, size = factors
      if ndice == '':
        # 'dN' without a preceding numeric factor means 1 die
        ndice = 1
      exp_value = sum(self._roll_d(size) for _ in range(int(ndice)))
    else:
      # only 1 'd' is allowed
      raise Exception(f'Malformed dice expression "{d_exp}"')

    return exp_value


  def roll_string(self, raw_string):
    LOG.debug(f"Processing {raw_string}")

    result = 0
    # whether we should negate the next value
    sign = 1
    for token in TOKEN_RE.findall(raw_string):
      if token == '-':
        sign = -sign
      elif token == '+':
        pass
      else:
        term_value = self._d_exp_value(token)
        result += sign * term_value
        LOG.debug(f'{token}: {sign * term_value}')
        sign = 1

    return result

  def roll_move(self, mod):
    return self.roll_string(f'2d6 + {mod}')

if __name__ == '__main__':
  roller = DiceRoller()

  print(roller.roll_string("2d6 + 100"))
  print(roller.roll_string("2d6 - 7 + d8"))
