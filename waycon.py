#!/bin/env python
import sys, argparse

def parseArgs():
	# Do things interactively if no arguments supplied
	if len(sys.argv) == 1:
		inputFile = input("Enter location of input file: ")
		outputFile = input("Enter name of output file: ")
		# Choose waypoint format (PC, PSP, BETA)
		wayFormat = ""
		while not (wayFormat.upper() in ("PC", "PSP", "BETA")):
			print("Select desired waypoint format: ")
			print("[PC/PSP/BETA]")
			wayFormat = input()
		# Begin conversion process
		startConversion(inputFile, outputFile, wayFormat)

	# Handle command line arguments 'properly'
	parser = argparse.ArgumentParser(description='Converts NZP Waypoints between formats')
	parser.add_argument("input", type=str, help="Location of input file")
	parser.add_argument("output", type=str, help="Name of output file")
	parser.add_argument("format", type=str, help="Desired waypoint format")
	args = parser.parse_args()
	inputFile = args.input
	outputFile = args.output
	wayFormat = args.format
	# Enforce proper waypoint format selection
	if not (wayFormat.upper() in ("PC", "PSP", "BETA")):
		raise ValueError("Invalid format specified")
	# Begin conversion process
	startConversion(inputFile, outputFile, wayFormat)

def startConversion(inputFile, outputFile, wayFormat):
	# Correct the file extension
	if not(outputFile.lower().endswith(".way")):
		outputFile += ".way"
	# Read in old waypoints
	with open(inputFile, "r") as tempF:
		oldWayFile = tempF.readlines()

	# Check format
	header = oldWayFile[0].strip("\n")
	if header == "Waypoint": # PSP
		print("PSP format detected")
		if wayFormat.upper() == "PSP":
			raise ValueError("Already in PSP format!")
		wayArray = parseOLD(oldWayFile, "PSP", 15, 2, 14)
	elif header == "waypoint": # PC
		print("PC format detected")
		if wayFormat.upper() == "PC":
			raise ValueError("Already in PC format!")
		wayArray = parsePC(oldWayFile)
	else: # Check if BETA or just random crap
		where = header.strip("'").split() # Split xyz
		# Should look something like [-40.5, 12.2, 8.0]
		if len(where) != 3:
			print("Invalid waypoint file") # Clearly not co-ords
		else:
			try: # Check if they're actual numbers
				for i in range(len(where)):
					float(where[i])
				print("BETA format detected")
				if wayFormat.upper() == "BETA":
					raise ValueError("Already in BETA format!")
				wayArray = parseOLD(oldWayFile, "BETA", 10, 0, 7)
			except ValueError:
				print("Invalid waypoint co-ords")
	
	# Print out waypoint for now I guess
	for waypoint in wayArray:
		print(waypoint)
	exit(0)

def parseOLD(oldWayFile, detFormat, numLines, startL, endL):
	tempArray = [] # Temporarily stores waypoint fields
	wayArray = [] # Array of waypoints
	# Value for empty fields
	if detFormat == "BETA":
		blank = "0"
	else:
		blank = ""
	# Start processing waypoints
	for i, line in enumerate(oldWayFile):
		relativeLineNum = (i+1)%numLines
		# Ignore header stuff
		if relativeLineNum > startL and relativeLineNum < endL:
			# Add data from field to temporary array
			if detFormat == "PSP":
				tempArray.append(line[line.index('=')+2:].strip())
			else:
				tempArray.append(line.strip())
		if relativeLineNum == endL: # Reached end of that waypoint
			# NZP Beta 1.1 doesn't have special door targets
			if detFormat == "BETA":
				tempArray.insert(2,"")
			# Store waypoint fields in dictionary
			waydict = {
				"origin": tempArray[0],
				"id": tempArray[1],
				"door": tempArray[2],
				# Remove empty targets
				"targets": [value for value in tempArray[3:] if value != blank]
			}
			tempArray.clear() # Clear temporary array for next waypoint
			wayArray.append(waydict) # Add waypoint to array
	return wayArray

def parsePC(oldWayFile):
	return ["Notsee", "Zombies", "Portable", "2"]

parseArgs()
