#/usr/bin/env python


import os
import sys
import unittest
#os.chdir(sys.prefix)
import pmagpy_tests as pt



if __name__ == "__main__":
    #if '-gui' in sys.argv:
    #    os.system("pythonw -m unittest -v pmagpy_tests.test_pmag_gui pmagpy_tests.test_magic_gui pmagpy_tests.test_demag_gui pmagpy_tests.test_thellier_gui pmagpy_tests.test_er_magic_dialogs")
    #elif '-cmd' in sys.argv:
    #    os.system("pythonw -m unittest -v pmagpy_tests.test_builder pmagpy_tests.test_ipmag pmagpy_tests.test_pmag pmagpy_tests.test_validations pmagpy_tests.test_imports pmagpy_tests.test_programs")
    #else:
    #    #suite = unittest.TestLoader().loadTestsFromTestCase(TestStringMethods)
    #    #unittest.TextTestRunner(verbosity=2).run(suite)
    #    #
    #    #suite1 = module1.TheTestSuite()
    #    #suite2 = module2.TheTestSuite()
    #    #alltests = unittest.TestSuite([suite1, suite2])
    #    print dir(pt.test_ipmag)
    #os.chdir(sys.prefix)
    suite1 = unittest.TestLoader().loadTestsFromModule(pt.test_pmag_gui)
    suite2 = unittest.TestLoader().loadTestsFromModule(pt.test_pmag)
    suite3 = unittest.TestLoader().loadTestsFromModule(pt.test_imports)
    suite4 = unittest.TestLoader().loadTestsFromModule(pt.test_ipmag)
    #suite5 = unittest.TestLoader().loadTestsFromModule(pt.test_thellier_gui)
    #suite6 = unittest.TestLoader().loadTestsFromModule(pt.test_demag_gui)
    suite7 = unittest.TestLoader().loadTestsFromModule(pt.test_magic_gui)
    suite8 = unittest.TestLoader().loadTestsFromModule(pt.test_builder)
    suite9 = unittest.TestLoader().loadTestsFromModule(pt.test_validations)
    #suite10 = unittest.TestLoader().loadTestsFromModule(pt.test_programs)
    suite12 = unittest.TestLoader().loadTestsFromModule(pt.test_magic_gui2)
    suite13 = unittest.TestLoader().loadTestsFromModule(pt.test_new_builder)
    suite14 = unittest.TestLoader().loadTestsFromModule(pt.test_er_magic_dialogs)
    suite15 = unittest.TestLoader().loadTestsFromModule(pt.test_find_pmag_dir)
    full = unittest.TestSuite([suite1, suite2, suite3, suite4,
                               suite7, suite8, suite9,
                               suite12, suite13, suite14, suite15])

    unittest.TextTestRunner(verbosity=3).run(full)

    #one = unittest.TestSuite([suite15])
    #unittest.TextTestRunner(verbosity=3).run(one)
