#!/usr/bin/python
#Raspberry Pi Power Usage logging to Xively
#GPU\CPU code is from http://rollcode.com/use-python-get-raspberry-pis-temperature/
#By William Garrido (FriedCircuits.us)
#Created 05-22-2014
#Licensed as CC-BY-SA

import serial
import sys
import time
import cosm
import json
import commands
import psutil

ser = serial.Serial('/dev/ttyACM0', 115200, timeout=5)
API_KEY="API_KEY"
FEED_ID="FEED_ID"
timerSec = 20 #Number of seconds between Xively uploads

def writeCosm(curVoltage, curAmp, curmAh, curmWh, curWatt, curCPUTemp, curGPUTemp, curCPUUsage):
	
	
	pfu = cosm.PachubeFeedUpdate(FEED_ID,API_KEY)
	pfu.addDatapoint("Voltage",curVoltage)
	pfu.addDatapoint("Current",curAmp)
	pfu.addDatapoint("mAh",curmAh)
	pfu.addDatapoint("mWh",curmWh)
	pfu.addDatapoint("Watts",curWatt)
	pfu.addDatapoint("CPUTemp", curCPUTemp)
	pfu.addDatapoint("GPUTemp", curGPUTemp)
	pfu.addDatapoint("CPUUsage", curCPUUsage)
	pfu.buildUpdate()
	pfu.sendUpdate()
	
	print "Uploaded Power data to Xively"
	
	return
	
def get_cpu_temp():
    tempFile = open( "/sys/class/thermal/thermal_zone0/temp" )
    cpu_temp = tempFile.read()
    tempFile.close()
    #return float(cpu_temp)/1000
    # Uncomment the next line if you want the temp in Fahrenheit
    cpu = float(cpu_temp)
    return float(1.8*cpu/1000)+32
 
def get_gpu_temp():
    tempGPU = commands.getoutput( '/opt/vc/bin/vcgencmd measure_temp' ).replace( 'temp=', '' ).replace( '\'C', '' )
    gpu_temp = float(tempGPU)
    #return  float(gpu_temp)
    # Uncomment the next line if you want the temp in Fahrenheit
    return float(1.8*gpu_temp)+32
	
 
while 1:
	
	try:
		ser.close()
		ser.open()
		time.sleep(1)
		data = ser.readline()
		time.sleep(1)
		ser.close()
		json_data = json.loads(data)
		#print json_data
		curVoltage = json_data['v']['avg']
		curAmp = json_data['a']['avg']
		curmAh = json_data['mah']
		curmWh = json_data['mwh']
		curWatt = round((curVoltage * (curAmp/1000)),2)
		curCPUTemp = round(get_cpu_temp(),2)
		curGPUTemp = round(get_gpu_temp(),2)
		curCPUUsage = psutil.cpu_percent(interval=1, percpu=False)
		print curVoltage
		print curAmp	
		print curmAh
		print curmWh
		#print "{0:.2f}".format(curWatt)
		print curWatt
		print curCPUTemp
		print curGPUTemp
		print curCPUUsage
		writeCosm(curVoltage, curAmp, curmAh, curmWh, curWatt, curCPUTemp, curGPUTemp, curCPUUsage)
		ser.close()
		time.sleep(timerSec)
	except KeyboardInterrupt:
		ser.close()
		break
	except ValueError:
		print "Error!"
		

print "Done"
