import os
import sys
import io
import unittest
import subprocess

from .util import assertFilesEqual, deleteFiles

TARGET = ''
NEEDS = []

testSuiteBaseDir = os.path.dirname(__file__)
testsDir = os.path.join(testSuiteBaseDir, "tests")
tmpDir = os.path.join(testSuiteBaseDir, "tmp")


class CocoTester(object):
    def __init__(self, compiler, targetLanguageExt, testSuite):
        self._compiler = compiler
        self._fnTgtExt = targetLanguageExt
        self._suite = testSuite
   
    def generateTest(self, name, isErrorTest):
        dirName = os.path.join(testsDir, name)
        testFileName = os.path.join(dirName, 'Test.atg')
        
        outputFileName = os.path.join(dirName, 'Output.txt')
        traceFileName = os.path.join(dirName, 'Trace.txt')
        parserFileName = os.path.join(dirName, 'Parser.py')
        scannerFileName = os.path.join(dirName, 'Scanner.py')
        
        traceResFileName = os.path.join(tmpDir, 'trace.txt')
        parserResFileName = os.path.join(tmpDir, 'Parser.py')
        scannerResFileName = os.path.join(tmpDir, 'Scanner.py')
        
        class Test(unittest.TestCase):
            maxDiff = None
            @classmethod
            def setUpClass(cls):
                print('Running test: %s' % name)
                args = ['python', '-m', self._compiler, '-agfjs', '-O', tmpDir, testFileName]
                with subprocess.Popen(args, shell=False, stdout=subprocess.PIPE) as proc:
                    proc.wait()
                    __class__.output = io.TextIOWrapper(proc.stdout).read()
                os.makedirs(tmpDir, exist_ok=True)

            def testTrace(tself):
                assertFilesEqual(tself, traceFileName, traceResFileName)

            def testOutput(tself):
                with open(outputFileName, "rt", encoding="utf-8") as f:
                    referenceOuput = f.read()
                tself.assertEqual(__class__.output, referenceOuput)

            if not isErrorTest:
                def testGeneratedCode(tself):
                    assertFilesEqual(tself, parserResFileName, parserFileName)
                    assertFilesEqual(tself, scannerResFileName, scannerFileName)

            @classmethod
            def tearDownClass(cls):
                deleteFiles('*.py.old', 'Parser.py', 'Scanner.py', scannerResFileName)

        return Test

    def generateTests(self):
        for name, isErrorTest in self._suite:
            test = self.generateTest(name, isErrorTest)
            test.__name__ = name
            yield test

    def __call__(self):
        loader = unittest.TestLoader()
        runner = unittest.TextTestRunner()
        suite = unittest.TestSuite()

        for testClass in self.generateTests():
            testcase = loader.loadTestsFromTestCase(testClass)
            suite.addTest(testcase)

        result = runner.run(suite)
        sys.exit(not result.wasSuccessful())


suite = [
     ( 'TestAlts',           False ),
     ( 'TestOpts',           False ),
     ( 'TestOpts1',          False ),
     ( 'TestIters',          False ),
     ( 'TestEps',            False ),
     ( 'TestAny',            False ),
     ( 'TestAny1',           False ),
     ( 'TestSync',           False ),
#    ( 'TestSem',            False ),  # FIXME
     ( 'TestWeak',           False ),
     ( 'TestChars',          False ),
     ( 'TestTokens',         False ),
     ( 'TestTokens1',        True  ),
     ( 'TestComments',       False ),
     ( 'TestDel',            False ),
     ( 'TestTerminalizable', True  ),
     ( 'TestComplete',       True  ),
     ( 'TestReached',        True  ),
     ( 'TestCircular',       True  ),
     ( 'TestLL1',            False ),
     ( 'TestResOK',          False ),
     ( 'TestResIllegal',     True  ),
     ( 'TestCasing',         False )
]

tester = CocoTester('Coco', 'py', suite)
tester()
