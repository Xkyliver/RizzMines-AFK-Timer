import discord
from discord.ext import tasks
import asyncio
import os
import time

TOKEN = os.getenv("TOKEN")  # Bot token (set in Railway env or replace directly)
ROLE_ID = 1416579217000239124  # Your AFK role ID
GUILD_ID = 1416576228764160182  # Your server (guild) ID

intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = discord.app_commands.CommandTree(client)

afk_task = None
end_time = None


async def afk_cycle(interaction, minutes: int):
    """One AFK cycle with a 1-min warning + final ping."""
    global end_time
    end_time = time.time() + minutes * 60
    role = interaction.guild.get_role(ROLE_ID)

    # 1-minute warning
    if minutes > 1:
        await asyncio.sleep((minutes - 1) * 60)
        if role:
            await interaction.channel.send(f"⚠️ {role.mention} 1 minute left...")

    # Final ping
    await asyncio.sleep(60)
    if role:
        await interaction.channel.send(f"⚡ {role.mention} AFK tokens ready!")


@tree.command(name="afk", description="Start or stop the AFK timer")
async def afk(interaction: discord.Interaction, action: str, custom_minutes: int = None):
    global afk_task

    if action.lower() == "start":
        if afk_task and not afk_task.done():
            await interaction.response.send_message("⚠️ AFK Timer is already running.")
            return

        async def run_timer():
            if custom_minutes:
                await afk_cycle(interaction, custom_minutes)
            while True:
                await afk_cycle(interaction, 18)

        afk_task = asyncio.create_task(run_timer())
        await interaction.response.send_message(
            f"✅ AFK Timer started ({custom_minutes or 18} minutes, then repeats 18)."
        )

    elif action.lower() == "stop":
        if afk_task and not afk_task.done():
            afk_task.cancel()
            await interaction.response.send_message("🛑 AFK Timer stopped.")
        else:
            await interaction.response.send_message("⚠️ No AFK Timer is running.")


@tree.command(name="status", description="Check how much time is left on the AFK timer")
async def status(interaction: discord.Interaction):
    global end_time
    if end_time:
        remaining = int(end_time - time.time())
        if remaining > 0:
            minutes, seconds = divmod(remaining, 60)
            await interaction.response.send_message(
                f"⏳ Time left until next ping: **{minutes}m {seconds}s**"
            )
        else:
            await interaction.response.send_message("⚠️ Timer is about to finish.")
    else:
        await interaction.response.send_message("⚠️ No AFK Timer is running.")


@client.event
async def on_ready():
    await tree.sync(guild=discord.Object(id=GUILD_ID))
    print(f"✅ Bot online as {client.user}")


client.run(TOKEN)
