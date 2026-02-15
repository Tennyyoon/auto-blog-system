# 개인용 키워드 트래커 홈페이지

블로그 운영자가 혼자 쓰는 용도로, 아래를 한 화면에서 확인합니다.
- Google / Naver / Daum 키워드 관심도 점수
- 각 플랫폼 검색 결과량(발행량 추정)

## 실행 방법
```bash
cd keyword_dashboard
pip install -r requirements.txt
python app.py
```

브라우저 접속:
- http://localhost:8080

## 참고
- Google 관심도는 Google Trends(`pytrends`) 기반 0~100 상대 점수입니다.
- Naver/Daum 관심도는 자동완성 제안 개수 기반의 간이 점수입니다.
- 검색 결과량은 검색 결과 페이지의 노출 건수를 파싱한 값이라 환경/시점에 따라 달라질 수 있습니다.
