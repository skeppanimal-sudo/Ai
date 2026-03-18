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


# 🧠 Clean smart answer
def find_answer(question, doc):
    question = question.lower()

    parts = doc.split("====================================================")

    sections = []

    # Combine title + content
    for i in range(1, len(parts) - 1, 2):
        title = parts[i].strip()
        content = parts[i + 1].strip()
        sections.append((title, content))

    best_section = None
    best_score = 0

    for title, content in sections:
        section_text = (title + " " + content).lower()

        if "[identity]" in section_text or "[important rules]" in section_text:
            continue

        score = 0
        for word in question.split():
            if word in section_text:
                score += 1

        if score > best_score:
            best_score = score
            best_section = content

    if best_section and best_score > 0:
        lines = best_section.split("\n")

        clean_lines = []

        for line in lines:
            line = line.strip()

            # Skip useless lines
            if not line:
                continue
            if line.lower().startswith("you earn"):
                continue

            # Format bullet points
            if line.startswith("-"):
                clean_lines.append(f"• {line[1:].strip()}")
            else:
                clean_lines.append(line)

        return "\n".join(clean_lines[:10])

    return "I couldn't find that in the guide. Try asking differently."


@client.event
async def on_ready():
    print(f"✅ Logged in as {client.user}")


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if client.user in message.mentions:
        doc_text = get_doc_text()

        question = message.content.replace(f"<@{client.user.id}>", "").strip()

        if not question:
            await message.channel.send("Ask me something after mentioning me!")
            return

        answer = find_answer(question, doc_text)
        await message.channel.send(answer)


client.run(TOKEN)
