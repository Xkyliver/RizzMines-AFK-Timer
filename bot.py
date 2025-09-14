import discord
from discord.ext import commands
import asyncio
import os

TOKEN = os.getenv("TOKEN")  # Your bot token
ROLE_ID = 1416579217000239124  # Role to ping
GUILD_ID = 1416576228764160182  # Guild ID for slash commands

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")
    try:
        synced = await bot.tree.sync(guild=discord.Object(id=GUILD_ID))
        print(f"✅ Synced {len(synced)} commands to guild {GUILD_ID}")
    except Exception as e:
        print(f"❌ Sync failed: {e}")


@bot.tree.command(name="start", description="Start a timer", guild=discord.Object(id=GUILD_ID))
async def start(ctx: discord.Interaction, minutes: int):
    await ctx.response.send_message(f"⏳ Timer started for {minutes} minutes!")

    # Wait until 1 minute left
    if minutes > 1:
        await asyncio.sleep((minutes - 1) * 60)
        await ctx.followup.send(f"⚠️ <@&{ROLE_ID}> 1 minute remaining!")

    # Final wait
    await asyncio.sleep(60)
    await ctx.followup.send("⏰ Timer ended!")


bot.run(TOKEN)
