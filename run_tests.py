import logging
import os
import unittest

tests_dir = 'paip/tests'

for file in os.listdir(tests_dir):
    # Uncomment to enable test logging:
    #logging.basicConfig(level=logging.DEBUG)
    
    if not file.startswith('test_') or not file.endswith('.py'):
        continue
    qual_file = os.path.join(tests_dir, file)
    module = qual_file.replace('/', '.')[:-3] # leave off .py
    print 'Testing module %s' % module
    unittest.main(module, exit=False)
