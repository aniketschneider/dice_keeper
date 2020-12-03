import re
import sys
import os
import logging
import json
from collections import defaultdict

import gspread
from google.oauth2.service_account import Credentials
from discord.ext import commands
from Levenshtein import distance
from data_store import DataStore

from dice_roller import DiceRoller

logging.basicConfig()
LOG = logging.getLogger(__name__)
LOG.setLevel(logging.INFO)


class Macros():
  def __init__(self, sheet_key):
    self.sheet_key = sheet_key
    self.roller = DiceRoller()
    creds_json = os.getenv("GCP_SERVICE_ACCOUNT_CREDS")
    self.creds_dict = json.loads(creds_json)
    self.parse_macros()

  def parse_macros(self):
    creds = Credentials.from_service_account_info(info=self.creds_dict, scopes=gspread.auth.READONLY_SCOPES)
    gc = gspread.client.Client(auth=creds)

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

  def _canonical_move(self, user_move):
    def distance_to(a):
      return lambda b: distance(a,b)

    return min(self.move_names, key=distance_to(user_move.lower()))


  def handle_move(self, user, orig_move_name):
    move_name = self._canonical_move(orig_move_name)
    if move_name != orig_move_name:
      LOG.info(f'Interpreted move {orig_move_name} as {move_name}')
    mod = self.move_mods[user][move_name]
    result = self.roller.roll_move(mod)
    if mod >= 0:
      mod_clause = f'+ {self.move_mods[user][move_name]}'
    else:
      mod_clause = f'- {-self.move_mods[user][move_name]}'

    return f'{self.user_characters[user]} rolled 2d6 {mod_clause} for {move_name} and got {result}'

  def moves(self, user):
    moves = '\n'.join(sorted(self.move_mods[user].keys()))
    return f"{self.user_characters[user]} has the following moves available:\n{moves}"


if __name__ == '__main__':
  from dotenv import load_dotenv
  load_dotenv()

  token = os.getenv('DISCORD_TOKEN')
  sheet_key = os.getenv('SHEET_KEY')

  bot = commands.Bot(command_prefix='/')

  roller = DiceRoller()

  @bot.command()
  async def moves(ctx, *args):
    unique_user = f'{ctx.author.name}#{ctx.author.discriminator}'
    macros = Macros(sheet_key)
    message = macros.moves(unique_user)
    LOG.info(message)
    await ctx.send(message)

  @bot.command(name='roll', aliases=['r'])
  async def _roll(ctx, *args):
    macros = Macros(sheet_key)
    LOG.debug(macros.user_characters)
    LOG.debug(macros.move_mods)
    LOG.debug(macros.move_names)

    unique_user = f'{ctx.author.name}#{ctx.author.discriminator}'
    LOG.info(f'Processing < /roll {" ".join(args)} > from {unique_user}')

    if any(re.match('\d*d\d+', arg) for arg in args):
      dstr = ''.join(args)
      result = roller.roll_string(dstr)
      message = f'You rolled {dstr} and got {result}'
    else:
      message = macros.handle_move(unique_user, args[0])

    LOG.info(message)
    await ctx.send(message)

  @bot.command()
  async def setsheet(ctx, *args):
    sheet_id = args[0]
    guild_id = ctx.guild.id
    channel_id = ctx.channel.id

    ds = DataStore()
    ds.set_sheet_for_channel(guild_id, channel_id, sheet_id)
    message = f"Google Sheet ID set."
    await ctx.send(message)

  @bot.command()
  async def getsheet(ctx, *args):
    guild_id = ctx.guild.id
    channel_id = ctx.channel.id

    ds = DataStore()
    sheet_id = ds.get_sheet_for_channel(guild_id, channel_id)

    message = f"Sheet ID is {sheet_id}"
    await ctx.send(message)

  @bot.event
  async def on_ready():
    LOG.info('Bot is ready!')

  bot.run(token)
