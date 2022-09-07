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
	tempF = open(inputFile, "r")
	oldWayFile = tempF.read()
	tempF.close()
	print(oldWayFile)

parseArgs()