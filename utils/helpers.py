from datetime import date, timedelta
import calendar


def today_str() -> str:
    return date.today().isoformat()


def start_of_week(d: date) -> date:
    return d - timedelta(days=d.weekday())  # Monday


def end_of_week(d: date) -> date:
    return start_of_week(d) + timedelta(days=6)


def start_of_month(d: date) -> date:
    return d.replace(day=1)


def end_of_month(d: date) -> date:
    last = calendar.monthrange(d.year, d.month)[1]
    return d.replace(day=last)


def latest_progress(logs: list) -> int:
    with_prog = [l for l in logs if l.get('progress') is not None]
    if not with_prog:
        return 0
    return sorted(with_prog, key=lambda l: l['date'])[-1]['progress']


def week_label(d: date) -> str:
    s = start_of_week(d)
    e = end_of_week(d)
    return f"{s.strftime('%Y.%m.%d')} ~ {e.strftime('%m.%d')}"


def month_label(d: date) -> str:
    return d.strftime('%Y년 %m월')
