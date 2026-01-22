# test_models.py
import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("❌ Error: No se encontró GEMINI_API_KEY en el archivo .env")
    exit()

print(f"🔑 Usando API Key: {api_key[:5]}...{api_key[-4:]}")

try:
    genai.configure(api_key=api_key)
    print("✅ Conectado a Gemini. Listando modelos disponibles para 'generateContent':")
    print("-" * 50)
    
    found_any = False
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f"👉 {m.name}")
            found_any = True
            
    if not found_any:
        print("⚠️ No se encontraron modelos que soporten 'generateContent'.")
        
except Exception as e:
    print(f"❌ Error fatal: {e}")