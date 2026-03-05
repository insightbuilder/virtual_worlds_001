# AI Memory Engines: Cognee vs Graphiti for Minimal Compute

Based on our exploration of Cognee and Zep Graphiti via their Quickstart guides and simple testing, here are our findings:

## Cognee
**Best for minimal compute:** Cognee is highly suited for minimal server setups because it runs entirely locally (using SQLite, NetworkX, and LanceDB) by default. You do not need to stand up separate databases or Docker containers to run it.

**Requirements:** Even in its minimal configuration, Cognee requires an LLM Provider and an Embedding model to extract knowledge semantics from documents. We have configured it to connect to your local **LM Studio** instance to run completely offline without API usage.

## Zep Graphiti
**Heavier compute requirements:** Graphiti explicitly requires a running **Neo4j 5.26+** instance (either via Neo4j Desktop or Docker) to function. Unlike Cognee, it does not default to an in-memory or file-based property graph out of the box. 

**Conclusion:** Graphiti is not recommended if you have minimal server compute, since running Neo4j will require a dedicated JVM footprint that can be memory-heavy.

## LM Studio Setup (Cognee)
To use Cognee with LM Studio:
1. Open LM Studio.
2. Load an LLM (e.g., Llama 3 or Mistral).
3. Load an Embedding model (e.g., nomic-embed-text) if supported, or rely on a standard embedding model. *(Note: Cognee requires both Text Generation and Embeddings to function properly).*
4. Start the Local Server in LM Studio (typically on port 1234).
5. Run the `test_cognee.py` script.
