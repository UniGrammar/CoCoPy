"""Trace.py -- Trace file generation routines"""

__copyright__ = """
Compiler Generator Coco/R,
Copyright (c) 1990, 2004 Hanspeter Moessenboeck, University of Linz
extended by M. Loeberbauer & A. Woess, Univ. of Linz
ported from Java to Python by Ronald Longo
improved and refactored by KOLANICH

This program is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation; either version 2, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program.  If not, see <https://www.gnu.org/licenses/>.

As an exception, it is allowed to write an extension of Coco/R that is used as a plugin in non-free software.

If not otherwise stated, any source code generated by Coco/R (other than Coco/R itself) does not fall under the GNU General Public License.
"""  # pylint: disable=duplicate-code

import os
from pathlib import Path


class Trace:
	__slots__ = ("trace", "curLine")

	def __init__(self) -> None:
		self.trace = []
		self.curLine = []

	@staticmethod
	def formatString(s: str, w: int) -> str:  # not used?
		"""Returns a string with a minimum length of |w| characters
		the string is left-adjusted if w < 0 and right-adjusted otherwise"""
		assert isinstance(s, str)
		assert isinstance(w, int)
		b = " " * (abs(w) - len(s))
		return b + s if w >= 0 else s + b

	def Write(self, s: str, w: int = None):  # not used?
		"""writes a string with a maximum length of |w| characters"""
		assert isinstance(s, str)
		assert isinstance(w, int) or (w is None)
		if w is None:
			self.curLine.append(s)
		else:
			self.curLine.append(self.formatString(s, w))

	def WriteLine(self, s: str = None, w: int = None):  # not used?
		assert isinstance(s, str) or (s is None)
		assert isinstance(w, int) or (w is None)
		if self.curLine:
			self.trace.append("".join(self.curLine))
			self.curLine = []

		if s is not None:
			if w is not None:
				self.trace.append(self.formatString(s, w))
			else:
				self.trace.append(s)
