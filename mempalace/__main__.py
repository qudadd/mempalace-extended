"""Allow `python -m mempalace` to run the CLI without runpy warnings."""

from .cli import main


if __name__ == "__main__":
    main()
