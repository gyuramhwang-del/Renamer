# Renamer

디렉터리 안에 있는 파일 이름을 텍스트 파일로 저장하는 간단한 도구입니다. 파이썬 3.10 이상에서 동작하며 추가 의존성이 없습니다.

## 사용 방법

```bash
python renamer.py <대상_폴더_경로> [옵션]
```

예시:

- 지정한 폴더의 파일 이름을 `filenames.txt`로 생성

  ```bash
  python renamer.py ./my_folder
  ```

- 하위 폴더까지 모두 포함해 `output/list.txt`로 저장

  ```bash
  python renamer.py ./my_folder -r -o output/list.txt
  ```

- 숨김 파일까지 포함하려면 `--include-hidden` 옵션을 추가하세요.

옵션 요약:

- `-o, --output`: 결과를 기록할 텍스트 파일 경로 (기본값: `filenames.txt`)
- `-r, --recursive`: 하위 폴더까지 검색
- `--include-hidden`: 숨김 파일/폴더도 포함

## GUI 사용

```bash
python renamer.py --gui
```

또는 아무 인자 없이 실행하면 자동으로 GUI가 열립니다. 폴더와 저장 위치를 선택하고, 하위 폴더/숨김 파일 포함 여부를 체크한 뒤 **파일 목록 생성** 버튼을 누르면 됩니다.

## Windows용 실행 파일 만들기

`pyinstaller`를 사용해 GUI 전용 실행 파일을 만들 수 있습니다.

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name Renamer renamer.py
```

생성된 `dist/Renamer.exe`를 실행하면 바로 GUI가 열립니다.

## Grok 자동화 도구 (favorites 다운로드 + HD 업스케일 + 프롬프트 재실행)

Grok 즐겨찾기 페이지에서 체크된 항목을 다운로드한 뒤 HD 업스케일을 적용하고, 기존에 사용한 프롬프트로 다시 영상을 돌리는 자동화 스크립트입니다.

### 설치

> 아래 명령은 **이 저장소 폴더에서** 실행해야 합니다. (예: `C:\path\to\Renamer`)

```bash
pip install -r requirements.txt
python -m playwright install chromium
```

### 사용 방법

> `python grok_automation.py`가 동작하지 않으면, 현재 터미널이 이 저장소 폴더인지 확인하세요.

```bash
python grok_automation.py --wait-login
```

주요 옵션:

- `--profile-dir`: 로그인 세션을 저장하는 크롬 프로필 경로 (기본값: `grok_profile`)
- `--download-dir`: 다운로드 저장 경로 (기본값: `downloads`)
- `--headless`: 헤드리스 모드로 실행
- `--max-items`: 처리할 체크 항목 수 제한 (0이면 제한 없음)
- `--dry-run`: 체크된 항목만 확인하고 다운로드하지 않음
- `--config`: 셀렉터를 JSON으로 오버라이드

### 실행 파일 만들기 (Windows)

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name GrokAutomation grok_automation.py
```

생성된 `dist/GrokAutomation.exe`를 실행하면 됩니다.

### 문제 해결 (Windows)

- `requirements.txt`를 찾을 수 없다는 오류가 나면, 먼저 저장소 폴더로 이동하세요.

  ```bat
  cd /d C:\path\to\Renamer
  pip install -r requirements.txt
  ```

- `grok_automation.py`를 찾을 수 없다는 오류도 동일합니다. 아래처럼 저장소 폴더에서 실행하세요.

  ```bat
  cd /d C:\path\to\Renamer
  python grok_automation.py --wait-login
  ```

### 셀렉터 설정

Grok 페이지 UI가 바뀌면 셀렉터를 수정해야 할 수 있습니다. 예시 JSON:

```json
{
  "checkbox_selector": "input[type=\"checkbox\"]",
  "download_button_selector": "button:has-text(\"Download\")",
  "hd_toggle_selector": "button:has-text(\"HD\")"
}
```

## 개발

테스트 실행:

```bash
pytest
```
