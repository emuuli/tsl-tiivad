from tiivad import *
validate_files(['''student.py'''])
execute_test(file_name='''student.py''', contains_checks=[{'check_type':'''ANY_OF_THESE''', 'nothing_else':None, 'expected_value':['''helper'''], 'before_message':'''Kontrollin, kas programm kutsub välja funktsiooni `helper`.''', 'passed_message':'''Programm kutsub välja funktsiooni `helper`.''', 'failed_message':'''Programm ei kutsu välja funktsiooni `helper`.''', 'data_category':'''EQUALS''', 'ignore_case':False}], scope='''program''', target='''function''', scope_function_name=None, scope_class_name=None, type='''calls_test''', points_weight=1.0, id=1, name='''Programm kutsub välja funktsiooni''', inputs=None, passed_next=None, failed_next=None, visible_to_user=True)
print(Results(None))
