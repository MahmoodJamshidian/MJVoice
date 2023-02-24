from discord.ext.commands import Bot
from discord import Client
from discord import Intents
from dotenv import load_dotenv
from py_ytdl import YTvideo
import discord
import asyncio
import os, sys
import uuid

discord.opus.load_opus("./libopus.so")

def size2int(_unit: str, _size: str):
    _size = float(_size)
    _val: int
    match _unit.lower():
        case 'b':
            _val = 0
        case 'kb':
            _val = 1
        case 'mb':
            _val = 2
        case 'gb':
            _val = 3
        case 'tb':
            _val = 4
        case _:
            raise Exception(f"{_unit} unit is invalid")
    return _size * 1024 ** _val

DEL_MSG_TIME = 15
MAX_AUDIO_SIZE_STR = "100 MB"
MAX_AUDIO_SIZE = size2int(*MAX_AUDIO_SIZE_STR.split()[::-1])
load_dotenv()

intents = Intents.all()
client = Client(intents=intents)
bot = Bot("/", intents=intents)

class local_video:
    def __init__(self, _filepath: str, _vid: YTvideo):
        self._lnk = _filepath
        self._vid = _vid
        
    def __str__(self) -> str:
        return self._lnk
    
    def __del__(self):
        os.remove(self._lnk)
        
class link_controler:
    def __init__(self, main_path: str = "./tmp"):
        self.main_path = main_path
        if not os.path.isdir(main_path):
            os.mkdir(main_path)
    def open_url(self, url: str):
        vid = YTvideo(url)
        if 'mp3' in vid.links or 'ogg' in vid in vid.links:
            if 'mp3' in vid.links:
                _type = 'mp3'
            else:
                _type = 'ogg'
        else:
            raise Exception("audio file is not available")
        _quality, _size = [(i['k'], i['size'],) for i in vid.links[_type].values()][-1]
        _size = size2int(*_size.split()[::-1])
        yield _size
        _path = os.path.join(self.main_path, f"{uuid.uuid4()}.{_type}")
        vid.download(_type, _quality, _path)
        yield local_video(_path, vid)
        

voices: dict[str, discord.VoiceClient] = {}

lc = link_controler()

@bot.event
async def on_ready():
    print(f"logged in as {bot.user}, ID = {bot.user.id}")

@bot.slash_command("play", "play a mousic")
async def play(interaction: discord.Interaction, url: str = discord.SlashOption(required=True, description="youtube music url")):
    msg = await interaction.send("loading...")
    if not interaction.user.voice:
        await msg.edit(f"{interaction.user.mention}, your are not connected to a voice channel", delete_after=DEL_MSG_TIME)
    else:
        try:
            if not str(interaction.user.voice.channel.id) in voices:
                voices[str(interaction.user.voice.channel.id)] = await interaction.user.voice.channel.connect()
            elif not voices[str(interaction.user.voice.channel.id)].is_connected():
                voices[str(interaction.user.voice.channel.id)] = await interaction.user.voice.channel.connect()
            else:
                raise
        except:
            await msg.edit(f"{interaction.user.mention}, i can't connect to voice channel :(", delete_after=DEL_MSG_TIME)
            return
        async with interaction.channel.typing():
            vid = lc.open_url(url)
            try:
                a= next(vid)
                if a > MAX_AUDIO_SIZE:
                    del vid
                    await msg.edit(f"i can't play this video. Because the file size is more than {MAX_AUDIO_SIZE_STR}.", delete_after=DEL_MSG_TIME)
            except Exception as e:
                await msg.edit(f"{e}", delete_after=DEL_MSG_TIME)
                return
            link = next(vid)
            voices[str(interaction.user.voice.channel.id)].play(discord.FFmpegPCMAudio(executable="./ffmpeg", source=str(link)))
        await msg.edit('**Now playing:** {}'.format(link._vid.title))
        

if __name__ == "__main__":
    bot.run(os.environ['DISCORD_TOKEN'])