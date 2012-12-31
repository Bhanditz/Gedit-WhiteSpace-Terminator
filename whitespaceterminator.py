# coding: utf8
# Copyright © 2011 Kozea
# Licensed under a 3-clause BSD license.

"""
Strip trailing whitespace before saving.

"""

from gi.repository import GObject, Gedit


class WhiteSpaceTerminator2(GObject.Object, Gedit.WindowActivatable):
    """Strip trailing whitespace before saving."""
    window = GObject.property(type=Gedit.Window)

    def do_activate(self):
        self.handlers = []
        self._are_trailing_lines_stripped = True
        self._is_last_empty_line_kept = True
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
                # print "removing trailing lines, keeping last one"
                lines = document.props.text.splitlines()
                while (len(lines) > 1) and ((lines[-2].isspace()) or (len(lines[-2]) == 0)):
                    lines.pop()
                processed_lines = lines
                #
            else:
                # print "removing trailing lines, not keeping last one"
                lines = document.props.text.splitlines()
                while (len(lines) > 0) and ((lines[-1].isspace() or (len(lines[-1]) == 0))):
                    lines.pop()
                processed_lines = lines
                #
        else:
            processed_lines = document.props.text.splitlines()
            #

        print "processed lines: ",processed_lines

        for i, text in enumerate(processed_lines):
            strip_stop = document.get_iter_at_line(i)
            strip_stop.forward_to_line_end()
            strip_start = strip_stop.copy()
            strip_start.backward_chars(len(text) - len(text.rstrip()))
            # print "line: '%s'" %  document.get_text(strip_start, strip_stop, 0)
            document.delete(strip_start, strip_stop)

        strip_start = document.get_iter_at_line(len(processed_lines))
        #strip_start.forward_to_line_end()
        strip_stop = document.get_end_iter()
        #print "end: '%s'" % ( document.get_text(strip_stop, document.get_end_iter(), 0) )
        print "line: '%s'" %  document.get_text(strip_start, strip_stop, 0)
        document.delete(strip_start, strip_stop)

    def do_deactivate(self):
        for obj, handler in self.handlers:
            obj.disconnect(handler)
