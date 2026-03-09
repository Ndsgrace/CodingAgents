import os
from dotenv import load_dotenv
import google.generativeai as genai

# 1. Cargar configuración segura
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    print("❌ Error: No se encontró GOOGLE_API_KEY en el archivo .env")
    exit()

# 2. Configurar el SDK de Google
genai.configure(api_key=api_key)

print("--- Diagnóstico de Modelos Gemini ---")
try:
    # 3. Listar modelos disponibles para tu API Key
    available_models = genai.list_models()
    
    print(f"{'Nombre del Modelo':<40} | {'Operaciones Soportadas'}")
    print("-" * 70)
    
    found_pro = False
    for model in available_models:
        # Buscamos específicamente los que permiten generar contenido
        if 'generateContent' in model.supported_generation_methods:
            print(f"{model.name:<40} | OK")
            if "gemini-1.5-pro" in model.name:
                found_pro = True
                
    if not found_pro:
        print("\n⚠️ AVISO: El modelo 'pro' no aparece en tu lista.")
        print("Esto confirma por qué el error 404 persistía.")
    else:
        print("\n✅ El modelo 'pro' está disponible. Copia el nombre exacto de arriba.")

except Exception as e:
    print(f"❌ Error al conectar con la API: {e}")