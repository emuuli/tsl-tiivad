from tiivad import *

validate_files(['''lahendus.py'''])
execute_test(file_name='''lahendus.py''', standard_input_data=[], input_files=[('''andmed.txt''', '''abc''')],
             standard_output_checks=[{'check_type': '''ALL_OF_THESE''', 'nothing_else': None, 'expected_value': [],
                                      'elements_ordered': False, 'before_message': '''''', 'passed_message': '''OK''',
                                      'failed_message': '''Viga''', 'data_category': '''CONTAINS_STRINGS''',
                                      'ignore_case': False}], output_file_checks=[], exception_check=None,
             type='''program_execution_test''', points_weight=1.0, id=391, name='''Programmi käivituse test''',
             inputs=None, passed_next=None, failed_next=None, visible_to_user=True)
execute_test(file_name='''lahendus.py''', standard_input_data=['''iop''', '''jkl'''], input_files=[],
             standard_output_checks=[
                 {'check_type': '''ALL_OF_THESE''', 'nothing_else': None, 'expected_value': ['''42'''],
                  'elements_ordered': False, 'before_message': '''''', 'passed_message': '''Väljundis leidub arv 42''',
                  'failed_message': '''Ei leidnud väljundist arvu 42''', 'data_category': '''CONTAINS_NUMBERS''',
                  'ignore_case': False},
                 {'check_type': '''ALL_OF_THESE''', 'nothing_else': None, 'expected_value': ['''asd'''],
                  'elements_ordered': False, 'before_message': '''''',
                  'passed_message': '''Väljundis leidub sõne "asd"''',
                  'failed_message': '''Ei leidnud väljundist sõnet "asd"''', 'data_category': '''CONTAINS_STRINGS''',
                  'ignore_case': False}], output_file_checks=[], exception_check=None,
             type='''program_execution_test''', points_weight=1.0, id=231, name='''Näiteandmed''', inputs=None,
             passed_next=None, failed_next=None, visible_to_user=True)
execute_test(file_name='''lahendus.py''', standard_input_data=['''11''', '''2023'''], input_files=[],
             standard_output_checks=[
                 {'check_type': '''ALL_OF_THESE''', 'nothing_else': None, 'expected_value': ['''42'''],
                  'elements_ordered': False, 'before_message': '''''', 'passed_message': '''Väljundis leidub arv 42''',
                  'failed_message': '''Ei leidnud väljundist arvu 42''', 'data_category': '''CONTAINS_NUMBERS''',
                  'ignore_case': False},
                 {'check_type': '''ALL_OF_THESE''', 'nothing_else': None, 'expected_value': ['''asd'''],
                  'elements_ordered': False, 'before_message': '''''',
                  'passed_message': '''Väljundis leidub sõne "asd"''',
                  'failed_message': '''Ei leidnud väljundist sõnet "asd"''', 'data_category': '''CONTAINS_STRINGS''',
                  'ignore_case': False},
                 {'check_type': '''NONE_OF_THESE''', 'nothing_else': None, 'expected_value': ['''qwe'''],
                  'elements_ordered': False, 'before_message': '''''',
                  'passed_message': '''Väljundis ei ole sõne "qwe"''',
                  'failed_message': '''Leidsin programmi väljundist keelatud sõne "qwe"''',
                  'data_category': '''CONTAINS_STRINGS''', 'ignore_case': False}], output_file_checks=[],
             exception_check=None, type='''program_execution_test''', points_weight=1.0, id=686,
             name='''Keerulisemad andmed''', inputs=None, passed_next=None, failed_next=None, visible_to_user=True)

print(Results(None))
