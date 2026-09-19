import argparse
from pathlib import Path

from app.services.ai.member1.rag import ingest_directory


def main() -> None:
    parser = argparse.ArgumentParser(description="Index the canonical Member 1 knowledge corpus into ChromaDB.")
    parser.add_argument("organization_id")
    parser.add_argument("--directory", default=str(Path(__file__).resolve().parents[1] / "knowledge"))
    args = parser.parse_args()
    print(ingest_directory(args.directory, args.organization_id))


if __name__ == "__main__":
    main()