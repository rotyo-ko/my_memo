from google import genai
from django.conf import settings


client = genai.Client(api_key=settings.GEMINI_API_KEY)

def summarize(text: str) -> str:
    try:
        response = client.models.generate_content(
            model="gemini-3-flash-preview",
            contents="次の文章を日本語で、3〜5行程度に要約してください:\n\n"
            f"{text}",
        )
        if not response.text:
            raise ValueError("Empty response from Gemini")
    
        return response.text.strip()
    
    except Exception as e:
        print("Gemini summarize failed")
        return "要約の生成に失敗しました。"