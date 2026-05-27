import os
from pathlib import Path
from dotenv import dotenv_values

_env = dotenv_values(Path(__file__).resolve().parent.parent / '.env')
_OPENAI_KEY = _env.get("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY", "")


def generate_report_summary(
    range_label: str,
    start_date: str,
    end_date: str,
    project_name: str,
    items: list[str],
) -> str:
    api_key = _OPENAI_KEY
    if not api_key or api_key == "여기에_OpenAI_키를_입력하세요":
        raise ValueError("OPENAI_API_KEY가 .env 파일에 설정되지 않았습니다.")
    if not items:
        raise ValueError("요약할 업무 항목이 없습니다.")

    from openai import OpenAI
    client = OpenAI(api_key=api_key)

    item_list = "\n".join(f"- {it}" for it in items)
    user_prompt = (
        f'다음은 "{project_name}" 프로젝트의 {range_label} 업무 내용'
        f'({start_date} ~ {end_date})입니다.\n\n'
        f"{item_list}\n\n"
        "위 내용을 아래 조건에 맞게 요약해 주세요.\n"
        "1. 불릿 포인트(•) 형식으로 작성\n"
        "2. 각 항목은 한 문장으로 핵심만 서술\n"
        "3. 마크다운 기호(**)는 사용하지 않음\n"
        "4. 한국어로 작성"
    )

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": (
                    "당신은 기업 업무 보고서 작성 전문가입니다. "
                    "주어진 업무 일지 항목을 간결하고 전문적인 한국어 보고서 형식으로 요약합니다."
                ),
            },
            {"role": "user", "content": user_prompt},
        ],
        max_tokens=800,
        temperature=0.3,
    )

    text = (response.choices[0].message.content or "").strip()
    if not text:
        raise ValueError("OpenAI 응답이 비어 있습니다.")
    return text
