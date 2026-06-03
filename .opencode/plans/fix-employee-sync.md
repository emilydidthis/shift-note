# Fix Employee Name Persistence

## Problem
Employee name changes don't persist after page refresh.

## Root Cause Analysis

### Apps Script (SETUP.md)
The script actually looks correct:
- `doPost()` saves `data.employees` to the sheet
- `doGet()` reads and returns employees
- `saveData()` properly handles upsert

### Frontend (index.html)
The real issue is in `handleCloudData()`:
```javascript
state.employees = cloudEmployees;  // Line 1247
```
This **blindly overwrites** local employees with cloud data on every page load.

### The Bug Flow
1. User edits employee name → `state.employees` updated locally
2. User clicks "Done" → `closeSettings()` calls `saveAll()`
3. `saveAll()` saves to localStorage + async cloud save
4. **If page refreshes before cloud save completes**: cloud still has old data
5. On next load: `handleCloudData()` overwrites local with old cloud data → changes lost

## Proposed Fixes

### Fix 1: Frontend - Merge employees on cloud sync
Instead of `state.employees = cloudEmployees`, use:
```javascript
// Only use cloud employees if local is empty or cloud has newer data
if (!state.employees || state.employees.length === 0) {
  state.employees = cloudEmployees;
}
```

### Fix 2: Apps Script - Add timestamp to employee saves
Add `_updatedAt` to employee data so we can compare versions:
```javascript
function doPost(e) {
  const data = JSON.parse(e.postData.contents);
  if (data.action === 'saveAll') {
    if (data.employees) {
      data.employees._updatedAt = new Date().getTime();
      saveData('employees', data.employees);
    }
    // ...
  }
}
```

### Fix 3: Frontend - Wait for cloud save before allowing refresh
Add a brief loading indicator when `saveToCloud()` is in progress.

## Recommendation
Start with **Fix 1** (frontend merge) - it's the simplest and most impactful. The script doesn't actually need changes for this to work.

If the user wants cross-device sync, we can add **Fix 2** (timestamp-based merging).

## Files to Modify
- `/Users/emilyzhao/Documents/code/shift-note/index.html` - Fix `handleCloudData()` merge logic
- `/Users/emilyzhao/Documents/code/shift-note/SETUP.md` - Only if we change the Apps Script

## Tradeoffs
- **Frontend-only fix**: Each device can have different employee names (no cross-device sync)
- **Script + timestamp fix**: Cross-device sync but requires re-deploying the Apps Script
