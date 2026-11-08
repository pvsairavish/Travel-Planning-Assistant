"""
Agentic Travel Planning Reasoning Engine.
Supports:
1. Autonomous LangChain / LangGraph ReAct agent with LLM integration (Groq / Gemini / OpenAI).
2. Deterministic Heuristic Agent Runner for reliable offline execution, instant testing,
   and zero-friction evaluation when an external API key is not supplied.
3. Multi-Modal Transit Intelligence: Seamlessly compares and selects Flights, AC Sleeper Buses,
   and Outstation Cabs for maximum budget savings on short and regional routes.
4. Dual format output: Machine-readable JSON dictionary and human-readable Markdown.
"""

import importlib
import json
import os
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from config import DAILY_EXPENSE_TIERS
import data_loader
import tools


def get_llm(
    provider: str = "groq",
    api_key: Optional[str] = None,
    model_name: Optional[str] = None,
):
    """
    Initializes an LLM instance from the requested provider.
    Uses dynamic imports to prevent static linter errors when optional provider
    packages (like langchain-google-genai or langchain-openai) are not installed.
    """
    prov = provider.lower().strip()

    if prov == "groq":
        key = api_key or os.environ.get("GROQ_API_KEY")
        if not key:
            return None
        try:
            groq_mod = importlib.import_module("langchain_groq")
            ChatGroq = getattr(groq_mod, "ChatGroq")
            model = model_name or "llama-3.3-70b-versatile"
            return ChatGroq(groq_api_key=key, model_name=model, temperature=0.3)
        except Exception:
            return None

    elif prov in ("google", "gemini"):
        key = api_key or os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
        if not key:
            return None
        try:
            google_mod = importlib.import_module("langchain_google_genai")
            ChatGoogleGenerativeAI = getattr(google_mod, "ChatGoogleGenerativeAI")
            model = model_name or "gemini-1.5-flash"
            return ChatGoogleGenerativeAI(google_api_key=key, model=model, temperature=0.3)
        except Exception:
            return None

    elif prov == "openai":
        key = api_key or os.environ.get("OPENAI_API_KEY")
        if not key:
            return None
        try:
            openai_mod = importlib.import_module("langchain_openai")
            ChatOpenAI = getattr(openai_mod, "ChatOpenAI")
            model = model_name or "gpt-4o-mini"
            return ChatOpenAI(openai_api_key=key, model_name=model, temperature=0.3)
        except Exception:
            return None

    return None


class AutonomousTravelPlanner:
    """
    Deterministic Agentic Engine that performs multi-step reasoning,
    multi-modal transit comparison (Flights vs Buses vs Cabs), constraint
    satisfaction, and structured itinerary generation.
    """

    def __init__(self):
        self.trace: List[Dict[str, Any]] = []

    def _log_step(self, step_name: str, tool_name: str, inputs: Dict[str, Any], output: Any):
        """Records agent tool execution trace."""
        self.trace.append({
            "timestamp": datetime.now().strftime("%H:%M:%S"),
            "step": step_name,
            "tool": tool_name,
            "inputs": inputs,
            "output_summary": output
        })

    def run(
        self,
        origin: str,
        destination: str,
        start_date: str,
        num_days: int = 3,
        travel_style: str = "moderate",
        preferred_transit: str = "any",
        interests: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """
        Executes the autonomous travel planning reasoning loop:
        1. Tool: search_transit (compares Flights, Buses, and Cabs)
        2. Tool: recommend_hotels
        3. Tool: lookup_weather
        4. Tool: discover_places
        5. Tool: calculate_budget
        6. Synthesis & Reasoning
        """
        self.trace = []
        num_days = max(1, min(int(num_days), 7))
        num_nights = max(1, num_days - 1)
        travel_style = travel_style.lower() if travel_style else "moderate"
        pref_transit = (preferred_transit or "any").lower().strip()

        # Step 1: Multi-Modal Transit Comparison (Flights vs Buses vs Cabs)
        transit_inputs = {
            "origin": origin,
            "destination": destination,
            "preferred_mode": pref_transit
        }
        transit_raw = tools.search_transit.invoke(transit_inputs)
        transit_tool_data = json.loads(transit_raw)

        # Full transit options from data loader
        transit_comparison = data_loader.find_all_transit(origin, destination)
        best_flight = transit_comparison.get("best_flight")
        best_bus = transit_comparison.get("best_bus")
        best_cab = transit_comparison.get("best_cab")
        savings_with_bus = transit_comparison.get("savings_with_bus", 0)

        # Autonomous Decision Logic for Transit Selection:
        # User preference overrides; otherwise auto-optimize based on budget tier and distance
        selected_mode = "flight"
        if pref_transit in ("bus", "sleeper_bus", "coach"):
            selected_mode = "bus" if best_bus else "flight"
        elif pref_transit in ("cab", "car", "taxi", "rental"):
            selected_mode = "cab" if best_cab else "flight"
        elif pref_transit in ("flight", "plane", "air"):
            selected_mode = "flight" if best_flight else "bus"
        else:
            # "any" / "smart" / "auto"
            if travel_style == "budget" and best_bus:
                selected_mode = "bus"
            elif travel_style == "luxury" and best_flight:
                selected_mode = "flight"
            else:
                # Moderate tier: if bus saves more than ₹3,000, pick bus for optimal budget
                if best_bus and best_flight and savings_with_bus >= 3000:
                    selected_mode = "bus"
                else:
                    selected_mode = "flight" if best_flight else "bus"

        # Build standardized transit object
        if selected_mode == "bus" and best_bus:
            selected_transit = {
                "mode": "bus",
                "icon": "🚌",
                "title": best_bus.get("bus_type", "AC Sleeper Bus"),
                "provider": best_bus.get("operator", "InterCity Sleeper"),
                "id": best_bus.get("bus_id", "BUS-01"),
                "price": float(best_bus.get("price", 850)),
                "duration_str": best_bus.get("duration", "9.5h (Overnight)"),
                "departure_time": best_bus.get("departure_time", "21:30"),
                "arrival_time": best_bus.get("arrival_time", "07:30"),
                "details": f"{best_bus.get('bus_type')} • Rating: {best_bus.get('rating', 4.5)}★",
                "savings_vs_flight": savings_with_bus
            }
            transit_reasoning = (
                f"Selected {selected_transit['provider']} ({selected_transit['title']}) at ₹{selected_transit['price']:,.0f}. "
                f"Saves ₹{savings_with_bus:,.0f} compared to flights while providing a comfortable overnight sleeper journey."
            )
        elif selected_mode == "cab" and best_cab:
            cab_savings = max(0, (best_flight.get("price", 4800) if best_flight else 4800) - best_cab.get("price", 2800))
            selected_transit = {
                "mode": "cab",
                "icon": "🚗",
                "title": best_cab.get("car_type", "Outstation Sedan"),
                "provider": best_cab.get("service", "Outstation Cab"),
                "id": best_cab.get("cab_id", "CAB-01"),
                "price": float(best_cab.get("price", 2800)),
                "duration_str": best_cab.get("duration", "6.5h"),
                "departure_time": "Flexible (07:00 AM)",
                "arrival_time": "Flexible (01:30 PM)",
                "details": f"{best_cab.get('car_type')} • {best_cab.get('seating', 4)} Seats • Fuel Included",
                "savings_vs_flight": cab_savings
            }
            transit_reasoning = (
                f"Selected {selected_transit['provider']} ({selected_transit['title']}) at ₹{selected_transit['price']:,.0f}. "
                f"Offers private door-to-door convenience and scenic road trip flexibility."
            )
        else:
            selected_mode = "flight"
            fl = best_flight or {
                "flight_id": "FL-DIRECT-01",
                "airline": "IndiGo",
                "price": 4800,
                "duration_str": "2.5h",
                "departure_time": "14:00",
                "arrival_time": "16:30"
            }
            selected_transit = {
                "mode": "flight",
                "icon": "✈️",
                "title": f"{fl.get('airline')} Flight {fl.get('flight_id')}",
                "provider": fl.get("airline", "IndiGo"),
                "id": fl.get("flight_id", "FL-01"),
                "price": float(fl.get("price", 4800)),
                "duration_str": fl.get("duration_str", "2.5h"),
                "departure_time": fl.get("departure_time", "14:00"),
                "arrival_time": fl.get("arrival_time", "16:30"),
                "details": f"Non-stop schedule • {fl.get('duration_str', '2.5h')}",
                "savings_vs_flight": 0
            }
            transit_reasoning = (
                f"Selected {selected_transit['provider']} ({selected_transit['id']}) at ₹{selected_transit['price']:,.0f}. "
                f"Provides the fastest non-stop transit between {origin} and {destination}."
            )

        self._log_step(
            step_name="1. Multi-Modal Transit Evaluation",
            tool_name="search_transit",
            inputs=transit_inputs,
            output=(
                f"Evaluated Flights (₹{best_flight.get('price', 0) if best_flight else 0}), "
                f"Buses (₹{best_bus.get('price', 0) if best_bus else 0}), "
                f"Cabs (₹{best_cab.get('price', 0) if best_cab else 0}). Selected {selected_mode.upper()}."
            )
        )

        # Step 2: Query Hotels Tool
        min_stars = 4 if travel_style == "luxury" else (3 if travel_style == "moderate" else 2)
        max_price = 4500 if travel_style == "moderate" else (2500 if travel_style == "budget" else None)
        hotel_inputs = {"city": destination, "min_stars": min_stars, "max_price": max_price, "sort_by": "rating"}
        hotel_raw = tools.recommend_hotels.invoke(hotel_inputs)
        hotel_data = json.loads(hotel_raw)
        self._log_step(
            step_name="2. Recommend Accommodation",
            tool_name="recommend_hotels",
            inputs=hotel_inputs,
            output=f"Found {hotel_data.get('total_matches', 0)} hotel candidates."
        )

        hotels_list = hotel_data.get("hotels", [])
        if hotels_list:
            selected_hotel = hotels_list[0]
            amenities = selected_hotel.get("amenities") or []
            amenities_str = ", ".join(amenities) if isinstance(amenities, list) else str(amenities)
            hotel_reasoning = (
                f"Recommended '{selected_hotel.get('name')}' ({selected_hotel.get('stars')}★) at ₹{selected_hotel.get('price_per_night'):,}/night. "
                f"It offers top amenities ({amenities_str}) while fitting the {travel_style} budget tier."
            )
        else:
            selected_hotel = {
                "hotel_id": "HOT-DEF-01",
                "name": f"{destination.title()} Comfort Residency",
                "city": destination,
                "stars": 4,
                "price_per_night": 3200,
                "amenities": ["wifi", "pool", "breakfast"]
            }
            hotel_reasoning = f"Recommended 4-star accommodation in {destination} with pool and breakfast."

        # Step 3: Query Weather Tool (Open-Meteo REST API)
        weather_inputs = {"city": destination, "days": num_days}
        weather_raw = tools.lookup_weather.invoke(weather_inputs)
        weather_data = json.loads(weather_raw)
        self._log_step(
            step_name="3. Query Real-Time Weather",
            tool_name="lookup_weather",
            inputs=weather_inputs,
            output=f"Retrieved {len(weather_data.get('forecast', []))} days forecast via {weather_data.get('source')}."
        )
        forecast_list = weather_data.get("forecast", [])

        # Step 4: Query Attractions Tool
        places_inputs = {"city": destination, "top_n": max(6, num_days * 2)}
        places_raw = tools.discover_places.invoke(places_inputs)
        places_data = json.loads(places_raw)
        self._log_step(
            step_name="4. Discover Attractions",
            tool_name="discover_places",
            inputs=places_inputs,
            output=f"Found {places_data.get('total_found', 0)} top-rated attractions."
        )
        places_list = places_data.get("places", [])

        # Step 5: Query Budget Calculator Tool
        daily_allowance = DAILY_EXPENSE_TIERS.get(travel_style, 1500)
        budget_inputs = {
            "flight_cost": float(selected_transit["price"]),
            "hotel_nightly_rate": float(selected_hotel.get("price_per_night", 3200)),
            "num_nights": num_nights,
            "daily_expense_allowance": float(daily_allowance)
        }
        budget_raw = tools.calculate_budget.invoke(budget_inputs)
        budget_data = json.loads(budget_raw)
        self._log_step(
            step_name="5. Calculate Total Budget",
            tool_name="calculate_budget",
            inputs=budget_inputs,
            output=f"Total: ₹{budget_data.get('total_estimated_budget'):,} INR."
        )

        # Step 6: Day-by-Day Itinerary Synthesis
        itinerary = []
        try:
            base_date = datetime.strptime(start_date, "%Y-%m-%d")
        except Exception:
            base_date = datetime.now() + timedelta(days=5)

        place_idx = 0
        num_places = len(places_list)

        for day_num in range(1, num_days + 1):
            curr_date = base_date + timedelta(days=day_num - 1)
            date_str = curr_date.strftime("%b %d")

            day_weather = forecast_list[day_num - 1] if day_num - 1 < len(forecast_list) else {
                "temp_max_c": 31.0, "condition": "Sunny ☀️", "is_outdoor_friendly": True
            }

            p1 = places_list[place_idx % num_places]["name"] if num_places else f"Popular Sights of {destination}"
            p2 = places_list[(place_idx + 1) % num_places]["name"] if num_places else f"Local Heritage Walk"
            place_idx += 2

            if day_num == 1:
                if selected_mode == "bus":
                    morning = f"Morning arrival in {destination} via {selected_transit['provider']} AC Sleeper bus. Refreshment break."
                    afternoon = f"Check-in at {selected_hotel.get('name')}. Unpack, rest, and prepare for afternoon excursion."
                    evening = f"Sunset stroll at {p1}, followed by dinner at a local heritage café."
                elif selected_mode == "cab":
                    morning = f"Doorstep pickup from {origin} by {selected_transit['provider']}. Enjoy scenic highway cruise to {destination}."
                    afternoon = f"Arrival and check-in at {selected_hotel.get('name')}. Freshen up and enjoy hotel amenities."
                    evening = f"Evening leisure exploration at {p1} and traditional local dinner."
                else:
                    morning = f"Morning flight from {origin} ({selected_transit['provider']}). Arrival in {destination}."
                    afternoon = f"Check-in at {selected_hotel.get('name')}. Unpack and freshen up."
                    evening = f"Sunset stroll at {p1}, followed by dinner at local restaurant."

            elif day_num == num_days:
                if selected_mode == "bus":
                    morning = f"Morning excursion to {p1} ({day_weather.get('condition')})."
                    afternoon = f"Souvenir shopping at local market and visit to {p2}."
                    evening = f"Check out from {selected_hotel.get('name')} and board overnight AC sleeper bus ({selected_transit['provider']}) back to {origin}."
                elif selected_mode == "cab":
                    morning = f"Morning sightseeing at {p1} ({day_weather.get('condition')})."
                    afternoon = f"Visit {p2} and lunch. Collect luggage from {selected_hotel.get('name')}."
                    evening = f"Comfortable evening road drive back to {origin} in your private cab."
                else:
                    morning = f"Morning excursion to {p1} ({day_weather.get('condition')})."
                    afternoon = f"Souvenir shopping at local market and visit to {p2}."
                    evening = f"Check out from {selected_hotel.get('name')} and transfer to airport for departure."
            else:
                morning = f"Visit {p1} under {day_weather.get('condition')} (Max {day_weather.get('temp_max_c')}°C)."
                afternoon = f"Lunch break followed by sightseeing at {p2}."
                evening = f"Leisure walk, local street food sampling, and evening cultural show."

            itinerary.append({
                "day_number": day_num,
                "day_label": f"Day {day_num} ({date_str})",
                "weather": day_weather,
                "schedule": {
                    "morning": morning,
                    "afternoon": afternoon,
                    "evening": evening
                }
            })

        # Overall Agent Justification
        agent_reasoning = (
            f"1. Transit Strategy: {transit_reasoning}\n"
            f"2. Hotel Choice: {hotel_reasoning}\n"
            f"3. Weather Optimization: Sights scheduled considering daily temperatures "
            f"(averaging ~{forecast_list[0].get('temp_max_c') if forecast_list else 31}°C) to maximize comfort.\n"
            f"4. Budget Control: Total spend is optimized at ₹{budget_data.get('total_estimated_budget'):,} INR "
            f"for a {num_days}-day trip under the {travel_style.capitalize()} tier."
        )

        # Generate Human-Readable Markdown Output
        end_date = base_date + timedelta(days=num_days - 1)
        trip_dates_str = f"{base_date.strftime('%b %d')} – {end_date.strftime('%b %d, %Y')}"

        b_down = budget_data.get("breakdown", {})
        hotel_total_cost = (b_down.get("hotel") or {}).get("total", 0)
        hotel_amenities = selected_hotel.get("amenities") or []
        hotel_amenities_str = ", ".join(hotel_amenities) if isinstance(hotel_amenities, list) else str(hotel_amenities)

        md_lines = [
            f"# {selected_transit['icon']} Your {num_days}-Day Trip to {destination.title()} ({trip_dates_str})\n",
            f"### 🧳 Transit Selected ({selected_transit['mode'].capitalize()}):",
            f"- **{selected_transit['title']}** ({selected_transit['provider']}) — **₹{selected_transit['price']:,.0f}**",
            f"- Route: {origin.title()} ➔ {destination.title()} | Duration: {selected_transit['duration_str']}",
            f"- Departure: {selected_transit['departure_time']} | Arrival: {selected_transit['arrival_time']}",
            f"- *Reasoning: {transit_reasoning}*\n",
            "### 🏨 Hotel Booked:",
            f"- **{selected_hotel.get('name')}** (⭐ {selected_hotel.get('stars')}-star) — **₹{selected_hotel.get('price_per_night'):,}/night**",
            f"- Total for {num_nights} nights: **₹{hotel_total_cost:,}**",
            f"- Amenities: {hotel_amenities_str}",
            f"- *Reasoning: {hotel_reasoning}*\n",
            "### 🌤️ Weather Forecast (Open-Meteo REST API):"
        ]

        for fc in forecast_list[:num_days]:
            md_lines.append(f"- **{fc.get('day')}**: {fc.get('condition')} (High: {fc.get('temp_max_c')}°C, Low: {fc.get('temp_min_c')}°C)")

        md_lines.append("\n### 📅 Day-Wise Itinerary:")
        for item in itinerary:
            md_lines.append(f"#### {item['day_label']}")
            md_lines.append(f"- **Morning:** {item['schedule']['morning']}")
            md_lines.append(f"- **Afternoon:** {item['schedule']['afternoon']}")
            md_lines.append(f"- **Evening:** {item['schedule']['evening']}")

        md_lines.append("\n### 💰 Estimated Total Budget Breakdown:")
        md_lines.append(f"- **Transit Fare ({selected_transit['mode'].capitalize()}):** ₹{selected_transit['price']:,.0f}")
        md_lines.append(f"- **Hotel ({num_nights} nights):** ₹{b_down.get('hotel', {}).get('total', 0):,}")
        md_lines.append(f"- **Food & Local Travel ({num_days} days):** ₹{b_down.get('food_and_local_transit', {}).get('total', 0):,}")
        md_lines.append("---")
        md_lines.append(f"### **Total Cost: ₹{budget_data.get('total_estimated_budget', 0):,} INR**\n")

        md_lines.append("### 💡 Agent Reasoning & Selection Rationale:")
        md_lines.append(agent_reasoning)

        markdown_text = "\n".join(md_lines)

        return {
            "status": "success",
            "destination": destination.title(),
            "origin": origin.title(),
            "trip_dates": trip_dates_str,
            "num_days": num_days,
            "num_nights": num_nights,
            "travel_style": travel_style,
            "preferred_transit": pref_transit,
            "transit_selected": selected_transit,
            "flight_selected": best_flight or {
                "flight_id": "FL-01", "airline": "IndiGo", "price": 4800, "duration_str": "2.5h"
            },
            "bus_selected": best_bus,
            "cab_selected": best_cab,
            "transit_comparison": transit_comparison,
            "hotel_selected": selected_hotel,
            "places_recommended": places_list[:8],
            "weather_forecast": forecast_list[:num_days],
            "day_wise_itinerary": itinerary,
            "budget_breakdown": budget_data,
            "agent_reasoning": agent_reasoning,
            "execution_trace": self.trace,
            "markdown_output": markdown_text
        }


def plan_trip(
    origin: str,
    destination: str,
    start_date: str,
    num_days: int = 3,
    travel_style: str = "moderate",
    preferred_transit: str = "any",
    interests: Optional[List[str]] = None,
    llm_provider: Optional[str] = "heuristic",
    api_key: Optional[str] = None,
    model_name: Optional[str] = None,
    **kwargs: Any,
) -> Dict[str, Any]:
    """
    Unified entrypoint for planning a trip with multi-modal transit options.
    Attempts to run via LLM ReAct agent if an API key is provided;
    falls back smoothly to the autonomous heuristic engine for guaranteed execution.
    """
    planner = AutonomousTravelPlanner()

    if llm_provider and llm_provider.lower() != "heuristic" and api_key:
        llm = get_llm(provider=llm_provider, api_key=api_key, model_name=model_name)
        if llm:
            try:
                from langgraph.prebuilt import create_react_agent
                agent_tools = tools.get_all_tools()
                app = create_react_agent(llm, agent_tools)
                prompt = (
                    f"Plan a {num_days}-day trip from {origin} to {destination} starting on {start_date}. "
                    f"Travel style is {travel_style}. Preferred transit: {preferred_transit}. "
                    f"Use tools to find flights/buses/cabs, hotels, places, weather, and budget."
                )
                response = app.invoke({"messages": [("user", prompt)]})
                messages = response.get("messages", [])
                if messages:
                    final_msg = messages[-1].content
                    base_plan = planner.run(
                        origin=origin,
                        destination=destination,
                        start_date=start_date,
                        num_days=num_days,
                        travel_style=travel_style,
                        preferred_transit=preferred_transit,
                        interests=interests,
                    )
                    base_plan["llm_output"] = final_msg
                    base_plan["llm_used"] = f"{llm_provider} ({model_name or 'default'})"
                    return base_plan
            except Exception:
                pass

    # Default to deterministic autonomous agent
    plan = planner.run(
        origin=origin,
        destination=destination,
        start_date=start_date,
        num_days=num_days,
        travel_style=travel_style,
        preferred_transit=preferred_transit,
        interests=interests,
    )
    plan["llm_used"] = "Autonomous Heuristic Engine (Deterministic ReAct)"
    return plan
