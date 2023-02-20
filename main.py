from discord.ext.commands import Bot
from discord import Client
from discord import Intents
from dotenv import load_dotenv
import youtube_dl
import discord
import asyncio
import os, sys

DEL_MSG_TIME = 30

load_dotenv()

intents = Intents.all()
client = Client(intents=intents)
bot = Bot("/", intents=intents)

youtube_dl.utils.bug_reports_message = lambda : ""

ytdl_format_options = {
    'format': 'bestaudio/best',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0'
}

ffmpeg_options = {
    'options': '-vn'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

voices: dict[str, discord.VoiceClient] = {}

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')
        self.url = ""

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))
        if 'entries' in data:
            data = data['entries'][0]
        filename = data['title'] if stream else ytdl.prepare_filename(data)
        return filename

@bot.event
async def on_ready():
    print(f"logged in as {bot.user}, ID = {bot.user.id}")

@bot.slash_command("play", "play a mousic")
async def play(interaction: discord.Interaction, url: str = discord.SlashOption(required=True, description="youtube music url")):
    if not interaction.user.voice:
        await interaction.send(f"{interaction.user.mention}, your are not connected to a voice channel", delete_after=DEL_MSG_TIME)
    else:
        try:
            if not str(interaction.user.voice.channel.id) in voices:
                voices[str(interaction.user.voice.channel.id)] = await interaction.user.voice.channel.connect()
            elif not voices[str(interaction.user.voice.channel.id)].is_connected():
                voices[str(interaction.user.voice.channel.id)] = await interaction.user.voice.channel.connect()
            else:
                raise
        except:
            await interaction.send(f"{interaction.user.mention}, i can't connect to voice channel :(", delete_after=DEL_MSG_TIME)
            return
        async with interaction.channel.typing():
            filename = await YTDLSource.from_url(url, loop=bot.loop)
            voices[str(interaction.user.voice.channel.id)].play(discord.FFmpegPCMAudio(source=filename))
        await interaction.send('**Now playing:** {}'.format(filename))
        

if __name__ == "__main__":
    bot.run(os.environ['DISCORD_TOKEN'])


