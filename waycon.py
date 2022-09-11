import sys, argparse

def parseArgs():
	# Do things interactively if no arguments supplied
	if len(sys.argv) == 1:
		inputFile = input("Enter location of input file: ")
		outputFile = input("Enter name of output file: ")
		# Choose waypoint format (PC, PSP, BETA)
		wayFormat = ""
		while not (wayFormat in ("PC", "PSP", "BETA")):
			print("Select desired waypoint format: ")
			print("[PC/PSP/BETA]")
			wayFormat = input().upper()
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
	wayFormat = args.format.upper()
	# Enforce proper waypoint format selection
	if not (wayFormat in ("PC", "PSP", "BETA")):
		raise ValueError("Invalid format specified")
	# Begin conversion process
	startConversion(inputFile, outputFile, wayFormat)

def startConversion(inputFile, outputFile, wayFormat):
	# Correct the file extension
	if not(outputFile.lower().endswith(".way")) and wayFormat != "BETA":
		outputFile += ".way"
	# Read in old waypoints
	with open(inputFile, "r") as tempF:
		oldWayFile = tempF.readlines()

	# Check format
	header = oldWayFile[0].strip("\n")
	if header == "Waypoint": # PSP
		print("PSP format detected")
		if wayFormat == "PSP":
			raise ValueError("Already in PSP format!")
		wayArray = parseOLD(oldWayFile, "PSP", 15, 2, 14)
	elif header == "waypoint": # PC
		print("PC format detected")
		if wayFormat == "PC":
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
				if wayFormat == "BETA":
					raise ValueError("Already in BETA format!")
				wayArray = parseOLD(oldWayFile, "BETA", 10, 0, 7)
			except ValueError:
				print("Invalid waypoint co-ords")
	
	# Save waypoint file in the desired format
	if wayFormat == "BETA":
		saveBETA(wayArray, outputFile)
	if wayFormat == "PSP":
		savePSP(wayArray, outputFile)
	if wayFormat == "PC":
		savePC(wayArray, outputFile)
	print("Conversion complete")
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
	tempArray = [] # Temporarily stores waypoint fields
	wayArray = [] # Array of waypoints
	# Start processing waypoints
	for i, line in enumerate(oldWayFile):
		# Accept whatever for now, we'll yeet the fluff once waypoint is read
		if line.strip() != "":
			tempArray.append(line.strip())
		if line.strip() == "}": # Reached end of that waypoint
			# Check if door target present
			if tempArray[4][:4] == "door":
				tempArray[4] = tempArray[4][6:]
			else:
				tempArray.insert(4,"") # No door so keep it blank
			# Store waypoint fields in dictionary
			waydict = {
				"origin": tempArray[3][8:],
				"id": tempArray[2][4:],
				"door": tempArray[4],
				# Replace links to waypoint 0
				"targets": ["255" if value == "0" else value for value in tempArray[7:-2]]
			}
			# Replace id 0
			if waydict["id"] == "0":
				waydict["id"] = "255" # I sure do hope nobody has this many waypoints
			tempArray.clear() # Clear temporary array for next waypoint
			wayArray.append(waydict) # Add waypoint to array
	return wayArray

def saveBETA(wayArray, outputFile):
	print("WARNING: NZP Beta is limited to 4 links per waypoint")
	with open(outputFile, "w") as outF:
		for waypoint in wayArray:
			outF.write(waypoint["origin"] + "\n")
			outF.write(waypoint["id"] + "\n")
			# Only do 1st four links (Mapper would need to redo waypoints)
			numTargets = len(waypoint["targets"])
			# Pad out list with 0 for empty links
			if numTargets < 4:
				for i in range(4-numTargets):
					waypoint["targets"].append("0")
			# Warn user if waypoint has too many links
			if numTargets > 4:
				print(f"Waypoint {waypoint['id']} has more than 4 links")
			# Write waypoint links to file
			[outF.write(waypoint["targets"][i] + "\n") for i in range(4)]
			# Fill out 'owner' fields just in case
			[outF.write(waypoint["targets"][i] + "\n") for i in range(4)]

def savePSP(wayArray, outputFile):
	# Come to think of it, who needs more than 8 links anyways?
	#print("WARNING: PSP format is limited to 8 links per waypoint")
	with open(outputFile, "w") as outF:
		for waypoint in wayArray:
			outF.write("Waypoint\n{\n") # Header
			outF.write(f"origin = {waypoint['origin']}\n")
			outF.write(f"id = {waypoint['id']}\n")
			outF.write(f"special = {waypoint['door']}\n")
			# Only do 1st eight links (Mapper may need to tweak waypoints)
			numTargets = len(waypoint["targets"])
			# Pad out list with '' for empty links
			if numTargets < 8:
				for i in range(8-numTargets):
					waypoint["targets"].append("")
			# Warn user if waypoint has too many links
			if numTargets > 8:
				print(f"Waypoint {waypoint['id']} has more than 8 links")
			# Write waypoint links to file
			outF.write(f"target = {waypoint['targets'][0]}\n")
			[outF.write(f"target{i+1} = {waypoint['targets'][i]}\n") for i in range(1,8)]
			outF.write("}\n\n") # Footer of waypoint

def savePC(wayArray, outputFile):
	with open(outputFile, "w") as outF:
		for waypoint in wayArray:
			outF.write("waypoint\n{\n") # Header
			outF.write(f" id: {waypoint['id']}\n")
			outF.write(f" origin: {waypoint['origin']}\n")
			# Include door if present
			if waypoint['door'] != "":
				outF.write(f" door: {waypoint['door']}\n")
			outF.write(" targets:\n [\n") # Header
			numTargets = len(waypoint["targets"])
			# Write waypoint links to file
			[outF.write(f"  {waypoint['targets'][i]}\n") for i in range(numTargets)]
			outF.write(" ]\n}\n\n") # Footer of waypoint

parseArgs()
