import discord
import requests
import os
from openai import OpenAI

# ENV VARIABLES
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
DOC_URL = os.getenv("DOC_URL")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# OpenAI client
ai = OpenAI(api_key=OPENAI_API_KEY)

# Discord setup
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

# Cache doc (faster + cheaper)
DOC_CACHE = ""

def get_doc_text():
    try:
        response = requests.get(DOC_URL)
        return response.text[:4000]  # limit size (IMPORTANT)
    except:
        return ""

def ask_ai(question, doc):
    try:
        response = ai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant. Answer clearly using the provided guide. Keep answers clean and structured."
                },
                {
                    "role": "user",
                    "content": f"Guide:\n{doc}\n\nQuestion: {question}"
                }
            ],
            max_tokens=250
        )

        return response.choices[0].message.content.strip()

    except Exception as e:
        return "⚠️ AI error. Check API key or usage."

@client.event
async def on_ready():
    global DOC_CACHE
    DOC_CACHE = get_doc_text()
    print(f"✅ Logged in as {client.user}")

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if client.user in message.mentions:
        question = message.content.replace(f"<@{client.user.id}>", "").strip()

        if not question:
            await message.reply("Ask me something after mentioning me!")
            return

        answer = ask_ai(question, DOC_CACHE)

        await message.reply(answer)

client.run(DISCORD_TOKEN)
