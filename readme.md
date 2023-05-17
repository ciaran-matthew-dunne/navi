# Navi Language Specification

Navi is a language for performing actions within code editors. 
It provides commands for perform common navigation and editing tasks.

This repo contains code for converting English language to Navi scripts,
with help from OpenAI's GPT API. 

Navi scripts can be executed in Sublime Text's inner python terminal, 
giving the user voice control over their code editor.

## Commands

The following commands are available in the Navi language:

- `view-next`: moves the cursor to the next view
- `view-prev`: moves the cursor to the previous view
- `view-goto <number>`: moves the cursor to the view with the specified number
- `view-close`: closes the current view
- `tab-new`: creates a new tab
- `tab-next`: moves the cursor to the next tab
- `tab-prev`: moves the cursor to the previous tab
- `tab-goto <number>`: moves the cursor to the tab with the specified number
- `tab-close`: closes the current tab
- `insert <text>`: inserts the specified text at the cursor position
- `delete <length>`: deletes the specified number of characters from the cursor position
- `select-all`: selects all text in the current view
- `select-word`: selects the word at the cursor position
- `select-line`: selects the line at the cursor position
- `move-left <length>`: moves the cursor left by the specified number of characters
- `move-right <length>`: moves the cursor right by the specified number of characters
- `move-up <lines>`: moves the cursor up by the specified number of lines
- `move-down <lines>`: moves the cursor down by the specified number of lines
- `move-to <row> <col>`: moves the cursor to the specified row and column
- `scroll-up <lines>`: scrolls the view up by the specified number of lines
- `scroll-down <lines>`: scrolls the view down by the specified number of lines
