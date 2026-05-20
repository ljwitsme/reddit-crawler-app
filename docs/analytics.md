# Use of Different Types of Analytics

## Overview

This section outlines how the Reddit data collected by the crawler can support future analytics. Once comments, authors, timestamps, upvote counts, and reply relationships are stored in a structured format, the data can be analysed to generate deeper insights into discussion content, user behaviour, engagement patterns, and interaction structures.

The following sections focus on six analytics areas that are most relevant to the collected data: **sentiment analysis, topic modelling, user behaviour analysis, engagement analytics, temporal activity analysis, and network graph analysis**.

---

## 1. Sentiment Analysis

### Purpose

Sentiment analysis can be used to understand the overall tone of a Reddit discussion by classifying comments as positive, negative, or neutral.

### Insights that can be derived

- Whether users are generally reacting positively, negatively, or neutrally to a submission
- Whether highly upvoted comments tend to express positive or negative views
- Whether sentiment changes over time as more users join the discussion
- Comments or discussion areas that show stronger emotional reactions

### Value

Reddit discussions can contain a large number of comments, making it difficult to manually understand the overall mood of a thread. Sentiment analysis provides a quick summary of the general reaction towards a topic and can help highlight areas where users may have strong concerns, support, or disagreement.

### Technologies, frameworks, or methodologies

- **Text preprocessing:** Comment text can first be cleaned by removing URLs, extra whitespace, and deleted or removed comments. This ensures that the sentiment model analyses meaningful user-generated text.

- **VADER:** VADER can be used as a lightweight sentiment analysis method because it is designed for short, informal, social media-style text. Each Reddit comment can be assigned a positive, negative, neutral, and compound sentiment score.

- **BERT-based sentiment models:** For a more advanced extension, a transformer-based model can be used to better capture the context of words and phrases in comments. This may be useful for longer or more complex Reddit comments, although sarcasm and irony may still require careful handling.

- **Pandas:** Pandas can be used after sentiment scoring to combine each comment's sentiment result with the fields collected by the crawler, such as comment ID, submission ID, author, timestamp, and upvote count. Using `groupby()` and aggregation, the system can calculate the overall sentiment distribution of a thread, track sentiment changes over time, compare sentiment across authors, and analyse whether highly upvoted comments are generally more positive, negative, or neutral.

---

## 2. Topic Modelling

### Purpose

Topic modelling can be used to identify the main themes being discussed within a Reddit submission or across multiple submissions from the same subreddit.

### Insights that can be derived

- Common topics discussed within a thread
- Repeated concerns, questions, complaints, or suggestions
- Emerging themes across multiple submissions
- Groups of comments that discuss similar issues

### Value

Reddit comments are unstructured text. Topic modelling helps convert large volumes of comments into meaningful themes, allowing users to understand what the discussion is mainly about without reading every comment individually. It is especially useful for posts with many comments or for analysing patterns across multiple submissions in the same subreddit.

### Technologies, frameworks, or methodologies

- **Text preprocessing:** Extract the stored `comment_body` values from the database and clean them by removing URLs, stop words, extra spaces, and deleted or removed comments. This prepares the Reddit comments for analysis by keeping only meaningful discussion content.

- **Latent Dirichlet Allocation:** Convert the cleaned comments into TF-IDF or count-based features, then use LDA to group comments into topics. Each topic can then be reviewed based on its top keywords, and each comment can be assigned to the topic it most closely belongs to.

- **BERTopic:** As a more advanced option, convert comments into sentence embeddings and group semantically similar comments together. This allows the model to detect comments discussing the same idea even if users use different wording.

- **Scikit-learn or Gensim:** Use these libraries to perform the workflow, such as vectorising the cleaned comment text, training the topic model, extracting top keywords per topic, and assigning topic labels back to each comment record.

---

## 3. User Behaviour Analysis

### Purpose

User behaviour analysis can be used to understand how different authors participate in Reddit discussions.

### Insights that can be derived

- Most active users within a submission or subreddit
- Users who frequently start or continue discussions
- Users who receive higher upvotes or replies
- Whether a discussion is driven by a few active users or many different participants

### Value

This provides a clearer view of participation patterns within a Reddit community. For example, it can show whether a thread is dominated by a small group of users or whether engagement is spread across many authors. It also supports the author exploration feature by giving context to an individual author's contribution style.

### Technologies, frameworks, or methodologies

- **SQL aggregation queries:** Use the stored `author`, `comment_id`, `parent_comment_id`, and `upvotes` fields to calculate author-level metrics. For example, SQL can group comments by `author` to calculate each user's total number of comments, total upvotes received, average upvotes per comment, and number of replies received.

- **Reply count calculation:** Use the `parent_comment_id` field to count how many times each user's comments are replied to. This helps identify users who trigger further discussion, not just users who post frequently.

- **Pandas:** Load the SQL results into a DataFrame to compare author-level metrics more easily. For example, Pandas can be used to sort users by activity level, calculate engagement averages, and separate highly active users from occasional commenters.

---

## 4. Engagement Analytics

### Purpose

Engagement analytics can be used to identify which submissions or comments receive the most attention from users.

### Insights that can be derived

- Most upvoted comments
- Comments with the highest number of replies
- Submissions with high discussion activity
- Relationship between comment sentiment and upvote count
- Authors whose comments consistently receive stronger engagement

### Value

Engagement signals can help identify comments that are influential, controversial, informative, or strongly supported by the community. Upvotes may indicate agreement or usefulness, while reply counts may suggest that a comment has triggered further discussion or debate.

### Technologies, frameworks, or methodologies

- **SQL ranking queries:** Use the stored `comment_id`, `submission_id`, and `upvotes` fields to rank comments by upvote count. This helps identify comments that received the strongest direct engagement from users.

- **Engagement score:** Create a simple engagement score using available metrics, such as `upvotes + reply_count`. This allows comments to be ranked using both upvote-based engagement and reply-based engagement.

- **Pandas:** Load the engagement results into a DataFrame to compare engagement across comments, authors, or submissions. For example, Pandas can be used to calculate top comments by engagement score, average upvotes per submission, and authors whose comments receive higher engagement.

- **Matplotlib, Plotly, or Chart.js:** Use these tools to present engagement insights through ranked tables, bar charts, or dashboards. For example, the interface can display the top 10 most upvoted comments, comments with the most replies, or submissions with the highest total engagement.

---

## 5. Temporal Activity Analysis

### Purpose

Temporal activity analysis can be used to study how Reddit discussions develop over time.

### Insights that can be derived

- When users are most active
- How quickly a submission receives comments after being posted
- Whether discussion activity increases, decreases, or peaks at certain times
- Comment volume by hour, day, or time period
- Whether a post receives short-term attention or continues attracting discussion over a longer period

### Value

This helps explain the lifecycle of a Reddit discussion. Some posts may receive most of their engagement shortly after submission, while others may continue attracting comments over several days. Understanding activity patterns can help users identify peak discussion periods and how attention around a topic changes over time.

### Technologies, frameworks, or methodologies

- **Timestamp conversion:** Reddit timestamps can be converted to Singapore Time before analysis, which aligns with the project requirement to store date and time in SGT.

- **SQL timestamp grouping:** SQL can be used to group comments by hour, day, or date range. This helps identify when discussion activity is highest.

- **Pandas time-series grouping:** Pandas can be used to resample comment timestamps and analyse comment volume over time. This supports insights such as peak activity periods and how quickly a post gains traction.

- **Matplotlib, Plotly, or Chart.js:** These tools can be used to visualise comment activity using line charts or bar charts, making it easier for users to understand how discussion activity changes over time.

---

## 6. Network Graph Analysis

### Purpose

Network graph analysis can be used to model Reddit discussions as a graph. Users or comments can be represented as nodes, while replies can be represented as edges. This supports community interaction analysis by showing how users and comments are connected within a discussion.

### Insights that can be derived

- Which users are central to a discussion
- Which comments trigger the most follow-up replies
- How conversation threads branch from the original submission
- Whether interaction is concentrated around a few users or spread across many participants
- Clusters of users who frequently interact with one another

### Value

Reddit discussions are not always linear. Comments often branch into nested conversations, making it difficult to understand the structure of the discussion from a simple list of comments. Network graph analysis helps visualise and measure these relationships, making it easier to identify central users, active discussion clusters, and key reply chains.

This also avoids treating community interaction analysis as a completely separate area. Instead, network graph analysis can be positioned as the method used to analyse community interactions.

### Technologies, frameworks, or methodologies

- **Parent-child comment relationships:** The crawler stores parent comment IDs, which can be used to build reply relationships. Each comment can be connected to the comment it replies to, creating the structure needed for graph analysis.

- **NetworkX:** NetworkX can be used to build a graph where users or comments are represented as nodes, and replies are represented as edges. This allows the system to analyse how Reddit discussions branch and how users interact.

- **Graph metrics:** Metrics such as degree centrality can be used to identify highly connected users or comments. For example, a user with many incoming replies may be central to the discussion, while a comment with many child comments may have triggered significant follow-up discussion.

- **PyVis or Gephi:** These tools can be used to visualise the reply network. This helps users explore community interaction patterns more intuitively instead of reading comments only as a flat list.

---

## Conclusion

Overall, the collected Reddit data provides a strong foundation for future analytics. By applying sentiment analysis, topic modelling, user behaviour analysis, engagement analytics, temporal activity analysis, and network graph analysis, the application can generate deeper insights into Reddit discussions, user participation, and interaction patterns.

These analytics features are optional extensions, but they show how the crawler can support broader analytical use cases beyond data extraction.

---

## References

1. PRAW Documentation. *PRAW: The Python Reddit API Wrapper*. Used as a reference for Reddit API access through Python.  
   https://praw.readthedocs.io/

2. Hutto, C. J., & Gilbert, E. (2014). *VADER: A Parsimonious Rule-Based Model for Sentiment Analysis of Social Media Text*. Used as a reference for social media sentiment analysis.  
   https://ojs.aaai.org/index.php/ICWSM/article/view/14550

3. BERTopic Documentation. *BERTopic: Topic Modeling with Transformers and c-TF-IDF*. Used as a reference for embedding-based topic modelling.  
   https://maartengr.github.io/BERTopic/index.html

4. NetworkX Documentation. *NetworkX: Network Analysis in Python*. Used as a reference for graph and network analysis.  
   https://networkx.org/

5. NetworkX Documentation. *Degree Centrality*. Used as a reference for identifying highly connected nodes in a graph.  
   https://networkx.org/documentation/stable/reference/algorithms/generated/networkx.algorithms.centrality.degree_centrality.html

6. Pandas Documentation. *Time Series / Resampling*. Used as a reference for time-based grouping and temporal activity analysis.  
   https://pandas.pydata.org/docs/user_guide/timeseries.html