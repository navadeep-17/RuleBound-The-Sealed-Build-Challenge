from __future__ import annotations

import argparse
from pathlib import Path
import sys

# Ensure root package is discoverable
ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from run import process_rooms


def main() -> None:
    parser = argparse.ArgumentParser(description="RuleBound Python Runner")
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    sys.exit(process_rooms(args.input, args.output))


if __name__ == "__main__":
    main()
