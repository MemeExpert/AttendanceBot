import discord
from discord.ext import commands
import logging
import random
import asyncio
import config

description = '''First iteration of discord attendance bot'''
bot = commands.Bot(command_prefix='!', description=description)

@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')

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
        print(reaction)
        print(reaction.count)
        results += reaction.emoji + ": " + format(reaction.count) + "\n \n"
    
    embed = discord.Embed(title=text, description='Results: \n ' + results, colour=0xDEADBF)
    await ctx.author.send("Your recent poll:", embed=embed)
    # NOTE: Also grabs other reactions that user might have added to message
""" async def list_servers():
    await bot.wait_until_ready()
    while not bot.is_closed:
        print("Current servers:")
        for server in bot.servers:
            print(server.name)
        await asyncio.sleep(600)

# This is for logging into a discord.log file
logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

bot.loop.create_task(list_servers()) """
bot.run(config.discordToken)