import re
from dataclasses import dataclass, asdict
from typing import Optional
from urllib.parse import quote_plus

import requests
from bs4 import BeautifulSoup
from flask import Flask, jsonify, render_template, request
from pytrends.request import TrendReq

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/122.0.0.0 Safari/537.36"
)

app = Flask(__name__)


@dataclass
class PlatformResult:
    platform: str
    keyword: str
    trend_score: Optional[int]
    indexed_posts: Optional[int]
    raw_note: str


@dataclass
class AnalysisResponse:
    keyword: str
    google: PlatformResult
    naver: PlatformResult
    daum: PlatformResult


def parse_number(text: str) -> Optional[int]:
    if not text:
        return None
    numbers = re.findall(r"\d[\d,]*", text)
    if not numbers:
        return None
    return int(numbers[0].replace(",", ""))


def fetch_html(url: str) -> str:
    headers = {"User-Agent": USER_AGENT}
    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()
    return response.text


def google_trend_score(keyword: str) -> Optional[int]:
    """Google Trends 상대 점수(0~100)를 가져온다."""
    try:
        pytrends = TrendReq(hl="ko", tz=540)
        pytrends.build_payload([keyword], timeframe="today 3-m", geo="KR")
        data = pytrends.interest_over_time()
        if data.empty:
            return None
        score = int(data[keyword].iloc[-1])
        return score
    except Exception:
        return None


def google_indexed_posts(keyword: str) -> tuple[Optional[int], str]:
    try:
        html = fetch_html(f"https://www.google.com/search?q={quote_plus(keyword)}")
        soup = BeautifulSoup(html, "html.parser")
        stats = soup.select_one("#result-stats")
        if not stats:
            return None, "Google 결과 수 파싱 실패"
        count = parse_number(stats.get_text(" ", strip=True))
        return count, stats.get_text(" ", strip=True)
    except Exception as error:
        return None, f"Google 요청 실패: {error}"


def naver_indexed_posts(keyword: str) -> tuple[Optional[int], str]:
    try:
        html = fetch_html(
            f"https://search.naver.com/search.naver?where=nexearch&query={quote_plus(keyword)}"
        )
        soup = BeautifulSoup(html, "html.parser")
        source_text = soup.get_text(" ", strip=True)

        # 예: "약 1,234건"
        match = re.search(r"약\s*([\d,]+)\s*건", source_text)
        if not match:
            return None, "Naver 결과 수 파싱 실패"
        count = int(match.group(1).replace(",", ""))
        return count, f"약 {match.group(1)}건"
    except Exception as error:
        return None, f"Naver 요청 실패: {error}"


def naver_trend_proxy(keyword: str) -> tuple[Optional[int], str]:
    """자동완성 결과 개수를 간이 인기 점수(0~100)로 환산."""
    try:
        url = (
            "https://ac.search.naver.com/nx/ac?"
            f"q={quote_plus(keyword)}&con=0&frm=nv&ans=2&r_format=json"
            "&r_enc=UTF-8&r_unicode=0&t_koreng=1&run=2"
        )
        headers = {"User-Agent": USER_AGENT, "Referer": "https://www.naver.com/"}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        items = data.get("items", [])
        suggestion_count = len(items[0]) if items else 0
        score = min(100, suggestion_count * 10)
        return score, f"자동완성 {suggestion_count}개"
    except Exception as error:
        return None, f"Naver 자동완성 요청 실패: {error}"


def daum_indexed_posts(keyword: str) -> tuple[Optional[int], str]:
    try:
        html = fetch_html(f"https://search.daum.net/search?w=tot&q={quote_plus(keyword)}")
        soup = BeautifulSoup(html, "html.parser")
        source_text = soup.get_text(" ", strip=True)

        # 예: "약 12,345건"
        match = re.search(r"약\s*([\d,]+)건", source_text)
        if not match:
            return None, "Daum 결과 수 파싱 실패"
        count = int(match.group(1).replace(",", ""))
        return count, f"약 {match.group(1)}건"
    except Exception as error:
        return None, f"Daum 요청 실패: {error}"


def daum_trend_proxy(keyword: str) -> tuple[Optional[int], str]:
    """Daum 자동완성 API의 제안 개수를 간이 점수로 환산."""
    try:
        url = f"https://suggest.daum.net/suggest?mod=www&code=utf_in_out&q={quote_plus(keyword)}"
        headers = {"User-Agent": USER_AGENT, "Referer": "https://www.daum.net/"}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        text = response.text

        # callback([...]) 내부에서 ,"..." 패턴의 제안을 대략 카운트
        suggestions = re.findall(r'"([^"]+)"', text)
        suggestion_count = max(0, len(suggestions) - 2)
        score = min(100, suggestion_count * 8)
        return score, f"자동완성 추정 {suggestion_count}개"
    except Exception as error:
        return None, f"Daum 자동완성 요청 실패: {error}"


def analyze_keyword(keyword: str) -> AnalysisResponse:
    g_posts, g_note = google_indexed_posts(keyword)
    n_posts, n_note = naver_indexed_posts(keyword)
    d_posts, d_note = daum_indexed_posts(keyword)

    g_score = google_trend_score(keyword)
    n_score, n_extra = naver_trend_proxy(keyword)
    d_score, d_extra = daum_trend_proxy(keyword)

    google = PlatformResult(
        platform="Google",
        keyword=keyword,
        trend_score=g_score,
        indexed_posts=g_posts,
        raw_note=g_note,
    )
    naver = PlatformResult(
        platform="Naver",
        keyword=keyword,
        trend_score=n_score,
        indexed_posts=n_posts,
        raw_note=f"{n_note} / {n_extra}",
    )
    daum = PlatformResult(
        platform="Daum",
        keyword=keyword,
        trend_score=d_score,
        indexed_posts=d_posts,
        raw_note=f"{d_note} / {d_extra}",
    )

    return AnalysisResponse(keyword=keyword, google=google, naver=naver, daum=daum)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/analyze")
def api_analyze():
    keyword = request.args.get("keyword", "").strip()
    if not keyword:
        return jsonify({"error": "keyword query parameter is required"}), 400

    result = analyze_keyword(keyword)
    return jsonify(
        {
            "keyword": result.keyword,
            "results": [
                asdict(result.google),
                asdict(result.naver),
                asdict(result.daum),
            ],
        }
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
