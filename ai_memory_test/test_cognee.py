import cognee
import asyncio
import os

# Configure Cognee to use LM Studio's local server via LiteLLM's OpenAI compatibility
os.environ["LLM_PROVIDER"] = "openai" 
os.environ["LLM_API_KEY"] = "lm-studio"
os.environ["LLM_ENDPOINT"] = "http://localhost:1234/v1"
os.environ["LLM_MODEL"] = "openai/local-model" # Required prefix for LiteLLM to route correctly

# For embeddings, LM Studio also provides an OpenAI compatible endpoint
os.environ["EMBEDDING_PROVIDER"] = "openai"
os.environ["OPENAI_EMBEDDING_API_KEY"] = "lm-studio"
os.environ["OPENAI_EMBEDDING_API_BASE"] = "http://localhost:1234/v1"
os.environ["EMBEDDING_MODEL"] = "text-embedding-3-small" # Bypasses TikToken validation, routed to local by LM Studio

import cognee
from cognee.infrastructure.llm import get_llm_config
from cognee.infrastructure.databases.vector import get_vectordb_config

# Set text generation endpoints
llm_config = get_llm_config()
llm_config.llm_api_key = "lm-studio"
llm_config.llm_endpoint = "http://localhost:1234/v1"

# Set vector dimension explicitly (e.g. nomic is 768, OpenAI text-embedding-3-large is default 3072)
vectordb_config = get_vectordb_config()
vectordb_config.vector_db_embedding_dimensions = 768

async def main():
    print("Initializing Cognee clean slate...")
    await cognee.prune.prune_data()
    await cognee.prune.prune_system(metadata=True)
    
    # Add sample content
    text = "Cognee turns documents into AI memory. It allows for graph based semantic search."
    print(f"Adding text: {text}")
    await cognee.add(text)
    
    # Process with LLMs to build the knowledge graph
    print("Cognifying data (building knowledge graph)...")
    await cognee.cognify()
    
    # Search the knowledge graph
    print("Searching graph for 'What does Cognee do?'...")
    results = await cognee.search(
        query_text="What does Cognee do?"
    )
    
    print("\n--- Cognee Results ---")
    for result in results:
        print(result)

if __name__ == '__main__':
    asyncio.run(main())
