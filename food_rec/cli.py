"""
Command-line interface for the food recommendation system.
"""

import sys
import argparse
from typing import Optional
from .orchestrator import FoodRecommendationSystem


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Food Recommendation System - Find unique dishes to try when traveling",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --from USA --to India
  %(prog)s --from USA --to Japan --max 15
  %(prog)s -f USA -t Mexico -m 5 -b 2.0

This system helps travelers discover authentic local dishes that are 
not commonly available in their home country restaurants.
        """
    )
    
    parser.add_argument(
        "-f", "--from",
        dest="origin",
        required=True,
        help="Origin country (where you are from)"
    )
    
    parser.add_argument(
        "-t", "--to",
        dest="destination",
        required=True,
        help="Destination country (where you are traveling)"
    )
    
    parser.add_argument(
        "-m", "--max",
        dest="max_recommendations",
        type=int,
        default=10,
        help="Maximum number of recommendations (default: 10)"
    )
    
    parser.add_argument(
        "-b", "--boost",
        dest="boost_factor",
        type=float,
        default=1.5,
        help="Score boost factor for unique dishes (default: 1.5)"
    )
    
    parser.add_argument(
        "-q", "--quiet",
        action="store_true",
        help="Quiet mode - only show final recommendations"
    )
    
    args = parser.parse_args()
    
    # Validate arguments
    if args.max_recommendations < 1:
        print("Error: --max must be at least 1", file=sys.stderr)
        return 1
    
    if args.boost_factor < 1.0:
        print("Error: --boost must be at least 1.0", file=sys.stderr)
        return 1
    
    # Run the recommendation system
    try:
        system = FoodRecommendationSystem()
        
        # Suppress agent output in quiet mode
        if args.quiet:
            import io
            import contextlib
            
            with contextlib.redirect_stdout(io.StringIO()):
                result = system.get_recommendations(
                    origin_country=args.origin,
                    destination_country=args.destination,
                    max_recommendations=args.max_recommendations,
                    boost_unique=args.boost_factor
                )
        else:
            result = system.get_recommendations(
                origin_country=args.origin,
                destination_country=args.destination,
                max_recommendations=args.max_recommendations,
                boost_unique=args.boost_factor
            )
        
        # Print results
        system.print_recommendations(result)
        
        return 0
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
