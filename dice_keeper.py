import sys
from collections import defaultdict
import os
import random
import logging

import gspread
from discord.ext import commands
from dotenv import load_dotenv

logging.basicConfig()
LOG = logging.getLogger(__name__)
LOG.setLevel(logging.INFO)

def roll_d(size):
  return random.randint(1,int(size))

def roll(raw_dice_string):
  LOG.debug(raw_dice_string)
  dice_string = "".join(raw_dice_string.split())
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
        result += roll_d(die_size)
  LOG.info(f'Rolled {dice_string} and got {result}')
  return result

def roll_move(mod):
  return roll(f'2d6 + {mod}')


class Macros():
  def __init__(self, sheet_key):
    self.sheet_key = sheet_key
    self.parse_macros()

  def parse_macros(self):
    gc = gspread.service_account()
    spreadsheet = gc.open_by_key(self.sheet_key)
    worksheet = spreadsheet.worksheet("Macros")

    values = worksheet.get_all_values()
    characters = values[0][1:]
    discord_names = values[1][1:]
    self.user_characters = dict(zip(discord_names, characters))

    self.move_names = [row[0] for row in values[2:]]

    self.move_mods = defaultdict(dict)
    for row in values[2:]:
      move_name = row[0]
      for discord_name, modifier in zip(discord_names, row[1:]):
        try:
          self.move_mods[discord_name][move_name] = int(modifier)
        except:
          pass

  def handle_move(self, user, move_name):
    mod = self.move_mods[user][move_name]
    result = roll_move(mod)
    return f'{self.user_characters[user]} rolled 2d6 + {self.move_mods[user][move_name]} for {move_name} and got {result}'


if __name__ == '__main__':
  load_dotenv()

  random.seed()
  token = os.getenv('DISCORD_TOKEN')
  sheet_key = os.getenv('SHEET_KEY')

  bot = commands.Bot(command_prefix='/')

  @bot.command(name='roll')
  async def _roll(ctx, *args):
    macros = Macros(sheet_key)
    LOG.debug(macros.user_characters)
    LOG.debug(macros.move_mods)
    LOG.debug(macros.move_names)

    unique_user = f'{ctx.author.name}#{ctx.author.discriminator}'
    LOG.info(f'Processing < /roll {" ".join(args)} > from {unique_user}')

    if args[0] in macros.move_names:
      message = macros.handle_move(unique_user, args[0])
    else:
      dstr = ''.join(args)
      result = roll(dstr)
      message = f'You rolled {dstr} and got {result}'

    LOG.info(message)
    await ctx.send(message)

  @bot.event
  async def on_ready():
    LOG.info('Bot is ready!')

  bot.run(token)
