# Analytics & Insights — Reddit Data

In this document I discuss the analytical approaches I would apply to data collected by this crawler, with an internal-security audience in mind. My focus is on coordinated behaviour, foreign narrative injection, social cohesion, and early signs of public discontent rather than commercial concerns like brand sentiment.

The brief lists nine analytical areas. I focus on five that I see as most operationally relevant: network analysis, sentiment, topic modelling, temporal patterns, and toxicity and integrity. The remaining four (engagement, trend detection, user behaviour, community interaction) overlap with these and I would treat them as extensions of the same approaches.

---

## Network Graph Analysis

**Insight.** I would treat Reddit replies as a directed graph where each comment connects the commenter to the parent author. From this graph, centrality scores show who is most influential, community detection groups users who interact often, and brokers are users who bridge otherwise separate communities. Tight groups of accounts behaving very similarly can suggest coordination.

**Value.** Influential users and bridging accounts shape how narratives spread. Coordinated groups of accounts acting as one are a classic sign of foreign interference, and catching them early allows a measured response.

**Tools.**
- **Technologies:** I would use NetworkX for small-scale analysis, igraph for larger volumes, and Gephi for visualisation.
- **Frameworks:** A graph-based view where each user is a node and each reply is a directed edge.
- **Methodologies:** I would apply Louvain or Leiden algorithms for community detection, PageRank and betweenness centrality for influence ranking, and HDBSCAN clustering on per-author features (such as active hours and vocabulary patterns) to flag coordinated behaviour.

---

## Sentiment Analysis

**Insight.** I would label each comment as positive, negative, or neutral, then group results by subreddit, time window, or author to see how mood changes across communities.

**Value.** A sudden rise in negative sentiment after a policy announcement is an early sign of public discontent. When the same event triggers very different sentiment across subreddits, I would treat that as a possible signal of coordinated framing.

**Tools.**
- **Technologies:** I would start with VADER (NLTK) as a quick baseline, then move to Hugging Face `transformers` for production models such as `cardiffnlp/twitter-roberta-base-sentiment` or BERT.
- **Frameworks:** Lexicon-based scoring for fast baseline checks; transformer-based contextual classification for production use.
- **Methodologies:** Polarity classification per comment, aggregated by subreddit, time window, or author. Cross-subreddit comparison to detect divergence. I would flag Singlish as a domain challenge — production models would need fine-tuning on locally labelled data.

---

## Topic Modelling

**Insight.** I would use topic modelling to find the themes that emerge from a body of comments without needing predefined categories. Comments are grouped by similarity, producing clusters that reflect what people are actually talking about.

**Value.** This lets me answer questions like "what is r/singapore discussing this week" without assuming the answer in advance. Combined with sentiment, it shows which topics dominate and how people feel about each one. Comparing topics across subreddits also highlights when an issue jumps from a niche community into wider discussion.

**Tools.**
- **Technologies:** I would use BERTopic (sentence-transformers + UMAP + HDBSCAN) for the modern approach, and gensim LDA as a classical baseline.
- **Frameworks:** Unsupervised clustering of comments by semantic similarity to surface latent themes.
- **Methodologies:** For LDA, I would do model selection across a range of topic counts (typically 2 to 20) using coherence and perplexity scoring. For BERTopic, embedding-based clustering with HDBSCAN to produce flexible, variable-size topic groups.

---

## Temporal & Behavioural Analysis

**Insight.** I would run time-series analysis at three levels. Overall volume per subreddit shows where attention is concentrated. Per-user activity patterns show each account's normal behaviour. Event-anchored bursts show how accounts and communities react to outside events.

**Value.** A sudden spike in activity from a previously quiet account is a strong anomaly signal. Constant 24/7 posting with no weekly pattern often points to bots. I would also look at response timing to identify which accounts consistently lead breaking events versus simply follow, which is useful for spotting coordination.

**Tools.**
- **Technologies:** I would use Pandas for time-series work from the indexed `created_utc` column, statsmodels for STL decomposition, and the `ruptures` library for change-point detection.
- **Frameworks:** Time-series decomposition that separates baseline from anomaly, and cross-correlation between accounts to find synchronised behaviour.
- **Methodologies:** Per-user baselining, anomaly detection using z-scores and STL residuals, change-point detection for behavioural shifts, and pairwise correlation of activity over time.

---

## Toxicity & Integrity Analysis

**Insight.** I would classify each comment for toxicity, spam, and similarity to known harmful narratives. Toxic content is flagged with supervised models, spam through a mix of rules and machine learning, and narratives through embedding similarity against a library of known patterns.

**Value.** Toxic communities are more vulnerable to radicalisation pipelines. When narratives that started on extremist or foreign-state platforms appear in Singapore-context subreddits, I would treat that crossover as a useful signal in itself — both the content and where it came from matter.

**Tools.**
- **Technologies:** I would use Google's Perspective API for cloud-based toxicity classification, or Detoxify for an offline option. sentence-transformers for narrative embeddings, and scikit-learn for the supervised spam classifier.
- **Frameworks:** Multi-class classification (toxic, spam, narrative match) with a human review step before any action is taken.
- **Methodologies:** Supervised toxicity classification, hybrid rule-and-ML spam detection (link ratio, account age, repeated content), and cosine-similarity matching of comments against a library of known harmful narratives.

---

## References

**Network analysis**
- [NetworkX](https://networkx.org/) — Python library for graph analysis
- [igraph](https://igraph.org/) — high-performance graph library
- [Gephi](https://gephi.org/) — interactive graph visualisation
- [Louvain method](https://en.wikipedia.org/wiki/Louvain_method) — community detection algorithm
- [Leiden algorithm](https://www.nature.com/articles/s41598-019-41695-z) — refined community detection
- [HDBSCAN](https://hdbscan.readthedocs.io/) — density-based clustering

**Sentiment analysis**
- [VADER](https://github.com/cjhutto/vaderSentiment) — lexicon-based sentiment analyser
- [Hugging Face Transformers](https://huggingface.co/docs/transformers) — transformer model library
- [cardiffnlp/twitter-roberta-base-sentiment](https://huggingface.co/cardiffnlp/twitter-roberta-base-sentiment) — social-media sentiment model

**Topic modelling**
- [BERTopic](https://maartengr.github.io/BERTopic/) — transformer-based topic modelling
- [gensim](https://radimrehurek.com/gensim/) — classical topic modelling library
- [sentence-transformers](https://www.sbert.net/) — sentence embedding models
- [UMAP](https://umap-learn.readthedocs.io/) — dimensionality reduction

**Temporal analysis**
- [Pandas](https://pandas.pydata.org/) — data manipulation and time series
- [statsmodels](https://www.statsmodels.org/) — statistical models including STL
- [ruptures](https://centre-borelli.github.io/ruptures-docs/) — change-point detection

**Toxicity & integrity**
- [Perspective API](https://perspectiveapi.com/) — toxicity classification (Google)
- [Detoxify](https://github.com/unitaryai/detoxify) — offline toxicity classifier
- [scikit-learn](https://scikit-learn.org/) — machine learning library

**Scale & infrastructure**
- [DuckDB](https://duckdb.org/) — in-process analytical database
- [ClickHouse](https://clickhouse.com/) — columnar analytical database
- [Apache Spark](https://spark.apache.org/) — distributed compute framework
- [Dask](https://www.dask.org/) — parallel computing in Python