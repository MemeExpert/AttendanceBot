import discord
from discord.ext import commands
import logging
import random
import asyncio
import config
import re
import datetime
import time
import requests
import json

# This is for logging into a discord.log file
""" logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler) """

description = '''First iteration of discord attendance bot'''
bot = commands.Bot(command_prefix='!', description=description)

@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')
    print("Current servers:")
    for guild in bot.guilds:
        print(guild.name)

def checkUniqueDisplayName(displayName):
    print(displayName)
    r = requests.request('GET','http://127.0.0.1:5000/api/user', params = {"displayName":displayName})

    if not r.json().get("data"):
        return True
    return False

@bot.command()
async def poll(ctx, *, text): # , *emojis: discord.Emoji):      # Add this to use custom server emojis as a paramter in the command
    """Create an attendance poll given an event *INCOMPLETE*"""
    if (not text):
        ctx.send("Create an attendance poll using !poll [Event Name]")
        return

    eventName = text
    msg = await ctx.send("Can you attend: `" + eventName + "` ?")
    channel = msg.channel

    reactions = {u"\U0001F44D", u"\U0001F44E"} # Hardcoded array of Python unicode for thumbs up and down
    for reaction in reactions:
        await msg.add_reaction(reaction)

    attendeeList = []
    notAttendeeList = []
    t_end = time.time() + 61 * 10

    # TODO: handle unreacting?
    while(time.time() < t_end):
        def check(reaction, user):
            return (str(reaction.emoji) == '👍' or str(reaction.emoji) == '👎') and not user.bot

        try:
            reaction, user = await bot.wait_for('reaction_add', timeout=600.0, check=check)
        except asyncio.TimeoutError:
            await channel.send('Ok let me add up the people')
            break
        else:
            # await channel.send("Thanks {0}, you said {1}".format(user.name, reaction.emoji))
            if(reaction.emoji == '👎'):
                if str(user) in attendeeList: 
                    # await channel.send("Thanks {0}, removing you from `{1}`".format(user.name, eventName))
                    attendeeList.remove(str(user))
                if str(user) not in notAttendeeList: 
                    # await channel.send("Thanks {0}, adding you to notAttendeeList".format(user.name))
                    notAttendeeList.append(str(user))
            
            elif(reaction.emoji == '👍'):
                if str(user) in notAttendeeList: 
                    # await channel.send("Thanks {0}, removing you from notAttendeeList".format(user.name))
                    notAttendeeList.remove(str(user))
                if str(user) not in attendeeList: 
                    # await channel.send("Thanks {0}, adding you to `{1}`".format(user.name, eventName))
                    attendeeList.append(str(user))

            print(attendeeList)
            print(notAttendeeList)
        
        """ try:
            reaction, user = await bot.wait_for('reaction_remove', timeout=60.0, check=check)
        except asyncio.TimeoutError:
            await channel.send('Timeout')
            break
        else:
            await channel.send("Thanks {0}, you unreacted {1}".format(user.name, reaction.emoji))
            if(reaction.emoji == '👎'):
                # if str(user) in attendeeList: attendeeList.remove(str(user))
                if str(user) in notAttendeeList: 
                    await channel.send("Thanks {0}, removing you from notAttendeeList".format(user.name))
                    notAttendeeList.remove(str(user))
            
            if(reaction.emoji == '👍'):
                if str(user) in attendeeList: 
                    await channel.send("Thanks {0}, removing you from `{1}`".format(user.name, eventName))
                    attendeeList.remove(str(user))
 """
    # NOTE: Call API to save usernames of people attending list **************************************************
    # Parameters:
    #       eventName    : name of event
    #       attendeeList : list of usernames (with unique ID) marked as attending
    # ************************************************************************************************************

    print("Final list: {0}".format(attendeeList))
    embed = discord.Embed(title=eventName, description="Results: \n 👍 {0} \n \n  👎 {1}".format(attendeeList,notAttendeeList), colour=0xDEADBF)
    # await ctx.author.send("Your recent poll:", embed=embed)
    await ctx.send("Your recent poll:", embed=embed)
    # NOTE: Also grabs other reactions that user might have added to message


@bot.command()
async def create_event(ctx, *text): # , *emojis: discord.Emoji):      # Add this to use custom server emojis as a paramter in the command
    """Create a new event *INCOMPLETE*"""
    n = len(text)
    if n == 0 or text[0] == "help":
        await ctx.send("Create an event like: `!create_event [Event Name]`")
        return
    
    eventName = ""
    for i in range(int(n)):
        eventName = eventName + text[i] + " "
    eventName = eventName[:-1]
    msg = await ctx.send("Creating event called: `" + eventName + "` ... when is it?\n Example: `HH:MMpm MM/DD` \n     or   `12:00am 12/12`")
    channel = msg.channel
    

    goodDate = False

    while(not goodDate):
        def check(m):
            return m.author == ctx.author and m.channel == channel

        reply = await bot.wait_for('message', check=check)
        if(reply.content == "cancel"):
            ctx.send("OK, cancelling the event")
            return

        date = reply.content
        print("Trying to get event details: " + date)
        date_match = re.search(r'(\d+/\d+)',date)
        time_match = re.search(r'((1[0-2]|0?[1-9]):([0-5][0-9]) ?([AaPp][Mm]))',date)

        if date_match:
            try:
                
                eventDate = date_match.group()
                datetime.datetime.strptime(eventDate,"%m/%d")
                if time_match:
                    eventTime = time_match.group()
                    print(eventTime)
                    goodDate = True

                else:
                    await ctx.send("I didn't recognize that time format. Keep it like '4:00pm' (cancel event by typing `cancel`)")

            except ValueError as err:
                await ctx.send("I didn't recognize a valid date. Keep it like 'MM/DD' (cancel event by typing `cancel`)")
            
            print(eventDate)
            
        else:
            await ctx.send("I didn't recognize that date format. Keep it like 'MM/DD' (cancel event by typing `cancel`)")
        
    await ctx.send("OK thanks, saving `"+ eventName + "` at `" + eventTime + "` on `" + eventDate + "`")

    creatorId = ctx.author.id
    # NOTE: At this point we have eventName, eventTime, eventDate, creatorId
    # call api HERE with these strings to save them

@bot.command()
async def my_events(ctx):
    """See the events you've created *INCOMPLETE*"""
    user = ctx.author
    # embed = discord.Embed(title="Your events", description='Results: \n ' + results, colour=0xDEADBF)
    await ctx.author.send("Grabbing your events {0.name}...".format(user))
    
    print(user.id)
    # NOTE: Call API to get a user's created events as well as events they are attending
    # Parameter:
    #       user.id


# gets user by the id in db, not discord user id, pretty useless was for testing connection
# @bot.command() 
# async def get_user(ctx, id):
#     """Grab user data from db given id *useless*"""
#     id = int(id)
    
#     r = requests.request('GET','http://127.0.0.1:5000/api/user', params = {"id":id})
#     print(r.url)
#     print(r.json())

# adds new user to db. Command requires a displayname to add into db
@bot.command()
async def register(ctx, *displayName):
    """Register yourself given a display name"""
    id = int(ctx.author.id)
    if len(displayName) == 0 or displayName[0] == "help":
        await ctx.send("Register your info on the bot with `!register [display-name]`")
        return

    displayName = displayName[0]

    if len(displayName) > 15:
        print("Display name is too long")
        await ctx.author.send("Display name can't be longer than 15 characters!")
        return

    r = requests.request('GET','http://127.0.0.1:5000/api/user', params = {"discordUserId":id})

    if r.json().get("data"):
        data = r.json()["data"]
        print("User already exists")
        print(data)
        await ctx.author.send("You have already registered!\nYour display name is `{0}`".format(data[0]["displayName"]))
        return

    if not checkUniqueDisplayName(displayName):
        print("Display name already exists")
        await ctx.author.send("That display name is taken!")
        return

    payload = {'displayName':displayName, 'discordUserId':id,'slackName':""}
    r = requests.request('POST','http://127.0.0.1:5000/api/user', data=json.dumps(payload))

    # TODO: reply to the user here
    print(r.status_code)
    if r.status_code == 201:
        #await ctx.author.send("Thanks {0}, you have been added to the team!".format(displayName))
        await ctx.message.add_reaction('✅')

# updates a user's displayname in db
@bot.command()
async def update(ctx, *text):
    """Update your display name for the attendance bot"""
    if len(text) == 0 or text[0] == "help":
        await ctx.send("Update your info on the bot with `!update [new-display-name]`")
        return

    id = int(ctx.author.id)

    displayName = text[0]

    if len(displayName) > 15:
        print("Display name is too long")
        await ctx.author.send("Display name can't be longer than 15 characters!")
        return

    r = requests.request('GET','http://127.0.0.1:5000/api/user', params = {"discordUserId":id})

    if not r.json().get("data"):
        print("Nothing to update")
        await ctx.author.send("You can't update because you haven't registered. Use: \n`!register [display-name]`")
        return

    if not checkUniqueDisplayName(displayName):
        print("Display name already exists")
        await ctx.author.send("That display name is taken!")
        return

    dbID = r.json()["data"][0]["id"]
    payload = {"displayName":displayName,"discordUserId":id, "id":dbID, "slackName":""}
    r = requests.request('PUT','http://127.0.0.1:5000/api/user', data=json.dumps(payload))
    print(r.status_code)

    # reply to the user here
    if r.status_code == 204:
        #await ctx.author.send("Thanks {0}, your display name has been updated".format(displayName))
        await ctx.message.add_reaction('✅')

bot.run(config.DiscordBotToken)

