import asyncio
from telethon import TelegramClient
from telethon.sessions import StringSession

async def main():
    print("--- Telethon Session String Generator ---")
    print("This script will help you generate a session string to use on Railway.")
    
    api_id = input("Enter your API ID: ")
    api_hash = input("Enter your API Hash: ")
    phone = input("Enter your Phone Number (with +): ")
    
    client = TelegramClient(StringSession(), int(api_id), api_hash)
    
    await client.start(phone=phone)
    
    session_string = client.session.save()
    
    print("\n" + "="*50)
    print("YOUR SESSION STRING (Copy everything below):")
    print("="*50)
    print(session_string)
    print("="*50)
    print("\nIMPORTANT: Keep this string secret! Add it to Railway as TELEGRAM_SESSION_STRING.")
    
    await client.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
