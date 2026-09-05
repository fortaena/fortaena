# T6 Live-source testing — status after Jina probe

## Validated
- EOC: partial success, 2/3 real articles; keep
- AARO: full table parsed, 8 case-resolution reports with PDF links
- NASA/CIA FOIA: reachable, no direct useful JSON API from this env

## Blocked
- NUFORC: Cloudflare JS challenge; static `httpx` cannot bypass

## Decision
Proceed with EOC + AARO ingestion paths.
Skip NUFORC for now unless headless scraping is added.
