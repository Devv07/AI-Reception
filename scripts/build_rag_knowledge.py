from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from services.rag.knowledge_base import knowledge_base


if __name__ == "__main__":
    knowledge_base.index_documents()
    print(f"Indexed knowledge base from: {knowledge_base.persist_directory}")
