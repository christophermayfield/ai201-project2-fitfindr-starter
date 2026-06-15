"""
tools.py

The three required FitFindr tools. Each tool is a standalone function that
can be called and tested independently before being wired into the agent loop.

Complete and test each tool before moving to agent.py.

Tools:
    search_listings(description, size, max_price)  → list[dict]
    suggest_outfit(new_item, wardrobe)              → str
    create_fit_card(outfit, new_item)               → str
"""

import os
import re

from dotenv import load_dotenv
from groq import Groq

from utils.data_loader import load_listings

load_dotenv()

GROQ_MODEL = "llama-3.3-70b-versatile"


# ── Groq client ───────────────────────────────────────────────────────────────

def _get_groq_client():
    """Initialize and return a Groq client using GROQ_API_KEY from .env."""
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise ValueError(
            "GROQ_API_KEY not set. Add it to a .env file in the project root."
        )
    return Groq(api_key=api_key)


def _call_groq(system_prompt: str, user_prompt: str, temperature: float = 0.7) -> str:
    """Send a chat completion request to Groq and return the assistant reply."""
    client = _get_groq_client()
    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=temperature,
    )
    return response.choices[0].message.content.strip()


def _format_listing(listing: dict) -> str:
    """Format a listing dict as readable text for LLM prompts."""
    colors = ", ".join(listing.get("colors", []))
    tags = ", ".join(listing.get("style_tags", []))
    brand = listing.get("brand") or "unknown"
    return (
        f"Title: {listing.get('title', '')}\n"
        f"Description: {listing.get('description', '')}\n"
        f"Category: {listing.get('category', '')}\n"
        f"Size: {listing.get('size', '')}\n"
        f"Condition: {listing.get('condition', '')}\n"
        f"Price: ${listing.get('price', 0):.2f}\n"
        f"Colors: {colors}\n"
        f"Style tags: {tags}\n"
        f"Brand: {brand}\n"
        f"Platform: {listing.get('platform', '')}"
    )


def _format_wardrobe_item(item: dict) -> str:
    """Format a single wardrobe item for LLM prompts."""
    colors = ", ".join(item.get("colors", []))
    tags = ", ".join(item.get("style_tags", []))
    line = f"- {item.get('name', '')} ({item.get('category', '')}, {colors}; tags: {tags})"
    notes = item.get("notes")
    if notes:
        line += f" — {notes}"
    return line


def _fallback_outfit_suggestion(new_item: dict, wardrobe_items: list[dict]) -> str:
    """Return a non-empty styling suggestion when the LLM call fails."""
    title = new_item.get("title", "this item")
    tags = ", ".join(new_item.get("style_tags", [])[:3]) or "casual"

    if wardrobe_items:
        names = [item.get("name", "a wardrobe piece") for item in wardrobe_items[:3]]
        pieces = ", ".join(names)
        return (
            f"Pair {title} with pieces from your wardrobe like {pieces}. "
            f"Lean into the {tags} vibe — tuck or half-tuck for shape, "
            f"and balance proportions with your go-to bottoms and shoes."
        )

    return (
        f"{title} pairs well with wide-leg or straight jeans, neutral bottoms, "
        f"and sneakers or boots depending on the {tags} look you want. "
        f"Layer under an oversized jacket or flannel for a second outfit option."
    )


# ── Tool 1: search_listings ───────────────────────────────────────────────────

def search_listings(
    description: str,
    size: str | None = None,
    max_price: float | None = None,
) -> list[dict]:
    """
    Search the mock listings dataset for items matching the description,
    optional size, and optional price ceiling.

    Args:
        description: Keywords describing what the user is looking for
                     (e.g., "vintage graphic tee").
        size:        Size string to filter by, or None to skip size filtering.
                     Matching is case-insensitive (e.g., "M" matches "S/M").
        max_price:   Maximum price (inclusive), or None to skip price filtering.

    Returns:
        A list of matching listing dicts, sorted by relevance (best match first).
        Returns an empty list if nothing matches — does NOT raise an exception.

    Each listing dict has the following fields:
        id, title, description, category, style_tags (list), size,
        condition, price (float), colors (list), brand, platform

    TODO:
        1. Load all listings with load_listings().
        2. Filter by max_price and size (if provided).
        3. Score each remaining listing by keyword overlap with `description`.
        4. Drop any listings with a score of 0 (no relevant matches).
        5. Sort by score, highest first, and return the listing dicts.

    Before writing code, fill in the Tool 1 section of planning.md.
    """
    listings = load_listings()
    keywords = _extract_keywords(description)

    scored: list[tuple[int, dict]] = []
    for listing in listings:
        if max_price is not None and listing["price"] > max_price:
            continue
        if size is not None and not _size_matches(listing["size"], size):
            continue

        score = _score_listing(listing, keywords)
        if score > 0:
            scored.append((score, listing))

    scored.sort(key=lambda pair: pair[0], reverse=True)
    return [listing for _, listing in scored]


def _extract_keywords(description: str) -> list[str]:
    """Split a description into lowercase keywords for relevance scoring."""
    return re.findall(r"[a-z0-9]+", description.lower())


def _listing_search_text(listing: dict) -> str:
    """Combine searchable listing fields into one lowercase string."""
    style_tags = " ".join(listing.get("style_tags", []))
    colors = " ".join(listing.get("colors", []))
    return " ".join(
        [
            listing.get("title", ""),
            listing.get("description", ""),
            listing.get("category", ""),
            style_tags,
            colors,
        ]
    ).lower()


def _score_listing(listing: dict, keywords: list[str]) -> int:
    """Count how many description keywords appear in the listing's searchable text."""
    if not keywords:
        return 0
    text = _listing_search_text(listing)
    return sum(1 for keyword in keywords if keyword in text)


def _size_matches(listing_size: str, requested_size: str) -> bool:
    """Case-insensitive size match (e.g. 'M' matches 'S/M')."""
    return requested_size.lower() in listing_size.lower()


# ── Tool 2: suggest_outfit ────────────────────────────────────────────────────

def suggest_outfit(new_item: dict, wardrobe: dict) -> str:
    """
    Given a thrifted item and the user's wardrobe, suggest 1–2 complete outfits.

    Args:
        new_item: A listing dict (the item the user is considering buying).
        wardrobe: A wardrobe dict with an 'items' key containing a list of
                  wardrobe item dicts. May be empty — handle this gracefully.

    Returns:
        A non-empty string with outfit suggestions.
        If the wardrobe is empty, offer general styling advice for the item
        rather than raising an exception or returning an empty string.

    TODO:
        1. Check whether wardrobe['items'] is empty.
        2. If empty: call the LLM with a prompt for general styling ideas
           (what kinds of items pair well, what vibe it suits, etc.).
        3. If not empty: format the wardrobe items into a prompt and ask
           the LLM to suggest specific outfit combinations using the new item
           and named pieces from the wardrobe.
        4. Return the LLM's response as a string.

    Before writing code, fill in the Tool 2 section of planning.md.
    """
    wardrobe_items = wardrobe.get("items", [])
    item_text = _format_listing(new_item)

    if not wardrobe_items:
        system_prompt = (
            "You are a personal stylist helping someone style a secondhand find. "
            "The user has not added any wardrobe items yet. Give general styling "
            "advice for the item: what kinds of pieces pair well, what vibe it "
            "suits, and 1–2 complete outfit ideas using typical wardrobe staples. "
            "Do not pretend you know what they own. Be specific, practical, and "
            "conversational."
        )
        user_prompt = f"The user is considering buying this thrifted item:\n\n{item_text}"
    else:
        wardrobe_text = "\n".join(_format_wardrobe_item(item) for item in wardrobe_items)
        system_prompt = (
            "You are a personal stylist helping someone style a secondhand find. "
            "Suggest 1–2 complete outfits using the thrifted item AND specific "
            "named pieces from their wardrobe. Reference wardrobe items by name. "
            "Include practical styling tips (tucking, layering, rolling sleeves, etc.). "
            "Be specific, practical, and conversational."
        )
        user_prompt = (
            f"The user is considering buying this thrifted item:\n\n{item_text}\n\n"
            f"Their wardrobe:\n{wardrobe_text}"
        )

    try:
        result = _call_groq(system_prompt, user_prompt)
        if result:
            return result
    except Exception:
        pass

    return _fallback_outfit_suggestion(new_item, wardrobe_items)


# ── Tool 3: create_fit_card ───────────────────────────────────────────────────

def create_fit_card(outfit: str, new_item: dict) -> str:
    """Generate a short, shareable outfit caption for the thrifted find.
    

    Args:
        outfit:   The outfit suggestion string from suggest_outfit().
        new_item: The listing dict for the thrifted item.

    Returns:
        A 2–4 sentence string usable as an Instagram/TikTok caption.
        If outfit is empty or missing, return a descriptive error message
        string — do NOT raise an exception.

    The caption should:
    - Feel casual and authentic (like a real OOTD post, not a product description)
    - Mention the item name, price, and platform naturally (once each)
    - Capture the outfit vibe in specific terms
    - Sound different each time for different inputs (use higher LLM temperature)

    TODO:
        1. Guard against an empty or whitespace-only outfit string.
        2. Build a prompt that gives the LLM the item details and the outfit,
           and asks for a caption matching the style guidelines above.
        3. Call the LLM and return the response.

    Before writing code, fill in the Tool 3 section of planning.md.
    """
    if not outfit or not outfit.strip():
        return (
            "Cannot create a fit card: outfit suggestion is missing or empty. "
            "Run suggest_outfit first to generate styling ideas."
        )

    item_text = _format_listing(new_item)
    system_prompt = (
        "You are writing a casual Instagram or TikTok outfit caption (OOTD style). "
        "Write 2–4 sentences that feel authentic and personal—not like a product listing. "
        "Mention the item name, price, and platform naturally once each. "
        "Capture the outfit vibe in specific terms based on the styling suggestion provided. "
        "Use a relaxed, lowercase thrift-culture tone. Do not use bullet points."
    )
    user_prompt = (
        f"Thrifted item:\n{item_text}\n\n"
        f"Outfit styling:\n{outfit.strip()}\n\n"
        "Write the fit card caption."
    )

    try:
        result = _call_groq(system_prompt, user_prompt, temperature=0.9)
        if result:
            return result
    except Exception:
        pass

    title = new_item.get("title", "this find")
    price = new_item.get("price", 0)
    platform = new_item.get("platform", "depop")
    return (
        f"thrifted this {title.lower()} off {platform} for ${price:.0f} and honestly "
        f"it's giving exactly the vibe i wanted. full fit breakdown in my stories."
    )
