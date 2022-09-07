import sys

# FIXME Ability to convert to other formats instead of just PC
def parseArgs():
	if len(sys.argv) == 1: # No arguments supplied
		inputFile = input("Enter location of input file: ")
		outputFile = input("Enter name of output file: ")
		startConversion(inputFile, outputFile)
	elif len(sys.argv) == 3:
		startConversion(sys.argv[1], sys.argv[2])
	else:
		print("YOU TWONK")

def startConversion(inputFile, outputFile):
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
	elif header == "waypoint": # PC
		print("PC format detected")
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
			except ValueError:
				print("Invalid waypoint co-ords")

parseArgs()