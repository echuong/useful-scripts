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



class Usage(Exception):
	def __init__(self, msg):
		self.msg = msg


def main():
	global inBed, genomeFile
	defaultNumCPUs = 10

	parser = argparse.ArgumentParser()
	parser = argparse.ArgumentParser(description="Split bed files.")

	parser.add_argument("-i", "--inFile", help="input file")
	parser.add_argument("-o", "--outputDirectory", default="eachRep", help="output folder to contain all repeat bed files (one bed file per family)")


#	 parser.add_argument("y", type=int, help="the exponent")
	args = parser.parse_args()
	repDb = {}
	f
	
			
			
			
			
			
f = open(

   "outputs": [],
   "source": [
    "repDb = {}\n",
    "for line in f:\n",
    "    l = line.split(\"\\t\")\n",
    "    name = l[3]\n",
    "    if name not in repDb:\n",
    "        repDb[name] = []\n",
    "    repDb[name].append(line)\n",
    "f.close()\n",
    "\n",
    "\n",
    "for r in repDb:\n",
    "    fileName = r.split(\"#\")[0].replace(\"/\",\"_\") + \".bed\"\n",
    "    f = open(fileName, 'w')\n",
    "    \n",
    "    f.writelines(repDb[r])\n",
    "    f.close()"
	
	
	
	