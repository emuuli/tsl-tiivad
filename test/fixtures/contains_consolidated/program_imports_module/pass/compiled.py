from tiivad import *
validate_files(['''student.py'''])
execute_test(file_name='''student.py''', contains_checks=[{'check_type':'''ALL_OF_THESE''', 'nothing_else':None, 'expected_value':['''math'''], 'before_message':'''Kontrollin, kas programm impordib mooduli `math`.''', 'passed_message':'''Programm impordib mooduli `math`.''', 'failed_message':'''Programm ei impordi moodulit `math`.''', 'data_category':'''EQUALS''', 'ignore_case':False}], contains_what='''KEYWORD_WITH_PRECEDING_ARG''', contains_what_arg='''import''', scope='''program''', scope_class_name=None, scope_function_name=None, type='''contains_test''', points_weight=1.0, id=7, name='''Programm impordib mooduli math''', inputs=None, passed_next=None, failed_next=None, visible_to_user=True)
print(Results(None))
