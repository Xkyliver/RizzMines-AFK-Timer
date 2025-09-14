import discord
from discord.ext import commands
import asyncio
import os
import time

TOKEN = os.getenv("TOKEN")  # Bot token from environment variables
ROLE_ID = 123456789012345678  # Replace with your AFK role ID

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="/", intents=intents)

afk_task = None  # global task reference
end_time = None  # when the current cycle ends


async def afk_cycle(ctx, minutes: int):
    """Runs one AFK timer cycle with a 1-minute warning."""
    global end_time
    end_time = time.time() + minutes * 60  # store when this cycle ends

    role = ctx.guild.get_role(ROLE_ID)

    # Wait until 1 minute before completion
    if minutes > 1:
        await asyncio.sleep((minutes - 1) * 60)
        if role:
            await ctx.send(f"⚠️ {role.mention} 1 minute left...")

    # Final minute
    await asyncio.sleep(60)
    if role:
        await ctx.send(f"⚡ {role.mention} AFK tokens ready!")


@bot.command(name="afk")
async def afk(ctx, arg="start", custom_minutes: int = None):
    global afk_task

    if arg.lower() == "start":
        if afk_task and not afk_task.done():
            await ctx.send("⚠️ AFK Timer is already running.")
            return

        async def run_timer():
            if custom_minutes:
                await afk_cycle(ctx, custom_minutes)

            while True:
                await afk_cycle(ctx, 18)

        afk_task = asyncio.create_task(run_timer())
        await ctx.send(
            f"✅ AFK Timer started ({custom_minutes or 18} minutes, then repeats 18)."
        )

    elif arg.lower() == "stop":
        if afk_task and not afk_task.done():
            afk_task.cancel()
            await ctx.send("🛑 AFK Timer stopped.")
        else:
            await ctx.send("⚠️ No AFK Timer is running.")


@bot.command(name="status")
async def status(ctx):
    global end_time
    if end_time:
        remaining = int(end_time - time.time())
        if remaining > 0:
            minutes, seconds = divmod(remaining, 60)
            await ctx.send(
                f"⏳ Time left until next ping: **{minutes}m {seconds}s**"
            )
        else:
            await ctx.send("⚠️ Timer cycle is just about to finish.")
    else:
        await ctx.send("⚠️ No AFK Timer is running.")


@bot.event
async def on_ready():
    print(f"Bot is online as {bot.user}")


bot.run(TOKEN)
