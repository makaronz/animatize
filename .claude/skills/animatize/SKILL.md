```markdown
# animatize Development Patterns

> Auto-generated skill from repository analysis

## Overview
This skill teaches you how to contribute to the `animatize` JavaScript codebase, which is organized without a formal framework and follows clear, consistent conventions. You'll learn how to extend API endpoints, develop new UI modules, and update documentation using established workflows and coding patterns. The repository emphasizes modularity, maintainability, and thorough testing.

## Coding Conventions

### File Naming
- Use **snake_case** for all file names.
  - Example: `my_module.js`, `user_profile.js`

### Imports
- Use **relative import paths**.
  - Example:
    ```js
    import { fetchData } from './utils/data_fetcher.js';
    ```

### Exports
- Use **named exports** (not default).
  - Example:
    ```js
    // In utils/data_fetcher.js
    export function fetchData(url) { /* ... */ }
    ```

### Commit Messages
- Freeform, no strict prefix required.
- Average message length: ~68 characters.

## Workflows

### API Endpoint Extension with Contract Tests
**Trigger:** When you need to add new features or metadata to an existing API endpoint and ensure it is properly tested.  
**Command:** `/extend-api-endpoint`

1. Modify the API implementation file to add new fields or logic.
   - Example (in `src/web/app.py`):
     ```python
     @app.route('/api/data')
     def get_data():
         result = get_existing_data()
         result['new_field'] = compute_new_value()
         return jsonify(result)
     ```
2. Update or add integration/contract test files to cover the new behavior.
   - Example (in `tests/integration/test_data.py`):
     ```python
     def test_new_field_in_response(client):
         response = client.get('/api/data')
         assert 'new_field' in response.json
     ```
3. Optionally update `.gitignore` to handle new artifacts if needed.

### UI Feature Module Development
**Trigger:** When you want to add a new user-facing feature or module to the web UI.  
**Command:** `/add-ui-module`

1. Create or update ES module(s) under `src/web/static/modules/` for the new feature.
   - Example (`src/web/static/modules/animation_tools.js`):
     ```js
     export function startAnimation() { /* ... */ }
     ```
2. Update `src/web/static/app.js` to import and integrate the new module(s).
   - Example:
     ```js
     import { startAnimation } from './modules/animation_tools.js';
     startAnimation();
     ```
3. Modify `src/web/static/index.html` to include new UI elements or containers.
   - Example:
     ```html
     <div id="animation-controls"></div>
     ```
4. Update `src/web/static/styles.css` for new UI components.
   - Example:
     ```css
     #animation-controls { margin: 1em 0; }
     ```
5. Wire up to backend endpoints if needed.

### Documentation Report Update
**Trigger:** When you want to add a new report or update an existing strategic or audit document.  
**Command:** `/update-docs-report`

1. Create or update a markdown file in `docs/` with new analysis, models, or recommendations.
   - Example: `docs/performance_report.md`
2. Commit the changes with a detailed summary.

## Testing Patterns

- **Test Framework:** Unknown (not detected), but test files follow the pattern `*.test.ts`.
- **Location:** Test files are typically placed alongside source files or in a `tests/` directory.
- **Example:**
  ```typescript
  // math_utils.test.ts
  import { add } from './math_utils';

  test('adds two numbers', () => {
    expect(add(2, 3)).toBe(5);
  });
  ```

## Commands

| Command               | Purpose                                                         |
|-----------------------|-----------------------------------------------------------------|
| /extend-api-endpoint  | Extend an API endpoint and update/add contract/integration tests|
| /add-ui-module        | Add a new UI feature/module to the web application              |
| /update-docs-report   | Add or update documentation or analysis reports in `docs/`      |
```
