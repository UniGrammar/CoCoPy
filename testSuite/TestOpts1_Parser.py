#-------------------------------------------------------------------------
#Parser.py -- ATG file parser
#Compiler Generator Coco/R,
#Copyright (c) 1990, 2004 Hanspeter Moessenboeck, University of Linz
#extended by M. Loeberbauer & A. Woess, Univ. of Linz
#ported from Java to Python by Ronald Longo
#
#This program is free software; you can redistribute it and/or modify it
#under the terms of the GNU General Public License as published by the
#Free Software Foundation; either version 2, or (at your option) any
#later version.
#
#This program is distributed in the hope that it will be useful, but
#WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
#or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License
#for more details.
#
#You should have received a copy of the GNU General Public License along
#with this program; if not, write to the Free Software Foundation, Inc.,
#59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
#
#As an exception, it is allowed to write an extension of Coco/R that is
#used as a plugin in non-free software.
#
#If not otherwise stated, any source code generated by Coco/R (other than
#Coco/R itself) does not fall under the GNU General Public License.
#-------------------------------------------------------------------------*/

import sys

from Scanner import Token
from Scanner import Scanner
from Scanner import Position

class ErrorRec( object ):
   def __init__( self, l, c, s ):
      self.line   = l
      self.col    = c
      self.num    = 0
      self.str    = s


class Errors( object ):
   errMsgFormat = "file %(file)s : (%(line)d, %(col)d) %(text)s\n"
   eof          = False
   count        = 0         # number of errors detected
   fileName     = ''
   listName     = ''
   mergeErrors  = False
   mergedList   = None      # PrintWriter
   errors       = [ ]
   minErrDist   = 2
   errDist      = minErrDist
      # A function with prototype: f( errorNum=None ) where errorNum is a
      # predefined error number.  f returns a tuple, ( line, column, message )
      # such that line and column refer to the location in the
      # source file most recently parsed.  message is the error
      # message corresponging to errorNum.

   @staticmethod
   def Init( fn, dir, merge, getParsingPos, errorMessages ):
      Errors.theErrors = [ ]
      Errors.getParsingPos = getParsingPos
      Errors.errorMessages = errorMessages
      Errors.fileName = fn
      listName = dir + 'listing.txt'
      Errors.mergeErrors = merge
      if Errors.mergeErrors:
         try:
            Errors.mergedList = open( listName, 'wt', encoding="utf-8")
         except IOError:
            raise RuntimeError( '-- Compiler Error: could not open ' + listName )

   @staticmethod
   def storeError( line, col, s ):
      if Errors.mergeErrors:
         Errors.errors.append( ErrorRec( line, col, s ) )
      else:
         Errors.printMsg( Errors.fileName, line, col, s )

   @staticmethod
   def SynErr( errNum, errPos=None ):
      line,col = errPos if errPos else Errors.getParsingPos( )
      msg = Errors.errorMessages[ errNum ]
      Errors.storeError( line, col, msg )
      Errors.count += 1

   @staticmethod
   def SemErr( errMsg, errPos=None ):
      line,col = errPos if errPos else Errors.getParsingPos( )
      Errors.storeError( line, col, errMsg )
      Errors.count += 1

   @staticmethod
   def Warn( errMsg, errPos=None ):
      line,col = errPos if errPos else Errors.getParsingPos( )
      Errors.storeError( line, col, errMsg )

   @staticmethod
   def Exception( errMsg ):
      print(errMsg)
      sys.exit( 1 )

   @staticmethod
   def printMsg( fileName, line, column, msg ):
      vals = { 'file':fileName, 'line':line, 'col':column, 'text':msg }
      sys.stdout.write( Errors.errMsgFormat % vals )

   @staticmethod
   def display( s, e ):
      Errors.mergedList.write('**** ')
      for c in range( 1, e.col ):
         if s[c-1] == '\t':
            Errors.mergedList.write( '\t' )
         else:
            Errors.mergedList.write( ' ' )
      Errors.mergedList.write( '^ ' + e.str + '\n')

   @staticmethod
   def Summarize( sourceBuffer ):
      if Errors.mergeErrors:
         # Initialize the line iterator
         srcLineIter = iter(sourceBuffer)
         srcLineStr  = next(srcLineIter)
         srcLineNum  = 1

         try:
            # Initialize the error iterator
            errIter = iter(Errors.errors)
            errRec  = next(errIter)

            # Advance to the source line of the next error
            while srcLineNum < errRec.line:
               Errors.mergedList.write( '%4d %s\n' % (srcLineNum, srcLineStr) )

               srcLineStr = next(srcLineIter)
               srcLineNum += 1

            # Write out all errors for the current source line
            while errRec.line == srcLineNum:
               Errors.display( srcLineStr, errRec )

               errRec = next(errIter)
         except:
            pass

         # No more errors to report
         try:
            # Advance to end of source file
            while True:
               Errors.mergedList.write( '%4d %s\n' % (srcLineNum, srcLineStr) )

               srcLineStr = next(srcLineIter)
               srcLineNum += 1
         except:
            pass

         Errors.mergedList.write( '\n' )
         Errors.mergedList.write( '%d errors detected\n' % Errors.count )
         Errors.mergedList.close( )

      sys.stdout.write( '%d errors detected\n' % Errors.count )
      if (Errors.count > 0) and Errors.mergeErrors:
         sys.stdout.write( 'see ' + Errors.listName + '\n' )


class Parser( object ):
   _EOF = 0
   _a = 1
   _b = 2
   _c = 3
   _d = 4
   _e = 5
   _f = 6
   maxT = 7

   T          = True
   x          = False
   minErrDist = 2

   
   def __init__( self ):
      self.scanner     = None
      self.token       = None           # last recognized token
      self.la          = None           # lookahead token
      self.genScanner  = False
      self.tokenString = ''             # used in declarations of literal tokens
      self.noString    = '-none-'       # used in declarations of literal tokens
      self.errDist     = Parser.minErrDist

   def getParsingPos( self ):
      return self.la.line, self.la.col

   def SynErr( self, errNum ):
      if self.errDist >= Parser.minErrDist:
         Errors.SynErr( errNum )

      self.errDist = 0

   def SemErr( self, msg ):
      if self.errDist >= Parser.minErrDist:
         Errors.SemErr( msg )

      self.errDist = 0

   def Warning( self, msg ):
      if self.errDist >= Parser.minErrDist:
         Errors.Warn( msg )

      self.errDist = 0

   def Successful( self ):
      return Errors.count == 0;

   def LexString( self ):
      return self.token.val

   def LookAheadString( self ):
      return self.la.val

   def Get( self ):
      while True:
         self.token = self.la
         self.la = self.scanner.Scan( )
         if self.la.kind <= Parser.maxT:
            self.errDist += 1
            break
         
         self.la = self.token

   def Expect( self, n ):
      if self.la.kind == n:
         self.Get( )
      else:
         self.SynErr( n )

   def StartOf( self, s ):
      return self.set[s][self.la.kind]

   def ExpectWeak( self, n, follow ):
      if self.la.kind == n:
         self.Get( )
      else:
         self.SynErr( n )
         while not self.StartOf(follow):
            self.Get( )

   def WeakSeparator( self, n, syFol, repFol ):
      s = [ False for i in range( Parser.maxT+1 ) ]
      if self.la.kind == n:
         self.Get( )
         return True
      elif self.StartOf(repFol):
         return False
      else:
         for i in range( Parser.maxT ):
            s[i] = self.set[syFol][i] or self.set[repFol][i] or self.set[0][i]
         self.SynErr( n )
         while not s[self.la.kind]:
            self.Get( )
         return self.StartOf( syFol )

   def Test( self ):
      if (self.la.kind == 1):
         if (self.la.kind == 1):
            self.Get( )



   def Parse( self, scanner ):
      self.scanner = scanner
      self.la = Token( )
      self.la.val = ''
      self.Get( )
      self.Test()
      self.Expect(0)


   set = [
      [T,x,x,x, x,x,x,x, x]

   ]

   errorMessages = {
      0 : "EOF expected",
      1 : "a expected",
      2 : "b expected",
      3 : "c expected",
      4 : "d expected",
      5 : "e expected",
      6 : "f expected",
      7 : "??? expected",
   }


