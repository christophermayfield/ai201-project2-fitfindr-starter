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
<!-- Describe what this tool does in 1–2 sentences -->
this is a helps users finding secondhand pieces of clothing. It helps them figure out how to wear them. 

**Input parameters:**
<!-- List each parameter, its type, and what it represents -->
- `description` (str): describes context of the item
- `size` (str): Waist, Length
- `max_price` (float): maximum price they are willing to pay
- `category` (str): tops, bottoms, outer
-  `Conditions` (str): describes what condition the item is in
-  `brand`(str): brand of the item
- `colors`([str]): color of the item
- `platform`(str): where the item is sold
- `id` (str): unique identifier for the item
- `title`(str): title of the item
- `style_tags`([str]): tags that describe the style


**What it returns:**
<!-- Describe the return value — what fields does a result contain? -->
 Returns:
        A list of matching listing dicts, sorted by relevance (best match first).
        

**What happens if it fails or returns nothing:**
<!-- What should the agent do if no listings match? -->
Returns an empty list if nothing matches — does NOT raise an exception.
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
- `new_item` (dict): ...
- `wardrobe` (dict): ...

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
| create_fit_card | Outfit input is missing or incomplete | |

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

**Milestone 3 — Individual tool implementations:**

**Milestone 4 — Planning loop and state management:**

---

## A Complete Interaction (Step by Step)

Write out what a full user interaction looks like from start to finish — tool call by tool call. Use a specific example query.

**Example user query:** "I'm looking for a vintage graphic tee under $30. I mostly wear baggy jeans and chunky sneakers. What's out there and how would I style it?"

**Step 1:**
<!-- What does the agent do first? Which tool is called? With what input? -->

**Step 2:**
<!-- What happens next? What was returned from step 1? What tool is called now? -->

**Step 3:**
<!-- Continue until the full interaction is complete -->

**Final output to user:**
<!-- What does the user actually see at the end? -->
