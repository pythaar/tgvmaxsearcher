import os
import sys
import json
import discord
from discord.ext import commands
GIT_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(GIT_PATH)
from config import DISCORD_TOKEN, DISCORD_USER_ID
from src.functions import getDbStatus, getTrains
from src.file_manipulation import openJson
from datetime import datetime, timedelta, date


intents = discord.Intents.default()
intents.messages = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    
    #Open database
    db_path = os.path.join(GIT_PATH, 'database')
    tgvmax_to_find_path = os.path.join(db_path, 'trainsToFind.json')
    tgvmax_database = openJson(tgvmax_to_find_path)
    
    if tgvmax_database:
        user = await bot.fetch_user(DISCORD_USER_ID)
        dbStatus = getDbStatus()
        today = datetime.today().strftime('%d/%m/%Y')
        await user.send(f"------- Recherche TGV MAX du {today} -------")
        if dbStatus == True:
            await user.send(":white_check_mark: La database est à jour")
        elif dbStatus == False:
            await user.send(":x: La database n'est pas à jour")
        else:
            await user.send("Erreur lors du check de la database")
    
        for train in tgvmax_database:
            await user.send(f"-> De {train["Origine"]} à {train["Destination"]}, le {train["Date"]}:")
            available_train, message = getTrains(train)
            if available_train:
                for av_train in available_train:
                    if av_train["od_happy_card"] == "OUI":
                        emoji = ":white_check_mark:"
                    else:
                        emoji = ":x:"
                    await user.send(f"{av_train["heure_depart"]} -> {av_train["heure_arrivee"]}: {av_train["od_happy_card"]} {emoji}")
            else:
                await user.send(message)
    await bot.close()
    
bot.run(DISCORD_TOKEN)