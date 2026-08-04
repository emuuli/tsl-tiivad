from tiivad import *
validate_files(['''student.py'''])
execute_test(file_name='''student.py''', contains_checks=[{'check_type':'''ANY_OF_THESE''', 'nothing_else':None, 'expected_value':['''def'''], 'before_message':'''Kontrollin, kas klass `Counter` sisaldab meetodit.''', 'passed_message':'''Klass `Counter` sisaldab meetodit.''', 'failed_message':'''Klass `Counter` ei sisalda meetodit.''', 'data_category':'''EQUALS''', 'ignore_case':False}], contains_what='''KEYWORD_NO_ARG''', contains_what_arg=None, scope='''class''', scope_class_name='''Counter''', scope_function_name=None, type='''contains_test''', points_weight=1.0, id=3, name='''Klass sisaldab meetodit''', inputs=None, passed_next=None, failed_next=None, visible_to_user=True)
print(Results(None))
