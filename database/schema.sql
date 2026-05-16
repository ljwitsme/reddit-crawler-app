CREATE TABLE IF NOT EXISTS submissions (
    id VARCHAR(20) PRIMARY KEY,
    title TEXT NOT NULL,
    author VARCHAR(255) NULL,
    subreddit VARCHAR(255) NOT NULL,
    selftext MEDIUMTEXT NULL,
    url TEXT NOT NULL,
    score INT DEFAULT 0,
    num_comments INT DEFAULT 0,
    created_utc DATETIME NOT NULL,
    crawled_at DATETIME NOT NULL,
    INDEX ix_submissions_subreddit (subreddit),
    INDEX ix_submissions_created_utc (created_utc)
) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS comments (
    id VARCHAR(20) PRIMARY KEY,
    submission_id VARCHAR(20) NOT NULL,
    parent_id VARCHAR(20) NULL,
    author VARCHAR(255) NULL,
    body MEDIUMTEXT NULL,
    score INT DEFAULT 0,
    created_utc DATETIME NOT NULL,
    is_deleted BOOLEAN DEFAULT FALSE,
    submission_title TEXT NULL,
    submission_subreddit VARCHAR(255) NULL,
    FOREIGN KEY (submission_id) REFERENCES submissions(id) ON DELETE CASCADE,
    INDEX ix_comments_submission_id (submission_id),
    INDEX ix_comments_parent_id (parent_id),
    INDEX ix_comments_author (author),
    INDEX ix_comments_submission_parent (submission_id, parent_id)
) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS authors (
    username VARCHAR(255) PRIMARY KEY,
    last_fetched_at DATETIME NULL,
    total_comments_fetched INT DEFAULT 0
) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;