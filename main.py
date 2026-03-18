import discord
import requests
import os

TOKEN = os.getenv("DISCORD_TOKEN")
DOC_URL = os.getenv("DOC_URL")

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)


# 📄 Get Google Doc text
def get_doc_text():
    try:
        response = requests.get(DOC_URL)
        return response.text
    except:
        return ""


# 🧠 Smart section-based answering
def find_answer(question, doc):
    question = question.lower()

    # Split into sections
    sections = doc.split("====================================================")

    best_section = None
    best_score = 0

    for section in sections:
        section_lower = section.lower()

        # ❌ Skip useless sections
        if "[identity]" in section_lower or "[important rules]" in section_lower:
            continue

        score = 0
        for word in question.split():
            if word in section_lower:
                score += 1

        if score > best_score:
            best_score = score
            best_section = section

    if best_section and best_score > 0:
        return "🧠 **Answer:**\n\n" + best_section.strip()[:1500]

    return "❌ I couldn't find that in the guide. Try asking differently!"


@client.event
async def on_ready():
    print(f"✅ Logged in as {client.user}")


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    # Only respond if bot is mentioned
    if client.user in message.mentions:
        doc_text = get_doc_text()

        # Remove mention
        question = message.content.replace(f"<@{client.user.id}>", "").strip()

        if not question:
            await message.channel.send("Ask me something after mentioning me!")
            return

        answer = find_answer(question, doc_text)
        await message.channel.send(answer)


client.run(TOKEN)
