import httpx
from google import genai
from config import config


_client = None

def get_gemini_client():
    global _client
    if _client is None:
        if not config.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY is not set in config.")
        _client = genai.Client(api_key=config.GEMINI_API_KEY)
    return _client

async def generate_with_failover(prompt, model_name='gemini-flash-latest'):
    """
    Tries Gemini first, then falls back to OpenRouter (GPT-4o-mini/GPT-4o).
    """
    try:
        # 1. Try Gemini
        print(f"Trying Gemini ({model_name})...")
        client = get_gemini_client()
        response = client.models.generate_content(
            model=model_name,
            contents=prompt
        )
        return response.text
    except Exception as e:
        print(f"Gemini failed: {e}. Falling back to OpenRouter...")
        
        # 2. Try OpenRouter (GPT-4o-mini as a robust fallback)
        try:
            async with httpx.AsyncClient() as http_client:
                url = "https://openrouter.ai/api/v1/chat/completions"
                headers = {
                    "Authorization": f"Bearer {config.OPENROUTER_API_KEY}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "https://github.com/google-gemini/antigravity", # Optional
                    "X-Title": "Telegram-to-Book Bot"
                }
                payload = {
                    "model": "openai/gpt-4o-mini",
                    "messages": [
                        {"role": "user", "content": prompt}
                    ]
                }
                response = await http_client.post(url, headers=headers, json=payload, timeout=60.0)
                response.raise_for_status()
                result = response.json()
                return result['choices'][0]['message']['content']
        except Exception as o_e:
            print(f"OpenRouter also failed: {o_e}")
            raise Exception("Ikkala AI xizmati ham (Gemini va OpenRouter) ishlamayapti. Iltimos keyinroq urinib ko'ring.")

def process_content(raw_posts, mode="book", plan="Starter"):
    """
    Processes raw Telegram posts for book or cheatsheet with plan-specific depth.
    This is now just a wrapper for the prompt preparation.
    """
    # Sort posts chronologically
    sorted_posts = sorted(raw_posts, key=lambda x: x['date'])
    content_str = "\n---\n".join([f"Date: {p['date']}\nContent: {p['text']}" for p in sorted_posts])
    
    # Adjust depth/detail instruction based on plan
    depth_instr = {
        "Starter": "Sodda va qisqa tahlil qiling.",
        "Pro": "Batafsil va chuqurroq tahlil qiling, har bir mavzuni yaxshi yoritib bering.",
        "Max": "Professional va juda batafsil tahlil qiling. Eng yuqori sifatli kitob darajasida yozing."
    }.get(plan, "Sodda tahlil.")

    if mode == "cheatsheet":
        prompt = f"""
        Telegram kanalidan olingan xomaki postlarni "Cheatsheet" holatiga keltiring.
        Reja darajasi: {plan}. {depth_instr}

        Ko'rsatmalar:
        1. TO'LIQ O'ZBEK TILIDA yozing.
        2. Bullet points va mantiqiy sarlavhalardan foydalaning.
        3. Markdown formatida qaytaring.

        Xomaki postlar:
        {content_str}

        Yakuniy Cheatsheet (O'zbek tilida, Markdown formatida):
        """
    else:
        prompt = f"""
        Telegram kanalidan olingan postlarni professional kitob holatiga keltiring.
        Reja darajasi: {plan}. {depth_instr}
        
        Ko'rsatmalar:
        1. TO'LIQ O'ZBEK TILIDA yozing.
        2. Boblarga ajrating, Kirish va Xulosa qo'shing.
        3. Spam va reklamalarni olib tashlang.
        4. Markdown formatida qaytaring.
        
        Xomaki postlar:
        {content_str}
        
        Yakuniy kitob (O'zbek tilida, Markdown formatida):
        """
    
    return prompt

if __name__ == "__main__":
    # Test snippet
    dummy_posts = [
        {"date": "2023-01-01", "text": "Welcome to our channel about AI!"},
        {"date": "2023-01-02", "text": "AI is changing the world. Here is how..."},
        {"date": "2023-01-03", "text": "Buy crypto now! [SPAM]"},
        {"date": "2023-01-04", "text": "Conclusion: AI is here to stay."}
    ]
    print(process_content(dummy_posts))
