import os
import time
from pathlib import Path
from dotenv import dotenv_values

_env = dotenv_values(Path(__file__).resolve().parent.parent / '.env')
_GEMINI_KEY = _env.get("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY", "")

_MODELS = ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-2.0-flash-lite"]


def generate_report_summary(
    range_label: str,
    start_date: str,
    end_date: str,
    project_name: str,
    items: list[str],
) -> str:
    if not _GEMINI_KEY:
        raise ValueError("GEMINI_API_KEY가 .env 파일에 설정되지 않았습니다.")
    if not items:
        raise ValueError("요약할 업무 항목이 없습니다.")

    from google import genai

    client = genai.Client(api_key=_GEMINI_KEY)

    item_list = "\n".join(f"- {it}" for it in items)
    prompt = (
        f'다음은 "{project_name}" 프로젝트의 {range_label} 업무 내용'
        f'({start_date} ~ {end_date})입니다.\n\n'
        f"{item_list}\n\n"
        "위 내용을 아래 조건에 맞게 요약해 주세요.\n"
        "1. 불릿 포인트(•) 형식으로 작성\n"
        "2. 각 항목은 한 문장으로 핵심만 서술\n"
        "3. 마크다운 기호(**)는 사용하지 않음\n"
        "4. 한국어로 작성"
    )

    last_error = None
    for model in _MODELS:
        for attempt in range(3):
            try:
                response = client.models.generate_content(
                    model=model,
                    contents=prompt,
                )
                text = response.text.strip()
                if not text:
                    raise ValueError("Gemini 응답이 비어 있습니다.")
                return text
            except Exception as e:
                last_error = e
                err_str = str(e)
                if "503" in err_str or "UNAVAILABLE" in err_str:
                    # 일시적 과부하 — 잠시 후 재시도
                    time.sleep(3 * (attempt + 1))
                    continue
                # 다른 오류는 다음 모델로 폴백
                break

    raise RuntimeError(f"모든 모델 시도 실패: {last_error}")
