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

const SHEET_NAMES = ['Employees', 'Announcements', 'Todos', 'Events', 'ShoppingList', 'FaireList', 'ImportantLinks', 'DailyInfo', 'Archive'];

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
    Events: ['id', 'content', 'timestamp'],
    ShoppingList: ['id', 'content', 'purchased', 'timestamp'],
    FaireList: ['id', 'content', 'purchased', 'timestamp'],
    ImportantLinks: ['id', 'title', 'url'],
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
  const row = headers.map(h => item[h] !== undefined ? item[h] : '');
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
          sheet.getRange(i + 1, j + 1).setValue(item[h]);
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

// --- API endpoints ---

function doGet(e) {
  const employees = readSheet('Employees');
  const employeeNames = employees.map(e => e.name);

  return ContentService.createTextOutput(JSON.stringify({
    employees: employeeNames,
    announcements: resolveEmployeeData(readSheet('Announcements'), 'author'),
    todos: resolveEmployeeData(readSheet('Todos'), 'author'),
    dailyInfo: {
      ...readSingleRow('DailyInfo'),
      folks_working: readSingleRow('DailyInfo').folksWorking || '',
      register_open: readSingleRow('DailyInfo').registerOpen || 250,
      register_close: readSingleRow('DailyInfo').registerClose || 250,
      open_assignee: getEmployeeName(readSingleRow('DailyInfo').openAssignee),
      close_assignee: getEmployeeName(readSingleRow('DailyInfo').closeAssignee),
      monthly_goal_current: readSingleRow('DailyInfo').monthlyGoalCurrent || 0,
      monthly_goal_target: readSingleRow('DailyInfo').monthlyGoalTarget || 45000,
    },
    events: readSheet('Events'),
    shoppingList: readSheet('ShoppingList'),
    faireList: readSheet('FaireList'),
    importantLinks: readSheet('ImportantLinks'),
  })).setMimeType(ContentService.MimeType.JSON);
}

function doPost(e) {
  const data = JSON.parse(e.postData.contents);

  switch (data.action) {
    case 'addTodo': appendRow('Todos', data.item); break;
    case 'updateTodo': updateRow('Todos', data.id, data.item); break;
    case 'deleteTodo': deleteRow('Todos', data.id); break;

    case 'addAnnouncement': appendRow('Announcements', data.item); break;
    case 'updateAnnouncement': updateRow('Announcements', data.id, data.item); break;
    case 'deleteAnnouncement': deleteRow('Announcements', data.id); break;

    case 'addEvent': appendRow('Events', data.item); break;
    case 'deleteEvent': deleteRow('Events', data.id); break;

    case 'addShoppingItem': appendRow('ShoppingList', data.item); break;
    case 'toggleShoppingItem': updateRow('ShoppingList', data.id, data.item); break;
    case 'deleteShoppingItem': deleteRow('ShoppingList', data.id); break;

    case 'addFaireItem': appendRow('FaireList', data.item); break;
    case 'toggleFaireItem': updateRow('FaireList', data.id, data.item); break;
    case 'deleteFaireItem': deleteRow('FaireList', data.id); break;

    case 'addLink': appendRow('ImportantLinks', data.item); break;
    case 'deleteLink': deleteRow('ImportantLinks', data.id); break;

    case 'saveDailyInfo': updateSingleRow('DailyInfo', data.item); break;

    case 'addEmployee': appendRow('Employees', data.item); break;
    case 'updateEmployee': updateRow('Employees', data.id, data.item); break;
    case 'deleteEmployee': deleteRow('Employees', data.id); break;
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

All data syncs to your Google Sheet automatically. The sheet uses 9 separate sheets (Employees, Announcements, Todos, Events, ShoppingList, FaireList, ImportantLinks, DailyInfo, Archive) for better scalability and data recovery.

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
- Events, ShoppingList, FaireList, ImportantLinks: id + content fields
- Archive: empty, for old completed items
