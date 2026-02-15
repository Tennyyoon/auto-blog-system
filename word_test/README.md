# 네이버 SEO 블로그 자동 초안 생성기

이 스크립트는 **네이버 블로그용 초안**을 자동으로 생성합니다.
GitHub Actions로 실행하면 PC가 꺼져 있어도 매일 글이 만들어집니다.

## 어디서 실행하면 되나요?
### 1) PC에서 직접 실행 (즉시 테스트용)
아래 명령을 **내 컴퓨터 터미널**(VSCode 터미널, macOS 터미널, PowerShell 등)에서 실행하면 됩니다.

```bash
cd /workspace/auto-blog-system
pip install openai python-docx
OPENAI_API_KEY=여기에_키입력 python word_test/make_word.py
```

생성 파일 위치:
- `word_test/generated_posts/*.md`
- `word_test/generated_posts/*.docx`

### 2) GitHub에서 자동 실행 (PC 꺼져도 동작)
실제로 운영할 때는 이 방법을 권장합니다.

1. GitHub 저장소 → **Settings → Secrets and variables → Actions**
2. `OPENAI_API_KEY` 시크릿 등록
3. GitHub 저장소 → **Actions** 탭 → `Auto Blog Generator` 워크플로우 선택
4. `Run workflow` 버튼으로 수동 1회 실행
5. 이후에는 스케줄(cron)로 자동 실행

> 현재 스케줄: `0 0 * * *` (UTC 00:00) = **한국시간(KST) 오전 9시**

## 동작 방식
- `word_test/make_word.py`가 주제 3개를 뽑아 글 생성
- 글 길이는 **1500자 이하**로 자동 보정
- 결과물:
  - `word_test/generated_posts/*.md`
  - `word_test/generated_posts/*.docx`
- `word_test/progress.json`으로 다음 주제 인덱스 관리

## 사전 준비
1. GitHub 저장소 `Settings > Secrets and variables > Actions`에서
   - `OPENAI_API_KEY` 등록
2. 워크플로우 활성화 (`.github/workflows/main.yml`)

## 수동 실행 (로컬)
```bash
pip install openai python-docx
OPENAI_API_KEY=... python word_test/make_word.py
```

## 자동 실행 (PC 꺼져도 동작)
- 매일 UTC 00:00에 GitHub Actions가 자동 실행됩니다.
- 생성 결과를 저장소에 자동 커밋/푸시합니다.
