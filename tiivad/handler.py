import traceback
from itertools import chain
from typing import List

from tiivad.execution_analyzer import *
from tiivad.file_analyzer import *
from tiivad.results import Results
from tiivad.syntax_tree_analyzer import *

STATIC_TESTS_ONE = {
    'program_contains_loop_test',
    'program_contains_try_except_test',
    'program_calls_print_test',
    'function_contains_loop_test',
    'function_contains_try_except_test',
    'function_calls_print_test',
    'function_contains_return_test',
    'function_is_pure_test',
    'function_is_recursive_test',
    'mainProgram_contains_loop_test',
}

STATIC_TESTS_MANY = {
    'program_imports_module_test',
    'program_defines_function_test',
    'program_calls_function_test',
    'program_contains_keyword_test',
    'program_contains_phrase_test',
    'program_defines_class_test',
    'program_calls_class_test',
    'program_calls_class_function_test',
    'function_imports_module_test',
    'function_defines_function_test',
    'function_calls_function_test',
    'function_contains_keyword_test',
    'function_contains_phrase_test',
    'function_calls_class_function_test',
    'class_calls_class_function_test',
    'class_calls_function_test',
    'class_calls_class_test',
    'class_imports_module_test',
    'class_defines_function_test',
    'class_is_subclass_test',
    'class_is_parentclass_test',
    'class_contains_keyword_test',
    'class_contains_phrase_test',
    'mainProgram_calls_function_test',
    'mainProgram_calls_class_test',
    'mainProgram_contains_keyword_test',
    'mainProgram_contains_phrase_test',
    'mainProgram_calls_class_function_test',
}

EXECUTION_TESTS = {
    'program_execution_test',
    'class_instance_test',
    'function_execution_test'
}

FUNCTION_NOT_DEFINED_ERROR_MSG = 'Funktsiooni nimega `{function_name}` ei ole defineeritud.'
PROGRAM_NOT_DEFINED_ERROR_MSG = 'Programm nimega `{program_name}` ei ole defineeritud.'
CLASS_NOT_DEFINED_ERROR_MSG = 'Klassi nimega `{class_name}` ei ole defineeritud.'

FUNCTION_WRONG_NR_OF_ARGS_ERR_MSG = "Funktsioonil nimega `{function_name}` on vale arv argumente."

OUT_OF_INPUTS_ERR_MSG = "Programm küsis rohkem sisendeid, kui testil oli anda."
GENERATED_FILE_NOT_EXIST_ERROR_MSG = "Väljundfaili `{file_name}` ei genereeritud."

class TestResult:
    PASS = "PASS"
    FAIL = "FAIL"

def format_message(msg: str, d: dict):
    if d is None or d == {}:
        return msg
    for k, v in d.items():
        if "{" + str(k) + "}" in msg:
            if 'skip_format' in d and d['skip_format']:
                msg = msg.replace("{" + str(k) + "}", str(v))
            else:
                msg = msg.replace("{" + str(k) + "}", repr(v))
    return msg

def check_result(title, status, feedback, format_dict=None):
    return {'title': format_message(title, format_dict),
            'status': status,
            'feedback': format_message(feedback, format_dict)}

def validate_files(filenames: List[str]) -> bool:
    for filename in filenames:
        fa = FileAnalyzer(filename)
        if not fa.file_exists():
            Results.pre_evaluate_error = f"Faili {filename} ei ole."
            return False
        elif not fa.file_not_empty():
            Results.pre_evaluate_error = f"Fail {filename} on tühi."
            return False
        elif not fa.file_is_python():
            if fa.message is None:
                Results.pre_evaluate_error = f"Fail {filename} ei ole korrektne Pythoni fail."
            else:
                Results.pre_evaluate_error = fa.message
            return False
    return True

def execute_test(**kwargs):
    if Results.pre_evaluate_error:
        return

    test_type = kwargs["type"]

    checks = []
    test_exception_message = None
    actual_output = None
    actual_file_output = None
    converted_submission = None

    try:
        if test_type == "contains_test":
            test_status, actual_output, converted_submission, actual_file_output = run_contains_test(
                checks, kwargs
            )
        elif test_type == "calls_test":
            test_status, actual_output, converted_submission, actual_file_output = run_calls_test(
                checks, kwargs
            )
        elif test_type in STATIC_TESTS_ONE | STATIC_TESTS_MANY | EXECUTION_TESTS:
            component, check_type = test_type.split("_", 1)
            check_type = check_type[:-len("_test")]
            test_status, actual_output, converted_submission, actual_file_output = run_test(
                check_type,
                checks,
                component,
                kwargs,
                test_type
            )
        else:
            raise ValueError(f"Unknown test type: {test_type!r}")
    except Exception:
        test_status = TestResult.FAIL
        test_exception_message = str(traceback.format_exc())

    Results.total_points += kwargs["points_weight"]
    if test_status == TestResult.PASS:
        Results.passed_points += kwargs["points_weight"]
    Results({
        "title": kwargs.get("name", ""),
        "user_inputs": kwargs.get("standard_input_data", []),
        "created_files": [{"name": x[0], "content": x[1]} for x in kwargs.get("input_files", [])],
        "converted_submission": converted_submission,
        "actual_output": actual_output,
        "actual_file_output": actual_file_output,
        "exception_message": test_exception_message,
        "status": test_status,
        "checks": checks if test_exception_message is None else []
    })


def run_test(check_type, checks, component, kwargs, test_type):
    actual_output = None
    actual_file_output = None
    converted_submission = None
    test_status = TestResult.PASS

    if test_type in STATIC_TESTS_ONE | STATIC_TESTS_MANY:
        if component == "program":
            ta = ProgramSyntaxTreeAnalyzer(kwargs["file_name"])
        elif component == "class":
            ta = ClassSyntaxTreeAnalyzer(kwargs["file_name"], kwargs["class_name"])
        elif component == "function":
            ta = FunctionSyntaxTreeAnalyzer(kwargs["file_name"], kwargs["function_name"])
        elif component == "mainProgram":
            ta = MainProgramSyntaxTreeAnalyzer(kwargs["file_name"])
        else:
            ta = None
        
        for check in kwargs.get("generic_checks", []) + kwargs.get("contains_checks", []):
            ta.expected = check['expected_value']
            if ta is not None and ta.tree is not None and \
                    (test_type in STATIC_TESTS_ONE and getattr(ta, check_type)() == check['expected_value'] or
                     test_type in STATIC_TESTS_MANY and ta.analyze_with_quantifier(check_type, check['check_type'],
                                                                                   set(check['expected_value']),
                                                                                    check['nothing_else'])):
                checks.append(check_result(check['before_message'], TestResult.PASS, check['passed_message'],
                                           ta.__dict__))
            else:
                if(ta.raised_exception() and "No such file or directory:" in str(ta.exception)):
                    test_status = TestResult.FAIL
                    checks.append(check_result(test_type, test_status, PROGRAM_NOT_DEFINED_ERROR_MSG, ta.__dict__))
                elif(ta.raised_exception() and "Not found" in str(ta.exception) and isinstance(ta, FunctionSyntaxTreeAnalyzer)):
                    test_status = TestResult.FAIL
                    checks.append(check_result(test_type, test_status, FUNCTION_NOT_DEFINED_ERROR_MSG, ta.__dict__))
                elif(ta.raised_exception() and "Not found" in str(ta.exception) and isinstance(ta, ClassSyntaxTreeAnalyzer)):
                    test_status = TestResult.FAIL
                    checks.append(check_result(test_type, test_status, CLASS_NOT_DEFINED_ERROR_MSG, ta.__dict__))
                else:  
                    checks.append(check_result(check['before_message'], TestResult.FAIL, check['failed_message'],ta.__dict__))
                    test_status = TestResult.FAIL
                    break

    elif test_type in EXECUTION_TESTS:
        if component == "program":
            ea = ProgramExecutionAnalyzer(kwargs["file_name"], kwargs.get("standard_input_data", []),
                                          kwargs.get("input_files", []))
        elif component == "class":
            ea = ClassExecutionAnalyzer(kwargs["file_name"], kwargs.get("create_object", ""),
                                        kwargs.get("standard_input_data", []), kwargs.get("input_files", []))
        elif component == "function":
            ea = FunctionExecutionAnalyzer(kwargs["file_name"], kwargs["function_name"], kwargs["function_type"],
                                           kwargs.get("create_object", "pass"), kwargs["arguments"],
                                           kwargs.get("standard_input_data", []), kwargs.get("input_files", []))
        else:
            ea = None
        actual_output = ea.all_io
        converted_submission = ea.converted_script

        # Erind
        if ea.raised_exception() and isinstance(ea.exception, OutOfInputsError):
            test_status = TestResult.FAIL
            message = kwargs.get("out_of_inputs_error_msg", OUT_OF_INPUTS_ERR_MSG)
            checks.append(check_result(test_type, test_status, message, ea.__dict__))
        elif ea.raised_exception() and isinstance(ea, FunctionExecutionAnalyzer) and \
                "'NoneType' object is not callable" in ea.exception.args[0]:
            test_status = TestResult.FAIL
            message = kwargs.get("function_not_defined_error_msg", FUNCTION_NOT_DEFINED_ERROR_MSG)
            checks.append(check_result(test_type, test_status, message, ea.__dict__))
        elif ea.raised_exception() and isinstance(ea, FunctionExecutionAnalyzer) and \
                "positional argument" in ea.exception.args[0]:
            test_status = TestResult.FAIL
            message = kwargs.get("too_many_arguments_provided_error_msg", FUNCTION_WRONG_NR_OF_ARGS_ERR_MSG)
            checks.append(check_result(test_type, test_status, message, ea.__dict__))
        elif ea.raised_exception() and isinstance(ea, ClassExecutionAnalyzer) and \
                "is not defined"  in ea.exception.args[0]:
            test_status = TestResult.FAIL
            message = kwargs.get("class_not_defined_error_msg", CLASS_NOT_DEFINED_ERROR_MSG)
            checks.append(check_result(test_type, test_status, message, ea.__dict__))
        elif 'exception_check' in kwargs and kwargs['exception_check'] is not None:
            check = kwargs['exception_check']
            if ea.raised_exception() == check.get('expected_value', False):
                message = check['passed_message']
            else:
                test_status = TestResult.FAIL
                message = check['failed_message']
            checks.append(check_result(check['before_message'], test_status, message, ea.__dict__))
        elif ea.raised_exception():
            raise ea.exception
        check_lists = [
            # Standardväljund ja väljundfail
            kwargs.get("standard_output_checks", []) + kwargs.get("output_file_checks", []),
            # Funktsiooni muudetud väärtus
            kwargs.get("param_value_checks", []),
            # Funktsiooni tagastatud väärtus
            kwargs.get("return_value_checks", []),
            # Objekti olek
            kwargs.get("class_instance_checks", [])
        ]

        for i, check_list in enumerate(check_lists):
            if test_status == TestResult.FAIL:
                break
            for check in check_list:
                if i == 0:
                    if check['data_category'] == ElementsType.CONTAINS_NUMBERS:
                        # We make sure that the input values (if string) are also converted to numbers to match comparison.
                        check['expected_value'] = list(chain.from_iterable(
                            [v] if not isinstance(v, str) else extract_numbers(v) for v in check['expected_value'])
                        )
                    result = ea.analyze_output_with_quantifier(check.get('file_name', None), check['data_category'],
                                                               check['check_type'], check['expected_value'], check.get('output_category',""),
                                                               check['nothing_else'], check['elements_ordered'],
                                                               check.get('ignore_case', False))
                    if ea.raised_exception() and isinstance(ea.exception, FileNotFoundError):
                        test_status = TestResult.FAIL
                        checks.append(
                            check_result(check['before_message'], TestResult.FAIL, GENERATED_FILE_NOT_EXIST_ERROR_MSG,
                            ea.__dict__))
                        break
                    ea.skip_format = True
                    # Remove the [ ] symbols from the expected value for Lahendus UI.
                    ea.actual = ", ".join(map(lambda el: repr(el),ea.actually_found))
                    ea.expected = ", ".join(map(lambda el: repr(el), check['expected_value']))
                elif i == 1:
                    result = ea.value_correct(check.get('param_number', None), check['expected_value'])
                elif i == 2: # Return value check                   
                    expected_value = check.get("expected_value")
                    if isinstance(expected_value, str) and expected_value.startswith("lambda "):
                        result = ea.apply_lambda_validation(expected_value)
                    elif isinstance(expected_value, str) and expected_value.strip().startswith("def "):
                        expected_output = ea.execute_expected_function(expected_value, ea.arguments)
                        expected_value = expected_output
                        result = ea.result == expected_output
                    else:
                        result = ea.result == expected_value
                    # For logging/msg-s purposes
                    ea.expected = expected_value
                    ea.actual = ea.result
                elif i == 3:
                    result = ea.fields_correct(check['fields_final'], check['check_name'], check['check_value'],
                                               check['nothing_else'])
                    ea.actual = ea.class_real_fields
                    ea.expected = check['fields_final']
                else:
                    result = False

                if result:
                    checks.append(check_result(check['before_message'], TestResult.PASS, check['passed_message'],
                                               ea.__dict__))
                else:
                    test_status = TestResult.FAIL
                    checks.append(check_result(check['before_message'], TestResult.FAIL, check['failed_message'],
                                               ea.__dict__))
                    break
        actual_file_output = ea.all_file_io
    

    return test_status, actual_output, converted_submission, actual_file_output


def run_contains_test(checks, kwargs):
    """Dispatch for the consolidated `contains_test` shape emitted by the new
    TSL compiler in the `easy` repo. Translates `scope` + `containsWhat` +
    `genericCheck` into the existing analyzer + `analyze_with_quantifier`
    machinery, so this is purely a re-skin of the legacy
    `*_contains_keyword_test` / `*_contains_phrase_test` codepath."""
    actual_output = None
    actual_file_output = None
    converted_submission = None
    test_status = TestResult.PASS

    scope = kwargs["scope"]
    if scope == "program":
        ta = ProgramSyntaxTreeAnalyzer(kwargs["file_name"])
    elif scope == "class":
        ta = ClassSyntaxTreeAnalyzer(kwargs["file_name"], kwargs["scope_class_name"])
    elif scope == "function":
        ta = FunctionSyntaxTreeAnalyzer(kwargs["file_name"], kwargs["scope_function_name"])
    elif scope == "main_program":
        ta = MainProgramSyntaxTreeAnalyzer(kwargs["file_name"])
    else:
        raise ValueError(f"Unknown scope for contains_test: {scope!r}")

    contains_what = kwargs["contains_what"]
    contains_what_arg = kwargs.get("contains_what_arg")
    if contains_what == "KEYWORD_NO_ARG":
        target = "contains_keyword_used"
    elif contains_what == "PHRASE":
        target = "contains_phrase"
    elif contains_what == "KEYWORD_WITH_PRECEDING_ARG" and contains_what_arg == "import":
        target = "imports_module"
    else:
        raise ValueError(
            f"Unsupported contains_what for contains_test: "
            f"{contains_what!r} (arg={contains_what_arg!r})"
        )

    for check in kwargs.get("contains_checks", []):
        ta.expected = check['expected_value']
        if ta is not None and ta.tree is not None and \
                ta.analyze_with_quantifier(target, check['check_type'],
                                           set(check['expected_value']),
                                           check['nothing_else']):
            checks.append(check_result(check['before_message'], TestResult.PASS, check['passed_message'],
                                       ta.__dict__))
        else:
            if ta.raised_exception() and "No such file or directory:" in str(ta.exception):
                test_status = TestResult.FAIL
                checks.append(check_result("contains_test", test_status, PROGRAM_NOT_DEFINED_ERROR_MSG, ta.__dict__))
            elif ta.raised_exception() and "Not found" in str(ta.exception) and isinstance(ta, FunctionSyntaxTreeAnalyzer):
                test_status = TestResult.FAIL
                checks.append(check_result("contains_test", test_status, FUNCTION_NOT_DEFINED_ERROR_MSG, ta.__dict__))
            elif ta.raised_exception() and "Not found" in str(ta.exception) and isinstance(ta, ClassSyntaxTreeAnalyzer):
                test_status = TestResult.FAIL
                checks.append(check_result("contains_test", test_status, CLASS_NOT_DEFINED_ERROR_MSG, ta.__dict__))
            else:
                checks.append(check_result(check['before_message'], TestResult.FAIL, check['failed_message'], ta.__dict__))
                test_status = TestResult.FAIL
                break

    return test_status, actual_output, converted_submission, actual_file_output


def run_calls_test(checks, kwargs):
    """Dispatch for the consolidated `calls_test` shape emitted by the new
    TSL compiler in the `easy` repo. Translates `scope` + `target` +
    `genericCheck` into the existing analyzer + `analyze_with_quantifier`
    machinery, so this is purely a re-skin of the 11 legacy
    `*_calls_function_test` / `*_calls_class_test` / `*_calls_class_function_test`
    codepaths."""
    actual_output = None
    actual_file_output = None
    converted_submission = None
    test_status = TestResult.PASS

    scope = kwargs["scope"]
    if scope == "program":
        ta = ProgramSyntaxTreeAnalyzer(kwargs["file_name"])
    elif scope == "class":
        ta = ClassSyntaxTreeAnalyzer(kwargs["file_name"], kwargs["scope_class_name"])
    elif scope == "function":
        ta = FunctionSyntaxTreeAnalyzer(kwargs["file_name"], kwargs["scope_function_name"])
    elif scope == "main_program":
        ta = MainProgramSyntaxTreeAnalyzer(kwargs["file_name"])
    else:
        raise ValueError(f"Unknown scope for calls_test: {scope!r}")

    calls_what = kwargs["target"]
    if calls_what == "function":
        target = "calls_function"
    elif calls_what == "class":
        target = "calls_class"
    elif calls_what == "class_function":
        target = "calls_class_function"
    else:
        raise ValueError(f"Unsupported target for calls_test: {calls_what!r}")

    for check in kwargs.get("contains_checks", []):
        ta.expected = check['expected_value']
        if ta is not None and ta.tree is not None and \
                ta.analyze_with_quantifier(target, check['check_type'],
                                           set(check['expected_value']),
                                           check['nothing_else']):
            checks.append(check_result(check['before_message'], TestResult.PASS, check['passed_message'],
                                       ta.__dict__))
        else:
            if ta.raised_exception() and "No such file or directory:" in str(ta.exception):
                test_status = TestResult.FAIL
                checks.append(check_result("calls_test", test_status, PROGRAM_NOT_DEFINED_ERROR_MSG, ta.__dict__))
            elif ta.raised_exception() and "Not found" in str(ta.exception) and isinstance(ta, FunctionSyntaxTreeAnalyzer):
                test_status = TestResult.FAIL
                checks.append(check_result("calls_test", test_status, FUNCTION_NOT_DEFINED_ERROR_MSG, ta.__dict__))
            elif ta.raised_exception() and "Not found" in str(ta.exception) and isinstance(ta, ClassSyntaxTreeAnalyzer):
                test_status = TestResult.FAIL
                checks.append(check_result("calls_test", test_status, CLASS_NOT_DEFINED_ERROR_MSG, ta.__dict__))
            else:
                checks.append(check_result(check['before_message'], TestResult.FAIL, check['failed_message'], ta.__dict__))
                test_status = TestResult.FAIL
                break

    return test_status, actual_output, converted_submission, actual_file_output


if __name__ == "__main__":
    execute_test(file_name='''../test/samples/prog3-calc.py''',
                 type='''function_execution_test''',
                 function_name='''f''',
                 function_type='''FUNCTION''',
                 create_object=None,
                 arguments=[2],
                 standard_input_data=[],
                 input_files=[],
                 return_value_checks=[
                     {'expected_value': 4,
                      'before_message': '''Kas funktsioon tagastab õige väärtuse?''',
                      'passed_message': '''Funktsioon tagastas õige väärtuse {actual}.''',
                      'failed_message': '''Funktsioon tagastas vale väärtuse {actual}.'''
                      },
                     {'expected_value': 5,
                      'before_message': '''Kas funktsioon tagastab õige väärtuse?''',
                      'passed_message': '''Funktsioon tagastas õige väärtuse {actual}.''',
                      'failed_message': '''Funktsioon tagastas vale väärtuse {actual}.'''
                      }
                 ],
                 points_weight=1
                 )
    print(Results(None))
