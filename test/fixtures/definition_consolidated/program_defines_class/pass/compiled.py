from tiivad import *
validate_files(['''student.py'''])
execute_test(file_name='''student.py''', contains_checks=[{'check_type':'''ANY_OF_THESE''', 'nothing_else':None, 'expected_value':['''Auto'''], 'before_message':'''Kontrollin, kas programm defineerib klassi `Auto`.''', 'passed_message':'''Programm defineerib klassi `Auto`.''', 'failed_message':'''Programm ei defineeri klassi `Auto`.''', 'data_category':'''EQUALS''', 'ignore_case':False}], scope='''program''', definition_check_type='''CLASS''', scope_function_name=None, scope_class_name=None, definition_check_value='''Auto''', super_class_name=None, type='''definition_test''', points_weight=1.0, id=1, name='''Programm defineerib klassi Auto''', inputs=None, passed_next=None, failed_next=None, visible_to_user=True)
print(Results(None))
