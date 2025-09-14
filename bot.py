import discord
from discord.ext import commands
import asyncio
import os

TOKEN = os.getenv("DISCORD_TOKEN")  # get token from Railway
GUILD_ID = 1416576228764160182      # your server ID
ROLE_ID = 1416579217000239124       # your AFK role ID

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="/", intents=intents)

# Global timer state
timer_task = None
time_left = 0
running = False

async def run_timer(ctx, duration):
    global time_left, running
    running = True
    role = ctx.guild.get_role(ROLE_ID)

    while running:
        time_left = duration

        while time_left > 0 and running:
            if time_left in [180, 120, 60]:  # 3 min, 2 min, 1 min left
                await ctx.send(f"⏰ {role.mention} — {time_left // 60} minutes left!")
            await asyncio.sleep(1)
            time_left -= 1

        if not running:
            break

        # Timer finished
        await ctx.send(f"⚠️ {role.mention} AFK tokens ready! Restarting at 20 minutes.")
        duration = 20 * 60  # reset to 20 minutes

@bot.command()
async def starttimer(ctx, minutes: int = 20):
    """Start the timer (default 20 minutes)"""
    global timer_task, running
    if running:
        await ctx.send("❌ A timer is already running.")
        return

    timer_task = asyncio.create_task(run_timer(ctx, minutes * 60))
    await ctx.send(f"✅ Timer started for {minutes} minutes.")

@bot.command()
async def stoptimer(ctx):
    """Stop the timer"""
    global timer_task, time_left, running
    if timer_task:
        running = False
        timer_task.cancel()
        timer_task = None
        time_left = 0
        await ctx.send("🛑 Timer stopped.")
    else:
        await ctx.send("⚠️ No active timer.")

@bot.command()
async def timeleft(ctx):
    """Check remaining time"""
    global time_left, running
    if running and time_left > 0:
        minutes, seconds = divmod(time_left, 60)
        await ctx.send(f"⏳ Time left: {minutes}m {seconds}s")
    else:
        await ctx.send("⚠️ No active timer.")

bot.run(TOKEN)
