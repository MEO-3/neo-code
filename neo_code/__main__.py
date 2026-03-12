"""Entry point: python -m neo_code"""

import sys
from neo_code.app import NeoCodeApp


def main() -> None:
    app = NeoCodeApp()
    sys.exit(app.run(sys.argv))


if __name__ == "__main__":
    main()
