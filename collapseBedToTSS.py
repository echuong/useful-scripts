#!/usr/bin/env python
# encoding: utf-8
"""
collapseBedToTSS.py

Created by Edward Chuong on 2009-07-09.
Copyright (c) 2009 Baker Lab, Stanford University. All rights reserved.
"""
import sys
import getopt

help_message = '''
The help message goes here.
'''


class Usage(Exception):
	def __init__(self, msg):
		self.msg = msg


def main(argv=None):

	inFile = ''
	if argv is None:
		argv = sys.argv
	try:
		try:
			opts, args = getopt.getopt(argv[1:], "hi:v", ["help", "input="])
		except getopt.error, msg:
			raise Usage(msg)
	
		# option processing
		for option, value in opts:
			if option == "-v":
				verbose = True
			if option in ("-h", "--help"):
				raise Usage(help_message)
			if option in ("-i", "--input"):
				inFile = value
	
	except Usage, err:
		print >> sys.stderr, sys.argv[0].split("/")[-1] + ": " + str(err.msg)
		print >> sys.stderr, help_message
		return 2
		
	f = open(inFile)
	for line in f:
		if line.startswith('#') or line.startswith('track') or len(line.strip())==0: continue
		l = line.strip().split()
		strand = l[5]
		if strand == "-": 
			l[1] = str(int(l[2]) - 1)
		else:
			l[2] = str(int(l[1]) + 1)
		print "\t".join(l[0:6])

	f.close()


if __name__ == "__main__":
	sys.exit(main())
