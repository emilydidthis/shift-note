# Pinned Tasks from Returns & Alphabetizing Sheets

## Overview
Add "pinned" todo items pulled from two additional Google Sheets (Returns and Alphabetizing) that appear at the top of the todo list with special styling. Tasks are matched to the current week by parsing date ranges from task names.

## Data Source
- **Same spreadsheet** as existing app data
- Two new tabs: `Returns` and `Alphabetizing`
- **Returns columns**: Task, Status, Owner, Stage, Due date, Notes
- **Alphabetizing columns**: Task, Section to Alphabetize, Status, Shelves completed so far, Due date, Notes

## Requirements
1. One pinned todo per sheet per week (2 total: one Returns, one Alphabetizing)
2. Always show at the top of the todo list
3. Special badge/styling to distinguish from regular todos
4. Parse date ranges from task names (e.g., "June 1-6 Macmillan Return") to match current week
5. Show task name + status

---

## Implementation Plan

### 1. Apps Script Changes (`apps-script.js`)

**Add sheet names to SHEET_NAMES** (line 4):
```javascript
const SHEET_NAMES = ['Employees', 'Announcements', 'Todos', 'Lists', 'DailyInfo', 'Archive', 'Returns', 'Alphabetizing'];
```

**Add default headers** (line 36-46):
```javascript
Returns: ['Task', 'Status', 'Owner', 'Stage', 'Due date', 'Notes'],
Alphabetizing: ['Task', 'Section to Alphabetize', 'Status', 'Shelves completed so far', 'Due date', 'Notes'],
```

**Read sheets in doGet** (after line 252):
```javascript
const returns = parseRows(allData['Returns']);
const alphabetizing = parseRows(allData['Alphabetizing']);
```

**Return pinned tasks in response** (add to JSON output):
```javascript
pinnedTasks: [
  ...returns.map(r => ({ task: r.Task, status: r.Status, notes: r.Notes, source: 'Returns' })),
  ...alphabetizing.map(a => ({ task: a.Task, status: a.Status, notes: a['Notes'], source: 'Alphabetizing' }))
]
```

### 2. Frontend State Changes (`index.html`)

**Add pinnedTasks to default state** (around line 1461):
```javascript
let state = {
  // ... existing fields ...
  pinnedTasks: []
};
```

**Update handleCloudData** (around line 1740):
```javascript
if (data.pinnedTasks) {
  state.pinnedTasks = data.pinnedTasks;
}
```

**Update saveToLocal** (around line 1695):
```javascript
function saveToLocal() {
  localStorage.setItem('shiftNote', JSON.stringify({
    // ... existing fields ...
    pinnedTasks: state.pinnedTasks
  }));
}
```

**Update loadFromLocal** (around line 1671):
```javascript
state.pinnedTasks = parsed.pinnedTasks || [];
```

### 3. Date Parsing Logic (`index.html`)

**Add helper function** to parse week range from task name:
```javascript
function parseWeekRange(taskName) {
  // Match patterns like "June 1-6", "Aug 2-8", "September 15-21"
  const match = taskName.match(/([A-Za-z]+)\s+(\d{1,2})\s*-\s*(\d{1,2})/);
  if (!match) return null;
  
  const month = new Date(Date.parse(match[1] + ' 1, 2026')).getMonth();
  const startDay = parseInt(match[2]);
  const endDay = parseInt(match[3]);
  
  const now = new Date();
  const year = now.getFullYear();
  
  const startDate = new Date(year, month, startDay);
  const endDate = new Date(year, month, endDay);
  
  return { start: startDate, end: endDate };
}

function isCurrentWeek(taskName) {
  const range = parseWeekRange(taskName);
  if (!range) return false;
  
  const now = new Date();
  const weekStart = new Date(now);
  weekStart.setDate(now.getDate() - now.getDay()); // Sunday
  const weekEnd = new Date(weekStart);
  weekEnd.setDate(weekStart.getDate() + 6); // Saturday
  
  return range.start <= weekEnd && range.end >= weekStart;
}
```

### 4. CSS Styling (`index.html`)

**Add pinned task styles** (after line 546):
```css
.card.card-pinned {
  border-left: 3px solid var(--accent);
  background: rgba(212, 181, 122, 0.08);
}

.card.card-pinned:hover {
  background: rgba(212, 181, 122, 0.15);
}

.pinned-tag {
  font-size: 9px;
  font-weight: 700;
  letter-spacing: 0.5px;
  background: var(--accent);
  color: var(--white);
  padding: 1px 5px;
  border-radius: 3px;
  margin-right: 6px;
  vertical-align: middle;
}

.pinned-section {
  margin-bottom: 12px;
  padding-bottom: 8px;
  border-bottom: 1px dashed var(--border);
}

.pinned-section-header {
  font-size: 11px;
  font-weight: 600;
  color: var(--text-faint);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 8px;
}

.pinned-link {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 11px;
  color: var(--primary);
  text-decoration: none;
  margin-top: 6px;
  opacity: 0.7;
  transition: opacity 0.15s;
}

.pinned-link:hover {
  opacity: 1;
  text-decoration: underline;
}

.pinned-link-icon {
  font-size: 12px;
}
```

### 5. Render Logic Changes (`index.html`)

**Add pinned tasks container** in HTML (before `#todoList`, around line 1353):
```html
<div class="pinned-section" id="pinnedSection" style="display: none;">
  <div class="pinned-section-header">Pinned This Week</div>
  <div class="card-list" id="pinnedList"></div>
</div>
<div class="card-list" id="todoList"></div>
```

**Update render function** (around line 2400) to render pinned tasks first:
```javascript
// Render pinned tasks
const pinnedList = document.getElementById('pinnedList');
const pinnedSection = document.getElementById('pinnedSection');
const currentWeekPinned = state.pinnedTasks.filter(t => isCurrentWeek(t.task));

if (currentWeekPinned.length > 0) {
  pinnedSection.style.display = 'block';
  pinnedList.innerHTML = currentWeekPinned.map(t => `
    <div class="card card-pinned" data-id="pinned-${t.source}">
      <div class="todo-card-row">
        <div class="todo-card-body">
          <div class="card-text">
            <span class="pinned-tag">${t.source.toUpperCase()}</span>
            ${escapeHtml(t.task)}
          </div>
          <div class="card-meta">${t.status} · ${t.notes || ''} · <a href="${SHEET_URL}" target="_blank" class="pinned-link">🔗 Link to Update</a></div>
          <a href="${SHEET_URL}" target="_blank" class="pinned-link">
            <span class="pinned-link-icon">📊</span> Edit in Sheets
          </a>
        </div>
      </div>
    </div>
  `).join('');
} else {
  pinnedSection.style.display = 'none';
}

// ... existing todo rendering code ...
```

**Add SHEET_URL constant** (near APPS_SCRIPT_URL):
```javascript
const SHEET_URL = 'https://docs.google.com/spreadsheets/d/YOUR_SPREADSHEET_ID/edit';
```

Alternatively, have the Apps Script return the spreadsheet URL in the API response:
```javascript
// In apps-script.js doGet:
return ContentService.createTextOutput(JSON.stringify({
  // ... existing fields ...
  sheetUrl: getSpreadsheet().getUrl(),
  // ...
}))
```

---

## Files to Modify

1. **`apps-script.js`**
   - Add 'Returns' and 'Alphabetizing' to SHEET_NAMES
   - Add default headers for new sheets
   - Read and return pinned tasks in doGet

2. **`index.html`**
   - Add pinnedTasks to state
   - Add CSS for pinned styling
   - Add date parsing helpers
   - Add pinned tasks HTML container
   - Update render function to show pinned tasks
   - Update save/load functions for localStorage

---

## Edge Cases

1. **No matching week**: If no tasks match the current week, hide the pinned section
2. **Multiple tasks per sheet**: Show all matching tasks from each sheet (e.g., if there are two Returns tasks for the same week)
3. **Invalid date format**: If task name doesn't match expected format, exclude from pinned
4. **Completed tasks**: Show all tasks from the sheets regardless of status (status is displayed as metadata)

---

## Testing

1. Add test data to Returns and Alphabetizing sheets with current week dates
2. Verify pinned tasks appear at top with correct styling
3. Verify date parsing works for various formats (June 1-6, Aug 2-8, etc.)
4. Verify pinned section hides when no tasks match current week
5. Verify regular todos still work correctly below pinned section
