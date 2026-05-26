# Egyptian Statute Corpus

Each `*.json` file describes one Egyptian law and a representative subset of its articles.

## File schema

```json
{
  "law_number": 82,
  "year": 2002,
  "short_code": "82/2002",
  "title_ar": "قانون حماية حقوق الملكية الفكرية",
  "title_en": "Law on the Protection of Intellectual Property Rights",
  "domain_tags": ["ip", "patents", "trademarks"],
  "articles": [
    {
      "number": "113",
      "text_ar": "…",
      "text_en": "…",
      "tags": ["trademarks", "infringement"]
    }
  ]
}
```

## Files

| Short Code | Domain | Notes |
|---|---|---|
| `82/2002` | IP Rights | **First Use Case** — deepest coverage (10 articles) |
| `131/1948` | Civil Code | Contracts, obligations, property |
| `13/1968` | Civil & Commercial Procedures | Court process, deadlines |
| `17/1999` | Commercial Code | Business disputes |
| `12/2003` | Labour Law | Employment disputes |
| `151/2020` | Personal Data Protection | Data, privacy |
| `181/2018` | Consumer Protection | B2C disputes |
| `159/1981` | Companies Law | Corporate matters |

## Coverage

This scaffold ships 5–10 representative articles per law. Full digitization
of the codes is deferred to a separate workstream. The Arabic text is the
controlling original; English text is an aid for the simulation prompts.

## Loading

The corpus loads idempotently on backend startup via
`backend/app/corpus_loader.py`. Re-runs upsert by `(law_number, year)` and
`(statute_id, article_number)`.

To re-seed:

```sh
make seed
```
