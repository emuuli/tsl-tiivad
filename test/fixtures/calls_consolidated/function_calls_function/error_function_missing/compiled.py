from tiivad import *
validate_files(['''student.py'''])
execute_test(file_name='''student.py''', contains_checks=[{'check_type':'''ANY_OF_THESE''', 'nothing_else':None, 'expected_value':['''inner'''], 'before_message':'''Kontrollin, kas funktsioon `outer` kutsub välja funktsiooni `inner`.''', 'passed_message':'''Funktsioon `outer` kutsub välja funktsiooni `inner`.''', 'failed_message':'''Funktsioon `outer` ei kutsu välja funktsiooni `inner`.''', 'data_category':'''EQUALS''', 'ignore_case':False}], scope='''function''', target='''function''', scope_function_name='''outer''', scope_class_name=None, type='''calls_test''', points_weight=1.0, id=1, name='''Funktsioon kutsub välja funktsiooni''', inputs=None, passed_next=None, failed_next=None, visible_to_user=True)
print(Results(None))
