from tiivad import *
validate_files(['''student.py'''])
execute_test(file_name='''student.py''', contains_checks=[{'check_type':'''ANY_OF_THESE''', 'nothing_else':None, 'expected_value':['''for''', '''while'''], 'before_message':'''Kontrollin, kas programm sisaldab tsüklit.''', 'passed_message':'''Programm sisaldab tsüklit.''', 'failed_message':'''Programm ei sisalda tsüklit.''', 'data_category':'''EQUALS''', 'ignore_case':False}], contains_what='''KEYWORD_NO_ARG''', contains_what_arg=None, scope='''program''', scope_class_name=None, scope_function_name=None, type='''contains_test''', points_weight=1.0, id=10, name='''Programm sisaldab tsüklit''', inputs=None, passed_next=None, failed_next=None, visible_to_user=True)
print(Results(None))
