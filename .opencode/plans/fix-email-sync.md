# Fix Email and Sync Issues

## Issue 1: Email works once then stops
**Root cause**: `window.location.href = mailto:` changes the browser URL to `mailto:...`, breaking page state on subsequent clicks. `a.click()` helps but browsers may block repeated programmatic mailto clicks.

**Fix**: Use `window.open(mailtoLink, '_blank')` instead. This opens mailto in a new context without affecting the current page's URL or history.

## Issue 2: Sync failed
**Root cause**: Need to investigate. Possible causes:
1. `handleCloudData()` employee merge logic comparing `_updatedAt` timestamps might be causing conflicts
2. The cloud save queue might be failing silently
3. CORS or Apps Script deployment issue

**Fix approach**:
1. Add error logging to `saveToCloud()` to see what's failing
2. Check if the `_updatedAt` employee merge is causing data loss
3. If cloud has no employee `_updatedAt` yet (first sync), local data should win

## Files to Modify
- `/Users/emilyzhao/Documents/code/shift-note/index.html`

## Tradeoffs
- `window.open()` might be blocked by popup blockers if not user-initiated (but it is user-initiated here)
- For sync: need to handle the case where cloud data has no `_updatedAt` (first run) - should always use local data in that case
