import os
import time
from pathlib import Path
from dotenv import dotenv_values

_env = dotenv_values(Path(__file__).resolve().parent.parent / '.env')
_GEMINI_KEY = _env.get("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY", "")

_MODELS = ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-2.0-flash-lite"]


def _progress_label(progress: int | None) -> str:
    if progress is None:
        return "미집계"
    if progress >= 100:
        return "완료"
    if progress >= 90:
        return "마무리 단계"
    if progress >= 60:
        return "후반 진행"
    if progress >= 30:
        return "진행 중"
    return "초기 단계"


def generate_report_summary(
    range_label: str,
    start_date: str,
    end_date: str,
    project_name: str,
    items: list[str],
    members: list[str] | None = None,
    progress: int | None = None,
    total_hours: float | None = None,
    member_hours: dict[str, float] | None = None,
) -> str:
    if not _GEMINI_KEY:
        raise ValueError("GEMINI_API_KEY가 .env 파일에 설정되지 않았습니다.")
    if not items:
        raise ValueError("요약할 업무 항목이 없습니다.")

    from google import genai

    client = genai.Client(api_key=_GEMINI_KEY)

    # ── 컨텍스트 문자열 조합 ──────────────────────────────────
    members_str = "·".join(members) if members else "정보 없음"
    progress_str = f"{progress}% ({_progress_label(progress)})" if progress is not None else "정보 없음"
    hours_str = f"{total_hours}시간" if total_hours else "정보 없음"

    if member_hours:
        mh_lines = "\n".join(
            f"  · {name}: {h}시간"
            for name, h in sorted(member_hours.items(), key=lambda x: -x[1])
        )
    else:
        mh_lines = "  · 정보 없음"

    item_list = "\n".join(f"  · {it}" for it in items)

    prompt = f"""당신은 프로젝트 관리 전문가입니다. 아래 업무 데이터를 바탕으로 공식 업무 보고서 요약을 작성하세요.

[작성 규칙]
• 문장 종결: 명사형 종결어미 사용 (예: "~작업 완료", "~기능 구현", "~검토 진행", "~분석 수행")
• "~했습니다", "~하였습니다", "~했어요" 등 서술형·경어체 종결 사용 금지
• **, ##, ``` 등 마크다운 서식 기호 사용 금지
• 각 불릿은 1~2줄로 간결하게 핵심만 서술
• 한국어 작성

[프로젝트 현황]
• 프로젝트명: {project_name}
• 보고 기간: {start_date} ~ {end_date} ({range_label})
• 참여 팀원: {members_str}
• 현재 진척률: {progress_str}
• 총 투입 공수: {hours_str}
• 팀원별 공수:
{mh_lines}

[주요 업무 항목]
{item_list}

[보고서 작성 형식 — 반드시 아래 4개 섹션 순서로 작성]

▶ 주요 성과
(이번 기간 완료·달성된 핵심 업무를 불릿(•)으로 3~5개 나열. 중복·유사 항목은 통합)

▶ 투입 인력 현황
(팀원별 투입 공수 및 주요 담당 업무 영역을 간략히 서술)

▶ 이슈 및 특이사항
(업무 항목에서 리스크·이슈·지연 가능성이 있는 내용 기술. 없으면 "특이사항 없음" 기재)

▶ 차기 계획
(현재 진행 상황을 바탕으로 다음 기간에 수행할 후속 작업 및 예상 일정을 2~3개 제시)
"""

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


def chat_response(
    conversation: list[dict],   # [{'role': 'user'|'assistant', 'content': '...'}]
    system_context: str,
) -> str:
    """챗봇 응답 생성 (멀티턴, Gemini system_instruction 활용)"""
    if not _GEMINI_KEY:
        raise ValueError("GEMINI_API_KEY가 설정되지 않았습니다.")

    from google import genai
    from google.genai import types

    client = genai.Client(api_key=_GEMINI_KEY)

    # Gemini role: 'user' | 'model'
    contents = []
    for msg in conversation:
        role = "user" if msg["role"] == "user" else "model"
        contents.append({"role": role, "parts": [{"text": msg["content"]}]})

    last_error = None
    for model in _MODELS:
        for attempt in range(3):
            try:
                response = client.models.generate_content(
                    model=model,
                    contents=contents,
                    config=types.GenerateContentConfig(
                        system_instruction=system_context,
                    ),
                )
                text = response.text.strip()
                if not text:
                    raise ValueError("Gemini 응답이 비어 있습니다.")
                return text
            except Exception as e:
                last_error = e
                err_str = str(e)
                if "503" in err_str or "UNAVAILABLE" in err_str:
                    time.sleep(3 * (attempt + 1))
                    continue
                break

    raise RuntimeError(f"챗봇 응답 실패: {last_error}")
