# Fix Todo Filter and Task Page Name Matching

## Problems

### Issue 1: Todo filter by name doesn't work
The dropdown shows first names (e.g., "Emily") but the actual assignee values are full names (e.g., "Emily Z"). So `t.assignees.includes("Emily")` never matches "Emily Z".

### Issue 2: Task page (?user=Emily) doesn't show completions
`taskUser` from URL is "Emily" but employee names are "Emily Z". So:
- `t.assignees.includes(taskUser)` won't match
- `t.completions[taskUser]` won't find completion status
- `toggleCompletion('${t.id}', '${taskUser}')` toggles wrong key

## Root Cause
Both issues stem from the same problem: display names are first names only, but data uses full names.

## Solution

Add a helper function to resolve a display name (first name) to the full employee name:

```javascript
function resolveEmployee(displayName) {
  // If it's already a full name, return it
  if (state.employees.includes(displayName)) return displayName;
  // Otherwise find by first name
  return state.employees.find(e => getFirstName(e) === displayName) || displayName;
}
```

### Apply to:
1. **Todo filter**: When filtering, resolve the display name to full name
2. **Task page**: Resolve `taskUser` to full employee name on page load
3. **Toggle completion**: Use resolved name

## Files to Modify
- `/Users/emilyzhao/Documents/code/shift-note/index.html`

## Tradeoffs
- If two employees share the same first name (e.g., "Emily Z" and "Emily L"), `find()` returns the first match. This is acceptable for now.
- Alternative: use full names in dropdowns but that defeats the "first name only" display requirement.
