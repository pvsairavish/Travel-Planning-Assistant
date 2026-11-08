"""
Command-Line Interface (CLI) for the Agentic Travel Planning Assistant.
Allows running the assistant in terminal mode without launching the web server.
"""

import argparse
import json
from datetime import datetime, timedelta

import agent
import data_loader


def run_cli():
    parser = argparse.ArgumentParser(description="Agentic AI Travel Planning Assistant (CLI)")
    parser.add_argument("--origin", "--from", dest="origin", default="Delhi", help="Origin city (default: Delhi)")
    parser.add_argument("--destination", "--to", dest="destination", default="Goa", help="Destination city (default: Goa)")
    parser.add_argument("--days", dest="days", type=int, default=3, help="Duration in days (1 to 7, default: 3)")
    parser.add_argument("--date", dest="start_date", default=None, help="Travel start date YYYY-MM-DD")
    parser.add_argument("--style", dest="travel_style", default="moderate", choices=["budget", "moderate", "luxury"], help="Travel style tier")
    parser.add_argument("--transit", dest="preferred_transit", default="any", choices=["any", "bus", "flight", "cab"], help="Preferred transit mode (default: any)")
    parser.add_argument("--save", dest="save_path", default=None, help="Optional file path to save output JSON")

    args = parser.parse_args()

    # Default date: 7 days from now
    if not args.start_date:
        default_d = datetime.now() + timedelta(days=7)
        args.start_date = default_d.strftime("%Y-%m-%d")

    print("=" * 70)
    print("🤖 AGENTIC AI TRAVEL PLANNING ASSISTANT")
    print(f"Planning {args.days}-day trip: {args.origin} ➔ {args.destination}")
    print(f"Start Date: {args.start_date} | Style: {args.travel_style.capitalize()} | Transit: {args.preferred_transit.capitalize()}")
    print("=" * 70)
    print("Executing agent reasoning loop...")

    result = agent.plan_trip(
        origin=args.origin,
        destination=args.destination,
        start_date=args.start_date,
        num_days=args.days,
        travel_style=args.travel_style,
        preferred_transit=args.preferred_transit,
    )

    print("\n" + result.get("markdown_output", ""))
    print("=" * 70)
    print(f"✅ Itinerary successfully generated using {result.get('llm_used')}!")

    if args.save_path:
        with open(args.save_path, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, default=str)
        print(f"📁 Structured JSON saved to: {args.save_path}")


if __name__ == "__main__":
    run_cli()

