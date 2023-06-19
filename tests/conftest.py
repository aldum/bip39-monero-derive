
def pytest_addoption(parser):
    parser.addoption(
        "--run-equivalence-tests",
        action="store_true",
        default=False,
        help="Run utility equivalence tests",
    )

    parser.addoption(
        "--run-curses-test",
        action="store_true",
        default=False,
        help="Run UI test",
    )
