import os
import json
from typing import List
from dotenv import load_dotenv
from google import genai
from fastapi import HTTPException

current_dir = os.path.dirname(os.path.abspath(__file__))
dotenv_path = os.path.join(current_dir, ".env")
load_dotenv(dotenv_path)

async def generate_feedback(recommended_problems: List[dict], user_assessments: dict) -> dict:
    load_dotenv(dotenv_path, override=True)
    current_key = os.environ.get("GEMINI_API_KEY")
    if not current_key or current_key == "YOUR_GEMINI_API_KEY_HERE":
        return {"analyses": []}

    try:
        client = genai.Client(api_key=current_key)
        
        problems_text = ""
        for p in recommended_problems:
            tags_str = ",".join(p.get("tags", []))
            problems_text += f"ID:{p.get('id')}|{p.get('title')}|{p.get('difficulty')}|{tags_str}\n"

        assessments_text = ""
        for tag, assess in user_assessments.items():
            pref = "선호" if assess.preference == 1 else "기피" if assess.preference == -1 else "보통"
            sk = "전문" if assess.skill == 1 else "입문" if assess.skill == -1 else "숙련"
            assessments_text += f"{tag}:선호={pref},수준={sk}\n"

        prompt = f"""\
당신은 알고리즘 멘토입니다. 아래 문제에 대해 JSON 포맷으로만 답변하세요.
이모지 없이, 격식 있는 한글 높임말로 명확히 작성하세요.

[분석 지침]
1. overview: 문제 목표와 핵심 알고리즘/자료구조 요약.
2. reason: 사용자 수준(입문/숙련/전문) 및 선호도(선호/기피/보통)와 연계한 추천 사유.
3. hint: 소스코드 없이 논리 흐름 및 시간복잡도(Time Complexity) 최적화 힌트 제공.

[추천 문제 목록 (ID|제목|난이도|태그)]
{problems_text}
[사용자 성향 정보]
{assessments_text}
[응답 JSON 형식]
{{
  "analyses": [
    {{
      "id": 1,
      "overview": "요약",
      "reason": "사유",
      "hint": "힌트"
    }}
  ]
}}
"""

        response = await client.aio.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config={"response_mime_type": "application/json"}
        )
        
        if response.text:
            data = json.loads(response.text)
            return data
        return {"analyses": []}
    except Exception as e:
        print(f"Gemini API Error: {str(e)}")
        err_msg = str(e)
        if "RESOURCE_EXHAUSTED" in err_msg or "429" in err_msg:
            raise HTTPException(status_code=429, detail="Quota Exceeded")
        raise HTTPException(status_code=500, detail="API Error")
