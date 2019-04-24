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
import pymysql

# This is for logging into a discord.log file
""" logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler) """

description = '''First iteration of discord attendance bot'''
bot = commands.Bot(command_prefix='!', description=description)


# Periodically check for new Events
async def search_and_post_events():
    while(True):
        # wait for a minute before checking again for new events
        #print("Waiting 120s before checking for new events")
        await asyncio.sleep(10)
        # Get all pending events that haven't expired and haven't been announced yet
        db.execute("SELECT * FROM event WHERE announceMessageId = 0 AND occurence_date > NOW() ORDER BY occurence_date ASC LIMIT 1;")
        dbCon.commit()
        res = db.fetchone()
        # no unannounced events - nothing to do
        if not res:
            print("No new events")
            continue

        print("Found new event - posting now")
        eventId = res['id']
        channel = bot.get_channel(config.discordChannelId)
        message = await channel.send("**{0}** scheduled for *{1}*\nChoose a reaction to sign up".format(
            res['title'],
            res['occurence_date'].strftime("%a - %m/%d at %I:%M%p")))

        # add user react options
        reacts = {'⚠', '❌', '✅'}
        for r in reacts:
            await message.add_reaction(r)

        sqlString = "UPDATE event SET announceMessageId = {0} WHERE id = {1}".format(message.id, eventId)
        # print(sqlString)
        db.execute(sqlString)
        dbCon.commit()

bot.loop.create_task(search_and_post_events())

# init mysql connection
dbCon = pymysql.connect(
    host=config.DatabaseHost,
    port=config.DatabasePort,
    user=config.DatabaseUser,
    passwd=config.DatabasePassword,
    database=config.DatabaseName
)

# init mysql cursor (for making queries)
db = dbCon.cursor(pymysql.cursors.DictCursor)

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

def buildDatetimeString(eventDate, eventTime):
    form = '%m/%d/%Y %H:%M:%S'
    militaryTime = datetime.datetime.strptime(eventTime, '%I:%M%p').strftime('%H:%M:%S')
    eventDateTime = eventDate + " " + militaryTime
    eventDateTime = datetime.datetime.strptime(eventDateTime, form)

    return eventDateTime


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
async def event_signups(ctx, *text):
    n = len(text)
    if n == 0 or text[0] == "help":
        await ctx.send("Get info about an event, given an event ID (from !my_events): `!event_info [Event ID]`")
        return

    event_id = text[0]
    event_name = ""
    event_datetimeStr = ""
    r = requests.request('GET','http://127.0.0.1:5000/api/event', params = {"id":event_id})
    if r.json().get("data"):
        event = r.json()["data"][0]
        dateobj = datetime.datetime.strptime(event["occurence_date"][:-6], "%Y-%m-%dT%H:%M:%S")
        event_datetimeStr = dateobj.strftime("%a - %m/%d at %I:%M%p")

        event_name = event["title"]
    else:
        await ctx.send("There is no event with id {0}!".format(event_id))
        return

    reacts = {0 : '⚠', 1 : '❌', 2 : '✅'}
    await ctx.send("Grabbing signups for event #{0}...".format(event_id))
    r = requests.request('GET','http://127.0.0.1:5000/api/signup', params = {"event_id":event_id})
    if r.json().get("data"):
        signupList = r.json()["data"]
        results = ""

        for signup in signupList:
            dateobj = datetime.datetime.strptime(signup["signup_date"][:-6], "%Y-%m-%dT%H:%M:%S")
            date = dateobj.strftime("%m/%d at %I:%M%p")

            results += "{0} - {1} responded on {2}\n".format(
                reacts[signup["response"]],
                signup["user"]["displayName"],
                date)
        embed = discord.Embed(
            title="Signups for Event #{0} ({1} on {2})".format(event_id, event_name, event_datetimeStr),
            description='Results:\n ' + results,
            colour=0xDEADBF)
        await ctx.send("Here you go: ", embed=embed)
    else:
        await ctx.send("There are no signups for that event!")
        return

    

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
        
    creatorId = ctx.author.id
    eventDate = eventDate + "/2019"
    eventDatetime = buildDatetimeString(eventDate, eventTime)
    print(eventDatetime)
    # NOTE: At this point we have eventName, eventTime, eventDate, creatorId
    # call api HERE with these strings to save them

    # first get user's id based on discord id
    r = requests.request('GET','http://127.0.0.1:5000/api/user', params = {"discordUserId":creatorId})
    if r.json().get("data"):
        id = r.json()["data"][0]["id"]

    params = {"title":eventName,"occurence_date": eventDatetime,"creator_id":id}
    def converter(t):
        if isinstance(t,datetime.datetime):
            return t.__str__()
    r = requests.request('POST','http://127.0.0.1:5000/api/event', data = json.dumps(params, default=converter))
    print(params)
    if r.status_code == 201:
        await ctx.send("OK thanks, saved `"+ eventName + "` at `" + eventTime + "` on `" + eventDate + "`")
    else:
        await ctx.send("There was a problem trying to save the information :wrench:")


@bot.command()
async def my_events(ctx):
    """See the events you've created *INCOMPLETE*"""
    user = ctx.author
    await ctx.author.send("Grabbing your events {0.name}...".format(user))

    r = requests.request('GET','http://127.0.0.1:5000/api/user', params = {"discordUserId":user.id})
    if r.json().get("data"):
        id = r.json()["data"][0]["id"]
    else:
        await ctx.send("You need to !register first!")
        return

    r = requests.request('GET','http://127.0.0.1:5000/api/event', params = {"creator_id":id})
    if r.json().get("data"):
        eventList = r.json()["data"]
        results = ""
        for event in eventList:
            dateobj = datetime.datetime.strptime(event["occurence_date"][:-6], "%Y-%m-%dT%H:%M:%S")
            date = dateobj.strftime("%a - %m/%d at %I:%M%p")
            results = results + '\n**' + str(event["id"]) + '** `' + event["title"] + "` on " + date
        embed = discord.Embed(title="Your events", description='Results: \n ' + results, colour=0xDEADBF)
        await ctx.send("Here you go: ", embed=embed)
    else:
        await ctx.send("Couldn't find any events created by you")


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

@bot.event
async def on_raw_reaction_add(payload):
    if bot.user.id == payload.user_id:
        return

    reacts = {'⚠':0, '❌':1, '✅':2}
    if payload.emoji.name not in reacts:
        return

    # print("user ID {0} reacted to message {1}!".format(payload.user_id, payload.message_id))

    # try to get an event thats associated with the message ID that the user reacted to
    r = requests.request('GET','http://127.0.0.1:5000/api/event', params = {"announceMessageId":payload.message_id})

    # got something - this is an event message
    if r.json().get("data"):
        data = r.json()["data"]
        eventId = data[0]["id"]

        userId = 0
        # make sure the user that is reacting is registered with our service
        r = requests.request('GET','http://127.0.0.1:5000/api/user', params = {"discordUserId":payload.user_id})
        if r.json().get("data"):
            data = r.json()["data"]
            userId = data[0]["id"]
        # user is not registered - tell them to do so and then bail
        else:
            user = discord.utils.get(client.get_all_members(), id=payload.user_id)
            await bot.send_message(user, "Hi {0}! You aren't registered, so you can't sign up for events yet.\nType `!register YOURNAME` to get registered!")
            return

        print("Checking if id {0} is signed up for event {1}".format(userId, eventId))

        # check if the user is already signed up
        r = requests.request('GET','http://127.0.0.1:5000/api/signup', params = {
            "event_id" : eventId,
            "user_id"  : userId
            })

        # user is already signed up, so replace their signup status with the new one
        if r.json().get("data"):
            data = r.json()["data"]
            signupId = data[0]["id"]

            r = requests.request('PUT','http://127.0.0.1:5000/api/signup', json = {
            "id": signupId,
            "event_id" : eventId,
            "user_id"  : userId,
            "response": reacts[payload.emoji.name]
            })
        # user isn't signed up, so just add their signup
        else:
            r = requests.request('POST','http://127.0.0.1:5000/api/signup', json = {
            "event_id" : eventId,
            "user_id"  : userId,
            "response": reacts[payload.emoji.name]
            })

    # otherwise its just a random react, so ignore it
    else:
        return

# Start discord.py bot service
bot.run(config.discordToken)
