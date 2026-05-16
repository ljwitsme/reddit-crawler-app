from datetime import datetime, timezone
from zoneinfo import ZoneInfo

SGT = ZoneInfo("Asia/Singapore")
UTC = ZoneInfo("UTC")


def epoch_to_utc(epoch: float) -> datetime:
    """Convert a Unix epoch (seconds) to a naive UTC datetime for DB storage."""
    return datetime.fromtimestamp(epoch, tz=timezone.utc).replace(tzinfo=None)


def utc_to_sgt_iso(dt: datetime) -> str:
    """Convert a naive UTC datetime (from DB) to an SGT ISO string for display."""
    return dt.replace(tzinfo=UTC).astimezone(SGT).isoformat()