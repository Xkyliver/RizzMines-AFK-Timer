import discord
from discord.ext import commands
from discord import app_commands
import asyncio

import os
TOKEN = os.getenv("TOKEN") 
GUILD_ID = 1416576228764160182  # Replace with your server ID
ROLE_ID = 1416579217000239124   # Replace with your role ID

intents = discord.Intents.default()

# Bot setup
class MyClient(discord.Client):
    def __init__(self):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        await self.tree.sync(guild=discord.Object(id=GUILD_ID))

client = MyClient()

# Global control variables
afk_timer_running = False
afk_task = None


@client.tree.command(name="afk", description="AFK timer controls", guild=discord.Object(id=GUILD_ID))
@app_commands.describe(action="start or stop", minutes="Interval in minutes (default 18)")
async def afk(interaction: discord.Interaction, action: str, minutes: int = 18):
    global afk_timer_running, afk_task
    role = interaction.guild.get_role(ROLE_ID)

    if action.lower() == "start":
        if afk_timer_running:
            await interaction.response.send_message("⚠️ The AFK timer is already running!", ephemeral=True)
        else:
            afk_timer_running = True
            await interaction.response.send_message(f"✅ AFK timer started! Pinging {role.mention} every {minutes} minutes.")
            afk_task = asyncio.create_task(start_afk_timer(interaction.channel, role, minutes))

    elif action.lower() == "stop":
        if not afk_timer_running:
            await interaction.response.send_message("⚠️ No AFK timer is running right now.", ephemeral=True)
        else:
            afk_timer_running = False
            if afk_task:
                afk_task.cancel()
            await interaction.response.send_message("🛑 AFK timer stopped.")


async def start_afk_timer(channel, role, minutes):
    global afk_timer_running
    try:
        while afk_timer_running:
            await channel.send(f"{role.mention} ⏰ AFK check!")
            await asyncio.sleep(minutes * 60)
    except asyncio.CancelledError:
        pass


client.run(TOKEN)
