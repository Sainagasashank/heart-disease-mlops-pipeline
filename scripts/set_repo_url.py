"""Replace the README repository placeholder with the supplied repository URL."""

import argparse
from pathlib import Path

README = Path(__file__).resolve().parent.parent / "README.md"
PLACEHOLDER = "REPO_URL_TO_BE_FILLED"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("url")
    url = parser.parse_args().url.rstrip("/")
    text = README.read_text(encoding="utf-8").replace(PLACEHOLDER, url)
    README.write_text(text, encoding="utf-8")
    print(f"Updated {README}")


if __name__ == "__main__":
    main()
