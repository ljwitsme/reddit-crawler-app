# Reddit Crawler — MHA ISD Assignment

A web application that crawls Reddit submissions and comments, stores them in MySQL, and presents them through a dashboard interface.

---

## Table of Contents
- [Features](#features)
- [Project Structure](#project-structure)
- [Installation Guide](#installation-guide)
  - [Prerequisites](#prerequisites)
  - [MySQL Setup](#mysql-setup)
  - [Reddit API Credentials](#reddit-api-credentials)
  - [Environment Configuration](#environment-configuration)
  - [Install Dependencies](#install-dependencies)
- [Step to Run Codes Locally](#step-to-run-codes-locally)
- [Usage](#usage)
- [Database Schema](#database-schema)
- [Use of AI Tools](#use-of-ai-tools)
- [Tech Stack](#tech-stack)

---

## Features

### Core Requirements
- Accept any Reddit submission URL and crawl its full data
- Extract submission title, ID, subreddit, author, score, and timestamps
- Extract all comments including nested replies
- Handle deleted and removed comments gracefully
- Display all timestamps in Singapore Standard Time (SGT)
- Store data in MySQL with a relational schema

### Bonus Objective 1
- Batch crawl 50 submissions from any subreddit
- Fetch and display an author's comment history from across Reddit
- Click-through navigation between submissions, authors, and subreddits

### Bonus Objective 2
- Written discussion of analytical approaches in [`docs/analytics.md`](docs/analytics.md)

---

## Project Structure

```
reddit-crawler-app/
├── .env.example
├── requirements.txt
├── run.py
├── backend/
│   ├── config.py
│   ├── database.py
│   ├── api/         (routes + schemas)
│   ├── crawler/     (PRAW client, URL parser, mock + real crawler)
│   ├── db/          (SQLAlchemy models)
│   └── utils/       (timezone conversion)
├── database/
│   └── schema.sql
├── docs/
│   └── analytics.md
└── frontend/        (HTML, CSS, JS pages)
```

---

## Installation Guide

### Prerequisites
- Python 3.11+
- MySQL Server 8.0+
- Reddit account with verified email (for API credentials)

### MySQL Setup
In MySQL Workbench, run as root:

```sql
CREATE DATABASE reddit_crawler_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'reddit_user'@'localhost' IDENTIFIED WITH mysql_native_password BY 'your_password';
GRANT ALL PRIVILEGES ON reddit_crawler_db.* TO 'reddit_user'@'localhost';
FLUSH PRIVILEGES;
```

### Reddit API Credentials
1. Go to <https://www.reddit.com/prefs/apps>
2. Click **create another app**, choose type **script**
3. Set redirect URI to `http://localhost:8000`
4. Note the **client ID** and **client secret**

### Environment Configuration
Copy `.env.example` to `.env` and fill in:

```
REDDIT_CLIENT_ID=<your client ID>
REDDIT_CLIENT_SECRET=<your client secret>
REDDIT_USER_AGENT=reddit-crawler/0.1 by <your username>
DATABASE_URL=mysql+pymysql://reddit_user:your_password@localhost:3306/reddit_crawler_db
USE_MOCK=true
```

Set `USE_MOCK=false` to use real Reddit data once your API credentials are configured.

### Install Dependencies

```bash
python -m venv .venv
.venv\Scripts\activate         # Windows
# source .venv/bin/activate    # Mac/Linux
pip install -r requirements.txt
```

---

## Step to Run Codes Locally

```bash
python run.py
```

The application will be available at:
- **Dashboard:** <http://localhost:8000>
- **API documentation:** <http://localhost:8000/docs>

---

## Usage

| Action | How |
|---|---|
| Crawl a submission | Paste a Reddit URL into the first form, click Crawl |
| Batch crawl 50 posts | Type a subreddit name into the second form, click Crawl 50 posts |
| View author history | Click any username, then "Refresh from Reddit" |
| View subreddit submissions | Click any `r/subreddit` link |

---

## Database Schema

Three tables: `submissions`, `comments`, `authors`. Reddit IDs are used as primary keys to support idempotent upserts. Timestamps are stored as UTC and converted to SGT at the display layer.

Full schema: [`database/schema.sql`](database/schema.sql).

---

## Use of AI Tools

In line with Section 6 of the brief, AI assistants (Claude) were used for boilerplate generation, debugging, and documentation. All design decisions, architecture choices, and the final implementation are owned by the candidate.

---

## Tech Stack

#### Frontend UI
- [![HTML5](https://img.shields.io/badge/HTML5-E34F26.svg?style=for-the-badge&logo=HTML5&logoColor=white)](https://developer.mozilla.org/en-US/docs/Web/Guide/HTML/HTML5)
- [![CSS3](https://img.shields.io/badge/CSS3-1572B6.svg?style=for-the-badge&logo=CSS3&logoColor=white)](https://developer.mozilla.org/en-US/docs/Web/CSS)
- [![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E.svg?style=for-the-badge&logo=JavaScript&logoColor=black)](https://developer.mozilla.org/en-US/docs/Web/JavaScript)
- [![JSON](https://img.shields.io/badge/JSON-000000.svg?style=for-the-badge&logo=JSON&logoColor=white)](https://www.json.org/)

#### Backend
- [![Python](https://img.shields.io/badge/Python-3776AB.svg?style=for-the-badge&logo=Python&logoColor=white)](https://www.python.org/)
- [![FastAPI](https://img.shields.io/badge/FastAPI-009688.svg?style=for-the-badge&logo=FastAPI&logoColor=white)](https://fastapi.tiangolo.com/)
- [![Uvicorn](https://img.shields.io/badge/Uvicorn-499848.svg?style=for-the-badge&logo=Gunicorn&logoColor=white)](https://www.uvicorn.org/)
- [![Pydantic](https://img.shields.io/badge/Pydantic-E92063.svg?style=for-the-badge&logo=Pydantic&logoColor=white)](https://docs.pydantic.dev/)

#### Database
- [![MySQL](https://img.shields.io/badge/MySQL-4479A1.svg?style=for-the-badge&logo=MySQL&logoColor=white)](https://www.mysql.com/)
- [![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-D71F00.svg?style=for-the-badge&logo=SQLAlchemy&logoColor=white)](https://www.sqlalchemy.org/)

#### API Integration
- [![Reddit](https://img.shields.io/badge/Reddit%20API-FF4500.svg?style=for-the-badge&logo=Reddit&logoColor=white)](https://www.reddit.com/dev/api/)
- [![PRAW](https://img.shields.io/badge/PRAW-FF4500.svg?style=for-the-badge&logo=Reddit&logoColor=white)](https://praw.readthedocs.io/)

<br><br>

[![Built for MHA ISD](https://img.shields.io/badge/Built%20for-MHA%20ISD%20%3C%2F%3E-orange?style=for-the-badge)](https://www.mha.gov.sg/)