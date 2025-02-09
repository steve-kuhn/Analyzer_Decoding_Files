import sys
import os
import numpy as np
import getopt

# This debug variable allows the initialization beak signal glitch that occurs to be 
# "filtered" out to avoid the skewing of data. The "filter" simply ignores any
# beak signals that occur before 0s (CAM UP).
AEW_DEBUG = 1

def usage():
    print("extract_hold_time_stats.py -r <rotor name> [-o]")
    print(" -r <rotor name> Full prefix name of rotor")
    print(" -o Flag to indicate output file should be created")
    sys.exit(0)

argc = len(sys.argv)
if argc < 2:
    usage()

# Parse the command line options
try:
    opts, args = getopt.getopt(sys.argv[1:], "r:o")
except getopt.error:
    usage()
    sys.exit(2)
    
# Process options
rotor_name = ""
CREATE_OUTPUT_FILE = False
     
for o, a in opts:
    if o == "-r":
        rotor_name = a
    elif o == "-o":
        CREATE_OUTPUT_FILE = True

if rotor_name == "":
    usage()

rotor_name = rotor_name.replace("Exports", "Reports")

infilename = rotor_name + "_BeakTimingOut.txt"

all_holdTime = []

if infilename == "":
    print("No file name detected.")
    sys.exit(1)

print("\nFile Name: %s" % infilename)

try:
    fileIn = open(infilename, 'rt')
except:
    print("Could not open input file %s" % (infilename))
    sys.exit(1)

line = fileIn.readline()
line = fileIn.readline() # Get passed the File: etc. line

## Collect hold times
holdT = []
while "Done" not in line:
    line = [l.strip() for l in line.split()]
    holdT.append(float(line[1]))
    line = fileIn.readline()

while "Global Cuvette Delay" not in line:
    line = fileIn.readline()

## Workaround to get past the next 3 lines
for i in range(3):
    line = fileIn.readline()

holdTime = []
## Collect values

while line:
    line = fileIn.readline()
    if len(line) < 11:
        break
    line = [l.strip() for l in line.split()]
    holdTime.append( float(line[5]) - float(line[4]) )

## "Filter" the list to remove any beak values that occur before 0s
if AEW_DEBUG:
    temp = np.min(holdT)
    temp_idx = holdT.index(temp)
    del holdTime[temp_idx]

## Find statistics
avg = np.mean(holdTime)
min = np.min(holdTime)
max = np.max(holdTime)
std = np.std(holdTime)

print("Hold Time Stats\n")

print("     Hold Time")
print("     ---------")
print("Min  %9.3f" % (min))
print("Max  %9.3f" % (max))
print("Avg  %9.3f" % (avg))
print("Std  %9.3f" % (std))

if CREATE_OUTPUT_FILE:
    base = os.path.basename(rotor_name)
    basefile = os.path.splitext(base)[0]
    prefix = rotor_name.replace(base, "")
    prefix = prefix.replace("Exports", "Reports")
    abspath = os.path.abspath(prefix)
    outpath = abspath.replace("Exports", "Reports")
    if not os.path.exists(outpath):
        os.mkdir(outpath)

    outfilename = outpath + "\\" + basefile + "_HoldTimeStatsOut.txt"
    fileOut = open(outfilename, 'wt')

    fileOut.write("Hold Time Stats\n\n")
    fileOut.write("File Name: %s\n\n" % infilename)

    fileOut.write("     Hold Time\n")
    fileOut.write("     ---------\n")
    fileOut.write("Min  %9.3f\n" % (min))
    fileOut.write("Max  %9.3f\n" % (max))
    fileOut.write("Avg  %9.3f\n" % (avg))
    fileOut.write("Std  %9.3f\n" % (std))

    fileOut.close()


all_holdTime += holdTime


# avg = np.mean(all_holdTime)
# min = np.min(all_holdTime)
# max = np.max(all_holdTime)
# std = np.std(all_holdTime)

# print("\nCombined Statistics\n")

# print("     Hold Time")
# print("     ---------")
# print("Min  %9.3f" % (min))
# print("Max  %9.3f" % (max))
# print("Avg  %9.3f" % (avg))
# print("Std  %9.3f" % (std))

# fileOut.write("     Hold Time")
# fileOut.write("     ---------")
# fileOut.write("Min  %9.3f" % (min))
# fileOut.write("Max  %9.3f" % (max))
# fileOut.write("Avg  %9.3f" % (avg))
# fileOut.write("Std  %9.3f" % (std))