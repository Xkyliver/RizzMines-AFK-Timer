import discord
from discord.ext import commands
import asyncio
import os

TOKEN = os.getenv("DISCORD_TOKEN")  # get token from Railway
GUILD_ID = 1416576228764160182      # your server ID
ROLE_ID = 1416579217000239124       # your AFK role ID

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

# Global timer state
timer_task = None
time_left = 0
running = False

async def run_timer(interaction, duration):
    global time_left, running
    running = True
    guild = bot.get_guild(GUILD_ID)
    role = guild.get_role(ROLE_ID)

    while running:
        time_left = duration

        while time_left > 0 and running:
            if time_left in [180, 120, 60]:  # 3 min, 2 min, 1 min left
                await interaction.channel.send(f"⏰ {role.mention} — {time_left // 60} minutes left!")
            await asyncio.sleep(1)
            time_left -= 1

        if not running:
            break

        # Timer finished
        await interaction.channel.send(f"⚠️ {role.mention} AFK tokens ready! Restarting at 20 minutes.")
        duration = 20 * 60  # reset to 20 minutes

# --- SLASH COMMANDS ---
@bot.tree.command(name="starttimer", description="Start the AFK timer (default 20 minutes)")
async def starttimer(interaction: discord.Interaction, minutes: int = 20):
    global timer_task, running
    if running:
        await interaction.response.send_message("❌ A timer is already running.", ephemeral=True)
        return

    timer_task = asyncio.create_task(run_timer(interaction, minutes * 60))
    await interaction.response.send_message(f"✅ Timer started for {minutes} minutes.")

@bot.tree.command(name="stoptimer", description="Stop the AFK timer")
async def stoptimer(interaction: discord.Interaction):
    global timer_task, time_left, running
    if timer_task:
        running = False
        timer_task.cancel()
        timer_task = None
        time_left = 0
        await interaction.response.send_message("🛑 Timer stopped.")
    else:
        await interaction.response.send_message("⚠️ No active timer.")

@bot.tree.command(name="timeleft", description="Check remaining time")
async def timeleft(interaction: discord.Interaction):
    global time_left, running
    if running and time_left > 0:
        minutes, seconds = divmod(time_left, 60)
        await interaction.response.send_message(f"⏳ Time left: {minutes}m {seconds}s")
    else:
        await interaction.response.send_message("⚠️ No active timer.")

# Sync slash commands on startup
@bot.event
async def on_ready():
    await bot.tree.sync(guild=discord.Object(id=GUILD_ID))
    print(f"✅ Logged in as {bot.user}. Slash commands synced!")

bot.run(TOKEN)
