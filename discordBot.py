import os
import json
import discord
from discord.ext import commands
from IDs import TOKEN, USER_ID
from functions import getDbStatus, getTrains
from datetime import datetime, timedelta, date


intents = discord.Intents.default()
intents.messages = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    user = await bot.fetch_user(USER_ID)
    dbStatus = getDbStatus()
    today = datetime.today().strftime('%d/%m/%Y')
    await user.send("-----------------------------------------------------------------")
    await user.send(f"Recherche TGV MAX du {today}")
    if dbStatus == True:
        await user.send(":white_check_mark: La database est à jour")
    elif dbStatus == False:
        await user.send(":x: La database n'est pas à jour")
    else:
        await user.send("Erreur lors du check de la database")
    
    workdir = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(workdir, 'trainsToFind.json')
    with open(json_path, 'r') as json_file:
        train_database = json.load(json_file)
    for train in train_database:
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
    
bot.run(TOKEN)
