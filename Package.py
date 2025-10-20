import sublime, sublime_plugin
from .Edit import Edit as Edit

class selections_copy_to_new_files(sublime_plugin.WindowCommand):
	def run(self):
		window = sublime.active_window()
		_view = window.active_view()

		for region in _view.sel():
			text = _view.substr(sublime.Region(region.begin(), region.end()))
			view = window.new_file()
			with Edit(view) as edit:
				edit.replace(sublime.Region(0, view.size()), text)
			view.sel().clear()
			view.sel().add(sublime.Region(0))
			view.run_command('save')

	def is_enabled(self):
		window = sublime.active_window()
		_view = window.active_view()
		return True if (_view.sel() and _view.sel()[0] and not _view.sel()[0].empty()) else False