import discord
from discord.ext import commands
import random
from urllib import request as request
from urllib import parse as parser
from bs4 import BeautifulSoup
import atexit
from sys import exit

description = '''An example bot to showcase the discord.ext.commands extension
module.
There are a number of utility commands being showcased here.'''
bot = commands.Bot(command_prefix='!c ', description=description)


@bot.event
async def on_ready():
    print('Logged in as')
    bot.login
    print(bot.user.name)
    print(bot.user.id)
    print('------')
"""
@atexit.register
def bot_out():
    print('Logged out')
    bot.logout()


@bot.command()
async def logoff():
    #await bot.send_typing(discord.Channel.type)
    await bot.say('Logging out')
    await exit()

"""

@bot.command()
async def add(left : int, right : int):
    """Adds two numbers together."""
    await bot.say(left + right)

@bot.command()
async def roll(dice : str):
    """Rolls a dice in NdN format."""
    try:
        rolls, limit = map(int, dice.split('d'))
    except Exception:
        await bot.say('Format has to be in NdN!')
        return

    result = ', '.join(str(random.randint(1, limit)) for r in range(rolls))
    await bot.say(result)

@bot.command(description='For when you wanna settle the score some other way')
async def choose(*choices : str):
    """Chooses between multiple choices."""
    await bot.say(random.choice(choices))

@bot.command()
async def repeat(times : int, content):
    """Repeats a message multiple times."""
    for i in range(times):
        await bot.say(content)

@bot.command()
async def joined(member : discord.Member):
    """Says when a member joined."""
    await bot.say('{0.name} joined in {0.joined_at}'.format(member))

@bot.group(pass_context=True)
async def cool(ctx):
    """Says if a user is cool.
    In reality this just checks if a subcommand is being invoked.
    """
    if ctx.invoked_subcommand is None:
        await bot.say('No, {0.subcommand_passed} is not cool'.format(ctx))

@bot.command()
async def spamasshat(music):

    for i in range (0,5):
        await bot.say('<@!175826482923438081>'+' '+music)
@bot.command()
async def spamasshat2(music,times):
    for i in range (0,times):
        await bot.say('<@!175826482923438081>'+' '+music)
@bot.command()
async def asshatmusic():
    list=['nightcore','code geass','ok one rock', 'Marshmellow','Alan Walker Spectre']
    num=random.randint(0,len(list)-1)
    await bot.say('<@!175826482923438081>'+' '+getYoutube(list[num]))

@bot.command()
async def erfanmusic(user:discord.User):
    await  bot.say(user.mention+' '+getPlayListSong())


def getYoutube(textToSearch):
    query = textToSearch
    query=parser.quote(query)
    url = "https://www.youtube.com/results?search_query=" + query

    print(url)
    response = request.urlopen(url)
    html = response.read()
    soup = BeautifulSoup(html)
    list=[]

    for vid in soup.findAll(attrs={'class': 'yt-uix-tile-link'}):
        print ('https://www.youtube.com' + vid['href'])
        list.append('https://www.youtube.com' + vid['href'])
    return list[random.randint(0,len(list))]

def getPlayListSong():
    return 'https://www.youtube.com/watch?v=ui-pQ2tfytk&list=PLfu_lTdHwutANLVF3gwKEBKQ25FAQgQSb&index='+str(random.randint(0,195))

@cool.command(name='bot')
async def _bot():
    """Is the bot cool?"""
    await bot.say('Yes, the bot is cool.')

bot.run('Mzg2NzU4MzA3OTU3OTY0ODAw.DQUqpA.EEwZ6nhq3PaQjJsbZbnLj6UiRa4')