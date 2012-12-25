# coding: utf8
# Copyright © 2011 Kozea
# Licensed under a 3-clause BSD license.

"""
Strip trailing whitespace before saving.

"""

from gi.repository import GObject, Gedit


class WhiteSpaceTerminator(GObject.Object, Gedit.WindowActivatable):
    """Strip trailing whitespace before saving."""
    window = GObject.property(type=Gedit.Window)

    def do_activate(self):
        self.handlers = []
        self._are_trailing_lines_stripped = True
        self._is_last_empty_line_kept = False
        handler = self.window.connect("tab-added", self.on_tab_added)
        self.handlers.append((self.window, handler))
        for document in self.window.get_documents():
            document.connect("save", self.on_document_save)
            self.handlers.append((document, handler))

    def on_tab_added(self, window, tab, data=None):
        handler = tab.get_document().connect("save", self.on_document_save)
        self.handlers.append((tab, handler))

    def on_document_save(self, document, location, encoding, compression,
                         flags, data=None):

        if self._are_trailing_lines_stripped:
            if self._is_last_empty_line_kept:
                processed_lines = document.props.text.rstrip().splitlines()
                # if there is a new line in the document, then
                # add it as the last line to be procesed
                lines = document.props.text.splitlines()
                print "lines:"
                print lines
                if (len(lines[-1:][0]) == 0) or (lines[-1:][0].isspace()):
                    processed_lines.append("")
                    print "after:"
                    print processed_lines
            else:
                print "removing trailing lines, not keeping last one"
                lines = document.props.text.splitlines()
                print lines
                while (len(lines) > 0) and ((lines[-1].isspace() or (len(lines[-1]) == 0))):
                    lines.pop()
                processed_lines = lines
        else:
            processed_lines = document.props.text.splitlines()

        for i, text in enumerate(processed_lines):
            strip_stop = document.get_iter_at_line(i)
            strip_stop.forward_to_line_end()
            strip_start = strip_stop.copy()
            strip_start.backward_chars(len(text) - len(text.rstrip()))
            document.delete(strip_start, strip_stop)
        document.delete(strip_start, document.get_end_iter())

    def do_deactivate(self):
        for obj, handler in self.handlers:
            obj.disconnect(handler)
