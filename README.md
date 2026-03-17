<<<<<<< HEAD
# Telegram Auto Marketer

이 프로젝트는 텔레그램 웹을 자동으로 사용하여 여러 채널에 메시지를 홍보하는 봇입니다. CustomTkinter 기반의 GUI를 통해 쉽게 설정하고 실행할 수 있습니다.

## 기능

- 홍보 메시지 설정 및 저장
- 채널 추가/삭제 및 쿨타임 관리
- 자동화된 메시지 포스팅 (사람처럼 타이핑)
- 실시간 로그 표시
- 설정 데이터 JSON 파일로 저장

## 설치 및 실행

1. Python 환경이 설정되어 있는지 확인하세요 (Python 3.7 이상 권장).

2. 필요한 패키지를 설치하세요:
   ```
   pip install -r requirements.txt
   ```

3. Playwright 브라우저를 설치하세요:
   ```
   python -m playwright install chromium
   ```

4. **텔레그램 데스크톱 앱 준비**:
   - 텔레그램 데스크톱 앱을 설치하고 로그인하세요.
   - 앱을 디버깅 모드로 실행해야 합니다. 터미널에서 다음 명령으로 실행:
     ```
     /Applications/Telegram.app/Contents/MacOS/Telegram --remote-debugging-port=9222
     ```
     (앱 경로는 설치 위치에 따라 다를 수 있습니다. Finder에서 앱을 우클릭 > 패키지 내용 표시 > Contents/MacOS/Telegram)

5. 프로그램을 실행하세요:
   ```
   python main.py
   ```

## 사용법

1. 텔레그램 데스크톱 앱이 디버깅 모드로 실행 중인지 확인하세요 (위 4단계). 앱이 CDP를 지원하지 않으면 자동으로 새 브라우저가 열립니다.

2. GUI가 열리면 "홍보 메시지 설정"에 메시지를 입력하고 "메시지 저장"을 클릭하세요.

3. 좌측 패널에서 채널을 추가하세요:
   - 채널 별칭
   - 텔레그램 웹 URL (예: https://web.telegram.org/k/#-123456789 또는 https://web.telegram.org/k/#@channelname)
   - 쿨타임 (분 단위)

4. "자동 홍보 시작"을 클릭하여 봇을 시작하세요. 봇이 기존 텔레그램 앱의 세션에 연결되거나, 새 브라우저를 열어 텔레그램 웹에 연결됩니다.

## 주의사항

- 텔레그램의 이용 약관을 준수하세요. 자동화는 계정 정지에 이어질 수 있습니다.
- 설정은 `telegram_config.json`에 저장됩니다.

## 라이선스

이 프로젝트는 개인용으로만 사용하세요.
=======
# telehack
>>>>>>> 78e1cd483312c1d708b4d394bed67c7a86e56c0f
