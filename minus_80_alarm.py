import smtplib
import ssl
import RPi.GPIO as GPIO
from time import sleep
from time import time
from time import strftime
from time import localtime

def logging(message):
	"This function writes a time stamp and message to the minus_80.log file"
	time_stamp = strftime("%m-%d-%Y %H:%M", localtime(time()-6*60*60))

	with open("/home/pi/minus_80_alarm/minus_80.log", mode='a') as file:
		file.write("\n" + time_stamp + "\t" + message)

logging("\n \nProgram started")


###########  Email info ###############

# Sending email address information
sender_email = "tyo.lab.nu@gmail.com"
password = "synbiorox"

# Receiver email address information
receiver_email = "keith.tyo@gmail.com" 

#  This is the initialization email message
start_up_message = """\
Subject: -80 freezer alarm has been successfully booted.

This email confirms that the RasPi is currently monitoring the -80 freezer."""

# This is the alarm email message
message = """\
Subject: ***There is an alarm on the -80 freezer***

The alarm is currently active on the -80 freezer.  Please come to the lab and assess the situation.  

This message will be resent every 10 min until the alarm is off."""
######################################

# Set GPIO pin for detection
pin = 21
# Set amount of time that alarm has to stay on (in seconds) before email is sent
alarm_time = 10
# Set the delay between emails (in sec)
email_delay = 30

#### Setup GPIO to detect alarm ####
GPIO.setmode(GPIO.BCM)
# Set pin in second column, last row as sensor pin
# Set up_down to "up" because we will connect to ground
GPIO.setup(pin, GPIO.IN, GPIO.PUD_UP)





# Send initialization email

# Create a secure SSL context
context = ssl.create_default_context()

with smtplib.SMTP_SSL("smtp.gmail.com", context=context) as server:
    server.login("tyo.lab.nu@gmail.com","synbiorox")
    server.sendmail(sender_email, receiver_email, start_up_message)

logging("Initialization email sent.  Monitoring is beginning.")

t = time()

try:
	# Continuously monitor the -80 signal
	while True:
		sleep(0.5)
		# Detect if circuit becomes closed, because pin will shift from HIGH to LOW
		if GPIO.input(pin) == GPIO.HIGH:
			#Record time stamp of time
			start_time = time()
			logging("Alarm started") 

			while GPIO.input(pin) == GPIO.HIGH:
				time_elapse = time() - start_time
				if time_elapse > alarm_time:
					logging("Alarm exceeded alarm time, send email")
					#Initiate sending of warning email
					# Create a secure SSL context
					context = ssl.create_default_context()

					# Send warning email
					with smtplib.SMTP_SSL("smtp.gmail.com", context=context) as server:
						server.login("tyo.lab.nu@gmail.com","synbiorox")
						server.sendmail(sender_email, receiver_email, message)
					logging("Email sent. waiting...")

					# Wait 10 min before resend warning email
					sleep(email_delay)
					logging("Finished waiting")

			#Record time to file	
			time_elapse = time() - start_time
			logging("Alarm is no longer active. Alarm was active for" 
			     + str(time_elapse) + " sec")
		# Send a timestamp each day to confirm program is running.
		if t - time() > 86400:
			logging("Program is still running normally.")
			t = time()

except:
	#Send an email if exception has occured.
	print("An exception has occured.  Send alert email.")
	context = ssl.create_default_context()

	with smtplib.SMTP_SSL("smtp.gmail.com", context=context) as server:
		server.login("tyo.lab.nu@gmail.com","synbiorox")
		server.sendmail(sender_email, receiver_email, "Subject: ***Minus 80 alarm is no longer working.***")

