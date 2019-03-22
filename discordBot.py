import discord
from discord.ext import commands
import logging
import random
import asyncio
import config
import re
import datetime

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

# NOTE: the important command is at the bottom "create_poll()"

@bot.command()
async def hello(ctx):
    # we do not want the bot to reply to itself
    if ctx.author == bot.user:
        return

    msg = 'Hello {0.author.mention}'.format(ctx)
    await ctx.send(msg)

@bot.command()
async def yesorno(ctx):
    print("Trying to ask yes or no")
    await ctx.send('Discord, yes or no?')
    
    def check(m):
        print(m.author.id)
        return ctx.message.author.id == m.author.id # and m.channel == ctx.channel

    response = await bot.wait_for('message', check=check)
    if response.content.lower() == 'yes':
        await ctx.send('You said yes.')
    elif response.content.lower() == 'no':
        await ctx.send('You said no.')
    else:
        await ctx.send("That isn't a valid response.")

@bot.command()
async def add(ctx, left: int, right: int):
    """Adds two numbers together."""
    await ctx.author.send(left + right) # ctx.author.send to DM
    await ctx.send("I sent you a DM with the answer")

@bot.command(description='For when you wanna settle the score some other way')
async def choose(ctx, *choices: str):
    """Chooses between multiple choices given by user"""
    await ctx.send(random.choice(choices))

@bot.command()
async def create_poll(ctx, *, text): # , *emojis: discord.Emoji):      # Add this to use custom server emojis as a paramter in the command
    msg = await ctx.send(text)
    channel = msg.channel

    reactions = {u"\U0001F44D", u"\U0001F44E"} # Hardcoded array of Python unicode for thumbs up and down
    for reaction in reactions:
        await msg.add_reaction(reaction)

    # Asynchronous wait
    await asyncio.sleep(5) # Time in seconds to wait until counting reactions

    msg = await channel.get_message(msg.id) # Need to regrab the message using the stored message id

    # msg.reactions is an array of Reaction objects. 
    # One object per emoji that stores the emoji and the count
    #   Example: 
    #       msg.reactions = [<Reaction emoji='👍' me=True count=2>,<Reaction emoji='👎' me=True count=2>]
    results = ''
    for reaction in msg.reactions:

        # NOTE: for testing --------------
        print(reaction)
        print(reaction.count - 1) # minus 1 for bot
        # --------------------------------

        users = await reaction.users().flatten()

        # Build the string of usernames for each response: 
        listUsers = ''
        if len(users) == 1:
            listUsers = ' ...   '
        for user in users[1:]: # Skip the bot
            # user : looks like stevenwhy#4936 might want to store the whole thing

            if reaction.emoji == u"\U0001F44D": # Sends message to user if they responded '👍'
                await user.send("You've reacted " + reaction.emoji + " to the event")

            listUsers += user.name + ", "
        listUsers = listUsers[:-2]

        results += reaction.emoji + ": " + format(reaction.count - 1) + "  ("+ listUsers + ")\n \n"
    
    embed = discord.Embed(title=text, description='Results: \n ' + results, colour=0xDEADBF)
    # await ctx.author.send("Your recent poll:", embed=embed)
    await ctx.send("Your recent poll:", embed=embed)
    # NOTE: Also grabs other reactions that user might have added to message


@bot.command()
async def create_event(ctx, *text): # , *emojis: discord.Emoji):      # Add this to use custom server emojis as a paramter in the command
    n = len(text)
    if n == 0 or text[0] == "help":
        await ctx.send("Create an event like: `!create_event [Event Name]`")
        return
    
    eventName = ""
    for i in range(int(n)):
        eventName = eventName + text[i] + " "
    eventName = eventName[:-1]
    msg = await ctx.send("Creating event called: " + eventName + " ... when is it?\n Example: `HH:MMpm MM/DD` \n     or   `12:00am 12/12`")
    channel = msg.channel
    

    goodDate = False

    while(not goodDate):
        def check(m):
            return m.author == ctx.author and m.channel == channel

        reply = await bot.wait_for('message', check=check)
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
                    await ctx.send("I didn't recognize that time format. Keep it like '4:00pm'")

            except ValueError as err:
                await ctx.send("I didn't recognize a valid date. Keep it like 'MM/DD'")
            
            print(eventDate)
            
        else:
            await ctx.send("I didn't recognize that date format. Keep it like 'MM/DD'")
        
    await ctx.send("OK thanks, saving "+ eventName + " at " + eventTime + " on " + eventDate)

    # NOTE: At this point we have eventName, eventTime, and eventDate
    # call api HERE with these strings to save them


bot.run(config.discordToken)