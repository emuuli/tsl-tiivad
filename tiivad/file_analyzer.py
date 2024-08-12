import os
import py_compile


class FileAnalyzer:
    def __init__(self, filename):
        self.filename = filename
        self.message = None
    def file_exists(self):
        return os.path.isfile(self.filename)

    def file_not_empty(self):
        return self.file_exists() and os.path.getsize(self.filename) > 0

    def file_is_python(self):
        if not self.filename.endswith(".py"):
            return False
        try:
            py_compile.compile(self.filename, doraise=True)
            return True
        except (SyntaxError, py_compile.PyCompileError) as e:
            self.message = str(e)
            return False
