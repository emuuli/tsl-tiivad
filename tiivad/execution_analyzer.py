import ast
import re
import runpy
from typing import Counter

from tiivad.capture_io import IOCapturing, OutOfInputsError
from tiivad.syntax_tree_analyzer import ValidationType


class ElementsType:
    CONTAINS_STRINGS = "CONTAINS_STRINGS"
    CONTAINS_LINES = "CONTAINS_LINES"
    CONTAINS_NUMBERS = "CONTAINS_NUMBERS"
    EQUALS = "EQUALS"
    CUSTOM_FUNCTION = "CUSTOM_FUNCTION"

class OutputCategory:
    ALL_IO = "ALL_IO"
    ALL_OUTPUT = "ALL_OUTPUT"
    LAST_OUTPUT = "LAST_OUTPUT"
    OUTPUT_NUMBER_0 = "OUTPUT_NUMBER_0"
    OUTPUT_NUMBER_1 = "OUTPUT_NUMBER_1"
    OUTPUT_NUMBER_2 = "OUTPUT_NUMBER_2"
    OUTPUT_NUMBER_3 = "OUTPUT_NUMBER_3"
    OUTPUT_NUMBER_4 = "OUTPUT_NUMBER_4"
    OUTPUT_NUMBER_5 = "OUTPUT_NUMBER_5"
    OUTPUT_NUMBER_6 = "OUTPUT_NUMBER_6"
    OUTPUT_NUMBER_7 = "OUTPUT_NUMBER_7"
    OUTPUT_NUMBER_8 = "OUTPUT_NUMBER_8"
    OUTPUT_NUMBER_9 = "OUTPUT_NUMBER_9"


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
    words = list(dict.fromkeys(word_list)) 
    occurrences = []
    for word in words:
        if word.startswith("regex:"):
            pattern = word.replace("regex:", "")
        else:
            pattern = re.escape(word)
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
        self.output_numbers_map = iocap.get_output_map()
        self.output_number_0 = ""
        self.output_number_1 = ""
        self.output_number_2 = ""
        self.output_number_3 = ""
        self.output_number_4 = ""
        self.output_number_5 = ""
        self.output_number_6 = ""
        self.output_number_7 = ""
        self.output_number_8 = ""
        self.output_number_9 = ""
        self.converted_script = None
        self.all_file_io = ""
        self.actually_found = None
        self.expected = None
        self.actual = None
    def raised_exception(self) -> bool:
        return self.exception is not None

    def analyze_output_with_quantifier(self, file_name, data_category: str, quantifier, values: list, output_category: str,
                                       nothing_else: bool = False, ordered: bool = False, ignore_case = False) -> bool:
        # output message jaoks
        for i in range(10):
            setattr(self, f"output_number_{i}", self.output_numbers_map.get(i, ""))

        if file_name:
            self.file_name = file_name
            try:
                with open(file_name, encoding="UTF-8") as f:
                    content = f.read()
                    self.all_file_io = content
            except FileNotFoundError as e:
                self.exception = e
                return False
        else:
            match output_category:
                case OutputCategory.ALL_IO:
                    content = self.all_io
                case OutputCategory.ALL_OUTPUT:
                    content = self.all_output
                case OutputCategory.LAST_OUTPUT:
                    content = self.last_output
                case category if category.startswith("OUTPUT_NUMBER_"):
                    try:
                        index = int(category.split("_")[-1])
                        content = self.output_numbers_map.get(index, "")
                    except ValueError:
                        content = self.all_io
                case _:
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
        self.actually_found = all_values
        match quantifier:
            case ValidationType.ALL_OF_THESE:
                expected_counts = Counter(values)
                actual_counts = Counter(all_values)
                print(actual_counts)
                for expected_value, count in expected_counts.items():
                    match_count = 0
                    for value in all_values:
                        if isinstance(expected_value, str) and expected_value.startswith("regex:"):
                            pattern = expected_value[len("regex:"):].strip()
                            if re.fullmatch(pattern, value):
                                match_count += 1
                        elif expected_value == value:
                            match_count += 1
                    if match_count < count: 
                        return False
                    
                if ordered:
                    expected_index = 0
                    for value in all_values:
                        if expected_index < len(values) and value == values[expected_index]:
                            expected_index += 1
                        if expected_index == len(values):
                            break
                    if expected_index != len(values):
                        return False
                    
                return not nothing_else or expected_counts == actual_counts
            case ValidationType.ANY_OF_THESE:

                return any(expected_value in all_values or 
                                    (isinstance(expected_value, str) and expected_value.startswith("regex:") and 
                                        any(re.fullmatch(expected_value[len("regex:"):].strip(), value) for value in all_values)) 
                                    for expected_value in values) and (not nothing_else or set(all_values) <= set(values))
            case ValidationType.ANY:
                return len(all_values) > 0
            case ValidationType.MISSING_AT_LEAST_ONE_OF_THESE:
                for expected_value in values:
                    if isinstance(expected_value, str) and expected_value.startswith("regex:"):
                        pattern = expected_value[len("regex:"):].strip()
                        if not any(re.fullmatch(pattern, value) for value in all_values):
                            return True 
                    elif expected_value not in all_values:
                        return True 
                return False
            case ValidationType.NONE_OF_THESE:
                for expected_value in values:
                    if isinstance(expected_value, str) and expected_value.startswith("regex:"):
                        pattern = expected_value[len("regex:"):].strip()
                        if any(re.fullmatch(pattern, value) for value in all_values):
                            return False  
                    elif expected_value in all_values:
                        return False  
                return True  
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
        self.output_numbers_map = iocap.get_output_map()
        self.class_name = self.extract_class_name(create_object_body)
        self.class_real_fields = None
        
    def extract_class_name(self,create_object_body: str) -> str:
            match = re.search(r"=\s*([A-Za-z_][A-Za-z0-9_]*)\s*\(", create_object_body)
            return match.group(1) if match else None 
    
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
        self.class_real_fields = list(self.obj.__dict__.items())
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
    
        # For formatting the values in msg-s:
        self.skip_format = False
        self.file_name = file_name
        self.function_name = function_name
        self.arguments = arguments
        self.result = None

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
        self.output_numbers_map = iocap.get_output_map()

    def value_correct(self, param_number, value) -> bool:
        if param_number is None:
            return self.result == value
        else:
            return param_number < len(self.arguments) and self.arguments[param_number] == value
        
    def apply_lambda_validation(self, validation_function) -> bool:
        validation_func = eval(validation_function)  
        return validation_func(self.result) 
    
    def execute_expected_function(self, expected_function_code, arguments):
        local_namespace = {}
        exec(expected_function_code, globals(), local_namespace)
        function_name = list(local_namespace.keys())[0] 
        correct_function = local_namespace[function_name]
        return correct_function(*arguments)
    
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
