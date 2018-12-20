#!/usr/bin/env python
# encoding: utf-8
"""
Tool for describing genes. uses a specific format of xref downloaded from ENSEMBL from BioMART

Gene version, Transcript version, Transcript type, Gene name, Gene description

fiji-2:~/software/scripts$ head ~/hg38/gencode.v27.xref.txt
Gene stable ID version	Transcript stable ID version	Transcript type	Gene name	Gene description
ENSG00000283891.1	ENST00000385229.3	miRNA	MIR628	microRNA 628 [Source:HGNC Symbol;Acc:HGNC:32884]
ENSG00000251931.1	ENST00000516122.1	snRNA	RNU6-871P	RNA, U6 small nuclear 871, pseudogene [Source:HGNC Symbol;Acc:HGNC:47834]
ENSG00000207766.1	ENST00000385032.1	miRNA	MIR626	microRNA 626 [Source:HGNC Symbol;Acc:HGNC:32882]


Tool for describing genes. uses a specific format of xref downloaded from ENSEMBL from BioMART


-i INPUT_FILE (use "-" for stdin)

-d REFERENCE_FILE (link to xref file)

-s ASSEMBLY (shorthand for linking to an assembly, eg hg38)


-c COLUMN_NUM (which 1-based column in input file to use, default is 1)



-p remove periods (in case version numbers don't match)
-t print transcript type 





"""

import sys
import getopt
help_message = '''

'''
opts = None



#hardcoded paths

#hg38_full_gencode_xref = "/scratch/Shares/chuong/genomes/hg38/gencode.v27.xref.txt"
# use new v28 for hg38
hg38_full_gencode_xref = "/scratch/Shares/chuong/genomes/hg38/gencode.v28.xref.txt"
mm10_full_gencode_xref = "/scratch/Shares/chuong/genomes/mm10/gencode.xref.txt"
canFam3_full_gencode_xref = "/scratch/Shares/chuong/genomes/canFam3/canFam3.ensembl.xref.txt"
bosTau8_full_gencode_xref = "/scratch/Shares/chuong/genomes/bosTau8/ENSEMBL.Bos_taurus.UMD3.1.xref.txt"



class Usage(Exception):
	def __init__(self, msg):
		self.msg = msg


def main(argv=None):

	import optparse
	parser = optparse.OptionParser(description=help_message)
	required = optparse.OptionGroup(parser, "Required arguments")
	optional = optparse.OptionGroup(parser, "Optional arguments")
	
	required.add_option('-i', '--input', help="input (use \"-\" or don't set for stdin)", dest='input', action='store', default="-", metavar='[input]')
	optional.add_option('-d', '--database', help="ENSEMBL/Gencode xref file", dest='geneIDfile', action='store', default="")
	required.add_option('-c', '--column', help="infile column where gene ID is located, 1-based [%default]", dest='col', default=1,  metavar='[# things]', type='int', action='store')
	optional.add_option('-s', '--species', help="Species assembly (hardcoded keywords: hg38, mm10, canFam3, bosTau8)", dest='speciesAssembly', action='store', default=None)
	
	optional.add_option('-a', '--all', help="Prints all lines from input regardless of match [%default]", dest="printAll", default=True, action='store_true')
	optional.add_option('-p', '--removeperiod', help="Removes text after periods (use for refseq) [%default]", dest="removePeriods", default=True, action='store_true')
	optional.add_option('-g', '--gene', help="Use ensembl gene IDs (eg ENSG00000197818.11) [%default]", dest="useGene", default=True, action='store_true')
	optional.add_option('-t', '--transcript', help="Use ensembl transcript IDs (eg ENST00000489787.1) [%default]", dest="useTranscript", default=False, action='store_true')

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

	deliminator = "\t"	
	
	# add in hardcoded other assemblies eg mouse
	if opts.speciesAssembly:
		if opts.speciesAssembly == "hg38":
			opts.geneIDfile = hg38_full_gencode_xref
		elif opts.speciesAssembly == "mm10":
			opts.geneIDfile = mm10_full_gencode_xref	
		elif opts.speciesAssembly == "canFam3":
			opts.geneIDfile = canFam3_full_gencode_xref	
		elif opts.speciesAssembly == "bosTau8":
			opts.geneIDfile = bosTau8_full_gencode_xref			
		
	# begin program
	with open(opts.geneIDfile, 'r') if opts.geneIDfile is not "-" else sys.stdin as f:
		gene2name = {}
		gene2desc = {}
		gene2line = {}
		gene2type = {}
		for line in f:
			if line.startswith('#') or len(line.strip())==0: continue
			l = line.strip().split(deliminator) 
			if l[0].startswith("Gene"): continue
			
			if opts.useTranscript:
				gene = l[1]
			elif opts.useGene:
				gene = l[0]
			else:
				gene = l[0] # backup

			
			if opts.removePeriods:
				gene = gene.split(".")[0]	
	
			gene2line[gene] = [line.strip()]
			if len(l) > 2:
				gene2type[gene] = l[2]
			else:
				gene2type[gene] = "-"
			if len(l) > 3: 
				gene2name[gene] = l[3]
			else: 
				gene2name[gene] = "-"
			
			if len(l) > 4:
				gene2desc[gene] = l[4]
			else:
				gene2desc[gene] = "-"
	
		
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
				print "\t".join(l) + "\t" + "\t".join([gene2name[gene], gene2desc[gene], gene2type[gene]])
			else:
				if opts.printAll:
					print "\t".join(l + ["", ""])
			
	

if __name__ == "__main__":
	sys.exit(main())
