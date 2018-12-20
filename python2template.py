#!/usr/bin/env python
# encoding: utf-8
"""
Description
"""

import sys
#from numpy import *
help_message = '''

Program description
Python 2 template script


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
	optional.add_option('-n', '--number', help="some number [%default]", dest='someNumber', default=1000,  metavar='[# things]', type='int', action='store')
	optional.add_option('-d', '--debug', help="turns on debug mode [%default]", dest="debug", default=False, action='store_true')

	parser.add_option_group(required)
	parser.add_option_group(optional)
	global opts
	(opts, args) = parser.parse_args()
	
	mandatories = ["input"]
	for m in mandatories:
		if not opts.__dict__[m]:
			print "\n*** Mandatory option \"%s\" missing!\n" % m
			print help_message
			sys.exit(1)
    
    
    # to open the -i FILE or stdin
	#with open(opts.input, 'r') if opts.input is not "-" else sys.stdin as f:
	

if __name__ == "__main__":
	sys.exit(main())
