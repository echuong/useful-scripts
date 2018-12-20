#!/usr/bin/env python
# encoding: utf-8


import sys
import os
import shutil

#from numpy import *
help_message = '''

Program description
Hub Manager for uploading bigbed, bam, and bigwig files 

autodetects files based on name:
bigwig: *.bw, *.bigwig
bigbed: *.bb, *.bigbed
bam: *.bam

Notes

hubload.py --input input.bam --supertrack projectname --trackFile /path/to/speciesAssembly/trackDb.txt


Required arguments;
--input <bam/bigwig/bigbed file>
--trackDb </path/to/trackDb.txt>


Filled in by default:
bigDataUrl (determined relative to trackDb path)
type (filled by filename)


Optional settings:
--name <track name> (default basename of input, must be unique)
--shortLabel <short label> (default basename of input)
--longLabel <description> (default basename of input)
--color <RRR,GGG,BBB> (0-255 values default 15,15,150 = blue)
--visiblity <hide/dense/squish/pack/full> (default full)
--priority <value> (can be a float, 0.0 being first, default = 1)
--alwaysZero <value> (default on)
--supertrack <groupname> (default "ungrouped") 

Options for bigwig
--maxHeightPixels <max:default:min> (default 64:20:10)
--viewLimits <min:max> (default 0:1 good for TFs, but histones may need 0:5)
--autoScale <on/off> (default on)

Other options
--debug (dry run; no copying or modifying of files)


hubload.py will:
1. Reads in the target trackDb.txt groups and stanzas
2. Create a new stanza for input file, ensures no same-name collisions
3. Copy over the input file into the appropriate folder in your hub (including bam.bai index files)
3. Appends entry to trackDb.txt

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
	
	required.add_option('-i', '--input', help="input", dest='input', action='store', default=None)
	required.add_option('-t', '--trackDb', help="trackDb file", dest='trackDb', action='store', default=None)
	optional.add_option('-n', '--name', help="name [%default]", dest='name', default=None, action='store')
	optional.add_option('-s', '--shortLabel', help="shortLabel [%default]", dest='shortLabel', default=None, action='store')
	optional.add_option('-l', '--longLabel', help="longLabel [%default]", dest='longLabel', default=None, action='store')
	optional.add_option('-a', '--autoScale', help="autoScale [%default]", dest='autoScale', default="off", action='store')
	optional.add_option('-c', '--color', help="color [%default]", dest='color', default="15,15,150", action='store')
	optional.add_option('-v', '--visibility', help="visibility [%default]", dest='visibility', default=None, action='store')
	optional.add_option('-w', '--viewLimits', help="viewLimits [%default]", dest='viewLimits', default="0:1", action='store')
	optional.add_option('-m', '--maxHeightPixels', help="viewLimits [%default]", dest='maxHeightPixels', default="64:20:10", action='store')
	optional.add_option('-z', '--alwaysZero', help="alwaysZero [%default]", dest='alwaysZero', default="on", action='store')
	optional.add_option('-p', '--priority', help="priority [%default]", dest='priority', default="1", action='store')
	optional.add_option('-g', '--supertrack', help="supertrack [%default]", dest='supertrack', default="ungrouped", action='store')


	optional.add_option('-d', '--debug', help="turns on debug mode (no file modification) [%default]", dest="debug", default=False, action='store_true')

	parser.add_option_group(required)
	parser.add_option_group(optional)
	global opts
	(opts, args) = parser.parse_args()
	
	mandatories = ["input", "trackDb"]
	for m in mandatories:
		if not opts.__dict__[m]:
			print "\n*** Mandatory option \"%s\" missing!\n" % m
			print help_message
			sys.exit(1)
			
	if opts.debug:
		print "Debug mode on: no actual copying or writing will take place"

	allSuperTracks = {}
	allTracks = {}
	allTrackNames = set() # save track names to ensure no collisions
	
	# First read in current trackDb (this is currently overkill but may be useful for future options to remove entries by script)
	f = open(opts.trackDb, 'r')
	currentStanza = {}
	for line in f:
		l = line.strip().split(" ")
		
		if l == ['']: continue
		
		
		# new stanza
		if l[0] == "track":
			# no track collisions
			trackName = " ".join(l[1:])
			allTrackNames.add(trackName)
			
			# process previous track
			if len(currentStanza) > 0:
				if "superTrack" in currentStanza.keys():
					allSuperTracks[currentStanza["track"]] = currentStanza
				else:
					allTracks[currentStanza["track"]] = currentStanza
			currentStanza = {}
				
		currentStanza[l[0]] = " ".join(l[1:])
	f.close()
	
	
	linesToPrint = [] # lines to eventually append to trackDb.txt
	
	# Check if the supertrack already exists, if not, defines it
	if opts.supertrack:
		if opts.supertrack not in allSuperTracks.keys(): # track already exists
			print "Supertrack %s not yet defined, will add track definition." % opts.supertrack
		
			linesToPrint.append("track %s" % opts.supertrack)
			linesToPrint.append("superTrack on show")
			linesToPrint.append("shortLabel %s" % opts.supertrack)
			linesToPrint.append("longLabel %s" % opts.supertrack)
			linesToPrint.append("")
		else: 
			print "Supertrack %s already defined." % opts.supertrack
					
	
	# Parsing the input file name
	baseFullFileName = os.path.basename(opts.input)
	if not os.path.isfile(os.path.abspath(opts.input)):
		print "Input file %s doesn't exist. Exiting." % os.path.abspath(opts.input)
		sys.exit(0)
	basename = os.path.splitext(baseFullFileName)[0]
	extension = os.path.splitext(baseFullFileName)[1]
	
	# track file
	trackDirectory = os.path.dirname(opts.trackDb)
	# set some defaults
	if opts.name is None:
		opts.name = basename
	if opts.longLabel is None:
		opts.longLabel = basename
	if opts.shortLabel is None:
		opts.shortLabel = basename
	
	# No same-name collisions allowed
	if opts.name in allTrackNames:
		print "Error: track named \"%s\" already exists in track file %s. Exiting.." % (opts.name, opts.trackDb)
		sys.exit(0)
	
	
	# Parse bigwig files
	if extension in [".bw", ".bigwig"]:
		
		# set default visibility
		if not opts.visibility: opts.visibility="full"
		# make a bw folder if it doesn't exist
		
		supertrackFolder = opts.supertrack.replace(" ", "_") # replace spaces with underscores
		relativeNewDest = supertrackFolder + "/bw" 
		newDest = trackDirectory + "/" + relativeNewDest
		
		if not opts.debug:		
			if not os.path.exists(newDest):
				print "Making folder %s" % newDest
				os.makedirs(newDest)
			else:
				print "Folder %s exists" % newDest
		
			# copy to bigwig folder	
			print "Copying %s into %s" % (os.path.abspath(opts.input), newDest)		
			shutil.copy2(os.path.abspath(opts.input), newDest)
			
		else:
			print "Would have copied %s into %s" % (os.path.abspath(opts.input), newDest)		
		
		bigDataUrl = relativeNewDest + "/" + baseFullFileName
		trackType = "bigWig"
		linesToPrint.append("track %s" % opts.name)
		linesToPrint.append("bigDataUrl %s" % bigDataUrl)
		linesToPrint.append("shortLabel %s" % opts.shortLabel)
		linesToPrint.append("longLabel %s" % opts.longLabel)
		linesToPrint.append("type %s" % trackType)
		linesToPrint.append("autoScale %s" % opts.autoScale)
		linesToPrint.append("alwaysZero %s" % opts.alwaysZero)
		linesToPrint.append("maxHeightPixels %s" % opts.maxHeightPixels)
		linesToPrint.append("viewLimits %s" % opts.viewLimits)
		linesToPrint.append("color %s" % opts.color)
		linesToPrint.append("visibility %s" % opts.visibility)
		linesToPrint.append("priority %s" % opts.priority)
		linesToPrint.append("parent %s" % opts.supertrack)
		linesToPrint.append("")
		
	# Parse bam files
	if extension in [".bam"]:
		# make a bam folder if it doesn't exist)
		# set default visibility
		if not opts.visibility: opts.visibility="dense"		
		# expected bam file
		expectedBAMindex = opts.input + ".bai"
		
		if not os.path.isfile(os.path.abspath(expectedBAMindex)):
			print "BAM Index file missing (expected %s). Exiting." % os.path.abspath(expectedBAMindex)
			sys.exit(0)
		
		supertrackFolder = opts.supertrack.replace(" ", "_") # replace spaces with underscores
		relativeNewDest = supertrackFolder + "/bam"  # used in trackDb
		newDest = trackDirectory + "/" + relativeNewDest # used for copying
		
		if not opts.debug:		
			if not os.path.exists(newDest):
				print "Making folder %s" % newDest
				os.makedirs(newDest)
			else:
				print "Folder %s exists" % newDest
		
			# copy bam
			print "Copying %s into %s" % (os.path.abspath(opts.input), newDest)		
			shutil.copy2(os.path.abspath(opts.input), newDest)
			
			# copy bam index
			print "Copying %s into %s" % (os.path.abspath(expectedBAMindex), newDest)		
			shutil.copy2(os.path.abspath(expectedBAMindex), newDest)					
		else:
			print "Would have copied %s and %s into %s" % (os.path.abspath(opts.input), os.path.abspath(expectedBAMindex), newDest)		
			
		bigDataUrl = relativeNewDest + "/" + baseFullFileName
		trackType = "bam"
		linesToPrint.append("track %s" % opts.name)
		linesToPrint.append("bigDataUrl %s" % bigDataUrl)
		linesToPrint.append("shortLabel %s" % opts.shortLabel)
		linesToPrint.append("longLabel %s" % opts.longLabel)
		linesToPrint.append("type %s" % trackType)
		linesToPrint.append("pairEndsByName .") # maybe optional, only for paired, will this cause problems on SE reads?
		linesToPrint.append("bamColorMode strand")
		linesToPrint.append("visibility %s" % opts.visibility)
		linesToPrint.append("priority %s" % opts.priority)
		linesToPrint.append("parent %s" % opts.supertrack)
		linesToPrint.append("")		

	# Parse bigBed files
	if extension in [".bb", ".bigbed"]:
	# set default visibility
		if not opts.visibility: opts.visibility="full"
		# make a bb folder if it doesn't exist
		supertrackFolder = opts.supertrack.replace(" ", "_") # replace spaces with underscores
		relativeNewDest = supertrackFolder + "/bb" # used in trackDb
		newDest = trackDirectory + "/" + relativeNewDest # used for copying
		
		if not opts.debug:		
			if not os.path.exists(newDest):
				print "Making folder %s" % newDest
				os.makedirs(newDest)
			else:
				print "Folder %s exists" % newDest
		
			# copy bam
			print "Copying %s into %s" % (os.path.abspath(opts.input), newDest)		
			shutil.copy2(os.path.abspath(opts.input), newDest)
							
		else:
			print "Would have copied %s into %s" % (os.path.abspath(opts.input), newDest)		
			
		bigDataUrl = relativeNewDest + "/" + baseFullFileName
		trackType = "bigBed"
		linesToPrint.append("track %s" % opts.name)
		linesToPrint.append("bigDataUrl %s" % bigDataUrl)
		linesToPrint.append("shortLabel %s" % opts.shortLabel)
		linesToPrint.append("longLabel %s" % opts.longLabel)
		linesToPrint.append("type %s" % trackType)
		linesToPrint.append("color %s" % opts.color)
		linesToPrint.append("labelFields name")
		linesToPrint.append("darkerLabels on")
		linesToPrint.append("visibility %s" % opts.visibility)
		linesToPrint.append("priority %s" % opts.priority)
		linesToPrint.append("parent %s" % opts.supertrack)
		linesToPrint.append("")				


	# write files to trackDb
	
	if not opts.debug:
		print "Appended the following to %s\n--\n\n" % opts.trackDb
	else:
		print "Would have appended the following to %s\n--\n\n" % opts.trackDb
	
	f = open(opts.trackDb, 'a')
	if not opts.debug:
		f.write("\n") # add a new line before writing
	for l in linesToPrint:
		if not opts.debug:
			f.write(l + "\n")
		print l
	f.close()
	


if __name__ == "__main__":
	sys.exit(main())
