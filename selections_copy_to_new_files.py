# selections_copy_to_new_files.py
import os
import re
import sublime
import sublime_plugin


def _preview_from_text(text, max_len=30):
    # collapse whitespace/newlines to single spaces, trim, and clip
    if not text:
        return "selection"
    s = re.sub(r'\s+', ' ', text.strip())
    return s[:max_len]


def _sanitize_filename(name, max_length=80, fallback="selection.txt"):
    """
    Remove characters that are not safe for filenames and trim length.
    Keeps letters, numbers, spaces, hyphen, underscore and dot.
    Ensures we return something usable for a filename.
    """
    if not name:
        return fallback
    # Use only the first line for filenames
    name = name.splitlines()[0].strip()
    # Replace runs of whitespace with a single space
    name = re.sub(r'\s+', ' ', name)
    # Remove characters not safe for filenames
    name = re.sub(r'[^A-Za-z0-9 \-\._]', '', name)
    name = name.strip()
    if not name:
        return fallback
    if len(name) > max_length:
        name = name[:max_length].rstrip()
    return name


class SelectionsCopyToNewFilesCommand(sublime_plugin.WindowCommand):
    """
    For each non-empty selection in the active view, create a new file
    and insert the selection text. The new buffer will open a Save As
    dialog pre-filled with a sensible default filename.
    """

    def run(self):
        window = self.window
        view = window.active_view()
        if not view:
            return

        # Collect non-empty selections
        regions = [r for r in view.sel() if not r.empty()]
        if not regions:
            return

        # Optional safety: avoid creating an excessive number of tabs accidentally
        MAX_TABS = 100
        if len(regions) > MAX_TABS:
            sublime.status_message(
                "Too many selections ({}) — aborting.".format(len(regions))
            )
            return

        # original file base name (if the active view is a saved file)
        src_file = view.file_name() or ""
        src_base = os.path.splitext(os.path.basename(src_file))[0] if src_file else ""

        for idx, region in enumerate(regions, start=1):
            text = view.substr(region)

            # Create a new file for this selection
            new_view = window.new_file()

            # Keep the friendly preview for quick visual identification
            preview = _preview_from_text(text, max_len=30)
            # show a friendly preview in the status bar for this view/tab
            new_view.set_status('selections_copy_preview', "selection-{}: {}".format(idx, preview))

            # Build a sensible default filename suggestion:
            # Prefer: <original-base>-<first-line-short>.txt OR selection<idx>.txt
            first_line = text.splitlines()[0].strip() if text.splitlines() else ""
            if first_line and len(first_line) >= 3:
                desc = _sanitize_filename(first_line, max_length=30, fallback="selection{}".format(idx))
                if src_base:
                    suggested = "{}-{}.txt".format(src_base, desc)
                else:
                    suggested = "{}.txt".format(desc)
            else:
                suggested = "{}-selection{}.txt".format(src_base, idx) if src_base else "selection{}.txt".format(idx)

            suggested = _sanitize_filename(suggested, max_length=80, fallback="selection{}.txt".format(idx))

            # Set the buffer name to the suggested filename so Sublime's Save As
            # dialog usually pre-fills the filename with it.
            # We keep the status preview (above) for human-friendly tab text.
            new_view.set_name(suggested)

            # Insert text at the start using the TextCommand you already use
            new_view.run_command("insert_text", {"point": 0, "text": text})

            # Move caret to beginning
            new_view.sel().clear()
            new_view.sel().add(sublime.Region(0, 0))

            # Prompt the user with Save As (so they choose location / can edit the name)
            new_view.run_command('prompt_save_as')

    def is_enabled(self):
        """Only enable the command when there is at least one non-empty selection."""
        view = self.window.active_view()
        return bool(view and any(not r.empty() for r in view.sel() or []))