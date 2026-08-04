from tiivad import *
validate_files(['''student.py'''])
execute_test(file_name='''student.py''', contains_checks=[{'check_type':'''ANY_OF_THESE''', 'nothing_else':None, 'expected_value':['''Auto'''], 'before_message':'''Kontrollin, kas funktsioon `loo_auto` kutsub välja klassi `Auto`.''', 'passed_message':'''Funktsioon `loo_auto` kutsub välja klassi `Auto`.''', 'failed_message':'''Funktsioon `loo_auto` ei kutsu välja klassi `Auto`.''', 'data_category':'''EQUALS''', 'ignore_case':False}], scope='''function''', target='''class''', scope_function_name='''loo_auto''', scope_class_name=None, type='''calls_test''', points_weight=1.0, id=1, name='''Funktsioon kutsub välja klassi''', inputs=None, passed_next=None, failed_next=None, visible_to_user=True)
print(Results(None))
