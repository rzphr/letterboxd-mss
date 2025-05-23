import os
import discord
import psycopg2
from discord.ext import commands
from my_scraper import fetch_reviews
from db import store_reviews, get_cached_reviews
from dotenv import load_dotenv

intents = discord.Intents.default()
intents.message_content = True

load_dotenv()
bot = discord.Bot(command_prefix="!", intents=intents)
DATABASE_URL = os.getenv("DATABASE_URL")

def get_db_connection():
    conn = psycopg2.connect(DATABASE_URL)
    return conn

def insert_review(reviewer, movie_title, review_text, review_date):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO reviews (reviewer, movie_title, review_text, review_date)
        VALUES (%s, %s, %s, %s);
        """,
        (reviewer, movie_title, review_text, review_date)
    )
    conn.commit()
    cur.close()
    conn.close()

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

@bot.command(name="syncreviews")
async def sync_reviews(ctx, username: str):
    await ctx.send(f"🔄 Syncing reviews for `{username}` from Letterboxd...")
    try:
        count = scrape_and_save_reviews(username)
        await ctx.send(f"✅ Synced {count} reviews from `{username}`.")
    except Exception as e:
        await ctx.send(f"❌ Error syncing reviews: {e}")

@bot.slash_command(description="Adds user to reviewer list")
async def addreviewer(ctx, user: discord.User):
    await ctx.respond(f"✅ {user.name} added to reviewer list.")

@bot.slash_command(description="Remove user from reviewer list")
async def removereviewer(ctx, user: discord.User):
    await ctx.respond(f"❌ {user.name} removed from reviewer list.")

@bot.slash_command(description="Shows reviews for a given person")
async def crew(ctx, person: str):
    await ctx.respond(f"🎬 Showing reviews for crew member: {person}")

@bot.slash_command(description="Shows reviews for given list")
async def list(ctx, list_name: str):
    await ctx.respond(f"📋 Showing reviews for list: {list_name}")

@bot.slash_command(description="Shows list of reviews")
async def reviews(ctx):
    await ctx.respond("📖 Showing all reviews...")

@bot.slash_command(description="Search review results by parameters")
async def search(ctx, query: str):
    await ctx.respond(f"🔍 Searching for: {query}")

@bot.slash_command(description="Sync with the latest reviews")
async def syncreviews(ctx):
    await ctx.respond("🔄 Syncing latest reviews...")

bot.run(os.getenv("DISCORD_BOT_TOKEN"))
