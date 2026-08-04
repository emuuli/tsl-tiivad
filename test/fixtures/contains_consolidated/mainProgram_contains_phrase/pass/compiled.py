from tiivad import *
validate_files(['''student.py'''])
execute_test(file_name='''student.py''', contains_checks=[{'check_type':'''ANY_OF_THESE''', 'nothing_else':None, 'expected_value':['''Tere'''], 'before_message':'''Kontrollin, kas põhiprogramm sisaldab sõnet 'Tere'.''', 'passed_message':'''Põhiprogramm sisaldab sõnet 'Tere'.''', 'failed_message':'''Põhiprogramm ei sisalda sõnet 'Tere'.''', 'data_category':'''EQUALS''', 'ignore_case':False}], contains_what='''PHRASE''', contains_what_arg=None, scope='''main_program''', scope_class_name=None, scope_function_name=None, type='''contains_test''', points_weight=1.0, id=6, name='''Põhiprogramm tervitab''', inputs=None, passed_next=None, failed_next=None, visible_to_user=True)
print(Results(None))
