import discord
import requests
import os
import time

# ===== CONFIG =====
TOKEN = os.getenv("DISCORD_TOKEN")
DOC_URL = os.getenv("DOC_URL")

# ===== DISCORD SETUP =====
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

# ===== CACHE SYSTEM =====
brain_cache = ""
last_fetch = 0

def load_brain():
    global brain_cache, last_fetch

    # Refresh every 60 seconds
    if time.time() - last_fetch > 60:
        try:
            response = requests.get(DOC_URL)
            brain_cache = response.text
            last_fetch = time.time()
        except:
            return "Error loading knowledge base."

    return brain_cache

# ===== CLEAN MENTION =====
def clean_mention(message, bot):
    content = message.content
    content = content.replace(f"<@{bot.user.id}>", "")
    content = content.replace(f"<@!{bot.user.id}>", "")
    return content.strip()

# ===== SMART SEARCH =====
def find_best_match(question, brain):
    # Split into sections using your doc separators
    chunks = brain.split("====================================================")

    question_words = question.lower().split()
    best_chunk = ""
    best_score = 0

    for chunk in chunks:
        chunk_lower = chunk.lower()
        score = sum(word in chunk_lower for word in question_words)

        if score > best_score:
            best_score = score
            best_chunk = chunk

    return best_chunk.strip()

# ===== FORMAT RESPONSE =====
def format_answer(answer):
    # Clean up long messy chunks
    answer = answer.strip()

    if len(answer) > 1500:
        answer = answer[:1500] + "\n...\n(Truncated)"

    return f"🧠 {answer}"

# ===== EVENTS =====
@client.event
async def on_ready():
    print(f"Bot is online as {client.user}")

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    # Only respond if bot is mentioned
    if client.user in message.mentions:
        question = clean_mention(message, client)

        if not question:
            await message.reply("Ask me something!")
            return

        async with message.channel.typing():
            brain = load_brain()
            answer = find_best_match(question, brain)

        if answer:
            await message.reply(format_answer(answer))
        else:
            await message.reply("I don't know that yet.")

# ===== RUN =====
client.run(TOKEN)
