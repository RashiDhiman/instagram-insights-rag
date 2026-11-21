# Instagram Insights RAG

A static, local **hybrid Retrieval-Augmented Generation (RAG)** prototype built over exported Instagram data.

## What it does
- Ingests the supplied CSV exports for reels, stories and posts.
- Creates one semantic document per export record, preserving source IDs.
- Stores all normalized records and numerical metrics in SQLite.
- Generates text embeddings with `sentence-transformers/all-MiniLM-L6-v2`.
- Stores embeddings and metadata in a persistent ChromaDB collection.
- Routes supported numerical questions to SQL; semantic questions use vector retrieval.
- Optionally sends retrieved evidence to an OpenAI chat model to synthesize a grounded answer.
- Includes a Streamlit interface and an evaluation question set.

## Architecture

```text
Instagram CSV exports
       |
       v
Data ingestion + normalization
       |
       +--------------------+
       |                    |
       v                    v
SQLite (records/metrics)   Text embedding model
       |                    |
       |                    v
       |                ChromaDB
       |                    |
       +--------+-----------+
                |
         Question router
           /         \
          v           v
      SQL query    Vector retrieval
          \           /
           v         v
       Evidence / context
                |
       Optional LLM synthesis
                |
       Answer + source IDs
```

## Run locally

### Requirements
Python 3.10+ recommended.

### 1. Set up
```bash
python -m venv .venv
# Windows
.venv\\Scripts\\activate
# macOS/Linux
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Data
The `data/` directory contains:
- `reels_dataset.csv` (43 rows)
- `stories_dataset.csv` (56 rows)
- `posts_dataset.csv` (139 export entries)

These are export records, not guaranteed unique content objects. Story text can be incomplete, and post export entries may represent repeated media/metadata records.

### 3. Validate and load structured data
```bash
python -m src.validate
```
This audits records and creates `storage/instagram.db`.

### 4. Build vector index
```bash
python -m src.ingest
```
The first run downloads the sentence-transformer model if it is not already cached. It creates `storage/chroma/`.

### 5. Ask questions
```bash
python -m src.query "Which reel had the highest reach?"
python -m src.query "Find reels about non-technical Google career pathways"
```

### 6. Optional LLM generation
Copy `.env.example` to `.env`, then set `OPENAI_API_KEY` and `OPENAI_MODEL`.
Without an API key, semantic queries still retrieve records and show the evidence; the app does not pretend that retrieval-only output is an LLM-generated synthesis.

### 7. Optional web app
```bash
streamlit run app.py
```

## Example questions
- Which reel had the highest reach?
- What is the average reach across reels?
- Find content about Google career pathways.
- Find stories about impersonation or scams.
- Find posts mentioning food at Google.

## Evaluation
See [`evaluation_questions.md`](evaluation_questions.md). It includes structured-query checks, semantic retrieval checks and a manual evaluation rubric. Do not claim retrieval accuracy or faithfulness scores until the test set has been labelled and run.

## Design choices
- **Document-based chunking:** one Instagram export record is the initial retrieval unit. Captions are generally short and self-contained; splitting them further would risk losing context.
- **Metadata vs embeddings:** semantic text is embedded; dates, source IDs and metrics are retained in SQLite and selected Chroma metadata. Numerical questions are answered with SQL rather than vector similarity.
- **Hybrid retrieval:** semantic search handles meaning-based discovery; SQL handles exact aggregation and ranking.
- **Source traceability:** every record retains a stable ID such as `reels_12` so retrieved evidence can be inspected.

## Limitations
- Static snapshot only; it does not sync live Instagram data.
- Instagram API ingestion, webhooks, scheduled refresh, authentication, monitoring and deployment are out of scope for Version A.
- The semantic model is a general-purpose embedding model, not fine-tuned on Instagram-specific language.
- The SQL question router intentionally supports a limited set of metric questions; it is not a general natural-language-to-SQL agent.
- Metrics may be missing and export-level totals may not reconcile with account-level insights.


## Smoke tests
```bash
python -m src.validate
python -m src.query "Which reel had the highest reach?"
python -m src.query "What is the average reach across reels?"
```
The automated tests in `tests/` can be run with `pytest`. Structured SQL tests do not need the embedding model. Semantic retrieval requires the dependencies in `requirements.txt` and a first-run model download.
