import argparse
from . import run


def main():
    parser = argparse.ArgumentParser(description="Run OPC UA simulators")
    parser.add_argument(
        "--mode",
        type=str,
        default="oil",
        choices=["oil", "life", "discrete", "all"],
        help="Which simulator to run: 'oil', 'life', or 'all'",
    )
    args = parser.parse_args()
    run(mode=args.mode)


if __name__ == "__main__":
    main()
