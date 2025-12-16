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

## 개발

테스트 실행:

```bash
pytest
```
