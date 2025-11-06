# insert_text.py
import sublime
import sublime_plugin

class InsertTextCommand(sublime_plugin.TextCommand):
    """
    Usage: view.run_command('insert_text', {'point': 0, 'text': 'hello'})
    Inserts `text` at `point` using the canonical TextCommand API.
    """

    def run(self, edit, point=0, text=""):
        # defensive: coerce point into int and clip into buffer
        try:
            point = int(point)
        except Exception:
            point = 0
        if point < 0:
            point = 0
        if point > self.view.size():
            point = self.view.size()

        # Do the actual insertion using Sublime's View.insert
        self.view.insert(edit, point, text)
