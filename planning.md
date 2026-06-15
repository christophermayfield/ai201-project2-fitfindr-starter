# FitFindr — planning.md

> Complete this document before writing any implementation code.
> Your spec and agent diagram are what you'll use to direct AI tools (Claude, Copilot, etc.) to generate your implementation — the more specific they are, the more useful the generated code will be.
> Your planning.md will be reviewed as part of your submission.
> Update it before starting any stretch features.

---

## Tools

List every tool your agent will use. For each tool, fill in all four fields.
You must have at least 3 tools. The three required tools are listed — add any additional tools below them.

### Tool 1: search_listings

**What it does:**
Searches the mock secondhand listings dataset for items that match the user's keywords, with optional size and price filters. Results are ranked by relevance so the best matches appear first.

**Input parameters:**
- `description` (str, required): Keywords describing what the user is looking for (e.g., `"vintage graphic tee"`). Used to score listings by keyword overlap against each listing's `title`, `description`, `style_tags`, `category`, and `colors`.
- `size` (str | None, optional): Size to filter by, or `None` to skip size filtering. Matching is case-insensitive (e.g., `"M"` matches `"S/M"`).
- `max_price` (float | None, optional): Maximum price in dollars (inclusive), or `None` to skip price filtering.

**What it returns:**
A list of matching listing dicts, sorted by relevance (best match first). Returns an empty list if nothing matches.

Each listing dict in the list contains these fields (these are **output** fields, not inputs to the tool):
- `id` (str): unique identifier (e.g., `"lst_033"`)
- `title` (str): short listing title
- `description` (str): full item description
- `category` (str): one of `tops`, `bottoms`, `outerwear`, `shoes`, `accessories`
- `style_tags` (list[str]): style descriptors (e.g., `["vintage", "graphic tee", "grunge"]`)
- `size` (str): listed size
- `condition` (str): item condition (e.g., `"good"`, `"fair"`)
- `price` (float): price in dollars
- `colors` (list[str]): item colors
- `brand` (str | null): brand name, or `null` if unknown
- `platform` (str): where the item is sold (e.g., `"depop"`, `"poshmark"`)

**What happens if it fails or returns nothing:**
Returns an empty list if no listings match — does **not** raise an exception. The agent should set `session["error"]` to a helpful message (e.g., suggest broadening the description, raising `max_price`, or dropping the size filter) and stop — it must **not** call `suggest_outfit` with empty input.
---

### Tool 2: suggest_outfit

**What it does:**
<!-- Describe what this tool does in 1–2 sentences -->

Given a thrifted item and the user's wardrobe, suggest 1–2 complete outfits.

    Args:
        new_item: A listing dict (the item the user is considering buying).
        wardrobe: A wardrobe dict with an 'items' key containing a list of
                  wardrobe item dicts. May be empty — handle this gracefully.

**Input parameters:**
<!-- List each parameter, its type, and what it represents -->
- `new_item` (dict): A listing dict (the item the user is considering buying).
- `wardrobe` (dict): A wardrobe dict with an 'items' key containing a list of
                  wardrobe item dicts. 

**What it returns:**
<!-- Describe the return value -->
     Returns:
        A non-empty string with outfit suggestions.
        

**What happens if it fails or returns nothing:**
<!-- What should the agent do if the wardrobe is empty or no outfit can be suggested? -->
If the wardrobe is empty, offer general styling advice for the item
        rather than raising an exception or returning an empty string.

It should fail gracefully and return a helpful message. 

---

### Tool 3: create_fit_card

**What it does:**
<!-- Describe what this tool does in 1–2 sentences -->
Generate a short, shareable outfit caption for the thrifted find. (something sick)

**Input parameters:**
<!-- List each parameter, its type, and what it represents -->
- `outfit` (str): shareable outfit caption for the thrifted find.
- `new_item` (dict): the item that was found.


**What it returns:**
<!-- Describe the return value -->

A 2–4 sentence string usable as an Instagram/TikTok caption.
        

**What happens if it fails or returns nothing:**
<!-- What should the agent do if the outfit data is incomplete? -->
If outfit is empty or missing, return a descriptive error message
        string — do NOT raise an exception in t his case

---

### Additional Tools (if any)

<!-- Copy the block above for any tools beyond the required three -->

---

## Planning Loop

**How does your agent decide which tool to call next?**
<!-- Describe the logic your planning loop uses. What does it look at? What conditions change its behavior? How does it know when it's done? -->

Search the lists and return 3 matching listings. Next, suggest outfit returns something to the effect of "pair this with your wide-leg jeans and platform Docs for a timeless and classic 90s grunge look. Roll the sleeves once and tuck the front corner slightly for shape" Next the fit-card will come in. this returns something to the effect of "thirfted this faded band tee off depop for $22 and honestly it was made for my wide-legs full look in my stories babies hehe" if the search_listings returns nothing, FitFindr tells the user what to try differently and stops, it does not call suggest_outfit with empty input

---

## State Management

**How does information from one tool get passed to the next?**
<!-- Describe how your agent stores and accesses state within a session. What data is tracked? How is it passed between tool calls? -->
the search listings function holds 3 matches. This gets passed to the suggest outfit function. Finally, this gets passed to the fit card function. 




## Error Handling

For each tool, describe the specific failure mode you're handling and what the agent does in response.

| Tool | Failure mode | Agent response |
|------|-------------|----------------|
| search_listings | No results match the query | Returns an empty list if nothing matches — does NOT raise an exception. |
| suggest_outfit | Wardrobe is empty | If the wardrobe is empty, offer general styling advice for the item
        rather than raising an exception or returning an empty string. |
| create_fit_card | Outfit input is missing or incomplete | If outfit is empty or missing, return a descriptive error message
        string — do NOT raise an exception. |

---

## Architecture

<!-- Draw a diagram of your agent showing how the components connect:
     User input → Planning Loop → Tools (search_listings, suggest_outfit, create_fit_card)
                                                                          ↕
                                                                   State / Session
     Show what triggers each tool, how state flows between them, and where error paths branch off.
     ASCII art, a Mermaid diagram (https://mermaid.js.org/syntax/flowchart.html), or an embedded
     sketch are all fine. You'll share this diagram with an AI tool when asking it to implement
     the planning loop and each individual tool. -->

---

┌─────────────────────────────────────────────────────────────┐
│                        FitFindr Flow                        │
└─────────────────────────────────────────────────────────────┘

         User submits style query
                   │
                   ▼
         ┌─────────────────┐
         │  search_listings │
         │  (scan 3 matches)│
         └────────┬────────┘
                  │
         ┌────────▼────────┐
         │  Any results?   │
         └──┬──────────────┘
            │               │
           YES              NO
            │               │
            │               ▼
            │     ┌──────────────────────┐
            │     │  FitFindr explains   │
            │     │  what to try         │
            │     │  differently & STOPS │
            │     └──────────────────────┘
            │
            ▼
  ┌──────────────────────┐
  │   suggest_outfit     │
  │                      │
  │ "Pair this with your │
  │  wide-leg jeans and  │
  │  platform Docs for a │
  │  timeless 90s grunge │
  │  look. Roll sleeves  │
  │  once, tuck front    │
  │  corner for shape."  │
  └──────────┬───────────┘
             │
             ▼
  ┌──────────────────────┐
  │      fit_card        │
  │                      │
  │ "Thrifted this faded │
  │  band tee off depop  │
  │  for $22 — made for  │
  │  my wide-legs. Full  │
  │  look in my stories  │
  │  babies hehe"        │
  └──────────────────────┘

## AI Tool Plan

<!-- For each part of the implementation below, describe:
     - Which AI tool you plan to use (Claude, Copilot, ChatGPT, etc.)
     - What you'll give it as input (which sections of this planning.md, your agent diagram)
     - What you expect it to produce
     - How you'll verify the output matches your spec before moving on

     "I'll use AI to help me code" is not a plan.
     "I'll give Claude my Tool 1 spec (inputs, return value, failure mode) and ask it to implement
     search_listings() using load_listings() from the data loader — then test it against 3 queries
     before trusting it" is a plan. -->

For the initial search_listings function, I'll use claude code to implement the tool 1 spec above with Args:
        description: Keywords describing what the user is looking for
                     (e.g., "vintage graphic tee").
        size:        Size string to filter by, or None to skip size filtering.
                     Matching is case-insensitive (e.g., "M" matches "S/M").
        max_price:   Maximum price (inclusive), or None to skip price filtering.

After this, I will test using pytest and several use cases.

For the suggest outfit function, I'll use claude code (or another model) to implement the function using tool 2 spec above. I'll have it explain to me and from there i'll use some other testing frameworks, such as pytest in isolation. 

For the fit_card function, I'll use claude code (or another model) to implement the last function using the tool 3 spec. I'll have it implement it using a "human in the loop" methodology. lastely i'll use modern testing frameworks to ensure its effacacy. 

**Milestone 3 — Individual tool implementations:**

Yes, all the functions look like how they're implemented in the sped

**Milestone 4 — Planning loop and state management:**

Implemented in `agent.py` using regex query parsing (`_parse_query`). The planning loop matches the architecture diagram:

1. `run_agent()` initializes a session dict (`_new_session`) as the single source of truth.
2. Parsed query params (`description`, `size`, `max_price`) are stored in `session["parsed"]`.
3. `search_listings` runs first; up to 3 matches are stored in `session["search_results"]`.
4. If no results: `session["error"]` is set and the function returns early — `suggest_outfit` and `create_fit_card` are **not** called.
5. On success: top result → `session["selected_item"]` → `session["outfit_suggestion"]` → `session["fit_card"]`.
6. `app.py` `handle_query()` reads the completed session and maps it to the three Gradio panels.

Verified with `tests/test_agent.py`: branching on empty search results, session field population, and downstream tools not called on the no-results path.
---

## A Complete Interaction (Step by Step)

Write out what a full user interaction looks like from start to finish — tool call by tool call. Use a specific example query.

**Example user query:** "I'm looking for a vintage graphic tee under $30. I mostly wear baggy jeans and chunky sneakers. What's out there and how would I style it?"

**Step 1 — User submits query; agent initializes session and parses intent**

The user types the example query into the Gradio search box and leaves the wardrobe set to **"Example wardrobe"**. Clicking **Find it** calls `handle_query()`, which passes the query and `get_example_wardrobe()` into `run_agent()`.

`run_agent()` calls `_new_session()` and stores:
- `session["query"]` — the full natural-language request
- `session["wardrobe"]` — the example wardrobe (10 items, including baggy jeans and chunky sneakers)

The agent parses the query and writes to `session["parsed"]`:
- `description`: `"vintage graphic tee"` (keywords for what to find)
- `max_price`: `30.0` (from "under $30")
- `size`: `None` (no size mentioned — skip size filtering)

The user also mentioned baggy jeans and chunky sneakers; that styling context stays in the original query and is used later by `suggest_outfit` via the wardrobe, not as `search_listings` filters.

**Step 2 — `search_listings` scans the dataset and ranks matches**

The agent calls:

```python
search_listings(
    description="vintage graphic tee",
    size=None,
    max_price=30.0,
)
```

Inside the tool, `load_listings()` loads all 40 mock listings. Listings over $30 are filtered out. Remaining listings are scored by keyword overlap with the description (`vintage`, `graphic`, `tee`, etc.). Listings with score 0 are dropped; the rest are sorted highest-first.

`session["search_results"]` is set to the top matches, e.g.:

| Rank | id | title | price | platform |
|------|----|-------|-------|----------|
| 1 | `lst_033` | Vintage Band Tee — Faded Grey | $19.00 | depop |
| 2 | `lst_006` | Graphic Tee — 2003 Tour Bootleg Style | $24.00 | depop |
| 3 | `lst_002` | Y2K Baby Tee — Butterfly Print | $18.00 | depop |

Because results exist, the agent does **not** set `session["error"]` and does **not** stop early.

**Step 3 — Agent selects the top listing and stores it in session**

The agent picks the highest-scoring result as `session["selected_item"]`:

```python
session["selected_item"] = session["search_results"][0]  # lst_033
```

This listing dict is the single item passed into the outfit and fit-card tools — `suggest_outfit` is never called with an empty or missing item.

**Step 4 — `suggest_outfit` builds styling advice from the wardrobe**

The agent calls:

```python
suggest_outfit(
    new_item=session["selected_item"],   # Vintage Band Tee — Faded Grey
    wardrobe=session["wardrobe"],        # example wardrobe with 10 items
)
```

The tool formats the new item plus wardrobe pieces (notably **baggy straight-leg jeans** `w_001` and **chunky white sneakers** `w_007`) into an LLM prompt and asks for 1–2 complete outfit ideas using named pieces from the closet.

`session["outfit_suggestion"]` is set to a non-empty string, e.g.:

> *"Pair the faded grey band tee with your baggy straight-leg jeans in dark wash and your chunky white sneakers for an easy vintage streetwear look. Tuck just the front of the tee or leave it loose over the waistband — both work with the boxy fit. For a second option, layer your black cropped zip hoodie over the tee, keep the same jeans, and swap to your black combat boots for a grungier night-out vibe."*

Because the wardrobe is not empty, the response references specific wardrobe items rather than only generic advice.

**Step 5 — `create_fit_card` turns the outfit into a shareable caption**

The agent calls:

```python
create_fit_card(
    outfit=session["outfit_suggestion"],
    new_item=session["selected_item"],
)
```

The tool sends the outfit text plus item details (title, price, platform) to the LLM with a casual OOTD-style prompt and higher temperature so captions feel varied.

`session["fit_card"]` is set to a 2–4 sentence caption, e.g.:

> *"thrifted this faded grey band tee off depop for $19 and it was literally made for my baggy jeans era. full fit breakdown in my stories — the chunky sneaker combo is undefeated rn"*

**Step 6 — Agent returns session; Gradio maps results to the three panels**

`run_agent()` returns the completed session with `session["error"]` still `None`. `handle_query()` formats `session["selected_item"]` into readable listing text and passes three strings to the UI:

- **Top listing found** — formatted details for `lst_033`
- **Outfit idea** — `session["outfit_suggestion"]`
- **Your fit card** — `session["fit_card"]`

**Final output to user:**

The user sees three side-by-side panels in the FitFindr UI:

**🛍️ Top listing found**
```
Vintage Band Tee — Faded Grey
$19.00 · depop · size L · fair condition
Faded grey band-style tee with distressed graphic. Crew neck. Fits boxy.
Colors: grey, charcoal
Tags: vintage, grunge, band tee, graphic tee, streetwear
```

**👗 Outfit idea**
```
Pair the faded grey band tee with your baggy straight-leg jeans in dark wash
and your chunky white sneakers for an easy vintage streetwear look. Tuck just
the front of the tee or leave it loose over the waistband — both work with
the boxy fit. For a second option, layer your black cropped zip hoodie over
the tee, keep the same jeans, and swap to your black combat boots for a
grungier night-out vibe.
```

**✨ Your fit card**
```
thrifted this faded grey band tee off depop for $19 and it was literally made
for my baggy jeans era. full fit breakdown in my stories — the chunky sneaker
combo is undefeated rn
```

---

**Alternate path (no results):** If `search_listings` returned `[]` (e.g., query `"designer ballgown size XXS under $5"`), the agent would set `session["error"]` to a helpful message like *"No listings matched — try raising your max price, dropping the size filter, or broadening your description."*, return immediately, and **not** call `suggest_outfit` or `create_fit_card`. The UI would show that message in the first panel only, with the other two panels empty.
