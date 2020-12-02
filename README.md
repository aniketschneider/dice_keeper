dice_keeper
-----------

This is a Discord dice rolling bot. It's designed to work with tabletop RPG character sheets stored in Google Sheets, known as "character keepers." The idea is that you have your character sheets with various numerical stats in one worksheet, and then you have a separate worksheet called "Macros" with formulas that compute the modifiers for common, character-specific rolls. Currently the Google Sheets connector is specialized for Apocalypse World style moves, in that it assumes that they are all of the form 2d6 + modifier.

Setup
=====

To run this bot you will need the following:

* A discord account
* A Google Cloud account
* Python 3

In broad strokes:

1. Create a discord app, then add a bot to it. Get the client ID and enter it here: https://discordapi.com/permissions.html#3072 to generate a link, then use that link to add the bot to a server.
2. Create a Google Cloud project. Add a service account to it. Add the Google Drive and Google Sheets APIs to the project.
3. Share your character keeper spreadsheet with the service account's email address.
4. Create a .env file, or set environment variables, as described in the .env.sample file.
5. Add a "Macros" worksheet to the google sheet. It should look like this:

| Character | <Character 1 Name> | <Character 2 Name> |
|-|-|-|
| Discord ID | <Character 1 Player> | <Character 2 Player> |
| <Move 1 Name> | <Char 1 Move 1 Mod> | <Char 2 Move 1 Mod> |
| <Move 2 Name> | <Char 1 Move 2 Mod> | <Char 2 Move 2 Mod> |

Then just run `python3 dice_keeper.py`. The bot should respond to commands like these:

* `/roll 2d6` (generic dice roller)
* `/moves` (moves from Macros worksheet based on the discord user running the command)
* `/roll <move_name>`
