from tiivad import *
validate_files(['''student.py'''])
execute_test(file_name='''student.py''', contains_checks=[{'check_type':'''ALL_OF_THESE''', 'nothing_else':None, 'expected_value':['''try''', '''except'''], 'before_message':'''Kontrollin, kas programm sisaldab try/except-i.''', 'passed_message':'''Programm sisaldab try/except-i.''', 'failed_message':'''Programm ei sisalda try/except-i.''', 'data_category':'''EQUALS''', 'ignore_case':False}], contains_what='''KEYWORD_NO_ARG''', contains_what_arg=None, scope='''program''', scope_class_name=None, scope_function_name=None, type='''contains_test''', points_weight=1.0, id=13, name='''Programm sisaldab try/except-i''', inputs=None, passed_next=None, failed_next=None, visible_to_user=True)
print(Results(None))
