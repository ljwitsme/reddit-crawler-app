# Reddit Crawler — Assignment

A web application that crawls Reddit submissions and comments via PRAW, stores them in MySQL, and presents them through an analyst-friendly dashboard.

---

## Table of Contents

1. [Overview](#overview)
2. [Features](#features)
3. [Quick Start (Docker)](#quick-start-docker)
4. [Demo Screenshots](#demo-screenshots)
5. [Architecture](#architecture)
6. [Project Structure](#project-structure)
7. [Detailed Setup (Local Python)](#detailed-setup-local-python)
8. [Running the App](#running-the-app)
9. [Usage](#usage)
10. [Database Schema](#database-schema)
11. [Technical Considerations](#technical-considerations)
12. [Analytics Discussion](#analytics-discussion)
13. [Containerisation](#containerisation)
14. [Use of AI Tools](#use-of-ai-tools)
15. [Tech Stack](#tech-stack)

---

## Overview

Paste any Reddit submission URL and get a fully crawled view of the post, its complete nested comment tree, and 50 more posts from the same subreddit. Every author becomes a clickable profile showing their recent activity across all of Reddit. Data is stored in MySQL using a schema designed for both operational and analytical use.

---

## Features

| S/N | Feature | Explanation |
|---|---|---|
| 1 | Core Crawling | Accepts any Reddit submission URL and crawls the full post plus its complete comment tree using PRAW. Extracts submission title, ID, subreddit, comment IDs, parent IDs, authors, body content, SGT timestamps, and upvote counts. Nested comments are fully expanded via `replace_more(limit=None)`. Deleted and removed comments are flagged with an `is_deleted` column and styled distinctly in the UI rather than dropped. |
| 2 | Subreddit Expansion | Pasting a Reddit URL automatically crawls 50 additional submissions from the same subreddit, each with its full nested comment tree. The subreddit is derived from the URL — no separate input needed. |
| 3 | Author History Across Reddit | Every author has a clickable profile page. Clicking **Refresh from Reddit** fetches their 100 most recent comments from across all of Reddit via `redditor.comments.new(limit=100)`, not just one subreddit. |
| 4 | User Exploration | Every author, subreddit, and submission is clickable, enabling free navigation through the data. |
| 5 | UX Polish | Sortable submissions list, paginated views, collapsible comment threads with hidden-reply counts, "Expand all" / "Collapse all" controls, breadcrumb navigation, empty states, and loading spinners. |
| 6 | Analytics Discussion | A written discussion of analytical approaches lives at [`docs/analytics.md`](docs/analytics.md), covering sentiment analysis, topic modelling, user behaviour, engagement, temporal activity, and network graph analysis. |

---

## Quick Start (Docker)

The fastest way to run the entire stack. Spins up the FastAPI app and MySQL together.

### Prerequisites
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed and running
- Reddit API credentials (see [Step 2 in Detailed Setup](#step-2-get-reddit-api-credentials) for how to obtain them)

### Step 1: Clone the repository
```bash
git clone <your-repo-url>
cd reddit-crawler-app
```

### Step 2: Create your `.env` file
```bash
cp .env.example .env
```
Open `.env` and fill in your Reddit credentials (see [Step 3 in Detailed Setup](#step-3-configure-your-environment) for the template and field descriptions). The `DATABASE_URL` is already configured for the bundled MySQL container.

### Step 3: Start the stack
```bash
docker compose up --build
```

### Step 4: Open the dashboard
Visit <http://localhost:8000>

### Stop the app (keep data)
```bash
docker compose down
```
This stops the containers but preserves the database. Next time you run `docker compose up`, all your crawled data is still there.

### Reset everything (wipe the database)
```bash
docker compose down -v
docker compose up --build
```
The `-v` flag deletes the MySQL volume, giving you a completely empty database. Use this when you want a fresh start. After this, your dashboard will show all zeros until you crawl something new.

---

## Demo Screenshots

### 1. Empty dashboard
![Empty dashboard](docs/screenshots/01_empty_dashboard.png)

Clean start state with all stats at zero.

### 2. One URL paste → 51 submissions auto-batched
![Populated dashboard](docs/screenshots/02_populated_dashboard.png)

A single URL triggers the original crawl plus 50 more from the same subreddit, each with full comment trees.

### 3. Submission detail with full metadata
![Submission detail](docs/screenshots/03_submission_detail.png)

Title, author, subreddit, score, SGT timestamp, and the full comment thread.

### 4. Nested comments and deletion handling
![Nested and deleted comments](docs/screenshots/04_nested_and_deleted_comments.png)

Full reply trees rendered with visual indentation.

### 5. Cross-Reddit author exploration
![Author profile](docs/screenshots/05_author_profile.png)

Author profile populated with comments captured during regular crawls. The subreddit chips show which subreddits this author has commented in (based on what we've crawled so far).

### 6. Author history expanded across Reddit
![Subreddit listing](docs/screenshots/06_subreddits_listing_all.png)

After clicking **Refresh from Reddit**, the app fetches the author's 100 most recent comments from across all of Reddit via PRAW's `redditor.comments.new(limit=100)`. New subreddit chips appear, including subreddits we've never crawled — demonstrating that the author history feature reaches beyond our local dataset.

---

## Architecture

Browser → FastAPI app → Reddit API (via PRAW) and MySQL (via SQLAlchemy). The entire application can be run using Docker.

```
┌────────────────────┐
│      Browser       │
│  HTML / CSS / JS   │
└─────────┬──────────┘
          │ HTTP
          ▼
┌─────────────────────┐
│    FastAPI app      │
│  Python + uvicorn   │
└──┬─────────────┬────┘
   │             │
   │PRAW         │SQLAlchemy
   ▼             ▼
┌──────────┐  ┌────────────┐
│ Reddit   │  │  MySQL 8   │
│   API    │  │ (Docker)   │
└──────────┘  └────────────┘
```

---

## Project Structure

```
reddit-crawler-app/
├── .env.example
├── .gitignore
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── run.py
├── README.md
├── backend/
│   ├── config.py
│   ├── database.py
│   ├── api/             (FastAPI routes + Pydantic schemas)
│   ├── crawler/         (PRAW client, URL parser, crawler dispatcher)
│   ├── db/              (SQLAlchemy models)
│   └── utils/           (UTC ↔ SGT conversion)
├── database/
│   └── schema.sql
├── docs/
│   ├── analytics.md            (Analytics discussion)
│   └── screenshots/            (Demo screenshots)
└── frontend/
    ├── index.html
    ├── submission.html
    ├── author.html
    ├── subreddit.html
    ├── favicon.svg
    ├── css/
    └── js/
```

---

## Detailed Setup (Local Python)

For running directly without Docker.

### Prerequisites
Python 3.11+, MySQL Server 8.0+, and a Reddit account with a verified email.

### Step 1: Set up MySQL
In MySQL Workbench, connect as root and run:

```sql
CREATE DATABASE reddit_crawler_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'reddit_user'@'localhost' IDENTIFIED WITH mysql_native_password BY 'your_password';
GRANT ALL PRIVILEGES ON reddit_crawler_db.* TO 'reddit_user'@'localhost';
FLUSH PRIVILEGES;
```

### Step 2: Get Reddit API credentials
Go to <https://www.reddit.com/prefs/apps>, click **create another app**, choose type **script**, and set redirect URI to `http://localhost:8000`. Note the client ID (shown under the app name) and client secret.

### Step 3: Configure your environment
Copy `.env.example` to `.env` and fill in:

```env
REDDIT_CLIENT_ID=<your client ID>
REDDIT_CLIENT_SECRET=<your client secret>
REDDIT_USER_AGENT=windows:reddit-crawler:v0.1 (by u/your_reddit_username)
DATABASE_URL=mysql+pymysql://reddit_user:your_password@localhost:3306/reddit_crawler_db
```

### Step 4: Install dependencies
```bash
python -m venv .venv
.venv\Scripts\activate         # Windows
# source .venv/bin/activate    # Mac/Linux
pip install -r requirements.txt
```

---

## Running the App

```bash
python run.py
```

Dashboard at <http://localhost:8000>. Swagger UI at <http://localhost:8000/docs>.

---

## Usage

| Action | How |
|---|---|
| Crawl a submission + auto-batch 50 more from the same subreddit | Paste a Reddit URL on the dashboard, click **Crawl** (1–3 min) |
| View a crawled submission with nested comments | Click any submission title |
| View an author's cross-Reddit history | Click any username → **Refresh from Reddit** |
| Sort or paginate | Use the dropdown and page buttons |
| Browse the API surface | Visit `/docs` for Swagger UI |
| Reset the database | Run `docker compose down -v` then `docker compose up --build` |

### Suggested test URLs

The application works with any Reddit submission URL. Some examples for testing:

- `https://www.reddit.com/r/singapore/comments/1t6tvf3/minimum_occupation_period_for_executive_condos/`
- `https://www.reddit.com/r/technology/comments/1tigi9j/ai_is_too_expensive_ai_is_as_it_stands_not/`

The data accumulates across crawls until the volume is wiped with `docker compose down -v`.

---

## Database Schema

The database has three tables: `submissions`, `comments`, and `authors`. Each row uses its Reddit ID as the primary key, so re-crawling the same post never creates duplicates. The `comments` table points back to itself via `parent_id` to preserve reply chains. All timestamps are stored in UTC and converted to SGT when shown to the user.

### `submissions`

| Column | Type | Purpose |
|---|---|---|
| `id` | String(50) | Reddit submission ID. Primary key — enables idempotent upserts on re-crawl. **(Required: Submission ID)** |
| `title` | Text | The submission's title. **(Required: Submission title)** |
| `author` | String(255), nullable | Reddit username of the submitter. Null if the account was deleted. |
| `subreddit` | String(255), indexed | Subreddit the submission was posted to. **(Required: Subreddit name)** |
| `selftext` | MEDIUMTEXT, nullable | Body text for self-posts. Null for link posts. |
| `url` | Text | Permalink to the submission on Reddit. |
| `score` | Integer | Net upvotes on the submission. **(Required: Upvote count)** |
| `num_comments` | Integer | Total comment count on Reddit (used for sorting). |
| `created_utc` | DateTime, indexed | When the submission was posted on Reddit (UTC, converted to SGT at display). **(Required: Date and time)** |
| `crawled_at` | DateTime | When this row was last crawled (used for sorting "newest crawled"). |

### `comments`

| Column | Type | Purpose |
|---|---|---|
| `id` | String(50) | Reddit comment ID. Primary key — enables idempotent upserts on re-crawl. **(Required: Comment ID)** |
| `submission_id` | String(20), FK, indexed | Foreign key to `submissions.id` with `ON DELETE CASCADE`. |
| `parent_id` | String(20), nullable, indexed | Reddit ID of the parent comment, or null for top-level comments. Preserves the reply tree. **(Required: Parent comment ID)** |
| `author` | String(255), nullable, indexed | Reddit username of the commenter. Null if the comment was deleted. **(Required: Comment author)** |
| `body` | MEDIUMTEXT, nullable | The comment text. `[deleted]` or `[removed]` if applicable. **(Required: Comment content)** |
| `score` | Integer | Net upvotes on the comment. **(Required: Upvote count)** |
| `created_utc` | DateTime | When the comment was posted on Reddit (UTC, converted to SGT at display). **(Required: Date and time)** |
| `is_deleted` | Boolean | True if the comment was deleted or removed. Used to render greyed-italic styling without dropping the row. |
| `submission_title` | Text, nullable | Cached parent-submission title. Populated for author-history comments crawled outside of a known submission, so the author profile page can display context. |
| `submission_subreddit` | String(255), nullable | Cached parent-submission subreddit. Same rationale as `submission_title`. |

### `authors`

| Column | Type | Purpose |
|---|---|---|
| `username` | String(255) | Reddit username. Primary key. |
| `last_fetched_at` | DateTime, nullable | When this author's cross-Reddit comment history was last refreshed. Drives the "Refresh from Reddit" timestamp shown on the author profile page. |
| `total_comments_fetched` | Integer | Running count of comments fetched for this author across all "Refresh from Reddit" runs. |

### Indexes

A composite index `ix_comments_submission_parent` on `(submission_id, parent_id)` accelerates the recursive tree query used to render comment threads. Individual indexes on `comments.author`, `comments.parent_id`, `submissions.subreddit`, and `submissions.created_utc` support fast analytical queries.

Full schema: [`database/schema.sql`](database/schema.sql).

---

## Technical Considerations

**Nested comments** are fully expanded via PRAW's `replace_more(limit=None)`. The frontend renders the tree recursively with visual indentation.

**Deleted comments** (null author or body `[deleted]`/`[removed]`) are flagged with `is_deleted = TRUE` and rendered greyed-italic, preserving the thread structure.

**Error handling** maps PRAW exceptions to HTTP responses: 400 for invalid URLs, 404 for missing items, 403 for private subreddits, 502 for Reddit API issues. PRAW's built-in throttle handles rate limiting automatically.

**Data persistence and accumulation.** The MySQL volume persists across container restarts (`docker compose down` keeps the data). Crawling additional URLs adds to the existing dataset rather than replacing it. To reset, use `docker compose down -v`.

---

## Analytics Discussion

The discussion document at [`docs/analytics.md`](docs/analytics.md) outlines how the collected Reddit data can support future analytics. Once comments, authors, timestamps, scores, and reply relationships are stored in a structured format, the data can be analysed to generate deeper insights into discussion content, user behaviour, engagement patterns, and interaction structures.

Six analytics areas are covered, each with their purpose, insights derived, value, and the technologies/frameworks/methodologies that would be applied:

| Area | Methods & Tools |
|---|---|
| **Sentiment Analysis** | Text preprocessing using `comments.body`, VADER baseline, BERT-based models for context handling, Pandas for aggregation by `comments.submission_id`, `comments.author`, `comments.created_utc`, and `comments.score` |
| **Topic Modelling** | Text preprocessing using `comments.body`, LDA with count-based features, TF-IDF keyword analysis, BERTopic for embedding-based clustering, Scikit-learn / Gensim |
| **User Behaviour Analysis** | SQL aggregation queries on `comments.author`, `comments.id`, `comments.parent_id`, and `comments.score`; reply count derived by counting rows where another comment's `parent_id` references the comment |
| **Engagement Analytics** | SQL ranking queries using `comments.score`, derived reply count from `comments.parent_id`, engagement score such as `score + reply_count`, Pandas, Matplotlib / Plotly / Chart.js |
| **Temporal Activity Analysis** | Timestamp analysis using `comments.created_utc`, conversion to SGT for display, SQL timestamp grouping, Pandas time-series resampling, visualisation libraries |
| **Network Graph Analysis** | Parent-child relationships using `comments.parent_id`, NetworkX graph construction, degree centrality, PyVis / Gephi for visualisation |

These analytics features are optional extensions to the core crawler. They demonstrate how the structured Reddit data captured by this application can support broader analytical use cases beyond data extraction.

---

## Containerisation

The application is fully containerised. The `Dockerfile` builds the FastAPI app image and `docker-compose.yml` orchestrates the app container alongside a MySQL 8 container with persistent volume storage. See [Quick Start (Docker)](#quick-start-docker) above for the commands to run it.

---

## Use of AI Tools

AI assistants (Claude, ChatGPT) were used to brainstorm ideas, explore approaches, and assist with code generation. The candidate reviewed and verified all output to ensure the final implementation reflects the intended design and requirements.

---

## Tech Stack

#### Frontend
[![HTML5](https://img.shields.io/badge/HTML5-E34F26.svg?style=for-the-badge&logo=HTML5&logoColor=white)](https://developer.mozilla.org/en-US/docs/Web/Guide/HTML/HTML5)
[![CSS3](https://img.shields.io/badge/CSS3-1572B6.svg?style=for-the-badge&logo=CSS3&logoColor=white)](https://developer.mozilla.org/en-US/docs/Web/CSS)
[![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E.svg?style=for-the-badge&logo=JavaScript&logoColor=black)](https://developer.mozilla.org/en-US/docs/Web/JavaScript)

#### Backend
[![Python](https://img.shields.io/badge/Python-3776AB.svg?style=for-the-badge&logo=Python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688.svg?style=for-the-badge&logo=FastAPI&logoColor=white)](https://fastapi.tiangolo.com/)
[![Uvicorn](https://img.shields.io/badge/Uvicorn-499848.svg?style=for-the-badge&logo=Gunicorn&logoColor=white)](https://www.uvicorn.org/)
[![Pydantic](https://img.shields.io/badge/Pydantic-E92063.svg?style=for-the-badge&logo=Pydantic&logoColor=white)](https://docs.pydantic.dev/)

#### Database
[![MySQL](https://img.shields.io/badge/MySQL-4479A1.svg?style=for-the-badge&logo=MySQL&logoColor=white)](https://www.mysql.com/)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-D71F00.svg?style=for-the-badge&logo=SQLAlchemy&logoColor=white)](https://www.sqlalchemy.org/)

#### API Integration
[![Reddit](https://img.shields.io/badge/Reddit%20API-FF4500.svg?style=for-the-badge&logo=Reddit&logoColor=white)](https://www.reddit.com/dev/api/)
[![PRAW](https://img.shields.io/badge/PRAW-FF4500.svg?style=for-the-badge&logo=Reddit&logoColor=white)](https://praw.readthedocs.io/)

#### Containerisation
[![Docker](https://img.shields.io/badge/Docker-2496ED.svg?style=for-the-badge&logo=Docker&logoColor=white)](https://www.docker.com/)
