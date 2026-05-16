import re


SUBMISSION_URL_PATTERNS = [
    r"/comments/([a-z0-9]+)",
    r"redd\.it/([a-z0-9]+)",
]


def extract_submission_id(url: str) -> str:
    """Extract the Reddit submission ID from any valid Reddit submission URL.

    Accepts:
      https://www.reddit.com/r/singapore/comments/1t6tvf3/some_slug/
      https://reddit.com/comments/1t6tvf3
      https://redd.it/1t6tvf3
    """
    for pattern in SUBMISSION_URL_PATTERNS:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    raise ValueError(f"Could not extract submission ID from URL: {url}")