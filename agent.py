"""
agent.py

The FitFindr planning loop. Orchestrates the three tools in response to a
natural language user query, passing state between them via a session dict.

Complete tools.py and test each tool in isolation before implementing this file.

Usage (once implemented):
    from agent import run_agent
    from utils.data_loader import get_example_wardrobe

    result = run_agent(
        query="vintage graphic tee under $30, size M",
        wardrobe=get_example_wardrobe(),
    )
    print(result["fit_card"])
    print(result["error"])   # None on success
"""

from tools import search_listings, suggest_outfit, create_fit_card

import re

TOP_RESULTS = 3


# ── session state ─────────────────────────────────────────────────────────────

def _new_session(query: str, wardrobe: dict) -> dict:
    """
    Initialize and return a fresh session dict for one user interaction.

    The session dict is the single source of truth for everything that happens
    during a run — it stores the original query, parsed parameters, tool results,
    and any error that caused early termination.

    You may add fields to this dict as needed for your implementation.
    """
    return {
        "query": query,              # original user query
        "parsed": {},                # extracted description / size / max_price
        "search_results": [],        # list of matching listing dicts
        "selected_item": None,       # top result, passed into suggest_outfit
        "wardrobe": wardrobe,        # user's wardrobe dict
        "outfit_suggestion": None,   # string returned by suggest_outfit
        "fit_card": None,            # string returned by create_fit_card
        "error": None,               # set if the interaction ended early
    }


def _parse_query(query: str) -> dict:
    """
    Extract search parameters from a natural-language query using regex.

    Pulls out max_price (e.g. "under $30") and size (e.g. "size M"), then
    cleans the remaining text into a keyword description for search_listings.
    """
    text = query.strip()
    max_price = None
    size = None

    price_match = re.search(
        r"(?:under|below|less than|max|up to)\s*\$?\s*(\d+(?:\.\d+)?)",
        text,
        re.IGNORECASE,
    )
    if price_match:
        max_price = float(price_match.group(1))

    size_match = re.search(
        r"(?:in\s+)?size\s+([A-Za-z0-9/]+)",
        text,
        re.IGNORECASE,
    )
    if size_match:
        size = size_match.group(1)

    description = re.sub(
        r"(?:under|below|less than|max|up to)\s*\$?\s*\d+(?:\.\d+)?",
        " ",
        text,
        flags=re.IGNORECASE,
    )
    description = re.sub(
        r"(?:in\s+)?size\s+[A-Za-z0-9/]+",
        " ",
        description,
        flags=re.IGNORECASE,
    )

    for pattern in (
        r"\bi(?:'m| am) looking for\b",
        r"\blooking for\b",
        r"\bwhat(?:'s| is) out there\b",
        r"\bhow would i style (?:it|this)\??",
        r"\bi mostly wear\b.*",
    ):
        description = re.sub(pattern, " ", description, flags=re.IGNORECASE)

    description = description.split(".")[0].strip()
    description = re.sub(r"\s+", " ", description).strip(" ,.-")
    description = re.sub(r"^(?:a|an|the)\s+", "", description, flags=re.IGNORECASE)

    if not description:
        description = text

    return {
        "description": description,
        "size": size,
        "max_price": max_price,
    }


# ── planning loop ─────────────────────────────────────────────────────────────

def run_agent(query: str, wardrobe: dict) -> dict:
    """
    Main agent entry point. Runs the FitFindr planning loop for a single
    user interaction and returns the completed session dict.

    Args:
        query:    Natural language user request
                  (e.g., "vintage graphic tee under $30, size M")
        wardrobe: User's wardrobe dict — use get_example_wardrobe() or
                  get_empty_wardrobe() from utils/data_loader.py

    Returns:
        The session dict after the interaction completes. Check session["error"]
        first — if it is not None, the interaction ended early and the other
        output fields (outfit_suggestion, fit_card) will be None.

    Planning loop (see planning.md):
        1. Init session → 2. Parse query → 3. search_listings
        → branch on results → 4. select top item → 5. suggest_outfit
        → 6. create_fit_card → 7. return session
    """
    # Step 1: initialize session
    session = _new_session(query, wardrobe)

    # Step 2: parse query and store extracted parameters
    session["parsed"] = _parse_query(query)
    parsed = session["parsed"]

    # Step 3: search listings — store up to 3 matches in session
    results = search_listings(
        description=parsed["description"],
        size=parsed.get("size"),
        max_price=parsed.get("max_price"),
    )
    session["search_results"] = results[:TOP_RESULTS]

    # Branch: no results → set error and stop (do not call downstream tools)
    if not session["search_results"]:
        session["error"] = (
            "No listings matched your search. Try broadening your description, "
            "raising your max price, or dropping the size filter."
        )
        return session

    # Step 4: pass top match into outfit + fit-card tools via session
    session["selected_item"] = session["search_results"][0]

    # Step 5: outfit suggestion uses selected_item + wardrobe from session
    session["outfit_suggestion"] = suggest_outfit(
        session["selected_item"],
        session["wardrobe"],
    )

    # Step 6: fit card uses outfit_suggestion + selected_item from session
    session["fit_card"] = create_fit_card(
        session["outfit_suggestion"],
        session["selected_item"],
    )

    # Step 7: return completed session
    return session


# ── CLI test ──────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    from utils.data_loader import get_example_wardrobe, get_empty_wardrobe

    print("=== Happy path: graphic tee ===\n")
    session = run_agent(
        query="looking for a vintage graphic tee under $30",
        wardrobe=get_example_wardrobe(),
    )
    if session["error"]:
        print(f"Error: {session['error']}")
    else:
        print(f"Found: {session['selected_item']['title']}")
        print(f"\nOutfit: {session['outfit_suggestion']}")
        print(f"\nFit card: {session['fit_card']}")

    print("\n\n=== No-results path ===\n")
    session2 = run_agent(
        query="designer ballgown size XXS under $5",
        wardrobe=get_example_wardrobe(),
    )
    print(f"Error message: {session2['error']}")
