import discord
from discord.ext import commands, tasks
import asyncio
import os
import time

TOKEN = os.getenv("TOKEN")  # Your bot token
ROLE_ID = 1416579217000239124  # Role to ping
GUILD_ID = 1416576228764160182  # Guild ID for slash commands

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

# Timer variables
timer_end = None
timer_task = None


async def start_timer(minutes: int, ctx: discord.ApplicationContext):
    global timer_end, timer_task

    if timer_task and not timer_task.done():
        timer_task.cancel()

    timer_end = time.time() + (minutes * 60)

    async def run_timer():
        global timer_end
        # Wait until 1 minute before end
        await asyncio.sleep((minutes - 1) * 60)
        await ctx.respond(f"⚠️ <@&{ROLE_ID}> 1 minute remaining!")

        # Wait for final minute
        await asyncio.sleep(60)
        await ctx.respond("⏰ Timer ended!")

        # Reset to 18 minutes automatically
        await start_timer(18, ctx)

    timer_task = asyncio.create_task(run_timer())


@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")
    try:
        synced = await bot.tree.sync(guild=discord.Object(id=GUILD_ID))
        print(f"✅ Synced {len(synced)} commands to guild {GUILD_ID}")
    except Exception as e:
        print(f"❌ Sync failed: {e}")


@bot.tree.command(name="start", description="Start a custom timer", guild=discord.Object(id=GUILD_ID))
async def start(ctx: discord.Interaction, minutes: int):
    """Start a timer for X minutes, then auto-resets to 18 minutes"""
    await start_timer(minutes, ctx)
    await ctx.response.send_message(f"⏳ Timer started for {minutes} minutes!")


@bot.tree.command(name="timeleft", description="Check remaining time", guild=discord.Object(id=GUILD_ID))
async def timeleft(ctx: discord.Interaction):
    global timer_end
    if not timer_end:
        await ctx.response.send_message("⚠️ No timer is currently running.")
        return
    remaining = int(timer_end - time.time())
    if remaining < 0:
        await ctx.response.send_message("⚠️ Timer has already ended.")
        return
    mins, secs = divmod(remaining, 60)
    await ctx.response.send_message(f"⏳ Time left: {mins}m {secs}s")


bot.run(TOKEN)
