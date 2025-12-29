# Golden Prompt Library

This directory contains the golden prompt library for video generation testing.

## Structure

- `prompt_library.json` - Main prompt library with all validated prompts
- `categories/` - Prompts organized by category (optional subdirectory)

## Usage

```python
import json

with open('data/golden_prompts/prompt_library.json', 'r') as f:
    library = json.load(f)

# Get a specific prompt
prompt = library['prompts']['GP_CHAR_001']
canonical = prompt['canonical_prompt']
```

## Adding New Prompts

1. Test the prompt with multiple scenarios
2. Record performance metrics (CLIP score, temporal consistency)
3. Get expert validation
4. Add to `prompt_library.json` with all required fields
5. Update the version number and total_prompts count

## Prompt Fields

Required:
- `prompt_id`: Unique identifier (format: GP_{CATEGORY}_{NUMBER})
- `category`: Category path (e.g., "characters/locomotion")
- `canonical_prompt`: The validated prompt text
- `tested_scenarios`: List of scenario IDs where tested
- `expert_validated`: Boolean indicating validation status

Optional:
- `template`: Parametrized version with {variables}
- `variables`: Dictionary of variable options
- `performance`: Performance metrics
- `validation_date`: Date of validation
- `notes`: Additional notes
- `best_model_versions`: Model versions where this performs best
