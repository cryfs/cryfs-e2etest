from cryfs.e2etest import e2etest_app
import sys


def main() -> None:
    e2etest_app.create_instance()
    app = e2etest_app.get_instance()
    app.setupUncaughtExceptionHandler()
    app.start()
    sys.exit(0)


if __name__ == '__main__':
    main()
