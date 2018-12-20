#!/usr/bin/env python
# encoding: utf-8
"""
untitled.py

Created by Edward Chuong on 2011-08-08.
Copyright (c) 2011 Baker Lab, Stanford University. All rights reserved.
"""

import sys
import getopt
from chromaDB import *
from numpy import *
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
	required.add_option('-g', '--geneID', help="geneID file", dest='geneIDfile', action='store', default="/data/genomes/Homo_sapiens/hg38/hg38.xref.txt", metavar='')
	required.add_option('-c', '--column', help="infile ID column, 1-based [%default]", dest='col', default=1,  metavar='[# things]', type='int', action='store')
	required.add_option('-x', '--xrefcolumn', help="xref column, 1-based (1 is kgid, 2 is genbank mRNA, 6 is refseq mRNA, 7 is refseq prot) [%default]", dest='xcol', default=1,  metavar='[# things]', type='int', action='store')
	optional.add_option('-d', '--debug', help="turns on debug mode [%default]", dest="debug", default=False, action='store_true')
	optional.add_option('-p', '--removeperiod', help="Removes periods (use for refseq) [%default]", dest="removePeriods", default=False, action='store_true')

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
	
	# begin program
	f = openAnything(opts.geneIDfile)
	gene2name = {}
	gene2desc = {}
	for line in f:
		if line.startswith('#') or len(line.strip())==0: continue
		l = line.strip().split("\t")
		if l[0].startswith("Ensembl"): continue
		if len(l) < 3:
			gene = l[0]
			name = ""
			desc = ""
		else:
			gene = l[0]
			rna = l[1]
			
			
			# adding opt
			gene = l[opts.xcol-1]
			
			name = l[4]
			refseq = l[5]
			protrefseq = l[6]
			desc = l[7]
			
		gene2name[gene] = name
		gene2desc[gene] = desc
		
		

	f.close()
	f = openAnything(opts.input)
	for line in f:
		#if line.startswith('#') or len(line.strip())==0: continue
		l = line.strip().split("\t")
		
		gene = l[opts.col-1]
		if opts.removePeriods:
			gene = gene.split(".")[0]
		if gene in gene2name:
			print "\t".join(l + [gene2name[gene], gene2desc[gene]])
		else:
			print "\t".join(l + ["-", "-"])

	f.close()

if __name__ == "__main__":
	sys.exit(main())
