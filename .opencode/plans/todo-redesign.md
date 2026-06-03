# Todo Card Redesign Plan

## User Requirements
1. Tasks assigned to multiple people (or "All") should show all avatars left-aligned
2. Each avatar should indicate whether that person has completed the task
3. Task is only marked complete when ALL assignees have completed it (already working)
4. A checkbox to the left of the task

## Current State
- Todo cards show: progress bar → task text → tag chips with checkboxes → meta
- Tags show assignee names with inline checkboxes
- No avatars on todo cards (only announcements use avatars)
- `isTodoComplete()` already correctly requires all assignees to complete

## Proposed Design

### Card Layout (left to right)
```
[☐] [Avatar1][Avatar2][Avatar3]  Task text here
     (green border = done)        Progress bar (if multi-assignee)
                                  Added by X - time
```

### Changes

#### 1. CSS Additions
- `.todo-card-row` - flex container for checkbox + avatars + body
- `.todo-checkbox` - larger checkbox on the left (18px), styled
- `.avatar-stack` - overlapping avatar group (negative margin for overlap)
- `.avatar-stack .avatar` - smaller (24px), with completion indicator ring
- `.avatar.done` - green ring/border around avatar
- `.avatar.pending` - muted/gray ring

#### 2. HTML Structure (render function)
Replace current todo card structure:
```html
<div class="card ${complete ? 'completed' : ''}" data-id="${t.id}">
  <div class="todo-card-row">
    <input type="checkbox" class="todo-checkbox" 
           ${complete ? 'checked' : ''} 
           onclick="toggleTodoCompletion('${t.id}')" />
    <div class="avatar-stack">
      ${t.assignees.map(a => `
        <div class="avatar ${t.completions[a] ? 'done' : 'pending'}" 
             onclick="toggleCompletion('${t.id}', '${a}')"
             title="${a}: ${t.completions[a] ? 'Done' : 'Pending'}">
          ${getInitials(a)}
        </div>
      `).join('')}
    </div>
    <div class="card-body">
      <div class="card-text">${escapeHtml(t.content)}</div>
      ${t.assignees.length > 1 ? `
        <div class="progress-bar-container">
          <div class="progress-bar-bg">
            <div class="progress-bar-fill" style="width: ${pct}%"></div>
          </div>
          <div class="progress-text">${done}/${total} completed</div>
        </div>
      ` : ''}
      <div class="card-meta">Added by ${t.author} - ${formatTime(t.timestamp)}</div>
    </div>
  </div>
  <button class="card-edit" ...>✎</button>
  <button class="card-delete" ...>×</button>
</div>
```

#### 3. New JS Function
- `toggleTodoCompletion(id)` - when clicking the main checkbox:
  - If task is complete: uncheck all assignees
  - If task is not complete: check all assignees (bulk complete)

#### 4. Remove
- Old `.card-tags` tag chip system from todo cards
- Old inline tag checkboxes

## Files to Modify
- `/Users/emilyzhao/Documents/code/shift-note/index.html`
  - CSS: Add todo-card-row, todo-checkbox, avatar-stack styles
  - JS render(): Restructure todo card HTML
  - JS: Add toggleTodoCompletion() function

## Tradeoffs
- Bulk complete via main checkbox is convenient but loses per-person granularity
- Could alternatively: main checkbox only shows state (not clickable), users click individual avatars
- Recommendation: make main checkbox clickable for bulk toggle, avatars clickable for individual toggle
