## Converting natural language requests to navi instructions.
import os, sys

import tinyGPT

navi_prompt = """
You convert natural language requests to scripts in the Navi language:
- `view-goto <nat>`: moves the cursor to the view with the specified number
- `view-open <path>
- `view-close`: closes the current view
- `insert <str>`: inserts the specified text at the cursor position
- `insert-line <str> : inserts the string followed by newline.
- `delete <nat>`: deletes the specified number of characters from the cursor position
- `delete-line <nat> : deletes the specified line
- `select-all`: selects all text in the current view
- `select-word`: selects the word at the cursor position
- `select-line`: selects the line at the cursor position
- `move-to <nat> <nat>`: moves the cursor to the specified row and column
- `find <regex>`: moves the cursor to the first match of the specified regular expression

- <nat> is a placeholder for a natural number
- <str> is a placeholder for a string literal, NOT containing the new-line character "\n".
- <path> is a filepath
- <regex> is a regular expression.

Every response you give must consist entirely of Navi code.
"""

fine_tune = [
{"prompt": "Please move the cursor to the start of the third line", "completion": "move-to 3 0"},
{"prompt": "I need to select the entire document. How do I do that?", "completion": "select-all"},
{"prompt": "Can you insert the word 'hello' at the current cursor position?", "completion": "insert 'hello'"},
{"prompt": "I want to delete the next 5 characters from the current cursor position", "completion": "delete 5"},
{"prompt": "Please close the current view", "completion": "view-close"},
{"prompt": "I need to find the first occurrence of the word 'world'", "completion": "find 'world'"},
{"prompt": "Scroll up 10 lines, please", "completion": "scroll-up 10"},
{"prompt": "Create a new tab for me", "completion": "tab-new"},
{"prompt": "Can you move the cursor to the fourth view?", "completion": "view-goto 4"},
{"prompt": "I want to select the entire current line", "completion": "select-line"},
{"prompt": "I want to insert the text 'Hello, World!' at the beginning of line 5", "completion": "view-goto 5\nmove-to 5 0\ninsert 'Hello, World!'\n"},
{"prompt": "I need to delete the next 10 characters and then move to the end of the line", "completion": "delete 10\nmove-to 0 $"},
{"prompt": "Find the first occurrence of the word 'example' and delete it", "completion": "find 'example'\ndelete 7\n"},
{"prompt": "Scroll down 5 lines and then select the current line", "completion": "scroll-down 5\nselect-line\n"},
{"prompt": "I need to close the current tab and then go to the next view", "completion": "tab-close\nview-next\n"},
{"prompt": "Go to line 10, column 5 and then select the word at the cursor position", "completion": "move-to 10 5\nselect-word\n"},
{"prompt": "Insert the text 'Lorem ipsum dolor sit amet' and then go to the beginning of the line", "completion": "insert 'Lorem ipsum dolor sit amet'\nmove-to 0 0\n"},
{"prompt": "Select all text and then delete it", "completion": "select-all\ndelete\n"},
{"prompt": "Scroll up 3 lines, then find the word 'example' and insert the text 'new' before it", "completion": "scroll-up 3\nfind 'example'\nmove-to +0 0\ninsert 'new'\n"},
{"prompt": "Go to the beginning of the document, select all text, and then delete it", "completion": "move-to 0 0\nselect-all\ndelete\n"}
]


examples_prompt = '\n\n'.join([ f"Prompt: {ex['prompt']}\nResponse: {ex['completion']}" for ex in fine_tune]) 

navi_gpt_config = {
  "model": "gpt-3.5-turbo",
  "chat":  {"name": "navi_helper", "conv" : []},
  "sys_prompt": navi_prompt # + examples_prompt
}

init_chat(navi_gpt_config)
# define the function that uses the tinyGPT to generate navi scripts from natural language
def eng_to_navi(prompt):
  chat(navi_gpt_config, resp_stoud_md, prompt)

