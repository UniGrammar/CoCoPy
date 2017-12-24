import os
import unittest
import subprocess

from .util import assertFilesEqual, deleteFiles

TARGET = ''
NEEDS  = [ ]

testSuiteBaseDir = os.path.dirname(__file__)
testsDir = os.path.join(testSuiteBaseDir, "tests")
tmpDir = os.path.join(testSuiteBaseDir, "tmp")

class CocoTester( object ):
   def __init__( self, compiler, targetLanguageExt, testSuite ):
      self._compiler    = compiler
      self._fnTgtExt    = targetLanguageExt
      self._suite       = testSuite
   
   def generateTest(self, name, isErrorTest):
      dirName = os.path.join(testsDir, name)
      testFileName = os.path.join(dirName, 'Test.atg')
      
      outputFileName  = os.path.join(dirName, 'Output.txt')
      traceFileName   = os.path.join(dirName, 'Trace.txt')
      parserFileName  = os.path.join(dirName, 'Parser.py')
      scannerFileName = os.path.join(dirName, 'Scanner.py')
      
      traceResFileName   = os.path.join(tmpDir, 'trace.txt')
      parserResFileName  = os.path.join(tmpDir, 'Parser.py')
      scannerResFileName = os.path.join(tmpDir, 'Scanner.py')
      
      class Test(unittest.TestCase):
         maxDiff=None
         def setUpClass():
            print(" ".join(('Running test:', name)))
            with subprocess.Popen(
               [
                  "python3",
                  "-m", self._compiler, "-agfjs", '-O', tmpDir, testFileName
               ],
               shell=False,
               stdout=subprocess.PIPE
            ) as proc:
               __class__.output = proc.communicate()[0].decode("utf-8")
            os.makedirs(tmpDir, exist_ok=True)
         
         def testTrace(tself):
            assertFilesEqual(tself, traceFileName, traceResFileName)
         
         def testOutput(tself):
            with open(outputFileName, "rt", encoding="utf-8") as f:
               referenceOuput = f.read()
            tself.assertEqual(__class__.output, referenceOuput)

   def generateTests( self ):
      for name, isErrorTest in self._suite:
         test=self.generateTest(name, isErrorTest)
         test.__name__=name
         yield test
   def __call__(self):
      loader = unittest.TestLoader()
      runner = unittest.TextTestRunner()
      suite = unittest.TestSuite()

   def tearDownClass():
      deleteFiles(tmpDir+'/*.*')

      result = runner.run(suite)
      sys.exit(not result.wasSuccessful())


   def __call__(self):
      loader = unittest.TestLoader()
      suite = unittest.TestSuite()

      for testClass in self.generateTests():
         testcase = loader.loadTestsFromTestCase(testClass)
         suite.addTest(testcase)

      return suite


suite = [
   ( 'TestAlts',           False ),
   ( 'TestOpts',           False ),
   ( 'TestOpts1',          False ),
   ( 'TestIters',          False ),
   ( 'TestEps',            False ),
   ( 'TestAny',            False ),
   ( 'TestAny1',           False ),
   ( 'TestSync',           False ),
   ( 'TestSem',            False ), #  FIXME
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
   ( 'TestResOK',          False ), #  FIXME: add -x to _compiler args. Cross reference list
   ( 'TestResIllegal',     True  ), #  FIXME: add -x to _compiler args. Cross reference list
   ( 'TestCasing',         False )
]


def test_suite(suite):
   return CocoTester('Coco', 'py', suite)()


if __name__ == '__main__':
   unittest.main(defaultTest='test_suite')
