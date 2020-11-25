import sys
from collections import defaultdict
import os
import logging

import gspread
from discord.ext import commands
from dotenv import load_dotenv

from dice_roller import DiceRoller

logging.basicConfig()
LOG = logging.getLogger(__name__)
LOG.setLevel(logging.INFO)


class Macros():
  def __init__(self, sheet_key):
    self.sheet_key = sheet_key
    self.roller = DiceRoller()
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
    result = self.roller.roll_move(mod)
    if mod >= 0:
      mod_clause = f'+ {self.move_mods[user][move_name]}'
    else:
      mod_clause = f'- {-self.move_mods[user][move_name]}'

    return f'{self.user_characters[user]} rolled 2d6 {mod_clause} for {move_name} and got {result}'


if __name__ == '__main__':
  load_dotenv()

  token = os.getenv('DISCORD_TOKEN')
  sheet_key = os.getenv('SHEET_KEY')

  bot = commands.Bot(command_prefix='/')

  roller = DiceRoller()

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
      result = roller.roll_string(dstr)
      message = f'You rolled {dstr} and got {result}'

    LOG.info(message)
    await ctx.send(message)

  @bot.event
  async def on_ready():
    LOG.info('Bot is ready!')

  bot.run(token)
