import os
from google import genai
from google.genai import types

client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
try:
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents="Hello",
    )
    print("Success:", response.text)
except Exception as e:
    print("Error:", e)
