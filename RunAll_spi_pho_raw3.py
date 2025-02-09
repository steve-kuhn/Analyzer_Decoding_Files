import sys
import os
import math
import subprocess

argc = len(sys.argv)
if argc == 1:
    file_list = [os.path.join(dirpath, filename) for dirpath, _, filenames in os.walk('.') for filename in filenames if "_Group0.csv" in filename]
if argc > 2:
    print("Too many arguments.")
    sys.exit(0)
elif argc == 2:
    file_list = [sys.argv[1]]
    
file_count = 1
total_files = len(file_list)

for infilename in file_list:

    if infilename == "":
        print("No file name detected.")
        continue

    rotor_name = infilename.replace("_Group0.csv", "")

    # try:
    #     fileIn = open(infilename, 'rt')
    # except:
    #     print("Could not open input file %s" % (infilename))
    #     continue #sys.exit(1)
    
    # outfilename = os.path.splitext(infilename)[0] + "Data.txt"

    print("(%d/%d) Running: spi_pho_raw3.py for %s" % (file_count, total_files, infilename))
    # print("        Output file: %s" % outfilename)
    # fileOut = open(outfilename, 'wt')
    p = subprocess.Popen(["python3", "C:\\Users\\awong\\Documents\\Analyzer_Decoding_Files\\spi_pho_raw3.py", "-r", rotor_name, "-a", "Serial"])
    p.wait()
    # result = subprocess.run(["python3", "C:\\Users\\awong\\Documents\\Analyzer_Decoding_Files\\spi_pho_raw3.py", "-r", rotor_name, "-a", "Serial"], capture_output=False, text=True)
    # if result != 0:
    #     print("Could not decode this file")

    file_count += 1