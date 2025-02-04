import discord
import requests
from flask import Flask
import threading
import os

# Load bot token securely (Use Replit Secrets or .env file)
TOKEN = os.getenv("TOKEN")

# Setup bot with intents
intents = discord.Intents.default()
intents.message_content = True  # Needed to read message content
client = discord.Client(intents=intents)

# Function to fetch CTFtime data using team ID
def fetch_ctftime_data(team_id):
    url = f"https://ctftime.org/api/v1/teams/{team_id}/"
    headers = {"User-Agent": "DiscordBot (https://yourwebsite.com, 0.1)"}
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()

        # Extract data safely, avoiding NoneType errors
        return {
            "name": data.get("name", "Unknown Team"),
            "rating": data.get("rating", {}).get("2024", {}).get("rating_points", "N/A"),
            "country": data.get("country", "Unknown"),
            "top_10": data.get("rating", {}).get("2024", {}).get("top_10", "Not Ranked"),
            "international_rank": data.get("rating", {}).get("2024", {}).get("rating_place", "N/A"),
            "national_rank": data.get("rating", {}).get("2024", {}).get("country_place", "N/A"),
            "profile_pic": data.get("logo", "https://ctftime.org/static/images/favicon.png"),  # Default CTFtime logo if none
            "ctftime_url": f"https://ctftime.org/team/{team_id}"
        }
    else:
        return None

# Command handler for !searchteamid <team_id>
@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith("!searchteamid"):
        parts = message.content.split()
        if len(parts) != 2:
            await message.channel.send("❌ Usage: `!searchteamid <team_id>`")
            return

        try:
            team_id = int(parts[1])
        except ValueError:
            await message.channel.send("❌ Please provide a valid team ID (integer).")
            return

        team_data = fetch_ctftime_data(team_id)

        if team_data:
            embed = discord.Embed(
                title=f"CTF Team: {team_data['name']}",
                color=0x00ff00,
                url=team_data["ctftime_url"]
            )
            embed.set_thumbnail(url=team_data["profile_pic"])  # ✅ Show team profile picture
            embed.add_field(name="🌍 Country", value=team_data['country'], inline=True)
            embed.add_field(name="🏆 International Rank", value=team_data['international_rank'], inline=True)
            embed.add_field(name="🇺🇳 National Rank", value=team_data['national_rank'], inline=True)
            embed.add_field(name="⭐ Rating Points", value=team_data['rating'], inline=True)
            embed.add_field(name="🔥 Top 10 Rank", value=team_data['top_10'], inline=True)
            embed.set_footer(text=f"Team ID: {team_id}")

            await message.channel.send(embed=embed)
        else:
            await message.channel.send(f"❌ No team found with ID `{team_id}`.")

# Flask server to keep the bot alive
def keep_alive():
    app = Flask(__name__)

    @app.route("/")
    def home():
        return "Bot is alive!"

    app.run(host="0.0.0.0", port=8080)

# Start Flask server in background thread
t = threading.Thread(target=keep_alive)
t.start()

client.run(TOKEN)
