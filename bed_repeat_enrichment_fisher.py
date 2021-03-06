#!/usr/bin/env python2 

import pandas as pd
import numpy as np
import pybedtools
import sys
import os
#from pathlib import Path


import glob
import multiprocessing
import argparse

# co-opting pybedtools FisherOutput function to parse fisher output
class FisherOutput(object):
	def __init__(self, s, **kwargs):
		"""
		fisher returns text results like::

			# Contingency Table
			#_________________________________________
			#			| not in -b	   | in -b		  |
			# not in -a | 3137160615   | 503		  |
			#	  in -a | 100		   | 46			  |
			#_________________________________________
			# p-values for fisher's exact test
			left	right	two-tail	ratio
			1.00000 0.00000 0.00000 2868973.922

		"""

		table = {
			'not in -a': {
				'not in -b': None,
				'in -b': None
			},
			'in -a': {
				'not in -b': None,
				'in -b': None,
			},
		}
		self.text = s
		lines = s.splitlines()
		for i in lines:
			if 'not in -a' in i:
				_, in_b, not_in_b, _= i.strip().split('|')
				table['not in -a']['not in -b'] = int(not_in_b)
				table['not in -a']['in -b'] = int(in_b)

			if '    in -a' in i:
				_, in_b, not_in_b, _ = i.strip().split('|')
				table['in -a']['not in -b'] = int(not_in_b)
				table['in -a']['in -b'] = int(in_b)
		self.table = table
		left, right, two_tail, ratio = lines[-1].split()
		self.left_tail = float(left)
		self.right_tail = float(right)
		self.two_tail = float(two_tail)
		self.ratio = float(ratio)


	def __str__(self):
		return self.text

	def __repr__(self):
		return '<%s at %s>\n%s' % (self.__class__.__name__, id(self), self.text)


def calculateRepeatFisher(repeatFile):
	r = repeatFile.split("/")[-1].split(".bed")[0]
	cmd = "bedtools fisher -a \"%s\" -b \"%s\" -g %s" % (inBed.fn, repeatFile, genomeFile)
	f = os.popen(cmd, 'r')
	outputString = f.read()
	f.close()
	#print(outputString)
	a = FisherOutput(outputString)
	out = {}
	out["name"] = r
	out["left_tail"] = a.left_tail
	out["right_tail"] = a.right_tail
	out["two_tail"] = a.two_tail
	out["ratio"] = a.ratio	  
	out["overlap"] = a.table['in -a']['in -b']	 
	if out["ratio"] == np.inf:
		out["ratio"] = 1e4
	elif out["ratio"] == 0:
		out["ratio"] = 1e-4
	out["expected"] = float(out["overlap"]) / out["ratio"]
	out["log2ratio"] = np.log2(out["ratio"])

	# the bedtools output was seemingly switching the tails randomly. this keeps p values near 0 = enrichment, and values near 1 = depletion
	if out['ratio'] >= 1:
		out["one_p"] = out["two_tail"] / 2.
	else:
		out["one_p"] = 1 - (out["two_tail"] / 2.)
	return out	  

	

def main():
	global inBed, genomeFile	
	defaultNumCPUs = 10
	#defaultRepeatsDirectory='/home/edwardc/hg19/repeats/eachRep'
	#defaultGenome="/home/edwardc/hg19/hg19.chrom.sizes"
	#repeatFile="/data/genomes/Homo_sapiens/hg19/repeats/hg19.repname.bed"
	parser = argparse.ArgumentParser()
	parser = argparse.ArgumentParser(description="Calculate enrichment of input bed file to each repeat family (using bedtools Fisher). Also calculates an \"expected\" value based on the given ratio. Outputs a results table. Uses folder of repeat files (some names with slashes may be modified).")
	#group = parser.add_mutually_exclusive_grup()
	#group.add_argument("-v", "--verbose", action="store_true")
	#group.add_argument("-q", "--quiet", action="store_true")
	parser.add_argument("-i", "--inFile", help="input file")

	parser.add_argument("-r", "--repeatsDirectory", default=None, help="folder with all repeat bed files to test (one bed file per family)")
	parser.add_argument("-s", "--species", default="hg38", help="mm10, hg19, or hg38 for presets for genome and repeatsDirectory file")

	parser.add_argument("-g", "--genome", default=None, help="genome contig size file")
	parser.add_argument("-p", "--numCPUs", type=int, default=defaultNumCPUs, help="number of CPUs to use")

#	 parser.add_argument("y", type=int, help="the exponent")
	args = parser.parse_args()
	

	
	if args.species == "hg19":
		genomeFile = "/scratch/Shares/chuong/genomes/hg19/hg19.chrom.sizes"
		repeatsDirectory = "/scratch/Shares/chuong/genomes/hg19/repeats/eachRep"
	if args.species == "hg38":
		genomeFile = "/scratch/Shares/chuong/genomes/hg38/hg38.chrom.sizes"
		repeatsDirectory = "/scratch/Shares/chuong/genomes/hg38/repeats/eachRep"
	if args.species == "mm10":
		genomeFile = "/scratch/Shares/chuong/genomes/mm10/mm10.chrom.sizes"
		repeatsDirectory = "/scratch/Shares/chuong/genomes/mm10/repeats/eachRep"	
	if args.genome: genomeFile = args.genome
	if args.repeatsDirectory: repeatsDirectory = args.repeatsDirectory		
		
	inBed = pybedtools.BedTool(args.inFile).sort()
	repeatFiles = glob.glob(repeatsDirectory + '/*.bed')

	pool = multiprocessing.Pool(processes=args.numCPUs)
	rep = pool.map(calculateRepeatFisher, repeatFiles)
	repDF = pd.DataFrame.from_records(rep,index="name")
	repDF = repDF[['overlap', 'expected', 'ratio', 'log2ratio', 'left_tail', 'right_tail', 'two_tail', 'one_p']].sort_values("one_p")
	repDF.to_csv(sys.stdout, sep="\t")
	pybedtools.cleanup()
	

if __name__ == "__main__":
	sys.exit(main())
	# defaults
