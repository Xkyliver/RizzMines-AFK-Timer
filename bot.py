# main.py
import discord
from discord.ext import commands
import asyncio
import os
import time

TOKEN = os.getenv("DISCORD_TOKEN")  # set this in Railway (or replace for local testing)
GUILD_ID = 1416576228764160182
ROLE_ID = 1416579217000239124

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

# Global state
timer_task = None
timer_end = None
running = False

async def run_timer(channel: discord.abc.Messageable, initial_duration: int):
    """Run timer loop: first run uses initial_duration (seconds), afterward 20 minutes cycles."""
    global timer_end, running, timer_task

    duration = initial_duration
    try:
        while running:
            timer_end = time.time() + duration
            # announce start in channel (optional)
            await channel.send(f"⏳ Timer cycle started: **{duration//60}** minutes")

            # Warnings we want (in seconds)
            warnings = [3*60, 2*60, 60]

            for w in warnings:
                # compute when to warn: warn_at = timer_end - w
                warn_at = timer_end - w
                to_sleep = warn_at - time.time()
                if to_sleep <= 0:
                    # warning time already passed (timer shorter than this warning) => skip
                    continue
                # sleep until that warning
                await asyncio.sleep(to_sleep)
                if not running:
                    return
                # Send warning
                await channel.send(f"⚠️ <@&{ROLE_ID}> — **{w//60}** minute{'s' if w//60 > 1 else ''} remaining!")

            # sleep until end
            to_sleep_end = timer_end - time.time()
            if to_sleep_end > 0:
                await asyncio.sleep(to_sleep_end)
            if not running:
                return

            # finished
            await channel.send(f"⚡ <@&{ROLE_ID}> AFK tokens ready!")

            # after the first cycle, every next cycle uses 20 minutes
            duration = 20 * 60

    except asyncio.CancelledError:
        # gracefully stop on cancel
        return
    finally:
        # cleanup if we exit loop naturally
        timer_end = None
        running = False
        timer_task = None

# ---------------- SLASH COMMANDS ----------------
@bot.tree.command(name="ping", description="Check bot is alive", guild=discord.Object(id=GUILD_ID))
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message("pong")

@bot.tree.command(name="starttimer", description="Start the AFK timer") 
