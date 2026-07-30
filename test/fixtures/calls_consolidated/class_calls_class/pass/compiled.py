from tiivad import *
validate_files(['''student.py'''])
execute_test(file_name='''student.py''', contains_checks=[{'check_type':'''ANY_OF_THESE''', 'nothing_else':None, 'expected_value':['''Inner'''], 'before_message':'''Kontrollin, kas klass `Owner` kutsub välja klassi `Inner`.''', 'passed_message':'''Klass `Owner` kutsub välja klassi `Inner`.''', 'failed_message':'''Klass `Owner` ei kutsu välja klassi `Inner`.''', 'data_category':'''EQUALS''', 'ignore_case':False}], scope='''class''', target='''class''', scope_function_name=None, scope_class_name='''Owner''', type='''calls_test''', points_weight=1.0, id=1, name='''Klass kutsub välja klassi''', inputs=None, passed_next=None, failed_next=None, visible_to_user=True)
print(Results(None))
