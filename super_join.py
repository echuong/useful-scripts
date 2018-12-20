#!/usr/bin/env python
# encoding: utf-8
"""
A better join tool for describing genes

"""

import sys
import getopt
help_message = '''


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
	
	required.add_option('-i', '--input', help="input", dest='input', action='store', default="-", metavar='[input]')
	required.add_option('-d', '--database', help="geneID file", dest='geneIDfile', action='store')
	required.add_option('-c', '--column', help="infile ID column, 1-based [%default]", dest='col', default=1,  metavar='[# things]', type='int', action='store')
	required.add_option('-x', '--xrefcolumn', help="database column, 1-based", dest='xcol', default=1,  metavar='[# things]', type='int', action='store')

	optional.add_option('-a', '--all', help="Prints all lines from input regardless of match [%default]", dest="printAll", default=False, action='store_true')
	optional.add_option('-p', '--removeperiod', help="Removes periods (use for refseq) [%default]", dest="removePeriods", default=True, action='store_true')

	parser.add_option_group(required)
	parser.add_option_group(optional)
	global opts
	(opts, args) = parser.parse_args()
	
	mandatories = ["input", "geneIDfile"]
	for m in mandatories:
		if not opts.__dict__[m]:
			print "\n*** Mandatory option \"%s\" missing!\n" % m
			print help_message
			sys.exit(1)

	deliminator = "\t"	
	# begin program
	with open(opts.geneIDfile, 'r') if opts.geneIDfile is not "-" else sys.stdin as f:
		gene2name = {}
		gene2desc = {}
		gene2line = {}
		for line in f:
			if line.startswith('#') or len(line.strip())==0: continue
			l = line.strip().split(deliminator) 
			if l[0].startswith("Ensembl"): continue
			gene = l[opts.xcol-1]
			
			if opts.removePeriods:
				gene = gene.split(".")[0]	
	
			gene2line[gene] = [line.strip()]
	
		
	with open(opts.input, 'r') if opts.input is not "-" else sys.stdin as f:
		for line in f:
			#if line.startswith('#') or len(line.strip())==0: continue
			l = line.strip().split("\t")
			if len(l)<opts.col: 
				print "\t".join(l)
				continue
			gene = l[opts.col-1]
			if opts.removePeriods:
				gene = gene.split(".")[0]
			if gene in gene2line:
				print "\t".join(l + gene2line[gene])
			else:
				if opts.printAll:
					print "\t".join(l + ["", ""])
			
	

if __name__ == "__main__":
	sys.exit(main())
