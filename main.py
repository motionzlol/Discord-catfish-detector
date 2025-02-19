import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
from cmds.ReverseImage import setup as setup_reverse_image, ReverseImage

load_dotenv()
TOKEN = os.getenv('token')

intents = discord.Intents.all()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name} (ID: {bot.user.id})')
    print('------')

async def setup_cogs():
    await bot.add_cog(ReverseImage(bot))

@bot.event
async def setup_hook():
    await setup_cogs()

@bot.event
async def on_ready():
    await bot.tree.sync()

bot.run(TOKEN)