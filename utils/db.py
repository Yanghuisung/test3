import os
from pathlib import Path
import streamlit as st
from supabase import create_client, Client
from dotenv import dotenv_values
from datetime import datetime, timezone

_ENV_PATH = Path(__file__).resolve().parent.parent / '.env'
_env = dotenv_values(_ENV_PATH)

_SUPABASE_URL = _env.get("SUPABASE_URL") or os.getenv("SUPABASE_URL", "")
_SUPABASE_KEY = _env.get("SUPABASE_ANON_KEY") or os.getenv("SUPABASE_ANON_KEY", "")


@st.cache_resource
def get_supabase() -> Client:
    if not _SUPABASE_URL or not _SUPABASE_KEY:
        st.error(f".env 파일을 찾을 수 없거나 키가 비어 있습니다. (경로: {_ENV_PATH})")
        st.stop()
    return create_client(_SUPABASE_URL, _SUPABASE_KEY)


# ── Projects ──────────────────────────────────────────────────

def list_projects() -> list[dict]:
    sb = get_supabase()
    res = sb.table('projects').select('*').order('created_at').execute()
    return res.data or []


def get_project(id: str) -> dict | None:
    sb = get_supabase()
    res = sb.table('projects').select('*').eq('id', id).maybe_single().execute()
    return res.data


def save_project(data: dict) -> dict:
    sb = get_supabase()
    payload = {
        'name': data['name'],
        'description': data.get('description') or None,
        'start_date': data['start_date'],
        'end_date': data.get('end_date') or None,
        'member_ids': data.get('member_ids', []),
        'status': data.get('status', 'active'),
    }
    if data.get('id'):
        res = sb.table('projects').update(payload).eq('id', data['id']).execute()
    else:
        res = sb.table('projects').insert(payload).execute()
    return res.data[0]


def delete_project(id: str) -> None:
    sb = get_supabase()
    sb.table('projects').delete().eq('id', id).execute()


# ── Members ───────────────────────────────────────────────────

def list_members() -> list[dict]:
    sb = get_supabase()
    res = sb.table('members').select('*').order('created_at').execute()
    return res.data or []


def get_member(id: str) -> dict | None:
    sb = get_supabase()
    res = sb.table('members').select('*').eq('id', id).maybe_single().execute()
    return res.data


def save_member(data: dict) -> dict:
    sb = get_supabase()
    payload = {
        'name': data['name'],
        'role': data.get('role') or None,
        'email': data.get('email') or None,
    }
    if data.get('id'):
        res = sb.table('members').update(payload).eq('id', data['id']).execute()
    else:
        res = sb.table('members').insert(payload).execute()
    return res.data[0]


def delete_member(id: str) -> None:
    sb = get_supabase()
    affected = sb.table('projects').select('id, member_ids').contains('member_ids', [id]).execute()
    for p in (affected.data or []):
        new_ids = [mid for mid in (p.get('member_ids') or []) if mid != id]
        sb.table('projects').update({'member_ids': new_ids}).eq('id', p['id']).execute()
    sb.table('members').delete().eq('id', id).execute()


# ── Work Logs ─────────────────────────────────────────────────

def list_logs() -> list[dict]:
    sb = get_supabase()
    res = sb.table('work_logs').select('*').order('date', desc=True).execute()
    return res.data or []


def logs_by_member(member_id: str) -> list[dict]:
    sb = get_supabase()
    res = sb.table('work_logs').select('*').eq('member_id', member_id).order('date', desc=True).execute()
    return res.data or []


def logs_by_project(project_id: str) -> list[dict]:
    sb = get_supabase()
    res = sb.table('work_logs').select('*').eq('project_id', project_id).order('date').execute()
    return res.data or []


def save_log(data: dict) -> dict:
    sb = get_supabase()
    now = datetime.now(timezone.utc).isoformat()
    payload = {
        'project_id': data['project_id'],
        'member_id': data['member_id'],
        'date': data['date'],
        'items': data.get('items', []),
        'hours': data.get('hours') or None,
        'progress': data.get('progress') if data.get('progress') is not None else None,
        'updated_at': now,
    }
    if data.get('id'):
        res = sb.table('work_logs').update(payload).eq('id', data['id']).execute()
    else:
        res = sb.table('work_logs').insert(payload).execute()
    return res.data[0]


def delete_log(id: str) -> None:
    sb = get_supabase()
    sb.table('work_logs').delete().eq('id', id).execute()


# ── Report Summaries ──────────────────────────────────────────

def list_summaries_for_period(range_type: str, start_date: str, end_date: str) -> list[dict]:
    sb = get_supabase()
    try:
        res = (sb.table('report_summaries')
               .select('*')
               .eq('range', range_type)
               .eq('start_date', start_date)
               .eq('end_date', end_date)
               .execute())
        return res.data or []
    except Exception:
        return []


def save_summary(project_key: str, range_type: str, start_date: str, end_date: str, content: str) -> dict:
    sb = get_supabase()
    payload = {
        'project_key': project_key,
        'range': range_type,
        'start_date': start_date,
        'end_date': end_date,
        'content': content,
    }
    res = (sb.table('report_summaries')
           .upsert(payload, on_conflict='project_key,range,start_date,end_date')
           .execute())
    return res.data[0]


def delete_summary(id: str) -> None:
    sb = get_supabase()
    sb.table('report_summaries').delete().eq('id', id).execute()
