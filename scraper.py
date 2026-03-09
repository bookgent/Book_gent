import asyncio
from telethon import TelegramClient
from telethon.sessions import StringSession
from config import config

async def scrape_channel(channel_link, limit=None):
    """
    Scrapes text messages from a public Telegram channel.
    """
    # Clean up the channel link in case of typos
    channel_link = channel_link.strip().replace("https://https://", "https://")
    
    if config.TELEGRAM_SESSION_STRING:
        client = TelegramClient(StringSession(config.TELEGRAM_SESSION_STRING), config.TELEGRAM_API_ID, config.TELEGRAM_API_HASH)
    else:
        client = TelegramClient('session_name', config.TELEGRAM_API_ID, config.TELEGRAM_API_HASH)
    
    async with client:
        # start() handles the login flow interactively if needed
        # If using StringSession, it will just use the provided string.
        await client.start(phone=config.TELEGRAM_PHONE)

        channel = await client.get_entity(channel_link)
        messages = []
        
        print(f"Fetching messages from {channel_link}...")
        async for message in client.iter_messages(channel, limit=limit, reverse=True):
            if message.text:
                # Store message text and date
                messages.append({
                    "date": message.date.isoformat(),
                    "text": message.text
                })
        
        return messages

if __name__ == "__main__":
    # Test snippet
    import json
    channel = input("Enter channel link: ")
    loop = asyncio.get_event_loop()
    results = loop.run_until_complete(scrape_channel(channel, limit=10))
    print(json.dumps(results, indent=2))
