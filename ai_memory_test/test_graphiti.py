import asyncio
import os
import json
from datetime import datetime, timezone
from graphiti_core import Graphiti
from graphiti_core.nodes import EpisodeType

async def main():
    # Graphiti requires Neo4j connection parameters. 
    neo4j_uri = os.environ.get('NEO4J_URI', 'bolt://localhost:7687')
    neo4j_user = os.environ.get('NEO4J_USER', 'neo4j')
    neo4j_password = os.environ.get('NEO4J_PASSWORD', 'testpassword')
    
    try:
        print(f"Attempting to connect to Neo4j at {neo4j_uri}...")
        graphiti = Graphiti(neo4j_uri, neo4j_user, neo4j_password)
        await graphiti.build_indices_and_constraints()
        
        episodes = [
            {
                'content': 'Graphiti is a Python framework for building temporally-aware knowledge graphs.',
                'type': EpisodeType.text,
                'description': 'docs'
            }
        ]
        
        for i, episode in enumerate(episodes):
            print(f"Adding episode {i}")
            await graphiti.add_episode(
                name=f'test_doc_{i}',
                episode_body=episode['content'],
                source=episode['type'],
                source_description=episode['description'],
                reference_time=datetime.now(timezone.utc),
            )
            
        print("Searching for: 'What is Graphiti?'")
        results = await graphiti.search('What is Graphiti?')
        print("\n--- Graphiti Results ---")
        for result in results:
            print(f"UUID: {result.uuid}, Fact: {result.fact}")
            
    except Exception as e:
        print(f"Graphiti test failed (likely requires Neo4j running): {e}")
    finally:
        try:
            await graphiti.close()
        except:
            pass

if __name__ == '__main__':
    asyncio.run(main())
