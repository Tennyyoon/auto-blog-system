import os
import json
from datetime import datetime
from docx import Document
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# =========================
# 1️⃣ 30개 SEO 주제 리스트
# =========================
topics = [
"뉴질랜드 vs 호주 물가 체감 차이 현실 비교",
"해외생활 1년 차에 가장 많이 무너지는 순간",
"워홀 초반 3개월 돈이 줄줄 새는 이유",
"뉴질랜드 한 달 실제 생활비 공개",
"호주 워홀 시급 높은데 돈이 안 모이는 이유",
"해외에서 돈 모으는 사람들의 공통점",
"뉴질랜드에서 오래 남는 사람들의 특징",
"호주 워홀 중 가장 많이 후회하는 선택",
"해외에서 외로움이 가장 심해지는 시기",
"뉴질랜드 플랫메이트 갈등 현실",
"호주 쉐어하우스 계약 전 체크리스트",
"해외에서 친구 만드는 현실적인 방법",
"뉴질랜드 이민이 생각보다 어려운 이유",
"호주 영주권 목표라면 워홀 때 해야 할 준비",
"해외이민 실패하는 사람들의 공통 실수",
"뉴질랜드에서 한국 경력이 인정되는 직업",
"호주에서 빠르게 돈 모으는 직종",
"워홀러가 피해야 할 일자리 유형",
"뉴질랜드 차 없이 살기 좋은 도시",
"호주 병원비 실제 비용 경험 정리",
"해외생활 짐 싸기 전 버려야 할 물건",
"뉴질랜드 겨울 생존 팁",
"호주 여름 자외선 현실",
"워홀 중 한국 돌아가고 싶어지는 순간",
"해외 연애 현실 분석",
"뉴질랜드·호주 세금 환급 현실",
"해외 사기 패턴 정리",
"워홀 이후 가장 많이 선택하는 진로",
"한국과 뉴질랜드·호주의 가장 큰 차이",
"해외생활에서 남는 사람과 돌아오는 사람의 차이"
]

# =========================
# 2️⃣ 진행 저장 파일
# =========================
progress_file = "progress.json"

if os.path.exists(progress_file):
    with open(progress_file, "r") as f:
        progress = json.load(f)
else:
    progress = {"index": 0}

start_index = progress["index"]
end_index = start_index + 3

# =========================
# 3️⃣ SEO 프롬프트 생성 함수
# =========================
def generate_post(topic):

    prompt = f"""
    너는 네이버 SEO 전문 블로그 작가다.

    주제: {topic}

    반드시 아래 조건을 모두 지켜라.

    [검색 의도 반영]
    - 뉴질랜드 워홀
    - 호주 워킹홀리데이
    - 해외생활 적응
    - 해외생활 현실

    [작성 조건]
    1. 1500~1800자
    2. 클릭률 높은 제목 1개
    3. 도입부에 핵심 키워드 자연 삽입
    4. 소제목 3개 이상 (## 형식)
    5. 소제목에도 키워드 포함
    6. 체크리스트 또는 리스트 포함
    7. 해결 방법은 실전형으로 작성
    8. 감성 30% + 정보 70%
    9. 이미지 위치 표시 [이미지1], [이미지2]
    10. 결론에 행동 유도 문장 포함

    광고 느낌 없이 경험 기반 톤으로 작성해라.
    """

    response = client.responses.create(
        model="gpt-4o-mini",
        input=prompt
    )

    return response.output_text

# =========================
# 4️⃣ 글 생성 실행
# =========================
today = datetime.now().strftime("%Y-%m-%d")

for i in range(start_index, min(end_index, len(topics))):

    topic = topics[i]
    content = generate_post(topic)

    document = Document()

    for line in content.split("\n"):
        document.add_paragraph(line)

    safe_title = topic.replace(" ", "_")
    file_name = f"{today}_{i+1}_{safe_title}.docx"

    document.save(file_name)

    print(f"생성 완료: {file_name}")

# =========================
# 5️⃣ 다음 진행 저장
# =========================
progress["index"] = end_index
with open(progress_file, "w") as f:
    json.dump(progress, f)
