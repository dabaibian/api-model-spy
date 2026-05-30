# Model Signatures Database

Known model characteristics used by `analyze.py` to fingerprint API responses.

## OpenAI Models

| Model | Tier | Cutoff | Strawberry | 9.11 vs 9.9 | Reasoning Tokens |
|---|---|---|---|---|---|
| GPT-3.5 Turbo | budget | ~2021-09 | FAIL | FAIL | No |
| GPT-4 | premium | ~2023-04 | PASS | PASS | No |
| GPT-4 Turbo | premium | ~2023-12 | PASS | PASS | No |
| GPT-4o | mid | ~2023-10 | PASS | PASS | No |
| GPT-4o Mini | budget | ~2023-10 | FAIL | FAIL | No |
| o1 | premium+ | ~2024-06 | PASS | PASS | **Yes** |

## Anthropic Models

| Model | Tier | Cutoff | Strawberry | 9.11 vs 9.9 | Reasoning Tokens |
|---|---|---|---|---|---|
| Claude 3 Haiku | budget | ~2024-03 | FAIL | PASS | No |
| Claude 3 Sonnet | mid | ~2024-03 | PASS | PASS | No |
| Claude 3 Opus | premium | ~2024-03 | PASS | PASS | No |
| Claude 3.5 Sonnet | mid | ~2024-04 | PASS | PASS | No |
| Claude 3.5 Haiku | budget | ~2024-07 | FAIL | PASS | No |
| Claude Sonnet 4 | mid | ~2025-03 | PASS | PASS | No |
| Claude Opus 4 | premium | ~2025-03 | PASS | PASS | No |

## Google Models

| Model | Tier | Cutoff | Strawberry | 9.11 vs 9.9 | Reasoning Tokens |
|---|---|---|---|---|---|
| Gemini 1.5 Pro | mid | ~2023-11 | PASS | PASS | No |
| Gemini 1.5 Flash | budget | ~2023-11 | FAIL | PASS | No |

## Other Models

| Model | Provider | Tier | Strawberry | 9.11 vs 9.9 | Reasoning Tokens |
|---|---|---|---|---|---|
| Llama 3 70B | Meta | mid-low | FAIL | FAIL | No |
| Mistral Large | Mistral AI | mid | PASS | PASS | No |

## Tier Definitions

| Tier | Rank | Description |
|---|---|---|
| budget | 1 | Cheapest models, lower reasoning ability |
| mid-low | 2 | Decent quality, open-source tier |
| mid | 3 | Good quality, balanced cost/performance |
| premium | 4 | High-end models with strong reasoning |
| premium+ | 5 | Top-tier models with advanced capabilities |

## Key Probes

- **Strawberry test**: "How many r's in strawberry?" — weaker models often say 2 instead of 3
- **9.11 vs 9.9**: "Which is larger?" — weaker models often say 9.11
- **Reasoning tokens**: Only o1/o3-class models include `reasoning_tokens` in usage stats
- **Knowledge cutoff**: Different models have different training data recency
- **Self-identity**: Some models will reveal their name when asked directly
