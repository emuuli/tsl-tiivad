from tiivad import *
validate_files(['''student.py'''])
execute_test(file_name='''student.py''', contains_checks=[{'check_type':'''ANY_OF_THESE''', 'nothing_else':None, 'expected_value':['''for''', '''while'''], 'before_message':'''Kontrollin, kas funktsioon `sum_list` sisaldab tsüklit.''', 'passed_message':'''Funktsioon `sum_list` sisaldab tsüklit.''', 'failed_message':'''Funktsioon `sum_list` ei sisalda tsüklit.''', 'data_category':'''EQUALS''', 'ignore_case':False}], contains_what='''KEYWORD_NO_ARG''', contains_what_arg=None, scope='''function''', scope_class_name=None, scope_function_name='''sum_list''', type='''contains_test''', points_weight=1.0, id=11, name='''Funktsioon sisaldab tsüklit''', inputs=None, passed_next=None, failed_next=None, visible_to_user=True)
print(Results(None))
