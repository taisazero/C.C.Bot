import discord
from discord import VoiceClient
from discord.ext import commands
import random
from urllib import request as request
from urllib import parse as parser
from bs4 import BeautifulSoup
import atexit
import json
from sys import exit
import logging
import collections
import re
import asyncio
from async_timeout import timeout
from functools import partial
from youtube_dl import YoutubeDL

append_to_file=open('discord_msgs.txt','a',encoding='utf-8')
read_from_file=open('discord_msgs.txt','r',encoding='utf-8')
temp_file=open('keys\\token.txt','r')
bot_token=temp_file.readline()
bot_token=re.sub(r'\n','',bot_token)
giphy_token=temp_file.readline()
giphy_token=re.sub(r'\n','',giphy_token)
temp_file.close()

ytdlopts = {
    'format': 'bestaudio/best',
    'outtmpl': 'downloads/%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0'  # ipv6 addresses cause issues sometimes
}

ffmpegopts = {
    'before_options': '-nostdin',
    'options': '-vn'
}

ytdl = YoutubeDL(ytdlopts)

class VoiceConnectionError(commands.CommandError):
    """Custom Exception class for connection errors."""


class InvalidVoiceChannel(VoiceConnectionError):
    """Exception for cases of invalid Voice Channels."""

class YTDLSource(discord.PCMVolumeTransformer):

    def __init__(self, source, *, data, requester):
        super().__init__(source)
        self.requester = requester

        self.title = data.get('title')
        self.web_url = data.get('webpage_url')

        # YTDL info dicts (data) have other useful information you might want
        # https://github.com/rg3/youtube-dl/blob/master/README.md

    def __getitem__(self, item: str):
        """Allows us to access attributes similar to a dict.
        This is only useful when you are NOT downloading.
        """
        return self.__getattribute__(item)

    @classmethod
    async def create_source(cls, ctx, search: str, *, loop, download=False):
        loop = loop or asyncio.get_event_loop()

        to_run = partial(ytdl.extract_info, url=search, download=download)
        data = await loop.run_in_executor(None, to_run)

        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]

        await ctx.send(f'```ini\n[Added {data["title"]} to the Queue.]\n```', delete_after=15)

        if download:
            source = ytdl.prepare_filename(data)
        else:
            return {'webpage_url': data['webpage_url'], 'requester': ctx.author, 'title': data['title']}

        return cls(discord.FFmpegPCMAudio(source), data=data, requester=ctx.author)

    @classmethod
    async def regather_stream(cls, data, *, loop):
        """Used for preparing a stream, instead of downloading.
        Since Youtube Streaming links expire."""
        loop = loop or asyncio.get_event_loop()
        requester = data['requester']

        to_run = partial(ytdl.extract_info, url=data['webpage_url'], download=False)
        data = await loop.run_in_executor(None, to_run)

        return cls(discord.FFmpegPCMAudio(data['url']), data=data, requester=requester)

class MusicPlayer:
    """A class which is assigned to each guild using the bot for Music.
    This class implements a queue and loop, which allows for different guilds to listen to different playlists
    simultaneously.
    When the bot disconnects from the Voice it's instance will be destroyed.
    """

    __slots__ = ('bot', '_guild', '_channel', '_cog', 'queue', 'next', 'current', 'np', 'volume')

    def __init__(self, ctx):
        self.bot = ctx.bot
        self._guild = ctx.guild
        self._channel = ctx.channel
        self._cog = ctx.cog

        self.queue = asyncio.Queue()
        self.next = asyncio.Event()

        self.np = None  # Now playing message
        self.volume = .5
        self.current = None

        ctx.bot.loop.create_task(self.player_loop())

    async def player_loop(self):
        """Our main player loop."""
        await self.bot.wait_until_ready()

        while not self.bot.is_closed():
            self.next.clear()

            try:
                # Wait for the next song. If we timeout cancel the player and disconnect...
                async with timeout(300):  # 5 minutes...
                    source = await self.queue.get()
            except asyncio.TimeoutError:
                return self.destroy(self._guild)

            if not isinstance(source, YTDLSource):
                # Source was probably a stream (not downloaded)
                # So we should regather to prevent stream expiration
                try:
                    source = await YTDLSource.regather_stream(source, loop=self.bot.loop)
                except Exception as e:
                    await self._channel.send(f'There was an error processing your song.\n'
                                             f'```css\n[{e}]\n```')
                    continue

            source.volume = self.volume
            self.current = source

            self._guild.voice_client.play(source, after=lambda _: self.bot.loop.call_soon_threadsafe(self.next.set))
            self.np = await self._channel.send(f'**Now Playing:** `{source.title}` requested by '
                                               f'`{source.requester}`')
            await self.next.wait()

            # Make sure the FFmpeg process is cleaned up.
            source.cleanup()
            self.current = None

            try:
                # We are no longer playing this song...
                await self.np.delete()
            except discord.HTTPException:
                pass

    def destroy(self, guild):
        """Disconnect and cleanup the player."""
        return self.bot.loop.create_task(self._cog.cleanup(guild))


logger = logging.getLogger('discord')
logger.setLevel(logging.INFO)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

description = '''C.C. is a simple music bot. Below are the supported commands'''
bot = commands.Bot(command_prefix='!c ', description=description)
latest_msg=discord.Message
dic=collections.defaultdict(lambda :[])
async def readMessages(channel):
    counter =0

    temp_date=''
    for line in read_from_file.readlines():
        line= re.sub(r'[\n]','',line)
        for index in range(0,len(line)):
            if('2017'in line.split(' ')[0]):
                temp_date=line.split(' ')[0]+' '+line.split(' ')[1]
                dic[line.split(' ')[0]+' '+ line.split(' ')[1]].append( line.split(' ')[2])
                dic[temp_date].append(' '.join (line.split(' ')[3:len(line.split())]))#hi

            else:
                dic[temp_date][1]+=(line)

    read_from_file.close()
    async for message in bot.logs_from(channel, limit=10000):

        if(str(message.timestamp) not in dic.keys()):
            counter+=1
            append_to_file.write(str(message.timestamp)+' '+str(message.author)+' '+' '+str(message.content)+'\n')

    append_to_file.close()
    print(str(counter), 'new messages added')



@bot.event
async def on_ready():
    print('Logged in as')
    bot.login
    print(bot.user.name)
    print(bot.user.id)
    print('------')
    #await readMessages(bot.get_channel('275407824807264260'))
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



def get_pizza_gifs():
    url = 'https://api.giphy.com/v1/gifs/search?api_key='+giphy_token+'&q=code%20geass%20pizza&limit=25&offset=0&rating=G&lang=en'
    response = request.urlopen(url)
    result = response.read()


    d = json.loads(result)
    list = []
    for i in range(0, len(d['data'])):
        if (('cc' in d['data'][i]['slug'] and 'pizza' in d['data'][i]['slug']) or 'pizza' in d['data'][i][
            'title'] and 'cc' in d['data'][i]['title']):
            list.append(d['data'][i]['embed_url'])
    return list
#Todo add command not found
async def invalid():
    await bot.say('Invalid command! Please type !c help for list of commands')
@bot.command()
async def pin_msg():
    bot.pin_message(latest_msg)

@bot.command()
async def commands():
    em=discord.Embed(title='Commands!', description='List of C.C. bot Commands:\nPrefix is !c \nCommands: 1. eatpizza \n2. add num1 num2 : returns num1+num2 \n3. spamasshat message: sends 5 messages to Devansh\n4. spamasshat2 message times: sends messages according to number of times to Devansh\n 5. asshatmusic: sends Devansh a random nightcore, Alan Walker, Marshmellow, Code Geass song \n6. erfanmusic @user : sends the specified user a random song from Erfan\'s Youtube playlist! ', colour=0xFCC3E)
    em.set_author(name='C.C. Bot',icon_url='https://cdn.discordapp.com/app-icons/386758307957964800/bdee6902547c40608012eca1f37438aa.png')
    await bot.send_message(bot.get_channel('275407824807264260'), embed=em)

@bot.command()
async def eatpizza():
    list=get_pizza_gifs()
    await bot.say(':pizza:'+list[random.randint(0,len(list)-1)]+' :pizza:'+'!' +':heart: :heart: :heart:')
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
    list=['nightcore','code geass op','ok one rock', 'Marshmellow','Alan Walker Spectre', 'code geass ed', 'code geass ost']
    num=random.randint(0,len(list)-1)
    await bot.say('<@!175826482923438081>'+' '+getYoutube(list[num]))

@bot.command()
async def erfanmusic(user:discord.User):
    await  bot.say(user.mention+' '+getPlayListSong())

@bot.command(name='connect', aliases=['join'])
async def connect_(self, ctx, *, channel: discord.VoiceChannel=None):
    """Connect to voice.
    Parameters
    ------------
    channel: discord.VoiceChannel [Optional]
        The channel to connect to. If a channel is not specified, an attempt to join the voice channel you are in
        will be made.
    This command also handles moving the bot to different channels.
    """
    if not channel:
        try:
            channel = ctx.author.voice.channel
        except AttributeError:
            raise InvalidVoiceChannel('No channel to join. Please either specify a valid channel or join one.')

    vc = ctx.voice_client

    if vc:
        if vc.channel.id == channel.id:
            return
        try:
            await vc.move_to(channel)
        except asyncio.TimeoutError:
            raise VoiceConnectionError(f'Moving to channel: <{channel}> timed out.')
    else:
        try:
            await channel.connect()
        except asyncio.TimeoutError:
            raise VoiceConnectionError(f'Connecting to channel: <{channel}> timed out.')

    await ctx.send(f'Connected to: **{channel}**', delete_after=20)


    def get_player(self, ctx):
        """Retrieve the guild player, or generate one."""
        try:
            player = self.players[ctx.guild.id]
        except KeyError:
            player = MusicPlayer(ctx)
            self.players[ctx.guild.id] = player

        return player

@bot.command(pass_context=True)
async def disconnectvoice(ctx):
    server=ctx.message.server
    channel = ctx.message.author.voice_channel
   # VoiceClient.disconnect(channel)
    voice_client=bot.voice_client_in(server)
    await voice_client.disconnect()


@bot.command(name='play', aliases=['sing'])
async def play_(self, ctx, *, search: str):
    """Request a song and add it to the queue.
    This command attempts to join a valid voice channel if the bot is not already in one.
    Uses YTDL to automatically search and retrieve a song.
    Parameters
    ------------
    search: str [Required]
        The song to search and retrieve using YTDL. This could be a simple search, an ID or URL.
    """
    await ctx.trigger_typing()

    vc = ctx.voice_client

    if not vc:
        await ctx.invoke(self.connect_)

    player = self.get_player(ctx)

    # If download is False, source will be a dict which will be used later to regather the stream.
    # If download is True, source will be a discord.FFmpegPCMAudio with a VolumeTransformer.
    source = await YTDLSource.create_source(ctx, search, loop=self.bot.loop, download=False)

    await player.queue.put(source)

@bot.command(name='pause')
async def pause_(self, ctx):
    """Pause the currently playing song."""
    vc = ctx.voice_client

    if not vc or not vc.is_playing():
        return await ctx.send('I am not currently playing anything!', delete_after=20)
    elif vc.is_paused():
        return

    vc.pause()
    await ctx.send(f'**`{ctx.author}`**: Paused the song!')

@bot.command(name='resume')
async def resume_(self, ctx):
    """Resume the currently paused song."""
    vc = ctx.voice_client

    if not vc or not vc.is_connected():
        return await ctx.send('I am not currently playing anything!', delete_after=20)
    elif not vc.is_paused():
        return

    vc.resume()
    await ctx.send(f'**`{ctx.author}`**: Resumed the song!')


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







bot.run(bot_token)

