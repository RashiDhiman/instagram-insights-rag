# Evaluation set

Use these questions after indexing. The first group tests deterministic structured operations; the second group tests semantic retrieval.

## Structured query checks
1. Which reel had the highest reach?
2. What is the average reach across reels?
3. How many reel records are indexed?
4. How many story records are indexed?

Expected behavior:
- Return exact calculations from SQLite, not from an LLM's guessed arithmetic.
- State the population used in the calculation.
- Include the source record ID for ranking questions.
- Do not imply that exported post rows are necessarily unique published posts.

## Semantic retrieval checks
1. Find reels about non-technical career opportunities.
2. Find content discussing Google career pathways.
3. Find stories about account impersonation or scams.
4. Find posts mentioning food at Google.

Expected behavior:
- Retrieve source records whose text is relevant to the query.
- Display source IDs and retrieved text.
- If evidence is weak or absent, say so rather than inventing an answer.

## Manual evaluation rubric
Score each semantic query:
- Relevance@5: number of relevant results in top 5 / 5.
- Context precision: proportion of retrieved records that genuinely support the answer.
- Faithfulness: every factual claim in the generated answer is supported by retrieved evidence.
- Citation correctness: source IDs point to the records used.

Do not report a quality score until queries have been manually labelled and evaluated.
