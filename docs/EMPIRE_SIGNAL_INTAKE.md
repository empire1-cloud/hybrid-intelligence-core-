# Empire-1 Signal Intake

`POST /api/empire1/intake/map` converts an outside product, repository, article, customer request, or feature idea into an Empire-1 build directive.

The route enforces the founder's standing operating rule:

> WE EVOLVE. NEVER DELETE. FINISH COMPLETE PRODUCT LOOPS, NOT SLICES.

It does not create repositories or new universes. It maps the signal to the strongest existing Empire-1 lane, names supporting lanes, identifies reusable capabilities, attaches a revenue path, and states the evidence required before work can be called finished.

## Example

```bash
curl -X POST http://127.0.0.1:8001/api/empire1/intake/map \
  -H 'Content-Type: application/json' \
  -d '{
    "title": "Vocal Architectures",
    "summary": "Expressive singing and vocal-control architecture for creators",
    "source_type": "research"
  }'
```

The expected primary placement is Lyrica 3 inside Empire-1, supported by Soulfire, Cultura, Archisynapse, and HIC. No standalone company or repository is created automatically.
