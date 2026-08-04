from tiivad import *
validate_files(['''student.py'''])
execute_test(file_name='''student.py''', contains_checks=[{'check_type':'''ANY_OF_THESE''', 'nothing_else':None, 'expected_value':['''Dog'''], 'before_message':'''Kontrollin, kas põhiprogramm kutsub välja klassi `Dog`.''', 'passed_message':'''Põhiprogramm kutsub välja klassi `Dog`.''', 'failed_message':'''Põhiprogramm ei kutsu välja klassi `Dog`.''', 'data_category':'''EQUALS''', 'ignore_case':False}], scope='''main_program''', target='''class''', scope_function_name=None, scope_class_name=None, type='''calls_test''', points_weight=1.0, id=1, name='''Põhiprogramm kutsub välja klassi''', inputs=None, passed_next=None, failed_next=None, visible_to_user=True)
print(Results(None))
