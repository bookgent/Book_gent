import asyncio
import sys
from config import config
from scraper import scrape_channel
from processor import process_content
from generator import save_markdown, generate_pdf

async def main():
    try:
        # Validate config
        config.validate()
        
        channel_link = input("Enter the public Telegram channel link (e.g., https://t.me/example): ")
        if not channel_link:
            print("Channel link is required.")
            return

        # 1. Scrape
        print("Step 1: Scraping Telegram channel (fetching last 400 messages)...")
        raw_posts = await scrape_channel(channel_link, limit=400)
        if not raw_posts:
            print("No messages found.")
            return
        
        # 2. Process
        print("Step 2: Processing content with Gemini...")
        book_md = process_content(raw_posts)
        
        # 3. Generate
        print("Step 3: Generating output files...")
        save_markdown(book_md, "output_book.md")
        generate_pdf(book_md, "output_book.pdf")
        
        print("\nSuccess! Your book is ready in 'output_book.md' and 'output_book.pdf'.")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    asyncio.run(main())
