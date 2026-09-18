from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import asyncio

from services.rag.ingest import ingest_directory


if __name__ == "__main__":
    result = asyncio.run(ingest_directory(ROOT / "knowledge", "texas-college"))
    print(f"Indexed knowledge base: {result}")
