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
// Shift Note API - Single sheet, JSON storage
// On first run, creates a Google Sheet called "Shift Note Data"
// and stores its ID in script properties.

const SHEET_NAME = 'ShiftNote';

function getSpreadsheet() {
  const props = PropertiesService.getScriptProperties();
  let ssId = props.getProperty('SHEET_ID');
  
  if (!ssId) {
    const ss = SpreadsheetApp.create('Shift Note Data');
    ssId = ss.getId();
    props.setProperty('SHEET_ID', ssId);
    
    const sheet = ss.getSheets()[0];
    sheet.setName(SHEET_NAME);
    sheet.appendRow(['key', 'value']);
    SpreadsheetApp.flush();
  }
  
  return SpreadsheetApp.openById(ssId);
}

function getSheet() {
  const ss = getSpreadsheet();
  let sheet = ss.getSheetByName(SHEET_NAME);
  if (!sheet) {
    sheet = ss.insertSheet(SHEET_NAME);
    sheet.appendRow(['key', 'value']);
    SpreadsheetApp.flush();
  }
  return sheet;
}

function doGet(e) {
  const sheet = getSheet();
  const data = sheet.getDataRange().getValues();
  
  let annJson = null, todoJson = null, dailyJson = null;
  
  for (let i = 1; i < data.length; i++) {
    if (data[i][0] === 'announcements') annJson = data[i][1];
    if (data[i][0] === 'todos') todoJson = data[i][1];
    if (data[i][0] === 'dailyInfo') dailyJson = data[i][1];
  }
  
  const result = {
    announcements: annJson ? JSON.parse(annJson) : [],
    todos: todoJson ? JSON.parse(todoJson) : [],
    dailyInfo: dailyJson ? JSON.parse(dailyJson) : {
      folks_working: '',
      register_open: 250,
      register_close: 250,
      shopping_list: [],
      events: []
    }
  };
  
  const callback = e.parameter.callback;
  if (callback) {
    return ContentService.createTextOutput(callback + '(' + JSON.stringify(result) + ')')
      .setMimeType(ContentService.MimeType.JAVASCRIPT);
  }
  
  return ContentService.createTextOutput(JSON.stringify(result))
    .setMimeType(ContentService.MimeType.JSON);
}

function doPost(e) {
  const data = JSON.parse(e.postData.contents);
  
  if (data.action === 'saveAll') {
    saveData('announcements', data.announcements);
    saveData('todos', data.todos);
    saveData('dailyInfo', data.dailyInfo);
  }
  
  return ContentService.createTextOutput(JSON.stringify({ success: true }))
    .setMimeType(ContentService.MimeType.JSON);
}

function saveData(key, value) {
  const sheet = getSheet();
  const data = sheet.getDataRange().getValues();
  
  let found = false;
  for (let i = 1; i < data.length; i++) {
    if (data[i][0] === key) {
      sheet.getRange(i + 1, 2).setValue(JSON.stringify(value));
      found = true;
      break;
    }
  }
  
  if (!found) {
    sheet.appendRow([key, JSON.stringify(value)]);
  }
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
- Click **Email Snapshot** to generate a formatted email

All data syncs to your Google Sheet automatically. The sheet is created on first use and stored in your Google Drive as "Shift Note Data".

---

## Troubleshooting

**"Error loading data"**
- Check that your Apps Script URL is correct in `index.html`
- Verify deployment access is set to "Anyone"

**Data not saving**
- Re-deploy the Apps Script after any code changes (Deploy → Manage deployments → Edit → New version)
- Check browser console for errors (F12)

**CORS errors**
- Make sure you deployed as a Web app with "Anyone" access
- The URL must end in `/exec`, not `/dev`
