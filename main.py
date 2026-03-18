import discord
import requests
import os

TOKEN = os.getenv("DISCORD_TOKEN")
DOC_URL = os.getenv("DOC_URL")

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

def get_doc_text():
    try:
        response = requests.get(DOC_URL)
        return response.text.lower()
    except:
        return ""

def find_answer(question, doc):
    question = question.lower()

    # Example keyword logic (expand this yourself)
    if "currency" in question or "money" in question:
        if "currency" in doc or "earn" in doc:
            return (
                "💰 **How to earn currency:**\n\n"
                "- Play the game normally\n"
                "- Complete tasks or objectives\n"
                "- Trade or collect resources\n\n"
                "👉 Check the game systems in the guide for more detailed methods."
            )

    if "rules" in question:
        return "📜 Please follow the server rules listed in the guide."

    if "discord" in question:
        return "💬 This Discord is for helping players and community discussion."

    # fallback (smart-ish)
    for line in doc.split("\n"):
        if any(word in line for word in question.split()):
            return f"🧠 {line.strip()}"

    return "❌ I couldn't find that in the guide. Try asking differently!"

@client.event
async def on_ready():
    print(f"✅ Logged in as {client.user}")

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    # Only respond when pinged
    if client.user in message.mentions:
        doc_text = get_doc_text()

        # Remove mention from message
        question = message.content.replace(f"<@{client.user.id}>", "").strip()

        if not question:
            await message.channel.send("Ask me something after mentioning me!")
            return

        answer = find_answer(question, doc_text)
        await message.channel.send(answer)

client.run(TOKEN)
