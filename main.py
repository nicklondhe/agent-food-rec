"""Food Recommendation System - CLI Interface."""

import argparse
import contextlib
import io
import sys

from anthropic import APIError, APIStatusError

from food_rec.orchestrator import FoodRecommendationOrchestrator
from food_rec.outputs import (format_compact_json, format_detailed_text,
                              format_json, format_quick_summary)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Find unique food recommendations for your destination",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py -o "New York" -d "Tokyo" -n 5
  python main.py -o "Paris" -d "Bangkok" --format summary
  python main.py -o "London" -d "Mexico City" --format json --quiet
        """,
    )

    parser.add_argument(
        "-o",
        "--origin",
        required=True,
        help="Origin city/country (where you're traveling from)",
    )
    parser.add_argument(
        "-d",
        "--destination",
        required=True,
        help="Destination city/country (where you're traveling to)",
    )
    parser.add_argument(
        "-n",
        "--target",
        type=int,
        default=10,
        help="Target number of dish recommendations (default: 10)",
    )
    parser.add_argument(
        "--format",
        choices=["summary", "detailed", "json", "compact-json"],
        default="detailed",
        help=(
            "Output format: summary (name+score), detailed (full text), "
            "json (full JSON), compact-json (minimal JSON)"
        ),
    )
    parser.add_argument(
        "--quiet",
        "-q",
        action="store_true",
        help="Suppress progress output (only show final results)",
    )
    parser.add_argument(
        "--api-key",
        help="Anthropic API key (defaults to ANTHROPIC_API_KEY env var)",
    )

    args = parser.parse_args()

    # Validate target
    if args.target < 1:
        print("Error: Target must be at least 1", file=sys.stderr)
        sys.exit(1)

    try:
        # Initialize orchestrator
        orchestrator = FoodRecommendationOrchestrator(api_key=args.api_key, fast_mode=True)

        # Suppress progress if quiet mode
        if args.quiet:
            # Redirect stdout to suppress progress
            with contextlib.redirect_stdout(io.StringIO()):
                dishes = orchestrator.search(args.origin, args.destination, args.target)
        else:
            dishes = orchestrator.search(args.origin, args.destination, args.target)

        # Format and print results based on format choice
        if args.format == "summary":
            print("\n" + format_quick_summary(dishes))
        elif args.format == "json":
            print(format_json(dishes, args.origin, args.destination))
        elif args.format == "compact-json":
            print(format_compact_json(dishes))
        else:  # detailed
            print(format_detailed_text(dishes, args.origin, args.destination))
            print(f"\n{'='*70}")
            print(f"✅ Found {len(dishes)} unique dishes for your trip!")
            print(f"{'='*70}\n")

    except KeyboardInterrupt:
        print("\n\n⚠️  Search interrupted by user", file=sys.stderr)
        sys.exit(1)
    except (APIError, APIStatusError) as e:
        print(f"\n\n❌ API Error: {e}", file=sys.stderr)
        sys.exit(1)
    except (OSError, IOError) as e:
        print(f"\n\n❌ System Error: {e}", file=sys.stderr)
        sys.exit(1)
    except ValueError as e:
        print(f"\n\n❌ Invalid input: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
