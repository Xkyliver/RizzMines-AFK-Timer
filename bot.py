import discord
from discord.ext import commands
import asyncio
import os

TOKEN = os.getenv("DISCORD_TOKEN")  # Set in Railway variables
ROLE_ID = 1416579217000239124       # Role to ping
GUILD_ID = 1416576228764160182      # Your guild ID

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

# Timer state
timer_task = None
time_left = None
timer_running = False


async def afk_timer(interaction, duration: int):
    global timer_task, time_left, timer_running
    timer_running = True
    time_left = duration * 60
    role = interaction.guild.get_role(ROLE_ID)

    await interaction.followup.send(f"⏳ Timer started for **{duration} minutes**.")

    while time_left > 0 and timer_running:
        await asyncio.sleep(1)
        time_left -= 1

        minutes_left = time_left // 60
        seconds_left = time_left % 60

        # Ping at 3, 2, and 1 minutes left
        if minutes_left in [3, 2, 1] and seconds_left == 0:
            await interaction.channel.send(f"⚠️ {role.mention} — Only {minutes_left} minute(s) left!")

        # Timer ended
        if time_left == 0:
            await interaction.channel.send(f"⏰ {role.mention} Timer has ended!")
            await interaction.channel.send("🔄 Restarting timer for 20 minutes...")
            await afk_timer(interaction, 20)


@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")
    try:
        synced = await bot.tree.sync(guild=discord.Object(id=GUILD_ID))
        print(f"🔗 Synced {len(synced)} command(s).")
    except Exception as e:
        print(f"❌ Sync error: {e}")


@bot.tree.command(name="starttimer", description="Start the AFK timer", guild=discord.Object(id=GUILD_ID))
async def starttimer(interaction: discord.Interaction, minutes: int = 20):
    await interaction.response.defer()
    global timer_task, timer_running
    if timer_running:
        await interaction.followup.send("⚠️ Timer already running.")
        return
    timer_task = asyncio.create_task(afk_timer(interaction, minutes))


@bot.tree.command(name="stoptimer", description="Stop the AFK timer", guild=discord.Object(id=GUILD_ID))
async def stoptimer(interaction: discord.Interaction):
    global timer_running
    timer_running = False
    await interaction.response.send_message("🛑 Timer stopped.")


@bot.tree.command(name="timeleft", description="Check time left on the AFK timer", guild=discord.Object(id=GUILD_ID))
async def timeleft(interaction: discord.Interaction):
    global time_left, timer_running
    if not timer_running or time_left is None:
        await interaction.response.send_message("⏸️ No timer running.")
    else:
        mins = time_left // 60
        secs = time_left % 60
        await interaction.response.send_message(f"⏳ Time left: **{mins}m {secs}s**")


bot.run(TOKEN)
