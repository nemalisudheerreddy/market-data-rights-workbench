# Market Data Rights Workbench

Read `docs/product-spec.md` before making architectural changes.

Current implementation:

- React + TypeScript + Material UI
- FastAPI + Python
- SQLite
- BM25 lexical retrieval
- OpenAI provider
- Local document storage

Rules:

1. Never expose OPENAI_API_KEY to the frontend.
2. Never commit `.env`, SQLite databases, uploads or corpus files.
3. Do not fabricate contractual rights.
4. Contract silence does not imply permission.
5. Entitlement does not prove contractual authorization.
6. Preserve filename and PDF page provenance.
7. Deterministic logic handles parsing, hashes and precedence.
8. LLM logic handles interpretation and explanation.
9. Add tests with every feature.
10. Implement one phase at a time and keep the application runnable.