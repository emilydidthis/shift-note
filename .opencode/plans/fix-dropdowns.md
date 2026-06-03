# Fix Open/Close Dropdown Issues

## Problems
1. **Initials showing only 1 letter**: "Emily Z" should show "EZ" but shows "E"
2. **Dropdown menu opens upward**: Native browser behavior due to insufficient space below

## Root Cause Analysis

### Issue 1: Initials
The `getInitials` function looks correct:
```javascript
function getInitials(name) {
  return name.split(' ').map(w => w[0]).join('').substring(0, 2).toUpperCase();
}
```
For "Emily Z" → ["Emily", "Z"] → ["E", "Z"] → "EZ"

However, the user reports it shows only "E". Possible causes:
- The select element's width might be clipping the text
- The `displayFn` parameter might not be working correctly in some edge case
- The `selected` value in `state.dailyInfo.open_assignee` might be "Emily" (old format) while the employee list has "Emily Z", causing the `selected` comparison to fail (but this wouldn't affect display text)

### Issue 2: Dropdown Positioning
Native `<select>` elements open upward when there's not enough space below. The header has `padding: 12px 20px` which doesn't leave room for the dropdown to open downward.

## Proposed Fixes

### Fix 1: Initials Display
- Add `width: auto` and `white-space: nowrap` to `.shift-field select` to ensure text isn't clipped
- Update `getInitials` to handle edge cases: if only one word, take first 2 characters
- Verify `generateEmployeeOptions` is being called correctly with `getInitials` as displayFn

### Fix 2: Dropdown Positioning
- Add `padding-bottom: 40px` to the header to give dropdowns room to open downward
- Alternatively, add `position: relative` to the header and adjust select positioning

## Files to Modify
- `/Users/emilyzhao/Documents/code/shift-note/index.html`
  - CSS: Update `.shift-field select` styling and header padding
  - JS: Update `getInitials` to handle single-word names

## Tradeoffs
- Adding padding to header increases its height slightly
- Native selects have limited customization; custom dropdowns would be more work but give full control
