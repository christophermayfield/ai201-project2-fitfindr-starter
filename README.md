# FitFindr — Starter Kit

This starter kit contains everything you need to begin Project 2.

## What's Included

```
ai201-project2-fitfindr-starter/
├── data/
│   ├── listings.json          # 40 mock secondhand listings
│   └── wardrobe_schema.json   # Wardrobe format + example wardrobe
├── tests/
│   └── test_tools.py          # Pytest suite for the three tools
├── utils/
│   └── data_loader.py         # Helper functions for loading the data
├── tools.py                   # search_listings, suggest_outfit, create_fit_card
├── agent.py                   # Planning loop orchestration
├── app.py                     # Gradio UI
├── planning.md                # Your planning template — fill this out first
└── requirements.txt           # Python dependencies
```

## Setup

```bash
pip install -r requirements.txt
```

Set your Groq API key in a `.env` file (get a free key at [console.groq.com](https://console.groq.com)):
```
GROQ_API_KEY=your_key_here
```

## The Mock Listings Dataset

`data/listings.json` contains 40 mock secondhand listings across categories (tops, bottoms, outerwear, shoes, accessories) and styles (vintage, y2k, grunge, cottagecore, streetwear, and more).

Each listing has: `id`, `title`, `description`, `category`, `style_tags`, `size`, `condition`, `price`, `colors`, `brand`, and `platform`.

Load it with:
```python
from utils.data_loader import load_listings
listings = load_listings()
```

## The Wardrobe Schema

`data/wardrobe_schema.json` defines the format your agent uses to represent a user's existing wardrobe. It includes:

- `schema`: field definitions for a wardrobe item
- `example_wardrobe`: a sample wardrobe with 10 items you can use for testing
- `empty_wardrobe`: a starting template for a new user

Load an example wardrobe with:
```python
from utils.data_loader import get_example_wardrobe
wardrobe = get_example_wardrobe()
```

## Tests

The tool implementations are covered by `tests/test_tools.py`. Each documented failure mode from `planning.md` has at least one test. LLM calls in `suggest_outfit` and `create_fit_card` are mocked so tests run offline without hitting the Groq API.

Run the suite:

```bash
python3 -m pytest tests/test_tools.py -v
```

### Test coverage

| Tool | Test | What it verifies |
|------|------|------------------|
| `search_listings` | `test_no_results_returns_empty_list_without_raising` | No matches → `[]`, no exception |
| `search_listings` | `test_empty_description_returns_empty_list` | Empty description → `[]` |
| `search_listings` | `test_matching_query_returns_sorted_results` | Valid query returns filtered, ranked results |
| `suggest_outfit` | `test_empty_wardrobe_returns_non_empty_general_advice` | Empty wardrobe → non-empty general styling advice |
| `suggest_outfit` | `test_empty_wardrobe_fallback_when_llm_fails` | LLM failure + empty wardrobe → fallback advice |
| `suggest_outfit` | `test_non_empty_wardrobe_returns_suggestion` | Example wardrobe → outfit suggestion |
| `create_fit_card` | `test_empty_outfit_returns_error_message_without_raising` | Missing outfit → descriptive error string |
| `create_fit_card` | `test_whitespace_outfit_returns_error_message` | Whitespace-only outfit → same error path |
| `create_fit_card` | `test_llm_failure_returns_template_caption` | LLM failure → template caption with price/platform |
| `create_fit_card` | `test_valid_outfit_returns_caption` | Valid outfit → caption from LLM |

### Latest results

```
============================== test session starts ==============================
collected 10 items

tests/test_tools.py::TestSearchListings::test_no_results_returns_empty_list_without_raising PASSED
tests/test_tools.py::TestSearchListings::test_empty_description_returns_empty_list PASSED
tests/test_tools.py::TestSearchListings::test_matching_query_returns_sorted_results PASSED
tests/test_tools.py::TestSuggestOutfit::test_empty_wardrobe_returns_non_empty_general_advice PASSED
tests/test_tools.py::TestSuggestOutfit::test_empty_wardrobe_fallback_when_llm_fails PASSED
tests/test_tools.py::TestSuggestOutfit::test_non_empty_wardrobe_returns_suggestion PASSED
tests/test_tools.py::TestCreateFitCard::test_empty_outfit_returns_error_message_without_raising PASSED
tests/test_tools.py::TestCreateFitCard::test_whitespace_outfit_returns_error_message PASSED
tests/test_tools.py::TestCreateFitCard::test_llm_failure_returns_template_caption PASSED
tests/test_tools.py::TestCreateFitCard::test_valid_outfit_returns_caption PASSED

============================== 10 passed in 0.13s ===============================
```

## Where to Start

1. **Read `planning.md` and fill it out before writing any code.**
2. Verify the data loads correctly by running `python utils/data_loader.py`.
3. Build and test each tool individually before connecting them through your planning loop.

Your implementation files go in this same directory. There's no required file structure for your agent code — organize it however makes sense for your design.
