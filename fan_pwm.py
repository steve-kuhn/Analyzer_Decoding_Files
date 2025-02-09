#
# spi_u18_raw3.py
#
# Decode LA capture U18 ADS1258 and spindle motor
#

"""
ADC SYS U18
ch0   RTR_TEMP_IN
ch1   ANALOG_GND
ch2   TOP_TEMP
ch3   BOT_TEMP
ch4   TOP_CUR
ch5   BOT_CUR
ch6   FAN_SENSE
ch7   MTR_CUR
ch8   BC_SIGNAL
ch9   BC_TH
ch10  BC_CUR
ch11  CUV_SIGNAL
ch12  CUV_TH
ch13  CUV_CUR
ch14  -10V
ch15  +10V

V = Vref * (code / 0x780000
"""

import string
import sys
import getopt
import time
import os
import math
import numpy as np
import struct

T0 = -600.0

DEBUG1 = 0
DEBUG2 = 0
DEBUG3 = 0

DEBUG_R1 = 0 
DEBUG_T1 = 0 
DEBUG_RXTX = 0

"""
Group1 Capture of 3/8/23 

 0 SPI_ADC_CS#
 1 SPI_CLK
 2 SPI_MISO			=> MISO for ADC, TEMP
 3 SPI_MOSI			=> MOSI for ADC, DACA, DACB
 4 SPI_DACB_CS#
 5 SPI_DACA_CS#
 6 ADC_START
 7 SPI_TEMP_CS#
 8 ADC_DRDY
 9 BC_PULSE
10 FAN_PWM
11 CAM_UP
12 QUADB
13 QUADA
14 MOTOR_TX
15 MOTOR_RX
"""

IDX_TIME	= 0
IDX_ADC_CS	= 1
IDX_CLK		= 2
IDX_MISO	= 3
IDX_MOSI	= 4
IDX_DACB_CS	= 5
IDX_DACA_CS	= 6

IDX_TEMP_CS	= 8


IDX_FAN_PWM	= 11
IDX_CAM_UP	= 12
IDX_QUADB	= 13
IDX_QUADA	= 14
IDX_TX		= 15
IDX_RX		= 16

VREF = 4.096
# V = Vref * (code / 0x780000


#------------------------------------------------------------------------------------------------------------------------#

ENCODER_CPR = 360
ENCODER_POLARITY = 1
RAD_PER_SEC_TO_RPM = 9.5493
RAD_PER_SLOT = 2.0 * math.pi / ENCODER_CPR

#------------------------------------------------------------------------------------------------------------------------#

# class parse_Quad:
# 	def __init__(self):
# 		self.state = 0
# 		self.thisTime = 0.0
# 		self.prevTime = -2000.0
# 		self.direction = 0
# 		self.countEncA = 0
# 		self.Entries = []

# 	def update(self, cv, ev):
# 		# Begin

# 		# Rising edge on QuadA
# 		if (ev[IDX_QUADA] == 1) and (cv[IDX_QUADA] == 1):
# 			self.thisTime = cv[IDX_TIME]

# 			deltaT = self.thisTime - self.prevTime
# 			# filter out glitches
# 			if deltaT > 0.000001:
# 				speed = RAD_PER_SLOT/deltaT

# 				if cv[IDX_QUADB] == 1:
# 					# Counter-Clockwise
# 					self.direction = 1
# 					dirString = "CCW"
# 					speedRpm = -1.0 * speed * RAD_PER_SEC_TO_RPM
# 				else:
# 					# Clockwise
# 					self.direction = 0
# 					dirString = "CW"
# 					speedRpm = speed * RAD_PER_SEC_TO_RPM

# 				self.Entries.append((self.thisTime, speedRpm))

# 				self.countEncA += 1
# 				self.prevTime = self.thisTime

# 	def get_entries(self):
# 		return self.Entries

# #------------------------------------------------------------------------------------------------------------------------#

# class parse_DacA:
# 	def __init__(self):
# 		self.state = 0
# 		self.addr = 0
# 		self.pwr = 0
# 		self.spd = 0
# 		self.val = 0
# 		self.channel = {0: "Top_Set", 1: "Bot_Set", 2: "Cam_Cl", 3: "Dwr_Cl"}

# 	def show(self, begin, id, mosiBytes, misoBytes):
# 		self.addr = (mosiBytes[0] & 0xc0) >> 6
# 		self.pwr = (mosiBytes[0] & 0x20) >> 5
# 		self.spd = (mosiBytes[0] & 0x10) >> 4
# 		self.val = ((mosiBytes[0] & 0x0f) << 4) + ((mosiBytes[1] & 0xf0) >> 4)
# 		lenMosi = len(mosiBytes)
# 		lenMiso = len(misoBytes)
# 		fileOut.write ("DacA w  %10.6f %1d %1d %1d %-11s %3d (" % \
# 				(begin, self.addr, self.pwr, self.spd, self.channel[self.addr], self.val))
# 		for m in range (lenMosi):
# 			fileOut.write (" %2.2x" % (mosiBytes[m]))
# 		fileOut.write (" )\n")

# #------------------------------------------------------------------------------------------------------------------------#

# class parse_DacB:
# 	def __init__(self):
# 		self.state = 0
# 		self.addr = 0
# 		self.pwr = 0
# 		self.spd = 0
# 		self.val = 0
# 		self.channel = {0: "BC_Control", 1: "BC_Th", 2: "Cuv_Control", 3: "Cuv_Th"}

# 	def show(self, begin, id, mosiBytes, misoBytes):
# 		self.addr = (mosiBytes[0] & 0xc0) >> 6
# 		self.pwr = (mosiBytes[0] & 0x20) >> 5
# 		self.spd = (mosiBytes[0] & 0x10) >> 4
# 		self.val = ((mosiBytes[0] & 0x0f) << 4) + ((mosiBytes[1] & 0xf0) >> 4)
# 		lenMosi = len(mosiBytes)
# 		lenMiso = len(misoBytes)
# 		fileOut.write ("DacB w  %10.6f %1d %1d %1d %-11s %3d (" % \
# 				(begin, self.addr, self.pwr, self.spd, self.channel[self.addr], self.val))
# 		for m in range (lenMosi):
# 			fileOut.write (" %2.2x" % (mosiBytes[m]))
# 		fileOut.write (" )\n")

# #------------------------------------------------------------------------------------------------------------------------#

# class parse_TempSense:
# 	def __init__(self):
# 		self.state = 0
# 		self.sign = 0
# 		self.val = 0
# 		self.temperature = 0.0

# 	def show(self, begin, id, mosiBytes, misoBytes):
# 		self.sign = (misoBytes[0] & 0x80) >> 7
# 		self.val = (misoBytes[0] << 5) + (misoBytes[1] >> 3)
# 		self.temperature = float(self.val) * 0.0625
# 		lenMosi = len(mosiBytes)
# 		lenMiso = len(misoBytes)
# 		fileOut.write ("Temp r  %10.6f %1d %5.1f (" % (begin, self.sign, self.temperature))
# 		for m in range (lenMiso):
# 			fileOut.write (" %2.2x" % (misoBytes[m]))
# 		fileOut.write (" )\n")

# #------------------------------------------------------------------------------------------------------------------------#

# class parse_adc:
# 	def __init__(self):
# 		self.state = 0
# 		self.cmdNames = {0x00:"Chan Read Dir", 0x20: "Chan Read Reg", 0x60: "Write Reg"}
# 		self.chanNames = {0: "RTR_TEMP", 1: "ANALOG_GND", 2: "TOP_TEMP", 3: "BOT_TEMP", \
# 						  4: "TOP_CUR", 5: "BOT_CUR", 6: "FAN_SENSE", 7: "MTR_CUR", \
# 						  8: "BC_SIGNAL", 9: "BC_TH", 10: "BC_CUR", 11: "CUV_SIGNAL", \
# 						  12: "CUV_TH", 13: "CUV_CUR", 14: "-10V", 15: "+10V"}
# 		self.cmd = ""
# 		self.multi = 0
# 		self.reg = 0

# 	def conv_voltage(self, v):
# 		val_twos = -(v & 0x800000) | (v & 0x7fffff)
# 		val_volt = (VREF * float(val_twos)) / 0x780000
# 		if abs(val_volt) < 0.000000999:
# 			val_volt = 0.0
# 		return val_volt

# 	def conv_decimal(self, v):
# 		val_twos = -(v & 0x800000) | (v & 0x7fffff)
# 		val_dec = val_twos
# 		#if abs(val_dec) < 0.000000999:
# 		#	val_dec = 0.0
# 		return val_dec

# 	def show(self, begin, id, mosiBytes, misoBytes):
# 		self.cmd = mosiBytes[0] & 0xe0
# 		self.multi = mosiBytes[0] & 0x10
# 		self.reg = mosiBytes[0] & 0x0f
# 		lenMosi = len(mosiBytes)
# 		lenMiso = len(misoBytes)

# 		fileOut.write("ADC_SYS %10.6f %5d " % (begin, id))
# 		fileOut.write("%-13s " % (self.cmdNames[self.cmd]))

# 		#
# 		# Write Reg
# 		if self.cmd == 0x60:
# 			startReg = self.reg
# 			fileOut.write("  ")
# 			for j in range(lenMosi - 1):
# 				fileOut.write("%1d: %2.2x " % (startReg, mosiBytes[1+j]))
# 				startReg += 1
			
# 			# verbose
# 			if verbosity & 1:
# 				fileOut.write(" -> ")
# 				fileOut.write("[%2d] " % (lenMosi))	
# 				for i in range(len(mosiBytes)):
# 					fileOut.write ("0x%2.2x " % (mosiBytes[i]))
# 			fileOut.write("\n")	

# 		#
# 		# Read Data Reg
# 		if self.cmd == 0x20:
# 			status = misoBytes[1] & 0xe0
# 			chan = (misoBytes[1] & 0x1f) - 8
# 			value = (misoBytes[2] * 65536) + (misoBytes[3] * 256) + misoBytes[4]

# 			if status == 0x80:
# 				status_str = "*"
# 			else:
# 				status_str = "!"
# 			chan_str = self.chanNames[chan]
# 			volts = self.conv_voltage(value)
# 			dvalue = self.conv_decimal(value)	# decimal value
# 			fileOut.write("%s %-10s % 9.6f V 0x%6.6x %6d D" % (status_str, chan_str, volts, value, dvalue))

# 			# verbose
# 			if verbosity & 1:
# 				fileOut.write(" (%6.6x) <- " % (value))
# 				fileOut.write("[%2d] " % (lenMiso))	
# 				for i in range(len(misoBytes)):
# 					fileOut.write ("0x%2.2x " % (misoBytes[i]))
# 			fileOut.write("\n")	

# 		#
# 		# Read Data Direct
# 		if self.cmd == 0x00:
# 			status = misoBytes[0] & 0xe0
# 			chan = (misoBytes[0] & 0x1f) - 8
# 			value = (misoBytes[1] * 65536) + (misoBytes[2] * 256) + misoBytes[3]

# 			if status == 0x80:
# 				status_str = "*"
# 			else:
# 				status_str = "!"
# 			chan_str = self.chanNames[chan]
# 			volts = self.conv_voltage(value)
# 			dvalue = self.conv_decimal(value)	# decimal value
# 			fileOut.write("%s %-10s % 9.6f V 0x%6.6x %6d D" % (status_str, chan_str, volts, value, dvalue))

# 			# verbose
# 			if verbosity & 1:
# 				fileOut.write(" (%6.6x) <- " % (value))
# 				fileOut.write("[%2d] " % (lenMiso))	
# 				for i in range(len(misoBytes)):
# 					fileOut.write ("0x%2.2x " % (misoBytes[i]))
# 			fileOut.write("\n")	

# #------------------------------------------------------------------------------------------------------------------------#

# class parse_spi:
# 	def __init__(self, I_CS, I_CLK, I_MOSI, I_MISO, PH_CLK, pp):
# 		self.state = 0
# 		self.mosiBytes = []
# 		self.misoBytes = []
# 		self.numBytes = 0
# 		self.byteIdx = 0
# 		self.begin = 0.0
# 		self.end = 0.0
# 		self.id = 0
# 		self.countBits = 0
# 		self.pp = pp
# 		self.idx_CS = I_CS
# 		self.idx_CLK= I_CLK
# 		self.idx_MOSI = I_MOSI
# 		self.idx_MISO = I_MISO
# 		self.PH_CLK = PH_CLK

# 	def update(self, cv, ev):
# 		if ev[self.idx_CS] == 1 and cv[self.idx_CS] == 0:
# 			self.begin = cv[0]
# 			self.state = 1
# 			self.a = 0x00
# 			self.b = 0x00
# 			if DEBUG2:
# 				print ("Start %f" % self.begin)

# 		if self.state == 1 and ev[self.idx_CLK] == 1 and cv[self.idx_CLK] == self.PH_CLK:
# 			self.a = ((self.a<<1) | cv[self.idx_MOSI])
# 			self.b = ((self.b<<1) | cv[self.idx_MISO])
# 			self.countBits += 1
# 			if DEBUG2:
# 				print ("bits %d %d %d %d" % (self.byteIdx, self.countBits, cv[self.idx_MOSI], cv[self.idx_MISO]))
# 			if self.countBits == 8:
# 				self.countBits = 0
# 				self.byteIdx += 1
# 				self.mosiBytes.append(self.a)
# 				self.misoBytes.append(self.b)
# 				self.a = 0x00
# 				self.b = 0x00

# 		if ev[self.idx_CS] == 1 and cv[self.idx_CS] == 1:
# 			if self.state == 0:
# 				return
# 			if DEBUG3:
# 				print ("Bytes %10.6f %4d " %  (self.begin, self.id), end="")
# 				for i in range(self.byteIdx):
# 					print ("0x%2.2x " % (self.mosiBytes[i]), end="")
# 				print ("\n                      ", end="")	
# 				for i in range(self.byteIdx):
# 					print ("0x%2.2x " % (self.misoBytes[i]), end="")
# 				print("")

# 			self.pp.show(self.begin, self.id, self.mosiBytes, self.misoBytes)

# 			self.end = cv[0]
# 			self.state = 0
# 			self.countBits = 0
# 			self.byteIdx = 0
# 			self.mosiBytes = []
# 			self.misoBytes = []
# 			self.id += 1
# 			if DEBUG2:
# 				print ("End %f" % self.begin)
				
#------------------------------------------------------------------------------------------------------------------------#
class parse_fanPWM:

	def __init__(self):
		self.state = 0
		self.thisTime = 0.0
		self.prevRisingEdgeT = -2000.0
		self.fallingEdgeT = -2000.0
		self.direction = 0
		self.countFanEdge = 0
		self.Entries = []
		self.period = []

	def update(self, cv, ev):
		# Rising edge on FAN_PWM
		if (ev[IDX_FAN_PWM] == 1) and (cv[IDX_FAN_PWM] == 1):
			deltaT = self.thisTime - self.prevRisingEdgeT
			fileOut.write("FAN_PWM  %10f  Rising\n" % cv[IDX_TIME])
			# print("FAN_PWM  %f  Rising  %30.20f" % (cv[IDX_TIME], deltaT))
			self.thisTime = cv[IDX_TIME]
			self.prevRisingEdgeT = self.thisTime
			self.period.append(deltaT)

			# filter out glitches
			if deltaT > 0.000001:
				self.direction = 1
				self.Entries.append((self.thisTime, self.direction))
				self.countFanEdge += 1
				# self.prevTime = self.thisTime

		# High FAN_PWM
		elif (ev[IDX_FAN_PWM] == 0) and (cv[IDX_FAN_PWM] == 1):
			# print("%f ev=0, cv=1" % cv[IDX_TIME])
			pass

		# Falling edge on FAN_PWM
		elif(ev[IDX_FAN_PWM] == 1) and (cv[IDX_FAN_PWM] == 0):
			fileOut.write("FAN_PWM  %10f  Falling\n" % cv[IDX_TIME])
			# print("FAN_PWM  %f  Falling" % cv[IDX_TIME])
			self.thisTime = cv[IDX_TIME]
			deltaT = self.thisTime - self.prevRisingEdgeT

			# filter out glitches
			if deltaT > 0.000001:
				self.direction = 0
				self.Entries.append((self.thisTime, self.direction))
				self.countFanEdge += 1
				# self.prevRisingEdgeT = self.thisTime

		# Low FAN_PWM
		elif (ev[IDX_FAN_PWM] == 0) and (cv[IDX_FAN_PWM] == 0):
			# print("%f ev=0, cv=0" % cv[IDX_TIME])
			pass
	
	def get_entries(self):
		return self.Entries

#------------------------------------------------------------------------------------------------------------------------#

# class parse_AsyncSerial:
# 	def __init__(self, idx):
# 		self.startTime = 0.0
# 		self.thisTime = 0.0
# 		self.prevTime = -2000.0
# 		self.byte = 0x00
# 		self.bitCounter = 0
# 		self.Entries = []
# 		self.Values = []
# 		self.idx = idx
# 		self.bitsComb = 0
# 		self.bidx = 0
# 		self.debugstr = ""

# 	def update(self, cv, ev):
# 		# Begin
# 		self.thisTime = cv[IDX_TIME]

# 		# Edge on Serial line
# 		if (ev[self.idx] == 1):
				
# 			self.delta = self.thisTime - self.prevTime
# 			self.bitsComb = int((self.delta + 0.000008) / 0.00001734)

# 			if (self.bitCounter == 0):
# 				self.debugstr = " S"

# 			self.bitCounter += self.bitsComb

# 			if (cv[self.idx] == 0) and (self.bitCounter >= 9):
# 				self.debugstr = " E"
# 				if (self.bitsComb > 1):
# 					self.debugstr += "+"

# 			if (DEBUG_R1 and (self.idx == IDX_RX)) or (DEBUG_T1 and (self.idx == IDX_TX)):
# 				print ("%2d " % (self.idx), end='')

# 			for z in range(self.bitsComb):

# 				if (DEBUG_R1 and (self.idx == IDX_RX)) or (DEBUG_T1 and (self.idx == IDX_TX)):
# 					print ("(%2d, %1d)" % (self.bidx, cv[self.idx] ^ 1), end='')

# 				if (self.bidx >= 1) and (self.bidx <= 8):
# 					self.byte += (cv[self.idx] ^ 1) * 2 ** (self.bidx - 1)

# 				if self.bidx == 8:

# 					if (DEBUG_R1 and (self.idx == IDX_RX)) or (DEBUG_T1 and (self.idx == IDX_TX)):
# 						print (" VALUE %2.2x" % (self.byte), end='')

# 					self.debugstr = " VALUE %2.2x" % (self.byte)
# 					if self.prevTime > -1999.0:
# 						self.Values.append([self.startTime, self.byte])

# 				self.bidx += 1
# 				if self.bidx > 8:
# 					break

# 			if (DEBUG_R1 and (self.idx == IDX_RX)) or (DEBUG_T1 and (self.idx == IDX_TX)):
# 				print ("")

# 			thisEntry = [self.thisTime, self.prevTime, self.delta, cv[self.idx], \
# 						 self.bitCounter, self.bitsComb, self.debugstr]

# 			if self.prevTime > -1999.0:
# 				self.Entries.append(thisEntry)

# 			if (cv[self.idx] == 0) and (self.bitCounter >= 9):
# 				self.bitCounter = 0
# 				self.bidx = 0
# 				self.byte = 0
# 				self.startTime = self.thisTime

# 			self.prevTime = self.thisTime
# 			self.debugstr = ""

# 	def get_entries(self):
# 		return self.Entries

# 	def get_values(self):
# 		return self.Values

#------------------------------------------------------------------------------------------------------------------------#

def usage():
    print( "spi_u18_raw3 -r <rotor name> [-v <verbosity_level>] [-a]")
    print( " -r Rotor name ")
    print( " -v Verbosity")
    print( " -a Save separate AsyncSerial Rx and Tx files")
	
#------------------------------------------------------------------------------------------------------------------------#

argc = len(sys.argv)
if argc < 2:
	usage()
	sys.exit(0)

startTime = time.localtime(time.time())
tstr = time.strftime("%Y-%m-%d %H:%M:%S", startTime)

# cmd line defaults
infilename = ''
outfilename = ''
out_text = 0
verbosity = 0
ASYNC_TO_FILE = 0

#    
# parse command line options
#
try:
	opts, args = getopt.getopt(sys.argv[1:], "r:v:a")
except getopt.error:
	usage()
	sys.exit(2)

# process options
rotor_name = ""

for o, a in opts:
	if o == "-r":
		rotor_name = a
	elif o == "-v":
		verbosity = int(a)
	elif o == "-a":
		ASYNC_TO_FILE = 1

if rotor_name == '':
	usage()
	sys.exit(1)

infilename = rotor_name + "_Group1.csv"
outfilename = rotor_name + "_FanPWMOut.txt"

try:
	fileIn = open(infilename, 'rt')
except:
	print( "Could not open input file %s" % (infilename))
	sys.exit(1)

base = os.path.basename(infilename)
basefile = os.path.splitext(base)[0]
# AEW edit
prefix = infilename.replace(base, "")

lastmodified= os.stat("%s"%(infilename)).st_mtime
aa = time.localtime(lastmodified)
ftstr = time.strftime("%Y-%m-%d %H:%M:%S", aa)

ststr = time.strftime("%Y%m%d%H%M%S", aa)[2:]

if outfilename != "":
	try:
		fileOut = open(outfilename, 'wt')
	except:
		print( "Could not open output file %s" % (outfilename))
		sys.exit(1)
else:
	fileOut = sys.stdout

print("Input file: %s of %s" % (infilename, ftstr))
print("Output file: %s" % outfilename)
fileOut.write("Input file: %s of %s\n" % (infilename, ftstr))

# Create fan parser
fan = parse_fanPWM()

fileOut.write("\n")
fileOut.write("Module   Time        Edge Type\n")
fileOut.write("-------  ----------  ---------\n")

numlines = 0

# skip first row, it is a header
line = fileIn.readline()
numlines += 1

cur_vect  = [T0, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1]
prev_vect = [T0, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1]
edge_vect = [T0, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1]

while 1:
	line = fileIn.readline()
	if len(line) <= 0:
		break
	numlines += 1

	if len(line) <= 3:
		continue

	linesp = line.split(",")

	timestamp = float(linesp[IDX_TIME])
	cur_vect[0] = timestamp
	for i in range (1, 17):
		cur_vect[i] = int(linesp[i])

	# Detect edges
	if prev_vect[0] > T0:
		edge_vect[0] = cur_vect[0]
		for i in range (1, 17):
			edge_vect[i] = cur_vect[i] ^ prev_vect[i]

	# Call fan parser
	fan.update(cur_vect, edge_vect)

	if DEBUG1:
		print (prev_vect)
		print (cur_vect)
		print (edge_vect)
		print ("")

	prev_vect[:] = cur_vect[:]

## Process the fan PWM edge entries
fileOut.write("\n\n")
fileOut.write("Module   Rising T0   Falling T   Rising T1   Period      Duty Cycle\n")
fileOut.write("-------  ----------  ----------  ----------  ----------  ----------\n")
fan_edges = fan.get_entries()

idx = 0

while (fan_edges[idx][1] != 1):
	idx += 1

risingT = -2000.0
prevRisingT = -2000.0
fallingT = -2000.0

for _, f in enumerate(fan_edges[idx:]):
	# Rising Edge
	if f[1] == 1:
		prevRisingT = risingT
		risingT = f[0]
		periodT = risingT - prevRisingT
		# Find the duty cycle
		if fallingT < risingT and fallingT > prevRisingT:
			highTimeT = fallingT - prevRisingT
			dutyCycle = highTimeT / periodT
			fileOut.write("FAN_PWM  %10f  %10f  %10f %10f %9.2f%% \n" % (prevRisingT, fallingT, risingT, (risingT - prevRisingT),(dutyCycle * 100)))
	# Falling Edge
	elif f[1] == 0:
		fallingT = f[0]


fileOut.write("\nDone\n")
print("\nDone")
fileOut.write("Num FAN_PWM edges: %d\n" % fan.countFanEdge)
print("Num FAN_PWM edges: %d\n" % fan.countFanEdge)
# print("%24.20f" % np.mean(fan.period[1:]))
# print("%24.20f" % np.min(fan.period[1:]))
# print("%24.20f" % np.max(fan.period[1:]))
# print("%24.20f" % np.std(fan.period[1:]))

# Find duty cycles based on the period from rising->rising edge and calculate out the percentage of the time that is high
# based on the time between rising and falling edge and the total time between rising and rising edge
