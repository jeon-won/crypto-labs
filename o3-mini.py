# o3-mini API 사용하려면 Tier 3 이상 되어야 함... 😭
# (100달러 결제 후 7일 경과 시 Tier 3 되는 듯)

from openai import OpenAI
import os

OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')

client = OpenAI(api_key=OPENAI_API_KEY)

response = client.chat.completions.create(
    model="o3-mini",
    messages=[
        {"role": "system", "content": "당신은 STEM 주제에 특화된 유용한 조수입니다."},
        {"role": "user", "content": "이 미적분 문제를 해결하세요: f(x) = x2sin(x)의 도함수를 찾으세요."}
    ],
    reasoning_effort="medium"  # 옵션: "low", "medium", "high"
)

print(response.choices[0].message.content)