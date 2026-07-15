"""Allow `python -m thekey`."""

from .cli import main

if __name__ == "__main__":
    raise SystemExit(main())
