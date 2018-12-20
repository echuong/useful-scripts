#!/usr/bin/env python
# encoding: utf-8
"""
Created by Edward Chuong on 2012-01-18.
"""

import sys
import getopt
from chromaDB import *
from numpy import *
help_message = '''

Program description

Notes


'''
opts = None

class Usage(Exception):
	def __init__(self, msg):
		self.msg = msg


def main(argv=None):

	import optparse
	parser = optparse.OptionParser(description=help_message)
	required = optparse.OptionGroup(parser, "Required arguments")
	optional = optparse.OptionGroup(parser, "Optional arguments")
	
	required.add_option('-i', '--input', help="input", dest='input', action='store', default=None, metavar='[input]')
	required.add_option('-f', '--filter', help="filter", dest='filter', action='store', default=None, metavar='[input]')
	optional.add_option('-n', '--number', help="some number [%default]", dest='someNumber', default=1000,  metavar='[# things]', type='int', action='store')
	optional.add_option('-v', '--v', help="turns on inverse mode (like grep -v) [%default]", dest="inverse", default=False, action='store_true')
	optional.add_option('-d', '--debug', help="turns on debug mode [%default]", dest="debug", default=False, action='store_true')
	optional.add_option('-c', '--case', help="case sensitive [%default]", dest="caseSensitive", default=False, action='store_true')
	optional.add_option('-w', '--wholeColumn', help="whole column must match [%default]", dest="wholeColumn", default=True, action='store_true')

	parser.add_option_group(required)
	parser.add_option_group(optional)
	global opts
	(opts, args) = parser.parse_args()
	
	caseSensitive = opts.caseSensitive
	mandatories = ["input"]
	for m in mandatories:
		if not opts.__dict__[m]:
			print "\n*** Mandatory option \"%s\" missing!\n" % m
			print help_message
			sys.exit(1)
	
	
	# begin program
	
	f = openAnything(opts.filter)
	grepList = set()
	for line in f:
		if line.startswith('#') or len(line.strip())==0: continue
		l = line.strip()
		if not caseSensitive:
			l = l.lower()
		grepList.add(l)
			
		
		
	
	f.close()
	f = openAnything(opts.input)
	for line in f:
		if line.startswith('#') or len(line.strip())==0: continue
		l = line.strip()

		printMe = False

			
		if opts.wholeColumn:
			splitLine = l.split()
			for column in splitLine:
				for grepper in grepList:
					if not caseSensitive:
						column_test = column.lower()
					else:
						column_test = column
					if column_test == grepper:
						printMe = True
						break
				if printMe:
					break
		else:
			if not caseSensitive:
				l_test = l.lower()
			else:
				l_test = l
			for grepper in grepList:
				if l_test.find(grepper) > -1:
					printMe = True
					break
		
		if opts.inverse:
			if not printMe:
				print l
		else:
			if printMe:
				print l
				
		
		
		
		
	
	f.close()
	
	

if __name__ == "__main__":
	sys.exit(main())
