import ast
import re
import runpy

from tiivad.capture_io import IOCapturing, OutOfInputsError
from tiivad.syntax_tree_analyzer import ValidationType


class ElementsType:
    CONTAINS_STRINGS = "CONTAINS_STRINGS"
    CONTAINS_LINES = "CONTAINS_LINES"
    CONTAINS_NUMBERS = "CONTAINS_NUMBERS"
    EQUALS = "EQUALS"


def create_file(file_name, file_content, text_file_encoding=None):
    if text_file_encoding is None:
        text_file_encoding = "UTF-8"

    if isinstance(file_content, str):
        file_content = file_content.encode(text_file_encoding)

    with open(file_name, mode="wb") as fp:
        fp.write(file_content)


def convert_script(file_name, converted_file_name, create_object_body=None):
    with open(file_name, encoding="utf8") as f:
        file_content = f.read()
    lines = file_content.splitlines()
    try:
        tree = ast.parse(file_content)
    except:
        pass
    else:
        if 'body' in tree._fields:
            for node in tree.body:
                comment = True
                if isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.Import, ast.ImportFrom, ast.Assign)):
                    comment = False
                    if isinstance(node, ast.Assign):
                        for x in ast.walk(node.value):
                            if isinstance(x, (ast.Call, ast.Name)):
                                comment = True
                if comment:
                    for i in range(node.lineno - 1, node.end_lineno):
                        lines[i] = '#' + lines[i]
    body = '\n'.join(lines)
    if create_object_body:
        body += '\ndef create_object_fun_auto_assess():'
        body += ''.join('\n    ' + line for line in create_object_body.splitlines())
    with open(converted_file_name, 'w', encoding="utf8") as f:
        f.write(body)
    return body


def extract_numbers(s):
    """
    Extract all the numbers from a given string.
    In case of a string like "1.2.3", we return [1.2, 3].
    """
    numbers = []
    # Source: https://stackoverflow.com/questions/4289331/how-to-extract-numbers-from-a-string-in-python
    rr = re.findall(r"[-+]?[.]?[\d]+(?:[\.]\d\d\d)*[\.]?\d*(?:[eE][-+]?\d+)?", s)
    rr = [r.strip(".") for r in rr]
    for r in rr:
        try:
            numbers.append(int(r))
        except ValueError:
            numbers.append(float(r))
        else:
            pass
    return numbers

def extract_strings(text: str, word_list: list) -> list:
    if not word_list:
        return []

    occurrences = []

    # Create a pattern that matches any of the strings in the list
    pattern = '|'.join(re.escape(word) for word in word_list)

    # Use re.finditer to find all occurrences
    for match in re.finditer(pattern, text):
        occurrences.append(match.group())

    return occurrences


def extract_lines(s):
    lines = s.splitlines()
    return [line for line in lines if line.strip()]


class ProgramExecutionAnalyzer:
    def __init__(self, file_name: str, user_inputs: list, input_files: set):
        for name, content in input_files:
            create_file(name, content)
        with IOCapturing(user_inputs) as iocap:
            self.exception = None
            try:
                self.globals_dict = runpy.run_path(file_name, run_name="__main__")
            # When student submission contains exit() or quit(), we don't want to crash assessment
            except SystemExit:
                pass
            except Exception as e:
                self.exception = e
        if isinstance(self.exception, OutOfInputsError):
            self.actual_input_count = float('Inf')
        else:
            self.actual_input_count = len(user_inputs) - len(iocap.get_remaining_inputs())
        self.all_io = iocap.get_io()
        self.all_output = iocap.get_stdout()
        self.last_output = iocap.get_last_stdout()
        self.converted_script = None

    def raised_exception(self) -> bool:
        return self.exception is not None

    def analyze_output_with_quantifier(self, file_name, data_category: str, quantifier, values: list,
                                       nothing_else: bool = False, ordered: bool = False, ignore_case = False) -> bool:

        if file_name:
            try:
                with open(file_name, encoding="UTF-8") as f:
                    content = f.read()
            except FileNotFoundError as e:
                self.exception = e
                return False
        else:
            content = self.all_io

        if ignore_case:
            content = content.lower()
            values = [v.lower() for v in values]

        match data_category:
            case ElementsType.CONTAINS_NUMBERS:
                all_values = extract_numbers(content)
            case ElementsType.CONTAINS_STRINGS:
                all_values = extract_strings(content, values)
            case ElementsType.CONTAINS_LINES:
                all_values = extract_lines(content)
            case ElementsType.EQUALS:
                all_values = [content.rstrip()]
            case _:
                all_values = []
        match quantifier:
            case ValidationType.ALL_OF_THESE:
                if not ordered:
                    values.sort()
                    all_values.sort()
                i = 0
                for value in all_values:
                    if values[i] == value:
                        i += 1
                        if i == len(values):
                            break
                return i == len(values) and (not nothing_else or len(values) == len(all_values))
            case ValidationType.ANY_OF_THESE:
                return len(set(values) & set(all_values)) > 0 and (not nothing_else or set(all_values) <= set(values))
            case ValidationType.ANY:
                return len(all_values) > 0
            case ValidationType.MISSING_AT_LEAST_ONE_OF_THESE:
                return not (set(values) <= set(all_values))
            case ValidationType.NONE_OF_THESE:
                return len(set(values) & set(all_values)) == 0
            case ValidationType.NONE:
                return len(all_values) == 0
            case _:
                return False

    def analyze_exception(self, target: str) -> bool:
        pass


class ClassExecutionAnalyzer(ProgramExecutionAnalyzer):
    def __init__(self, file_name: str, create_object_body: str, user_inputs: list = [], input_files: set = set()):
        converted_file_name = "converted_file.py"
        self.converted_script = convert_script(file_name, converted_file_name, create_object_body)
        super().__init__(converted_file_name, [], input_files)
        if self.exception is not None:
            return

        for name, content in input_files:
            create_file(name, content)
        with IOCapturing(user_inputs) as iocap:
            try:
                self.obj = self.globals_dict.get("create_object_fun_auto_assess", None)()
            # When student submission contains exit() or quit(), we don't want to crash assessment
            except SystemExit:
                pass
            except Exception as e:
                self.exception = e

        if isinstance(self.exception, OutOfInputsError):
            self.actual_input_count = float('Inf')
        else:
            self.actual_input_count = len(user_inputs) - len(iocap.get_remaining_inputs())
        self.all_io = iocap.get_io()
        self.all_output = iocap.get_stdout()
        self.last_output = iocap.get_last_stdout()

    def fields_exist(self, quantifier: str, names: set, nothing_else: bool = False) -> bool:
        targetset = set(self.obj.__dict__.keys())
        match quantifier:
            case ValidationType.ALL_OF_THESE:
                return names <= targetset and (not nothing_else or targetset <= names)
            case ValidationType.ANY_OF_THESE:
                return len(names & targetset) > 0 and (not nothing_else or targetset <= names)
            case ValidationType.ANY:
                return len(targetset) > 0
            case ValidationType.MISSING_AT_LEAST_ONE_OF_THESE:
                return not (names <= targetset)
            case ValidationType.NONE_OF_THESE:
                return len(names & targetset) == 0
            case ValidationType.NONE:
                return len(targetset) == 0
            case _:
                return False

    def fields_correct(self, fields: list, check_name: bool, check_value: bool, nothing_else: bool = False) -> bool:
        for f in fields:
            if not any((not check_name or f[0] == of) and (not check_value or f[1] == ov)
                       for of, ov in self.obj.__dict__.items()):
                return False
        if nothing_else:
            for of, ov in self.obj.__dict__.items():
                if not any((not check_name or f[0] == of) and (not check_value or f[1] == ov)
                           for f in fields):
                    return False
        return True

    def obj_to_str(self) -> str:
        if hasattr(self.obj, '__dict__'):
            s = [f"{k} = {repr(v)}" for k, v in self.obj.__dict__.items()]
            return self.obj.__class__.__name__ + "(" + ", ".join(s) + ")"
        else:
            return str(self.obj)


class FunctionExecutionAnalyzer(ProgramExecutionAnalyzer):
    def __init__(self, file_name: str, function_name: str, function_type: str, create_object_body: str,
                 arguments: list, user_inputs: list = [], input_files: set = set()):
        self.arguments = arguments
        self.result = None

        # For formatting the values in msg-s:
        self.expected = None
        self.actual = None
        self.skip_format = False
        self.file_name = file_name
        self.function = function_name

        converted_file_name = "converted_file.py"
        self.converted_script = convert_script(file_name, converted_file_name, create_object_body)
        super().__init__(converted_file_name, [], input_files)
        if self.exception is not None:
            return

        if function_type == "FUNCTION":
            f_obj = self.globals_dict.get(function_name, None)
        else:  # "METHOD"
            try:
                obj = self.globals_dict.get("create_object_fun_auto_assess", None)()
                f_obj = getattr(obj, function_name)
            except Exception as e:
                self.exception = e
                return

        for name, content in input_files:
            create_file(name, content)
        with IOCapturing(user_inputs) as iocap:
            try:
                self.result = f_obj(*arguments)
            # When student submission contains exit() or quit(), we don't want to crash assessment
            except SystemExit:
                pass
            except Exception as e:
                self.exception = e
        if isinstance(self.exception, OutOfInputsError):
            self.actual_input_count = float('Inf')
        else:
            self.actual_input_count = len(user_inputs) - len(iocap.get_remaining_inputs())
        self.all_io = iocap.get_io()
        self.all_output = iocap.get_stdout()
        self.last_output = iocap.get_last_stdout()

    def value_correct(self, param_number, value) -> bool:
        if param_number is None:
            return self.result == value
        else:
            return param_number < len(self.arguments) and self.arguments[param_number] == value


if __name__ == "__main__":
    file_name = f"../test/samples/func_exec1.py"
    function_name = "sisend01"
    function_type = "FUNCTION"
    create_object_body = None
    arguments = [1]
    ea = FunctionExecutionAnalyzer(file_name, function_name, function_type, create_object_body, arguments)
    print(repr(ea.exception))
    print(repr(ea.result))
    # print(ea.analyze_output_with_quantifier(None, ElementsType.EQUALS, ValidationType.ANY_OF_THESE,
    #                                         ["Sisesta failinimi: sisendfail.txt\nFailis on 5 rida\nmille summa on 14.6."],
    #                                         True, True))
