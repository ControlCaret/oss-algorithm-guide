import os
import json
from typing import List
from dotenv import load_dotenv
from google import genai

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
            tags_str = ", ".join(p.get("tags", []))
            problems_text += f"- ID: {p.get('id')}, 제목: {p.get('title')}, 난이도: {p.get('difficulty')}, 태그: {tags_str}\n"

        assessments_text = ""
        for tag, assess in user_assessments.items():
            pref = "선호" if assess.preference == 1 else "기피" if assess.preference == -1 else "보통"
            sk = "잘함" if assess.skill == 1 else "서툼" if assess.skill == -1 else "보통"
            assessments_text += f"- {tag}: 선호도={pref}, 수준={sk}\n"

        prompt = f"""\
당신은 기술 면접 및 코딩 테스트를 전문적으로 지도하는 알고리즘 멘토입니다.
추천된 LeetCode 문제에 대해 아래 지침을 철저히 준수하여 문제별 분석 결과를 도출해 주세요.

[요구사항 및 분석 규칙]
1. overview (문제 설명):
   - 문제의 핵심 목표와 해결해야 할 주안점을 한글로 명확히 요약해 주세요.
   - 어떤 자료구조나 알고리즘 기법이 핵심이 되는지 명시하세요.
2. reason (추천 사유):
   - 사용자가 등록한 알고리즘 역량 등급(잘함, 서툼, 보통)과 선호도(선호, 기피)를 직접 연관 지어 논리적인 이유를 제시해야 합니다.
   - 예: "이 태그에 대해 다소 서투르다고 조사되었기 때문에, 이 기초 문제를 통해 개념을 다지기 좋습니다."
3. hint (핵심 힌트):
   - 전체 소스 코드를 제공하지 마세요. 대신 문제 해결을 위한 알고리즘적 논리 흐름(의사코드 수준)과 힌트를 제공하세요.
   - 시간 복잡도(Time Complexity)를 줄이기 위한 힌트(예: 투 포인터, 해시 테이블 활용 등)를 언급해 주세요.

[출력 형식 및 제약 조건]
- 반드시 격식 있는 한글 높임말(해요체 또는 하십시오체)로 작성하세요.
- 이모지(Emoji)는 절대로 포함하지 마세요.
- 다른 부가적인 인사말이나 설명 없이, 오직 아래 명시된 JSON 포맷 구조로만 출력해야 합니다.

### 추천 문제 목록:
{problems_text}
### 사용자 알고리즘 성향 조사 정보 (1=선호/잘함, 0=보통, -1=기피/서툼):
{assessments_text}
### JSON 응답 형식 예시:
{{
  "analyses": [
    {{
      "id": 1,
      "overview": "문제 설명 한글 요약",
      "reason": "추천한 구체적인 개인별 이유",
      "hint": "문제를 해결하기 위한 핵심 알고리즘 힌트"
    }}
  ]
}}
"""

        response = await client.aio.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt,
            config={"response_mime_type": "application/json"}
        )
        
        if response.text:
            data = json.loads(response.text)
            return data
        return {"analyses": []}
    except Exception as e:
        print(str(e))
        return {
            "analyses": [
                {
                    "id": 0,
                    "message": "Error occurred",
                    "reason": f"Exception: {str(e)}",
                }
            ]
        }
