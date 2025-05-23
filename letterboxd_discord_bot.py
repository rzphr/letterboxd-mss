import os
import discord
from discord.ext import commands
from my_scraper import fetch_reviews
from db import store_reviews, get_cached_reviews
from dotenv import load_dotenv

intents = discord.Intents.default()
intents.message_content = True

load_dotenv()
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.command()
async def review(ctx, *, movie_name: str):
    reviews = get_cached_reviews(movie_name)
    if not reviews:
        reviews = fetch_reviews(movie_name)
        store_reviews(movie_name, reviews)
    if reviews:
        await ctx.send(f"Reviews for **{movie_name}**:\n" + "\n".join(reviews[:3]))
    else:
        await ctx.send(f"No reviews found for **{movie_name}**.")

@bot.event
async def on_ready():
    print(f"✅ Bot is ready. Logged in as {bot.user}")

@bot.command()
async def ping(ctx):
    await ctx.send("Pong!")

bot.run(os.getenv("DISCORD_BOT_TOKEN"))
