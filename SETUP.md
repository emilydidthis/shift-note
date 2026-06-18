# Shift Note - Google Sheets Setup Guide

This guide walks you through setting up Google Sheets as the backend for your shift note app.

---

## Step 1: Set up Google Apps Script

1. Go to [script.google.com](https://script.google.com) and click **New project**
2. Delete any existing code in the editor
3. Paste the code below (Step 2)
4. Click **Save** (floppy disk icon)

---

## Step 2: Apps Script Code

Copy and paste this entire block into the Apps Script editor:

```javascript
// Shift Note API v2 - Multi-sheet, row-based storage
// Updated 06/18/26 — migrated from single-sheet JSON to multi-sheet format

const SHEET_NAMES = ['Employees', 'Announcements', 'Todos', 'Lists', 'DailyInfo', 'Archive'];

function getSpreadsheet() {
  const props = PropertiesService.getScriptProperties();
  let ssId = props.getProperty('SHEET_ID');

  if (!ssId) {
    const ss = SpreadsheetApp.create('Shift Note Data');
    ssId = ss.getId();
    props.setProperty('SHEET_ID', ssId);

    const sheet = ss.getSheets()[0];
    sheet.setName('Employees');
    sheet.appendRow(['id', 'name', 'createdAt']);
    SpreadsheetApp.flush();
  }

  return SpreadsheetApp.openById(ssId);
}

function getSheet(name) {
  const ss = getSpreadsheet();
  let sheet = ss.getSheetByName(name);
  if (!sheet) {
    sheet = ss.insertSheet(name);
    // Add default headers based on sheet name
    const headers = getDefaultHeaders(name);
    if (headers.length > 0) sheet.appendRow(headers);
    SpreadsheetApp.flush();
  }
  return sheet;
}

function getDefaultHeaders(name) {
  const defaults = {
    Employees: ['id', 'name', 'createdAt'],
    Announcements: ['id', 'content', 'author', 'timestamp', 'updatedAt'],
    Todos: ['id', 'content', 'assignees', 'completions', 'author', 'timestamp', 'dueDate', 'completedAt', 'updatedAt'],
    Lists: ['id', 'category', 'content', 'purchased', 'timestamp', 'title', 'url'],
    DailyInfo: ['folksWorking', 'registerOpen', 'registerClose', 'openAssignee', 'closeAssignee', 'monthlyGoalCurrent', 'monthlyGoalTarget', 'updatedAt'],
    Archive: ['id', 'type', 'content', 'assignees', 'author', 'timestamp', 'completedAt', 'archivedAt'],
  };
  return defaults[name] || [];
}

// --- Read helpers ---

function readSheet(name) {
  const sheet = getSheet(name);
  const data = sheet.getDataRange().getValues();
  if (data.length <= 1) return [];
  const headers = data[0];
  const rows = [];
  for (let i = 1; i < data.length; i++) {
    const row = {};
    headers.forEach((h, j) => row[h] = data[i][j]);
    rows.push(row);
  }
  return rows;
}

function readSingleRow(name) {
  const rows = readSheet(name);
  return rows.length > 0 ? rows[0] : {};
}

function getEmployeeName(id) {
  const employees = readSheet('Employees');
  const emp = employees.find(e => String(e.id) === String(id));
  return emp ? emp.name : '';
}

function resolveEmployeeData(items, authorField) {
  return items.map(item => {
    const resolved = { ...item };
    // Resolve author
    if (authorField && resolved[authorField]) {
      resolved[authorField] = getEmployeeName(resolved[authorField]);
    }
    // Resolve assignees array
    if (resolved.assignees) {
      try {
        const arr = typeof resolved.assignees === 'string' ? JSON.parse(resolved.assignees) : resolved.assignees;
        resolved.assignees = arr.map(a => a === 'All' ? 'All' : getEmployeeName(a));
      } catch (e) {}
    }
    // Resolve completions keys
    if (resolved.completions) {
      try {
        const obj = typeof resolved.completions === 'string' ? JSON.parse(resolved.completions) : resolved.completions;
        const resolvedObj = {};
        Object.keys(obj).forEach(k => {
          resolvedObj[k === 'All' ? 'All' : getEmployeeName(k)] = obj[k];
        });
        resolved.completions = resolvedObj;
      } catch (e) {}
    }
    return resolved;
  });
}

// --- Write helpers ---

function appendRow(sheetName, item) {
  const sheet = getSheet(sheetName);
  const headers = sheet.getDataRange().getValues()[0];
  const row = headers.map(h => {
    const val = item[h];
    if (Array.isArray(val) || (val !== null && typeof val === 'object')) {
      return JSON.stringify(val);
    }
    return val !== undefined ? val : '';
  });
  sheet.appendRow(row);
}

function updateRow(sheetName, id, item) {
  const sheet = getSheet(sheetName);
  const data = sheet.getDataRange().getValues();
  const headers = data[0];
  const idCol = headers.indexOf('id');
  for (let i = 1; i < data.length; i++) {
    if (String(data[i][idCol]) === String(id)) {
      headers.forEach((h, j) => {
        if (item[h] !== undefined) {
          let val = item[h];
          if (Array.isArray(val) || (val !== null && typeof val === 'object')) {
            val = JSON.stringify(val);
          }
          sheet.getRange(i + 1, j + 1).setValue(val);
        }
      });
      return;
    }
  }
}

function deleteRow(sheetName, id) {
  const sheet = getSheet(sheetName);
  const data = sheet.getDataRange().getValues();
  const headers = data[0];
  const idCol = headers.indexOf('id');
  for (let i = data.length - 1; i >= 1; i--) {
    if (String(data[i][idCol]) === String(id)) {
      sheet.deleteRow(i + 1);
      return;
    }
  }
}

function deleteRowByCategory(sheetName, id, category) {
  const sheet = getSheet(sheetName);
  const data = sheet.getDataRange().getValues();
  const headers = data[0];
  const idCol = headers.indexOf('id');
  const catCol = headers.indexOf('category');
  for (let i = data.length - 1; i >= 1; i--) {
    if (String(data[i][idCol]) === String(id) && data[i][catCol] === category) {
      sheet.deleteRow(i + 1);
      return;
    }
  }
}

function updateSingleRow(sheetName, item) {
  const sheet = getSheet(sheetName);
  const headers = sheet.getDataRange().getValues()[0];
  if (sheet.getLastRow() <= 1) {
    // No data row yet, append one
    const row = headers.map(h => item[h] !== undefined ? item[h] : '');
    sheet.appendRow(row);
  } else {
    headers.forEach((h, j) => {
      if (item[h] !== undefined) {
        sheet.getRange(2, j + 1).setValue(item[h]);
      }
    });
  }
}

// --- Caching with CacheService ---

function readAllSheets() {
  const ss = getSpreadsheet();
  const allSheets = ss.getSheets();
  const result = {};
  allSheets.forEach(s => {
    result[s.getName()] = s.getDataRange().getValues();
  });
  return result;
}

function getCachedAllSheets() {
  const cache = CacheService.getScriptCache();
  const cached = cache.get('cache_all_sheets');
  if (cached) return JSON.parse(cached);

  const data = readAllSheets();
  cache.put('cache_all_sheets', JSON.stringify(data), 300); // 5 min
  return data;
}

function invalidateAllCache() {
  const cache = CacheService.getScriptCache();
  // Remove all cache keys
  cache.remove('cache_all_sheets');
  cache.remove('cache_employees_lookup');
  cache.remove('cache_employees');
  cache.remove('cache_announcements');
  cache.remove('cache_todos');
  cache.remove('cache_dailyinfo');
  cache.remove('cache_lists');
}

// Legacy per-table cache functions (kept for backward compatibility)
function getCachedSheet(name, ttl) {
  const cache = CacheService.getScriptCache();
  const cached = cache.get('cache_' + name.toLowerCase());
  if (cached) return JSON.parse(cached);

  const allData = getCachedAllSheets();
  const rows = allData[name] || [];
  if (rows.length > 0) {
    const headers = rows[0];
    const data = rows.slice(1).map(row => {
      const obj = {};
      headers.forEach((h, i) => obj[h] = row[i]);
      return obj;
    });
    cache.put('cache_' + name.toLowerCase(), JSON.stringify(data), ttl);
    return data;
  }
  return [];
}

function getCachedSingleRow(name, ttl) {
  const rows = getCachedSheet(name, ttl);
  return rows.length > 0 ? rows[0] : {};
}

function invalidateCache(name) {
  invalidateAllCache(); // Simpler: invalidate everything on any write
}

// Legacy cache for employee lookups (uses CacheService now)
function getEmployeeCache() {
  const cache = CacheService.getScriptCache();
  const cached = cache.get('cache_employees_lookup');
  if (cached) return JSON.parse(cached);

  const allData = getCachedAllSheets();
  const rows = allData['Employees'] || [];
  const lookup = rows.slice(1).map(row => ({ id: row[0], name: row[1] }));
  cache.put('cache_employees_lookup', JSON.stringify(lookup), 900);
  return lookup;
}

function invalidateEmployeeCache() {
  invalidateAllCache();
}

// --- API endpoints ---

function doGet(e) {
  // Batch read all sheets in ONE call, cached for 5 minutes
  const allData = getCachedAllSheets();

  // Parse raw sheet data into structured objects
  const parseRows = (rows) => {
    if (!rows || rows.length <= 1) return [];
    const headers = rows[0];
    return rows.slice(1).map(row => {
      const obj = {};
      headers.forEach((h, i) => obj[h] = row[i]);
      return obj;
    });
  };

  const employees = parseRows(allData['Employees']);
  const announcements = parseRows(allData['Announcements']);
  const todos = parseRows(allData['Todos']);
  const dailyInfoRows = allData['DailyInfo'] || [];
  const dailyInfo = dailyInfoRows.length > 1 ? (() => {
    const headers = dailyInfoRows[0];
    const obj = {};
    headers.forEach((h, i) => obj[h] = dailyInfoRows[1][i]);
    return obj;
  })() : {};
  const lists = parseRows(allData['Lists']);

  return ContentService.createTextOutput(JSON.stringify({
    employees: employees.map(e => e.name),
    announcements: resolveEmployeeData(announcements, 'author'),
    todos: resolveEmployeeData(todos, 'author'),
    dailyInfo: {
      ...dailyInfo,
      folks_working: dailyInfo.folksWorking || '',
      register_open: dailyInfo.registerOpen || 250,
      register_close: dailyInfo.registerClose || 250,
      open_assignee: getEmployeeName(dailyInfo.openAssignee),
      close_assignee: getEmployeeName(dailyInfo.closeAssignee),
      monthly_goal_current: dailyInfo.monthlyGoalCurrent || 0,
      monthly_goal_target: dailyInfo.monthlyGoalTarget || 45000,
    },
    events: lists.filter(r => r.category === 'event'),
    shoppingList: lists.filter(r => r.category === 'shopping'),
    faireList: lists.filter(r => r.category === 'faire'),
    importantLinks: lists.filter(r => r.category === 'link'),
  })).setMimeType(ContentService.MimeType.JSON);
}

function doPost(e) {
  const data = JSON.parse(e.postData.contents);

  // Resolve author name to employee ID (only for sheets that need it)
  if (data.item && ['addTodo', 'addAnnouncement', 'updateTodo', 'updateAnnouncement'].includes(data.action)) {
    const employees = getEmployeeCache();
    if (data.item.author && typeof data.item.author === 'string') {
      const emp = employees.find(e => e.name === data.item.author);
      if (emp) data.item.author = emp.id;
    }
  }

  switch (data.action) {
    case 'addTodo': appendRow('Todos', data.item); invalidateCache('Todos'); break;
    case 'updateTodo': updateRow('Todos', data.id, data.item); invalidateCache('Todos'); break;
    case 'deleteTodo': deleteRow('Todos', data.id); invalidateCache('Todos'); break;

    case 'addAnnouncement': appendRow('Announcements', data.item); invalidateCache('Announcements'); break;
    case 'updateAnnouncement': updateRow('Announcements', data.id, data.item); invalidateCache('Announcements'); break;
    case 'deleteAnnouncement': deleteRow('Announcements', data.id); invalidateCache('Announcements'); break;

    case 'addEvent': data.item.category = 'event'; appendRow('Lists', data.item); invalidateCache('Lists'); break;
    case 'deleteEvent': deleteRowByCategory('Lists', data.id, 'event'); invalidateCache('Lists'); break;

    case 'addShoppingItem': data.item.category = 'shopping'; appendRow('Lists', data.item); invalidateCache('Lists'); break;
    case 'toggleShoppingItem': updateRow('Lists', data.id, data.item); invalidateCache('Lists'); break;
    case 'deleteShoppingItem': deleteRowByCategory('Lists', data.id, 'shopping'); invalidateCache('Lists'); break;

    case 'addFaireItem': data.item.category = 'faire'; appendRow('Lists', data.item); invalidateCache('Lists'); break;
    case 'toggleFaireItem': updateRow('Lists', data.id, data.item); invalidateCache('Lists'); break;
    case 'deleteFaireItem': deleteRowByCategory('Lists', data.id, 'faire'); invalidateCache('Lists'); break;

    case 'addLink': data.item.category = 'link'; appendRow('Lists', data.item); invalidateCache('Lists'); break;
    case 'deleteLink': deleteRowByCategory('Lists', data.id, 'link'); invalidateCache('Lists'); break;

    case 'saveDailyInfo': updateSingleRow('DailyInfo', data.item); invalidateCache('DailyInfo'); break;

    case 'addEmployee': appendRow('Employees', data.item); invalidateCache('Employees'); invalidateEmployeeCache(); break;
    case 'updateEmployee': updateRow('Employees', data.id, data.item); invalidateCache('Employees'); invalidateEmployeeCache(); break;
    case 'deleteEmployee': deleteRow('Employees', data.id); invalidateCache('Employees'); invalidateEmployeeCache(); break;
  }

  return ContentService.createTextOutput(JSON.stringify({ success: true }))
    .setMimeType(ContentService.MimeType.JSON);
}
```

---

## Step 3: Deploy the Apps Script

1. Click **Deploy** (blue button, top right) → **New deployment**
2. Click the gear icon next to "Select type" → **Web app**
3. Fill in:
   - **Description**: `Shift Note API`
   - **Execute as**: `Me` (your email)
   - **Who has access**: `Anyone` (important!)
4. Click **Deploy**
5. **Authorize** the script when prompted (click Review permissions → choose account → Advanced → Go to (unsafe) → Allow)
6. Copy the **Web App URL** (looks like `https://script.google.com/macros/s/.../exec`)
7. Paste it into `index.html` where it says `YOUR_APPS_SCRIPT_URL_HERE`

---

## Step 4: Use the App

- Open `index.html` in any browser (double-click the file)
- Add announcements, todos, shopping items, and events
- Click **Copy** or **Gmail** to send shift snapshots

All data syncs to your Google Sheet automatically. The sheet uses 6 separate sheets (Employees, Announcements, Todos, Lists, DailyInfo, Archive) for better scalability and data recovery.

---

## Troubleshooting

**"Error loading data"**
- Check that your Apps Script URL is correct in `index.html`
- Verify deployment access is set to "Anyone"
- Make sure all 9 sheets exist in your Google Sheet

**Data not saving**
- Re-deploy the Apps Script after any code changes (Deploy → Manage deployments → Edit → New version)
- Check browser console for errors (F12)

**CORS errors**
- Make sure you deployed as a Web app with "Anyone" access
- The URL must end in `/exec`, not `/dev`

**Missing data after migration**
- Verify CSVs were imported into the correct sheets
- Check that employee IDs match between Todos/Announcements and the Employees sheet

**Sheet structure**
- Employees: id, name, createdAt
- Announcements: id, content, author (employee ID), timestamp, updatedAt
- Todos: id, content, assignees (JSON array of IDs), completions (JSON object), author (employee ID), timestamp, dueDate, completedAt, updatedAt
- DailyInfo: single row with folksWorking, registerOpen, registerClose, openAssignee (employee ID), closeAssignee (employee ID), monthlyGoalCurrent, monthlyGoalTarget, updatedAt
- Events, ShoppingList, FaireList, ImportantLinks: combined into Lists sheet (category column: event, shopping, faire, link)
- Archive: empty, for old completed items
