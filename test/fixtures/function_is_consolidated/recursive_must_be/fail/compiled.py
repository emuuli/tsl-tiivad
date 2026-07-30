from tiivad import *
validate_files(['''student.py'''])
execute_test(file_name='''student.py''', function_name='''arvuta''', function_property='''RECURSIVE''', generic_checks=[{'expected_value':True, 'before_message':'''Kontrollin, kas funktsioon `arvuta` on rekursiivne.''', 'passed_message':'''Funktsioon `arvuta` on rekursiivne.''', 'failed_message':'''Funktsioon `arvuta` ei ole rekursiivne.'''}], type='''function_is_test''', points_weight=1.0, id=1, name='''Funktsioon arvuta on rekursiivne''', inputs=None, passed_next=None, failed_next=None, visible_to_user=True)
print(Results(None))
