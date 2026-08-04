from tiivad import *
validate_files(['''student.py'''])
execute_test(file_name='''student.py''', contains_checks=[{'check_type':'''ANY_OF_THESE''', 'nothing_else':None, 'expected_value':['''bark'''], 'before_message':'''Kontrollin, kas programm kutsub välja klassi funktsiooni `bark`.''', 'passed_message':'''Programm kutsub välja klassi funktsiooni `bark`.''', 'failed_message':'''Programm ei kutsu välja klassi funktsiooni `bark`.''', 'data_category':'''EQUALS''', 'ignore_case':False}], scope='''program''', target='''class_function''', scope_function_name=None, scope_class_name=None, type='''calls_test''', points_weight=1.0, id=1, name='''Programm kutsub välja klassi funktsiooni''', inputs=None, passed_next=None, failed_next=None, visible_to_user=True)
print(Results(None))
