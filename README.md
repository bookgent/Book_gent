# Telegram to Book Pipeline

This project scrapes public Telegram channels, processes the content using Gemini AI (1.5 Flash), and compiles a well-formatted book in Markdown and PDF formats.

## Prerequisites

- Python 3.8+
- [Telegram API ID and Hash](https://my.telegram.org)
- [Gemini API Key](https://aistudio.google.com/)

## Installation

1. **Clone the repository** (or just use the files provided).
2. **Create a virtual environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Configuration

1. Create a `.env` file in the root directory (copy from `.env.example`).
2. Fill in your credentials:
   ```env
   TELEGRAM_API_ID=your_id
   TELEGRAM_API_HASH=your_hash
   TELEGRAM_PHONE=your_phone
   GEMINI_API_KEY=your_key
   ```

## Usage

Run the main script:
```bash
python main.py
```

Follow the prompts:
1. Enter the public Telegram channel link (e.g., `https://t.me/example`).
2. If it's your first time, Telethon will ask for a login code sent to your Telegram.
3. Wait for the processing to finish.
4. Your book will be saved as `output_book.md` and `output_book.pdf`.

## Project Structure

- `main.py`: Orchestrates the whole flow.
- `scraper.py`: Fetches messages from Telegram using Telethon.
- `processor.py`: Cleans and formats content using Gemini.
- `generator.py`: Exports content to MD and PDF.
- `config.py`: Handles environment variables.
