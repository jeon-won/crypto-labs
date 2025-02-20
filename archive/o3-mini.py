# o3-mini API 사용하려고 Tier 3가 됐는데 'The model `o3-mini` does not exist or you do not have access to it.' 오류가 발생함... 😭
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