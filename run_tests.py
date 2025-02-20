import os
import unittest

os.environ['PYTHONDONTWRITEBYTECODE'] = '1'
# Discover and run all the test cases in the 'test' directory
if __name__ == '__main__':

    loader = unittest.TestLoader()
    suite = loader.discover(start_dir='tests', pattern='test_*.py')
    
    # Change the current working directory to the directory of the script
    #os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src/distributed_rest'))

    runner = unittest.TextTestRunner()
    runner.run(suite)
