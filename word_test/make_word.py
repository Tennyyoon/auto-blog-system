import json
import os
from datetime import datetime
from pathlib import Path

from docx import Document
from openai import OpenAI

BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "generated_posts"
PROGRESS_FILE = BASE_DIR / "progress.json"
PROMPT_TEMPLATE_FILE = BASE_DIR / "prompt_template.txt"

OUTPUT_DIR.mkdir(exist_ok=True)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# 30개 SEO 주제
TOPICS = [
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
    "해외생활에서 남는 사람과 돌아오는 사람의 차이",
]

PROMPT_TEMPLATE = """너는 네이버 SEO 전문 블로그 작가다.

[주제]
{topic}

[핵심 키워드]
- 뉴질랜드 워홀
- 호주 워킹홀리데이
- 해외생활 적응
- 해외생활 현실

[작성 규칙]
1) 전체 글자 수는 공백 포함 1200~1500자 (절대 1500자 초과 금지)
2) 첫 줄은 클릭률 높은 제목 1개
3) 도입부 3문장 안에 핵심 키워드 2개 이상 자연 삽입
4) ## 소제목 3개 이상
5) 소제목에도 키워드 자연 삽입
6) 체크리스트 또는 번호 리스트 1개 이상 포함
7) 해결 방법은 실제 실행 가능한 단계로 작성
8) 톤: 경험 기반, 감성 30% + 정보 70%
9) 이미지 삽입 위치를 [이미지1], [이미지2]로 표시
10) 마지막 문단은 행동 유도 문장(댓글/공유/저장)으로 마무리
11) 과장/허위/광고 문구 금지

출력은 마크다운으로만 작성해라.
"""


def load_progress() -> dict:
    if PROGRESS_FILE.exists():
        return json.loads(PROGRESS_FILE.read_text(encoding="utf-8"))
    return {"index": 0}


def save_progress(progress: dict) -> None:
    PROGRESS_FILE.write_text(
        json.dumps(progress, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def call_model(prompt: str) -> str:
    response = client.responses.create(model="gpt-4o-mini", input=prompt)
    return response.output_text.strip()


def count_chars(text: str) -> int:
    return len(text)


def trim_to_1500(topic: str, content: str) -> str:
    if count_chars(content) <= 1500:
        return content

    shorten_prompt = f"""다음 원고를 1500자 이하로 줄여라.

[주제] {topic}
[유지할 것]
- 제목 1개
- ## 소제목 3개 이상
- [이미지1], [이미지2]
- 체크리스트/리스트 1개
- 행동 유도 문장

[원고]
{content}

1500자 이하의 마크다운 최종본만 출력해라.
"""
    shortened = call_model(shorten_prompt)

    if count_chars(shortened) <= 1500:
        return shortened

    return shortened[:1490] + "\n\n(이하 생략)"


def save_as_docx(content: str, output_path: Path) -> None:
    document = Document()
    for line in content.split("\n"):
        document.add_paragraph(line)
    document.save(output_path)


def main() -> None:
    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError("OPENAI_API_KEY 환경변수가 필요합니다.")

    # 자동완성에 재활용 가능한 프롬프트 템플릿 파일
    PROMPT_TEMPLATE_FILE.write_text(PROMPT_TEMPLATE, encoding="utf-8")

    progress = load_progress()
    start_index = progress.get("index", 0)
    batch_size = 3
    end_index = min(start_index + batch_size, len(TOPICS))

    today = datetime.now().strftime("%Y-%m-%d")

    for i in range(start_index, end_index):
        topic = TOPICS[i]
        prompt = PROMPT_TEMPLATE.format(topic=topic)
        content = call_model(prompt)
        content = trim_to_1500(topic, content)

        safe_title = topic.replace(" ", "_")
        markdown_file = OUTPUT_DIR / f"{today}_{i+1}_{safe_title}.md"
        docx_file = OUTPUT_DIR / f"{today}_{i+1}_{safe_title}.docx"

        markdown_file.write_text(content, encoding="utf-8")
        save_as_docx(content, docx_file)

        print(f"생성 완료: {markdown_file.name} ({count_chars(content)}자)")

    progress["index"] = 0 if end_index >= len(TOPICS) else end_index
    save_progress(progress)


if __name__ == "__main__":
    main()
