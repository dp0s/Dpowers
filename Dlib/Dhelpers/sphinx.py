import sys


#### source of the following:
### https://stackoverflow.com/questions/7250659


import sys
from os.path import basename

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

from docutils.parsers.rst import Directive
from docutils import nodes, statemachine


class ExecDirective(Directive):
    """Execute the specified python code and insert the output into the
    document"""
    has_content = True
    
    def run(self):
        oldStdout, sys.stdout = sys.stdout, StringIO()
        
        tab_width = self.options.get('tab-width',
                self.state.document.settings.tab_width)
        source = self.state_machine.input_lines.source(
                self.lineno - self.state_machine.input_offset - 1)
        
        try:
            exec("\n".join(self.content), self.globals_)
            text = sys.stdout.getvalue()
            lines = statemachine.string2lines(text, tab_width,
                    convert_whitespace=True)
            self.state_machine.insert_input(lines, source)
            return []
        except Exception:
            return [nodes.error(None, nodes.paragraph(
                    text="Unable to execute python code at %s:%d:"%(
                    basename(source), self.lineno)),
                    nodes.paragraph(text=str(sys.exc_info()[1])))]
        finally:
            sys.stdout = oldStdout
    
    @classmethod
    def get_globals(cls, globals):
        cls.globals_ = globals



class ImprovedExecDirective(Directive):
    
    @classmethod
    def get_globals(cls, globals):
        cls.globals_ = globals

    
    def run(self):
        source = self.state_machine.input_lines.source(
                self.lineno - self.state_machine.input_offset - 1)
        tab_width = self.options.get('tab-width',
                self.state.document.settings.tab_width)
        text = self.create_text()
        lines = statemachine.string2lines(text, tab_width,
                convert_whitespace=True)
        self.state_machine.insert_input(lines, source)
        return []
    
    def create_text(self):
        raise NotImplementedError
    

class ActiveCode(ImprovedExecDirective):
    has_content = True
    
    def create_text(self):
        text = ".. code::\n\n"
        local = {}
        for line in self.content:
            assert isinstance(line, str)
            if line.startswith(">>>"):
                append = line
            else:
                try:
                    exec("__ret__ = " + line, self.globals_, local)
                except SyntaxError:
                    exec(line, self.globals_, local)
                    #important becuase it keeps the locals up to date
                    continue
                append = str(local["__ret__"])
            if isinstance(append, str):
                append_lines = append.split("\n")
            else:
                append_lines = (append,)
            #print("append_lines", append_lines)
            for line in append_lines:
                text += "\t" + line + "\n"
        return text
        