# 업무일지 관리 시스템 (WorkLog Management)

Streamlit 기반 업무일지 관리 시스템입니다.

## 주요 기능

- **대시보드**: 프로젝트 현황 및 최근 업무일지 요약
- **프로젝트 관리**: 프로젝트 CRUD, 팀원 배정, 진척률 관리
- **팀원 관리**: 팀원 CRUD, PM/일반 역할 구분
- **업무일지**: 일지 작성/수정/삭제, 프리셋 업무 항목, 공수 입력
- **업무 요약**: 주간/월간 프로젝트별 업무 현황 요약
- **보고서**: 주간(프로젝트별) / 월간(전체 통합) AI 보고서, 인쇄용 PDF 미리보기

## 기술 스택

- **Frontend**: Streamlit
- **Backend**: Supabase (PostgreSQL)
- **AI**: Google Gemini (gemini-2.5-flash)

## 실행 방법

```
pip install -r requirements.txt
streamlit run app.py
```

.env 파일에 아래 환경변수를 설정하세요:
SUPABASE_URL=...
SUPABASE_ANON_KEY=...
GEMINI_API_KEY=...
