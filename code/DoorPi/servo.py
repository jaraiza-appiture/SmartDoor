import RPi.GPIO as GPIO
import time
import socket

UDP_IP = "192.168.254.34"
UDP_PORT = 5005

sock = socket.socket(socket.AF_INET, #internet
			socket.SOCK_DGRAM) #UDP
sock.bind((UDP_IP,UDP_PORT))

servoPIN = 17
sensorPIN = 27
GPIO.setmode(GPIO.BCM)
GPIO.setup(servoPIN, GPIO.OUT)
GPIO.setup(sensorPIN,GPIO.IN,pull_up_down=GPIO.PUD_DOWN)

p = GPIO.PWM(servoPIN, 50) # GPIO 17 for PWM with 50Hz
p.start(1.5) # Initialization
try:
    while True:
        while True:
          data,addr = sock.recvfrom(1024)
          print("Received message: %s"%(data.decode()))
          p.ChangeDutyCycle(0)
          if data.decode() == "Open Door":
              break
          
        p.ChangeDutyCycle(4)
        #time.sleep(0.5)
        #p.ChangeDutyCycle(6)
        #time.sleep(0.5)
        #p.ChangeDutyCycle(6)
        time.sleep(0.5)
        p.ChangeDutyCycle(0)
        #p.ChangeDutyCycle(12.5) # Open
        
        start_time = time.time()
        elapsed_time = 0
        sig = ""
        
        while GPIO.input(sensorPIN) == GPIO.HIGH and elapsed_time < 5:
          sig = str(GPIO.input(sensorPIN))
          print("Waiting for door open || time: %s inSignal: %s"%(elapsed_time,sig))  
          elapsed_time = time.time() - start_time #wait for door open or 5 secs passed
        
        if elapsed_time >= 5 and GPIO.input(sensorPIN)== GPIO.HIGH:
          print("Closing Door!")
          p.ChangeDutyCycle(1.5)
          #time.sleep(0.5)
          #p.ChangeDutyCycle(1.5)
          #time.sleep(0.5)
          #p.ChangeDutyCycle(1.5)
          time.sleep(0.5)
          p.ChangeDutyCycle(0)

          #p.ChangeDutyCycle(2.5)
          print("Door Closed") # Open
        # Close door no one opened it
        else:
          time.sleep(0.5) 
          while GPIO.input(sensorPIN) == GPIO.LOW:
            sig = str(GPIO.input(sensorPIN))
            print("Waiting for door to close || inSignal: %s"%(sig))#wait for door to close
          sig = str(GPIO.input(sensorPIN))
          print("inSignal: %s"%(sig))
          time.sleep(2)
          print("Closing Door!")
          p.ChangeDutyCycle(1.5)
          #time.sleep(0.5)
          #p.ChangeDutyCycle(1.5)
          #time.sleep(0.5)
          #p.ChangeDutyCycle(1.5)
          time.sleep(0.5)
          p.ChangeDutyCycle(0)
          #p.ChangeDutyCycle(2.5)
          print("Door Closed") # Close door now
        
        #p.stop()
        #GPIO.cleanup()  

except KeyboardInterrupt:
  p.stop()
  GPIO.cleanup()
