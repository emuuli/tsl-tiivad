from tiivad import *
validate_files(['''student.py'''])
execute_test(file_name='''student.py''', contains_checks=[{'check_type':'''ANY_OF_THESE''', 'nothing_else':None, 'expected_value':['''name'''], 'before_message':'''Kontrollin, kas klass `Person` kasutab nime atribuuti.''', 'passed_message':'''Klass `Person` kasutab nime atribuuti.''', 'failed_message':'''Klass `Person` ei kasuta nime atribuuti.''', 'data_category':'''EQUALS''', 'ignore_case':False}], contains_what='''PHRASE''', contains_what_arg=None, scope='''class''', scope_class_name='''Person''', scope_function_name=None, type='''contains_test''', points_weight=1.0, id=4, name='''Klass kasutab nime''', inputs=None, passed_next=None, failed_next=None, visible_to_user=True)
print(Results(None))
