from cryfs.e2etest import Application
import sys


def main() -> None:
    Application.create_instance()
    app = Application.get_instance()
    app.setupUncaughtExceptionHandler()
    sys.exit(app.run())

if __name__ == '__main__':
    main()
