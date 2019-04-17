#This file is part of the testing program
#in this top level directory, run pytest and it will append this dir to the path so that the test files in the tests dir can find the correct imports

import sys, os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))