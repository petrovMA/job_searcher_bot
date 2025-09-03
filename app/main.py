from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import os
import re
from datetime import datetime, timedelta, timezone
from typing import List, Dict
import requests
from bs4 import BeautifulSoup

app = FastAPI()
security = HTTPBearer()


def parse_duration(duration_str: str) -> timedelta:
    pattern = r"^\s*(\d+)\s*(seconds?|minutes?|hours?|days?|weeks?|months?|years?)\s*$"
    match = re.match(pattern, duration_str, re.IGNORECASE)
    if not match:
        raise HTTPException(status_code=400, detail="Invalid duration format")
    value = int(match.group(1))
    unit = match.group(2).lower()
    if unit.startswith("second"):
        return timedelta(seconds=value)
    if unit.startswith("minute"):
        return timedelta(minutes=value)
    if unit.startswith("hour"):
        return timedelta(hours=value)
    if unit.startswith("day"):
        return timedelta(days=value)
    if unit.startswith("week"):
        return timedelta(weeks=value)
    if unit.startswith("month"):
        return timedelta(days=30 * value)
    if unit.startswith("year"):
        return timedelta(days=365 * value)
    raise HTTPException(status_code=400, detail="Unsupported duration unit")


def fetch_posts(channel: str, since: datetime) -> List[Dict[str, str]]:
    posts: List[Dict[str, str]] = []
    base_url = f"https://t.me/s/{channel}"
    before = None
    while True:
        url = base_url if before is None else f"{base_url}?before={before}"
        resp = requests.get(url, timeout=10)
        if not resp.ok:
            break
        soup = BeautifulSoup(resp.text, "html.parser")
        wrappers = soup.select("div.tgme_widget_message_wrap")
        if not wrappers:
            break
        for wrap in wrappers:
            message = wrap.select_one("div.tgme_widget_message")
            if not message:
                continue
            time_tag = message.select_one("time")
            if not time_tag or not time_tag.get("datetime"):
                continue
            dt = datetime.fromisoformat(time_tag["datetime"])
            if dt < since:
                return posts
            text_elem = message.select_one("div.tgme_widget_message_text")
            text = text_elem.get_text("\n") if text_elem else ""
            post_id = message.get("data-post", "")
            posts.append({"id": post_id, "date": dt.isoformat(), "text": text})
        last = wrappers[-1].select_one("div.tgme_widget_message")
        if not last:
            break
        before = last.get("data-post", "").split("/")[-1]
    return posts


@app.get("/jobs")
def get_jobs(duration: str, credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = os.getenv("API_TOKEN", "secret")
    if credentials.credentials != token:
        raise HTTPException(status_code=401, detail="Invalid token")
    delta = parse_duration(duration)
    since = datetime.now(timezone.utc) - delta
    posts = fetch_posts("easy_qa_jobs", since)
    return {"count": len(posts), "posts": posts}
