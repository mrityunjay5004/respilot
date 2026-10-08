import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

def get_llm_client():
    provider = os.getenv("LLM_PROVIDER", "openai").lower()
    
    if provider == "groq":
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY environment variable is missing.")
        client = OpenAI(
            base_url="https://api.groq.com/openai/v1",
            api_key=api_key
        )
        model = os.getenv("MODEL_NAME", "qwen/qwen3.8-27b")
    else:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is missing.")
        client = OpenAI(api_key=api_key)
        model = os.getenv("MODEL_NAME", "gpt-4o-mini")
        
    return client, model

import time

def call_llm(prompt: str, system_prompt: str = "You are a helpful assistant.", json_mode: bool = False) -> str:
    client, model = get_llm_client()
    
    # Use smaller max_tokens for JSON mode to avoid hitting the 1000 OTPM free tier limit quickly
    max_tokens = 400 if json_mode else 600
    
    kwargs = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.2,
        "max_tokens": max_tokens
    }
    
    if json_mode and "groq" not in str(client.base_url).lower():
        kwargs["response_format"] = {"type": "json_object"}
        
    for attempt in range(3):
        try:
            response = client.chat.completions.create(**kwargs)
            return response.choices[0].message.content
        except Exception as e:
            if "429" in str(e) or "rate_limit_exceeded" in str(e):
                if attempt < 2:
                    time.sleep(20) # wait 20 seconds for token bucket to refill
                    continue
            raise e

def call_llm_json(prompt: str, system_prompt: str = "You are a helpful assistant. Respond in JSON.", schema: dict = None) -> dict:
    content = call_llm(prompt, system_prompt, json_mode=True)
    try:
        # Strip markdown json block if present
        if content.startswith("```json"):
            content = content[7:-3].strip()
        elif content.startswith("```"):
            content = content[3:-3].strip()
            
        return json.loads(content)
    except json.JSONDecodeError as e:
        raise ValueError(f"LLM failed to return valid JSON: {e}\nContent: {content}")
