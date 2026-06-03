# CSS Reset Plan

## Problem
The previous `vh` → `px` replacement created broken CSS values like `1.20px` instead of `12px`, making the UI look janky.

## Solution
Replace the entire `<style>` block (lines 10-817) with a clean, well-proportioned CSS using:

### Design System
- **CSS Variables** for consistent theming (`--primary`, `--accent`, `--bg`, etc.)
- **Fixed `px` values** that look good on all screen sizes
- **Organized sections** with clear comments

### Key Size Changes
| Element | Old (broken) | New |
|---------|-------------|-----|
| Header date | 26px | 22px |
| Header padding | 1.20px | 12px |
| Column header | 20px | 18px |
| Card text | 16px | 14px |
| Card border-radius | 1.20px | 12px |
| Avatar font | 1.20px | 12px |
| Tag font | 1.20px | 11px |
| Buttons | 16px | 14px |
| Form inputs | 16px | 14px |
| Column max-height | calc(100vh - 100px) | calc(100vh - 120px) |

### Preserved
- `100vh` for structural containers (body, task-page, board-container)
- All functionality, colors, fonts, and layout structure
- Media queries, hover states, transitions

### File
- `/Users/emilyzhao/Documents/code/shift-note/index.html` - replace lines 10-817 (`<style>` block)
