## Converting natural language requests to navi instructions.
import os, sys
from flask import Flask, request, jsonify, Response, stream_with_context
from collections import deque

sys.path.append('/home/ciaran/prog/tinygpt')
import tinyGPT 

navi_prompt = """
Here is a list of commands for Navi, a language for describing scripting macros in text editors.
Responses must only consist of lines of Navi code which begin with '```navi\n' and end with '\n```'. 

Navi Language Commands:

- `focus-group <nat>` : Focuses a group in the active window.
- `focus-view <nat>`: Focuses a view within the active group.
- `view-open <path>`: Opens a new view using the specified file path.
- `view-close`: Closes the current view.
- `insert <str>`: Inserts the specified text at the cursor position.
- `insert-line <str>`: Inserts the string followed by a newline at the cursor position.
- `delete <nat>`: Deletes the specified number of characters from the cursor position.
- `delete-line <nat>`: Deletes the specified line from the cursor position.
- `select-all`: Selects all text in the current view.
- `select-word`: Selects the word at the cursor position.
- `select-line`: Selects the line at the cursor position.
- `move-to <nat> <nat>`: Moves the cursor to the specified row and column.
- `find <regex>`: Moves the cursor to the first match of the specified regular expression.
- `copy`: Copies the currently selected text to the clipboard.
- `paste`: Pastes the contents of the clipboard at the cursor position.
- `undo`: Undoes the last action.
- `redo`: Redoes the previously undone action.
- `replace <str> <str>`: Replaces an occurrence of the first string with the second string in the current view.
- `save <path>`: Saves the current view to the specified file path.
- `rename <path> <path>`: Renames a file or directory from the first path to the second path.
- `create-dir <path>`: Creates a new directory at the specified path.
- `delete-file <path>`: Deletes the file at the specified path.
- `comment-line`: Comments out the current line.
- `uncomment-line`: Uncomments the current line.
- `indent`: Indents the selected lines or the current line.
- `dedent`: Dedents the selected lines or the current line.

Placeholders:
- <nat>: Represents a natural number.
- <str>: Represents a string literal (excluding the new-line character "\n").
- <path>: Represents a file path.
- <regex>: Represents a regular expression.
"""

gen_examples_prompt = """
At the end of this message is a list of commands for Navi, a language that we will use to describe user requested actions in a code editor. 

Please generate 10 examples of natural language directives and their corresponding navi script. For example:
 {
        "directive": "Open a new document and insert the basic LaTeX structure.",
        "navi_script": 'view-open /home/ciaran/new_document.tex\ninsert "\\documentclass{article}\\n\\usepackage{amsmath}\\n\\n\\begin{document}\\n\\n\\end{document}"'
    }

The generated examples should have lots of variety in their length, complexity, and style.
Throughout the examples, all of the navi commands should have been used at least once.

Collect all of the examples into a Python list. 
""" + navi_prompt


navi_examples = [
    {
        "directive": "Open the file at path '/home/user/document.txt' and move the cursor to line 5, column 3.",
        "navi_script": 'view-open /home/user/document.txt\nmove-to 5 3'
    },
    {
        "directive": "Delete the current line and insert 'Hello, world!' at the cursor position.",
        "navi_script": 'delete-line 1\ninsert "Hello, world!"'
    },
    {
        "directive": "Save the current document to the path '/home/user/saved_document.txt'.",
        "navi_script": 'save /home/user/saved_document.txt'
    },
    {
        "directive": "Undo the last action.",
        "navi_script": 'undo'
    },
    {
        "directive": "Find the first occurrence of the regular expression '\\bclass\\b' and replace it with 'interface'.",
        "navi_script": 'find "\\bclass\\b"\nreplace "class" "interface"'
    },
    {
        "directive": "Close the current document and open a new one at path '/home/user/new_document.txt'.",
        "navi_script": 'view-close\nview-open /home/user/new_document.txt'
    },
    {
        "directive": "Focus the second view in the first group and delete 10 characters from the cursor position.",
        "navi_script": 'focus-group 1\nfocus-view 2\ndelete 10'
    },
    {
        "directive": "Create a new directory at path '/home/user/new_directory'.",
        "navi_script": 'create-dir /home/user/new_directory'
    },
    {
        "directive": "Rename the file from '/home/user/old_name.txt' to '/home/user/new_name.txt'.",
        "navi_script": 'rename /home/user/old_name.txt /home/user/new_name.txt'
    },
    {
        "directive": "Select the word at the cursor position, copy it, and then paste it at the end of the line.",
        "navi_script": 'select-word\ncopy\nmove-to <line number> <column number at the end of line>\npaste'
    },
    {
        "directive": "Open a file at '/home/user/test.txt', find the first occurrence of 'error', select the line, copy it, then open '/home/user/error_log.txt' and paste it.",
        "navi_script": 'view-open /home/user/test.txt\nfind "error"\nselect-line\ncopy\nview-open /home/user/error_log.txt\npaste'
    },
    {
        "directive": "Select all text in the current view, copy it, open a new file at '/home/user/copy.txt', and paste the copied content into it.",
        "navi_script": 'select-all\ncopy\nview-open /home/user/copy.txt\npaste'
    },
    {
        "directive": "Comment the first line of code, then indent it.",
        "navi_script": 'move-to 1 1\ncomment-line\nindent'
    },
    {
        "directive": "Open a file at '/home/user/document.txt', delete the first 15 characters, save the file, then undo the deletion.",
        "navi_script": 'view-open /home/user/document.txt\ndelete 15\nsave /home/user/document.txt\nundo'
    },
    {
        "directive": "Open a file at '/home/user/document.txt', move to line 3, select the line, comment it, then save the file.",
        "navi_script": 'view-open /home/user/document.txt\nmove-to 3 1\nselect-line\ncomment-line\nsave /home/user/document.txt'
    },
    {
        "directive": "Open a file at '/home/user/test.txt', find the first occurrence of 'TODO', uncomment the line, and replace 'TODO' with 'DONE'.",
        "navi_script": 'view-open /home/user/test.txt\nfind "TODO"\nuncomment-line\nreplace "TODO" "DONE"'
    },
    {
        "directive": "Open a file at '/home/user/old.txt', select all content, copy it, then create a new file at '/home/user/new.txt', paste the content, and save it.",
        "navi_script": 'view-open /home/user/old.txt\nselect-all\ncopy\nview-open /home/user/new.txt\npaste\nsave /home/user/new.txt'
    },
    {
        "directive": "Open a file at '/home/user/test.py', find all occurrences of the function 'def test', and replace it with 'def sample_test'.",
        "navi_script": 'view-open /home/user/test.py\nfind "def test"\nreplace "def test" "def sample_test"'
    },
    {
        "directive": "Close the current file, delete the file at '/home/user/temp.txt', then open a new file at '/home/user/new_temp.txt'.",
        "navi_script": 'view-close\ndelete-file /home/user/temp.txt\nview-open /home/user/new_temp.txt'
    },
    {
        "directive": "Focus the third view in the second group, select the word at the cursor position, indent it, and then save the file to '/home/user/updated_file.txt'.",
        "navi_script": 'focus-group 2\nfocus-view 3\nselect-word\nindent\nsave /home/user/updated_file.txt'
    }
]

navi_gpt_config = {
  "model": "gpt-3.5-turbo",
  "chat":  {"name": "navi_helper", "conv" : []},
  "sys_prompt": navi_prompt # + examples_prompt
}

app = Flask(__name__)

def init_navi():
  tinyGPT.add_msg(navi_gpt_config["chat"]["conv"], "user", navi_prompt)
  # for ex in navi_examples:
  #   tinyGPT.add_msg(navi_gpt_config["chat"]["conv"], "user", ex["directive"])
  #   scr = '```navi\n' + ex["navi_script"] + '\n```'
  #   tinyGPT.add_msg(navi_gpt_config["chat"]["conv"], "assistant", scr)


def remove_from_buffer(buffer, n):
    for _ in range(n):
        buffer.popleft()

def resp_to_sublime_and_stoud(gen):
  buffer = deque()
  in_navi_code = False

  for chunk in gen:
    print(chunk, end='', flush=True)
    buffer.extend(chunk)
    while len(buffer) > 7:
      # print(buffer)
      if not in_navi_code:
        if ''.join(list(buffer)) == "```navi\n":
          in_navi_code = True
          remove_from_buffer(buffer, 7)
        else:
          remove_from_buffer(buffer, 1)
      else:
        if ''.join(list(buffer)[:4]) == "\n```":
          in_navi_code = False
          remove_from_buffer(buffer, 4)
        else:
          if '\n' in buffer:
            line_end = buffer.index('\n')
            navi_line = ''.join(list(buffer)[:line_end])
            remove_from_buffer(buffer, line_end+1)
            yield navi_line
          else:
            break

@app.route('/receive', methods=['POST'])
def subl_receive():
  subl_data = request.get_json()
  state = subl_data.get('subl_state')
  msg = subl_data.get('user_prompt')
  
  tinyGPT.add_msg(navi_gpt_config["chat"]["conv"], "system", state)
  tinyGPT.add_msg(navi_gpt_config["chat"]["conv"], "user", f'Write a Navi script that achieves the following directive: "{msg}"')
  print(navi_gpt_config["chat"]["conv"])
  def gen():
    navi_stream = resp_to_sublime_and_stoud(tinyGPT.call_gpt(navi_gpt_config))
    for line in navi_stream:
      yield line

  return stream_with_context(gen())

if __name__ == "__main__":
  init_navi()
  app.run(port=5000)