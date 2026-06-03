# Name Display Format Update Plan

## User Request
Employees now have last initials (e.g., "John D", "Emma L"). Update display:
1. **Avatars**: Use initials (e.g., "John D" → "JD") - already working via `getInitials()`
2. **Open/Close assignee dropdowns**: Show initials only (e.g., "JD")
3. **Author dropdowns** (announcements & todos): Show first name only (e.g., "John")
4. **Assignee chips**: Show first name only
5. **Todo filter dropdown**: Show first name only
6. **Card meta text**: Show first name only (e.g., "Added by John")

## Changes Needed

### 1. Add Helper Function
```javascript
function getFirstName(name) {
  return name.split(' ')[0];
}
```

### 2. Update Dropdowns
- `generateEmployeeOptions(selected)`: Add a `displayFn` parameter to control display text
- Open/close dropdowns: Use `getInitials()` for display
- Author dropdowns: Use `getFirstName()` for display

### 3. Update Assignee Chips
- `generateAssigneeChips()`: Show first name only

### 4. Update Todo Filter
- Show first name only

### 5. Update Card Meta Display
- Announcements: `${getFirstName(a.author)} - ${formatTime(a.timestamp)}`
- Todos: `Added by ${getFirstName(t.author)} - ${formatTime(t.timestamp)}`

### 6. Update Avatar Tooltips
- Avatar stack tooltips: `${getFirstName(a)}: Done/Pending`

## Files
- `/Users/emilyzhao/Documents/code/shift-note/index.html`

## Tradeoffs
- Keep full name as value in dropdowns (for data integrity), only change display text
- `getInitials()` already handles "John D" → "JD" correctly
