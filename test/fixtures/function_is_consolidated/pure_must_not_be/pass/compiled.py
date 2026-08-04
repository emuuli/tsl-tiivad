from tiivad import *
validate_files(['''student.py'''])
execute_test(file_name='''student.py''', function_name='''arvuta''', function_property='''PURE''', generic_checks=[{'expected_value':False, 'before_message':'''Kontrollin, kas funktsioon `arvuta` kasutab globaalset muutujat.''', 'passed_message':'''Funktsioon `arvuta` kasutab globaalset muutujat, nagu ülesandes nõutud.''', 'failed_message':'''Funktsioon `arvuta` kasutab vaid lokaalseid muutujaid.'''}], type='''function_is_test''', points_weight=1.0, id=1, name='''Funktsioon arvuta kasutab globaalset muutujat''', inputs=None, passed_next=None, failed_next=None, visible_to_user=True)
print(Results(None))
