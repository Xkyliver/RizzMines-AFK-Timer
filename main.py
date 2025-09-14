import discord
from discord.ext import commands
from discord import app_commands
import asyncio
import os

# Get bot token safely from Railway/Environment variables
TOKEN = os.getenv("TOKEN")

GUILD_ID = 123456789012345678  # Replace with your server ID
ROLE_ID = 987654321098765432   # Replace with your role ID

intents = discord.Intents.default()

class MyClient(discord.Client):
    def __init__(self):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        await self.tree.sync(guild=discord.Object(id=GUILD_ID))

client = MyClient()

afk_timer_running = False
afk_task = None

@client.tree.command(name="afk", description="AFK timer controls", guild=discord.Object(id=GUILD_ID))
@app_commands.describe(action="start or stop", minutes="Interval in minutes (default 18)")
async def afk(interaction: discord.Interaction, action: str, minutes: int = 18):
    global afk_timer_running, afk_task
    role = interaction.guild.get_role(ROLE_ID)

    await interaction.response.defer(ephemeral=True)  # ✅ respond immediately to avoid timeout

    if action.lower() == "start":
        if afk_timer_running:
            await interaction.followup.send("⚠️ The AFK timer is already running!", ephemeral=True)
        else:
            afk_timer_running = True
