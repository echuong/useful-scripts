#!/usr/bin/env python
# encoding: utf-8
"""
ed.py

Created by Edward Chuong on 2009-03-10.
Copyright (c) 2009 Baker Lab, Stanford University. All rights reserved.
"""

import sys
import os
from numpy import *
import errno


# takes 2 iterables a/b, returns dictionary of sets: ['and', 'or', 'xor', 'a', 'b', 'a_only', 'b_only'] 
def getSetCategories(a_in, b_in):		
	a = set(a_in)
	b = set(b_in)
	setCategories = dict()
	setCategories['a_only'] = a - b
	setCategories['b_only'] = b - a
	setCategories['and'] = a & b
	setCategories['or'] = a | b
	setCategories['xor'] = a ^ b
	setCategories['a'] = a
	setCategories['b'] = b
	return setCategories
		

def openAnything(source):
	if source =='-': return sys.stdin
	else: return open(source)

	
def matchLists(testList, refList):
	testSet = set(testList)
	refSet = set(refList)
	numShared = len( testSet & refSet )
	return numShared

def createFolder(dirname):
	try:
	    # os.makedirs will also create all the parent directories
	    os.makedirs(dirname)
	except OSError, err:
	    if err.errno == errno.EEXIST:
	        if os.path.isdir(dirname):
	            print "Error: " + dirname + "directory already exists"
	        else:
	            print "Error: " + dirname + " already exists, but not a directory"
	            raise # re-raise the exception
	    else:
	        raise

def baseName(filename):
	return filename.split("/")[-1]

#keyType = "name" or "id"
def bedFileToDict(file, key_by_number=False):
	bedDict = dict()
	f = open(file)
	i = 0
	for line in f:
		if (line.startswith("track")) or (line.startswith("#") or len(line.strip())==0): continue
		l = line.strip().split()
		
		if len(l) < 3: raise Exception, "Not a proper BED file (expecting >= 3 columns)"
		
		l[1] = int(l[1])
		l[2] = int(l[2])
		
		i += 1
		# key by "i" or by name. make this parametized
		if (len(l) < 3) or key_by_number: key = i
		else: key = l[3]
		bedDict[key] = l
	return bedDict
	f.close()




def distanceBetweenRanges(a, b):
	if (len(a) != 2) or (len(b) != 2): raise Exception, "Error in distanceBetweenRanges"
	minDistance = sys.maxint
	if (a[0] <= b[0] <= a[1]) or (a[0] <= b[1] <= a[1]):
		distance = 0
	else: 
		distances = [a[0] - b[0], a[0] - b[1], a[1] - b[0], a[1] - b[1]]
		for d in distances:
			if abs(d) < abs(minDistance): minDistance = d
			
	return minDistance



def dictToBedFile(inDict, outFile):
	w = open(outFile, 'w')
	for record in inDict:
		r = [str(x) for x in inDict[record]]
		w.write("\t".join(r) + "\n")
	w.close()

def runOverlapSelect(select, infile, outfile, opt=""):
	
	cmd = " ".join(["overlapSelect", select, infile, outfile, opt])

	if outfile == "stdout":
		f = os.popen(cmd, 'r')
		lines = f.readlines()
		f.close()
		return lines
	else:
		os.system(cmd)
		return None

#chr10   102486594       102488039       635     chr10   102487029       102490113       6955
def parseMergedOverlap(mergeFile):
	f = open(mergeFile)
	
	select2in = dict()
	in2select = dict()
	for line in f:
		if line.startswith('#') or len(line.strip())==0: continue
		l = line.strip().split()
		
		if len(l) < 5: raise Exception, "Mergeoverlap error"
		colPerBed = len(l)/2
		nameCol = colPerBed-1
		
		inID = l[nameCol] 
		selectID = l[colPerBed + nameCol]
		
		if inID in in2select:
			in2select[inID].append(selectID)
		else:
			in2select[inID] = [selectID]

		if selectID in select2in:
			select2in[selectID].append(inID)
		else:
			select2in[selectID] = [inID]
	f.close()
	return (select2in, in2select)



def convertIDPairsToDict(idFile):

	f = open(idFile)
	a2b = dict()
	b2a = dict()		

	for line in f:
		if line.startswith('#') or len(line.strip())==0: continue
		l = line.strip().split()
		
		if len(l) != 2: raise Exception, "convertIDPairsToDict error"
		
		a = l[0]
		b = l[1]

		if a in a2b:
			a2b[a].append(b)
		else:
			a2b[a] = [b]
		
		if b in b2a:
			b2a[b].append(a)
		else:
			b2a[b] = [a]

	f.close()
	return (a2b, b2a)
	

def deleteFolder(folderName):
	if folderName == "/": return 0
	
	try:
		for root, dirs, files in os.walk(folderName, topdown=False):
		    for name in files:
		        os.remove(os.path.join(root, name))
		    for name in dirs:
		        os.rmdir(os.path.join(root, name))
		os.rmdir(folderName)	
		return 1
	except:
		raise Exception, "Couldn't delete folder " + folderName	
		




def expandBedFile(inBED, outBED=None, radius=0, upRadius=None, downRadius=None, useTSSOnly=False):

	if upRadius is None: upRadius = radius
	if downRadius is None: downRadius = radius
	
	upRadius = int(upRadius)
	downRadius = int(downRadius)
	
	f = open(inBED)
	o = 0
	if outBED is not None: o = open(outBED, 'w')
	
	for line in f:
		if line.startswith("#"): continue
		
		l = line.strip().split()
		if len(l) < 3: continue
		
		
		strand = '+'
		newStart = start = int(l[1])
		newEnd = end = int(l[2])
		
		# if the BED file does not have strand info (occurs on the 6th column)
		if len(l) >= 6:
			strand = l[5]
		
		if useTSSOnly:
			if strand == '+':
				newStart = start - upRadius
				newEnd = start + downRadius
			else:
				newStart = end - downRadius
				newEnd = end + upRadius
		else:
			if strand == '+':
				newStart = start - upRadius
				newEnd = end + downRadius
			else:
				newStart = start - downRadius
				newEnd = end + upRadius 
			
			
		if newStart < 0: newStart = 0
		
		l[1] = str(newStart)
		l[2] = str(newEnd)
		if not o: print "\t".join(l)
		else: o.write("\t".join(l) + "\n")
	o.close()			
	f.close()
		
		
		
		
# genes in gene list must be same format as those in expression files (kgID usually)
# returns a dict keyed by filename, with a (numMatching, numRefs) tuple
def correlateWithExpression(geneList, expressionFiles):
	matches = dict()
	for refFile in expressionFiles:
		f = open(refFile)
		refList = [x.strip() for x in f.readlines()]
		f.close()
		#refFileName = refFile.split('/')[-1]
		numRefs = len(refList)
		numMatching = matchLists(geneList, refList)
		matches[refFile] = (numMatching, numRefs)
	return matches
	



def getGeneBounds(geneFile, tssOnly, iso2canonical=None):
	genome = dict()
	g = open(geneFile)
	for line in g:
		l = line.strip().split()
		(chr, start, end, name) = l[0:4]
		if iso2canonical:
			name = iso2canonical[name]
		score = 0
		strand = '+'
		if len(l) > 4: 
			score = l[4]
			if len(l) > 5: strand = l[5]
		
		if chr not in genome:
			genome[chr] = []
			
		if tssOnly:
			tss = start
			if strand == '-': tss = end
			genome[chr].append((int(tss), name))
		else:
			genome[chr].append((int(start), name))
			genome[chr].append((int(end), name))

	g.close()
	
	# create parallel arrays
	for chr in genome: 
		genome[chr].sort(cmp=lambda x,y: x[0]-y[0])
		coords = []
		names = []
		for x in genome[chr]:
			coords.append(x[0])
			names.append(x[1])
		coordsA = array(coords)
		namesA = array(names)
		genome[chr] = (coordsA, namesA)
		
	return genome


def getClosestIx(x, l):
	rightIx = l.searchsorted(x)
	leftIx = 0
	if rightIx > 0: leftIx = rightIx - 1
	if rightIx >= len(l): rightIx = len(l)-1
	deltaRight = x-l[rightIx]
	deltaLeft = x-l[leftIx]
	if abs(deltaRight) < abs(deltaLeft):
		return (rightIx, deltaRight)
	else:
		return (leftIx, deltaLeft)
		
def getNearestGenes(inFile=None,
				geneFile = "/data/Users/echuong/hesc/ref_files/hg18.knownCanonical.bed",
				genome = None,
				radius = 1000000,
				tssOnly = True,
				statsOutput = False,
				fullOutput = True,
				negOutput = False,
				printOutput = False
				):
	if (not genome) and (not geneFile): raise Exception()
	
	if not genome:
		genome = getGeneBounds(geneFile, tssOnly)

	inRecs = bedFileToDict(inFile, key_by_number=True) # b/c scores are nonunique and i use them in the name field
	numRecsAssigned = 0
	genes = []
	negRecs = []
	dbOutput = []
	for rec in inRecs:
		r = inRecs[rec]
		name = ""
		[chr, start, end] = r[0:3]
		if chr not in genome: continue
		
		recString= chr + ":" + str(start) + "-" + str(end)
		if len(r) > 3: name = r[3]
		recString = recString + ":" + name
		coordList = genome[chr][0]
		geneList = genome[chr][1]
		closest = ""
		closeIx = 0		
		

		
		(startIx, deltaStart) = getClosestIx(start, coordList)
		(endIx, deltaEnd) = getClosestIx(end, coordList)
		
		
		# first should check if a TSS falls within this coordinate
		
		overlapTSS = False
		for ix in range (startIx, endIx + 1):
			if (start <= coordList[ix] <= end):
				closest = geneList[ix]
				recString = recString + ":0"
				dbOutput.append((closest, recString))
				overlapTSS = True
		if overlapTSS: continue


		# Otherwise, test each boundary

		minDistance = sys.maxint

		deltaMin = sys.maxint
		if abs(deltaStart) < abs(deltaEnd): 
			closeIx = startIx
			deltaMin = deltaStart
		else:
			closeIx = endIx
			deltaMin = deltaEnd
		
		closest = geneList[closeIx]
		# see if peak is within a gene region
		if not tssOnly:
			if deltaMin > 0:  # region is on the right side of nearest gene coordinate, look +1
				if len(geneList) > closeIx+1:
					if geneList[closeIx] == geneList[closeIx+1]:
						deltaMin = 0
			else:	# region is on left side of a gene coordinate, look -1
				if closeIx > 0:
					if geneList[closeIx] == geneList[closeIx-1]:
						deltaMin = 0
		if radius:
			if abs(deltaMin) <= radius: 
				numRecsAssigned += 1
				if not negOutput: 
					if fullOutput: genes.append("\t".join([str(x) for x in r]) + "\t" + closest + "\t" + str(deltaMin))
					else: genes.append(closest)
					#dbOutput.append((closest, deltaMin))
					recString = recString + ":" + str(deltaMin)
					dbOutput.append((closest, recString))

			else: 
				if negOutput: negRecs.append("\t".join([str(x) for x in r]))
		else:
			if deltaMin == sys.maxint: # should never happen..
				if negOutput: negRecs.append("\t".join([str(x) for x in r]))
			else:
				numRecsAssigned += 1
				if not negOutput: 
					if fullOutput: genes.append("\t".join([str(x) for x in r]) + "\t" + closest + "\t" + str(deltaMin))
					else: genes.append(closest)
					#dbOutput.append((closest, deltaMin))
					recString = recString + ":" + str(deltaMin)

					dbOutput.append((closest, recString))

	
	if printOutput:
		if statsOutput:
			print "#### Getting nearest genes ####"
			print "Input file: " + inFile
			if radius:
				print "Maximum radius (bp): %d" % (radius)
			else:
				print "Maximum radius (bp): none specified"
			print "Total records: %d" % (len(inRecs))
			print "Records matched to genes: %d" % (numRecsAssigned)
			print "Records unmatched to genes: %d" % (len(inRecs) - numRecsAssigned)
	
	
		else:
			if negOutput:
				print "\n".join(negRecs)
			else:
				if not fullOutput: genes = set(genes)
				print "\n".join(genes)

	return dbOutput











	
	
def padSpaces(num, char=' '):
	space = ""
	for i in range(0,num): space = space + char
	return space
	
	
	
	
	
	
	
	
	
	
