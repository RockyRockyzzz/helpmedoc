import os
import json
from openai import OpenAI  # ✅ 최신 버전 전용
from dotenv import load_dotenv
load_dotenv()

# OpenAI 클라이언트 초기화
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))  # 또는 직접 키 입력 가능

# JSON 테스트 파일 경로 (절대경로로 정확히 지정)
json_path = "C:/helpmedoc/tests/dori_prompt_test_script_input.json"

# 파일 열기
with open(json_path, "r", encoding="utf-8") as f:
    test_cases = json.load(f)

# 테스트 반복
for case in test_cases:
    print(f"\n=== Test #{case['id']} | Category: {case['category']} ===")
    print("Input:", case["input"])
    print("Expected:", case["expected"])

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=case["messages"]
        )
        reply = response.choices[0].message.content
        print("AI Response:\n", reply)
    except Exception as e:
        print("❌ Error:", e)

