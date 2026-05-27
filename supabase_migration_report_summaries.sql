-- ============================================================
-- report_summaries 테이블 생성
-- Supabase 대시보드 > SQL Editor 에서 실행하세요
-- ============================================================

CREATE TABLE IF NOT EXISTS report_summaries (
  id          UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
  project_key TEXT        NOT NULL,        -- 프로젝트 UUID 또는 'ALL'
  range       TEXT        NOT NULL,        -- 'weekly' | 'monthly'
  start_date  TEXT        NOT NULL,        -- YYYY-MM-DD
  end_date    TEXT        NOT NULL,        -- YYYY-MM-DD
  content     TEXT        NOT NULL,        -- GPT 요약 결과
  created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),

  CONSTRAINT report_summaries_unique
    UNIQUE (project_key, range, start_date, end_date)
);
