import discord
from discord.ext import commands
import asyncio
import os
import time

TOKEN = os.getenv("TOKEN")  # Your bot token
ROLE_ID = 1416579217000239124  # Role to ping
GUILD_ID = 1416576228764160182  # Guild ID

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

# Global variables
timer_task = None
timer_end = None


async def timer(minutes: int, ctx: discord.Interaction):
    global timer_end
    timer_end = time.time() + minutes * 60

    # Wait until 1 minute left
    if minutes > 1:
        await asyncio.sleep((minutes - 1) * 60)
        await ctx.followup.send(f"⚠️ <@&{ROLE_ID}> 1 minute remaining!")

    # Wait for final minute
    await asyncio.sleep(60)
    await ctx.followup.send("⏰ Timer ended!")
    timer_end = None


@bot.tree.command(name="start", description="Start a timer", guild=discord.Object(id=GUILD_ID))
async def start(ctx: discord.Interaction, minutes: int):
    global timer_task
    if timer_task and not timer_task.done():
        await ctx.response.send_message("⚠️ Timer already running!")
        return

    timer_task = asyncio.create_task(timer(minutes, ctx))
    await ctx.response.send_message(f"⏳ Timer started for {minutes} minutes!")


@bot.tree.command(name="stop", description="Stop the timer", guild=discord.Object(id=GUILD_ID))
async def stop(ctx: discord.Interaction):
    global timer_task, timer_end
    if timer_task and not timer_task.done():
        timer_task.cancel()
        timer_end = None
        await ctx.response.send_message("🛑 Timer stopped!")
    else:
        await ctx.response.send_message("⚠️ No timer is running.")


@bot.tree.command(name="timeleft", description="Check remaining time", guild=discord.Object(id=GUILD_ID))
async def timeleft(ctx: discord.Interaction):
    global timer_end
    if not timer_end:
        await ctx.response.send_message("⚠️ No timer is running.")
        return
    remaining = int(timer_end - time.time())
    if remaining <= 0:
        await ctx.response.send_message("⚠️ Timer is about to finish.")
        return
    mins, secs = divmod(remaining, 60)
    await ctx.response.send_message(f"⏳ Time left: {mins}m {secs}s")


@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")
    try:
        await bot.tree.sync(guild=discord.Object(id=GUILD_ID))
        print("✅ Commands synced")
    except Exception as e:
        print(f"❌ Sync failed: {e}")


bot.run(TOKEN)
