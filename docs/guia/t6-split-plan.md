# T6 Live-source testing — split plan

## Subtask T6.1: EOC live dry-run
- Status: ✅ partial
- Result: 2/3 URLs usable; 1 category page returned 51 words
- Action: keep scraper, do not block pipeline

## Subtask T6.2: NUFORC live dry-run
- Status: 🔴 blocked
- Result: HTTP 403 + Cloudflare challenge HTML
- Root cause: site requires JS challenge; static httpx cannot pass
- Action: do NOT burn retries. Mark as “requires headless/playwright or alternate endpoint”
- Fallback options:
  1) Try `https://www.nuforc.org/databank/` with a browser-driven session
  2) Skip NUFORC for now; continue with EOC + gov sources

## Subtask T6.3: Gov sources discovery
- Status: ⏳ pending
- Next: inspect `gov_scraper.py` for endpoints and run a 1-request probe

## Subtask T6.4: Validation + normalization
- Status: ⏳ pending
- Dependencies: T6.1 (EOC) complete; T6.2/T6.3 results
- Action: add schema validation after fetch; reject bad payloads

## Subtask T6.5: Rate-limit + backoff hardening
- Status: ⏳ pending
- Action: 429/403 handling, exponential backoff, circuit breaker
