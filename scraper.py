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
        # Fallback to local session file if exists, but warn
        print("ℹ️ Using local 'session_name' for Telegram. This will NOT work on Railway without TELEGRAM_SESSION_STRING.")
        client = TelegramClient('session_name', config.TELEGRAM_API_ID, config.TELEGRAM_API_HASH)
    
    try:
        # We use start() with no phone if session string is provided
        # If no session string, it will try interactive login, which we want to catch
        if config.TELEGRAM_SESSION_STRING:
            await client.start()
        else:
            # If no session string and not in a terminal, this will likely fail with EOFError
            await client.start(phone=config.TELEGRAM_PHONE)
    except EOFError:
        raise ValueError("❌ Telegram login failed: 'EOF when reading a line'.\n"
                         "Bu xatolik bot serverga (masalan Railway) yuklanganda yuz beradi.\n"
                         "Iltimos, local kompyuteringizda 'generate_session.py' ni ishga tushiring va SESSION_STRING ni oling.")
    except Exception as e:
        raise Exception(f"Telegram client start failed: {str(e)}")

    async with client:

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
