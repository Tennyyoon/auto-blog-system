# 개인용 키워드 트래커 홈페이지

블로그 운영자가 혼자 쓰는 용도로, 아래를 한 화면에서 확인합니다.
- Google / Naver / Daum 키워드 관심도 점수
- 각 플랫폼 검색 결과량(발행량 추정)

## 1) 로컬 실행
```bash
cd keyword_dashboard
pip install -r requirements.txt
python app.py
```

브라우저 접속:
- http://localhost:8080

---

## 2) 실제 주소(URL)로 바로 쓰기 - Render 배포
이 저장소에는 Render 배포용 `render.yaml`이 포함되어 있어, 클릭 몇 번으로 실제 주소를 만들 수 있습니다.

### 배포 순서
1. GitHub에 이 저장소 푸시
2. https://render.com 접속 후 로그인
3. **New +** → **Blueprint** 선택
4. 방금 푸시한 GitHub 저장소 연결
5. 배포 완료 대기

배포가 끝나면 Render가 아래 형태의 실제 주소를 자동 발급합니다.
- `https://personal-keyword-tracker.onrender.com`

> 서비스 이름이 중복되면 주소는 약간 달라질 수 있습니다.

### 동작 확인
- 홈: `https://<발급주소>/`
- 헬스체크: `https://<발급주소>/health`
- API 예시: `https://<발급주소>/api/analyze?keyword=뉴질랜드%20워홀`

---

## 3) 새 GitHub 프로젝트 `keywords`로 옮기기
아래 명령을 실행하면 현재 프로젝트를 **새 원격 저장소 `keywords`**로 푸시할 수 있습니다.

### 방법 A: 새 폴더로 복제해서 분리(권장)
```bash
# 1) 현재 저장소에서 keywords용 복사본 생성
cd ..
git clone auto-blog-system keywords
cd keywords

# 2) 새 GitHub 저장소 URL 연결
# 예: https://github.com/<계정명>/keywords.git
git remote remove origin
git remote add origin https://github.com/<계정명>/keywords.git

# 3) 메인 브랜치로 첫 푸시
git push -u origin HEAD:main
```

### 방법 B: 현재 저장소에서 origin만 교체
```bash
cd /workspace/auto-blog-system
git remote remove origin
git remote add origin https://github.com/<계정명>/keywords.git
git push -u origin HEAD:main
```

> 방법 B는 기존 원격 연결이 바뀌므로, 기존 저장소와 연결을 유지하고 싶다면 방법 A를 사용하세요.

---

## 참고
- Google 관심도는 Google Trends(`pytrends`) 기반 0~100 상대 점수입니다.
- Naver/Daum 관심도는 자동완성 제안 개수 기반의 간이 점수입니다.
- 검색 결과량은 검색 결과 페이지의 노출 건수를 파싱한 값이라 환경/시점에 따라 달라질 수 있습니다.
- 검색엔진 측 차단/레이아웃 변경 시 일부 값이 비어 보일 수 있습니다.
