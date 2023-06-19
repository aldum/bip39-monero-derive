
def pytest_addoption(parser):
    parser.addoption(
        "--run-equivalence-tests",
        action="store_true",
        default=False,
        help="Run utility equivalence tests",
    )
