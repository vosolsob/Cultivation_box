#!/usr/bin/python3
import time
import csv
import board
import adafruit_dht      #sudo pip3 install adafruit-circuitpython-dht
#import RPi.GPIO as GPIO #on Raspberry
import pigpio
import math
import sys, getopt

#sudo pigpiod
#python3 box.py -r 5 -s 18 -m 5 -n 20 -e 15 -l 10,30,5,100,0,10,20 -i -j
#or
#python3 box.py -f config_file

pi = pigpio.pi()

t_temperature = 0
t_humidity = 0
b_temperature = 0
b_humidity = 0
dif0 = 100.0

conf = "/home/pi/Desktop/box.conf"
useconf = False

sunrise = 6.0
sunset = 18.0

morn_t = 15.0
noon_t = 25.0
even_t = 15.0
sin_l = 0.0
sin_t = 0.0
sin_A = 0.0
led = [0,0,0,0,0,0,0]
f = 0.0
c = 0
fast_test = 0
check_dev = 0
cooling = "cooling_OFF"

hours = 0.0
#LEDs
R = 12 #GPIO12
G = 25 #GPIO25
B = 22 #GPIO22
W = 23 #GPIO23
U = 5 #GPIO5
P = 6 #GPIO6
A = 24 #GPIO24

#fPWM = 300  # Hz PWM oscilator

# Relays
C = 17 #GPIO17 heating = 1, cooling = 0 
F = 27 #GPIO27 cooling/heating intensity

def main(argv):
   global conf
   global useconf
   global sunrise
   global sunset
   global morn_t
   global noon_t
   global even_t
   global sin_l
   global sin_t
   global led
   global fast_test
   global check_dev

   try:
      opts, args = getopt.getopt(argv,"hfr:s:m:n:e:l:ijt:c",["help","file=","sunrise=","sunset=","morning_temp=","noon_temp=","evening_temp=","LED_int=","sin_light","sin_temp","fast_test=","check_dev"])
   except getopt.GetoptError:
      print ('box.py -f -r <sunrise> -s <sunset> -m <morning_temp> -n <noon_temp> -e <evening_temp> -l R,G,B,W,UV,PLANT,AQUARIUM -i -j -t <fast_time_increment> -c')
      sys.exit(2)
   for opt, arg in opts:
      if opt in ("-h", "--help"):
         print ('box.py -r <sunrise> -s <sunset> -m <morning_temp> -n <noon_temp>-e <evening_temp> -l R,G,B,W,UV,PLANT,AQUARIUM -i -j -t <fast_time_increment> -c')
         print ("")
         print ("... or")
         print ("")
         print("box.py -f box.conf")
         print ("")
         print("    -h         --help                print this help")
         print("    -f         --file=<file>         configuration file, `box.config` is default") 
         print("    -r <num>   --sunrise=<num>       sunrise time (hours), e.g. -r 6.75 for 6:45")
         print("    -s <num>   --sunset=<num>        sunset time (hours)")
         print("    -m <num>   --mornimg_temp=<num>  morning temperature at the time of sunrise")
         print("    -n <num>   --noon_temp=<num>     maximum day temperature;")
         print("                                     is being reached after after 12 am")
         print("    -e <num>   --evening_temp=<num>  evening temperature at the time of sunset")
         print("    -l <list>  --LED_int=<list>      intensities of LEDs for each colour in %")
         print("                                     (RED,GREEN,BLUE,WHITE,UV,PLANT,AQUARIUM),")
         print("                                     e.g. -l 10,30,5,100,0,10,20")
         print("    -i         --sin_light           illumination during day as sinusoid curve,")
         print("                                     otherwise constant")
         print("    -j         --sin_temp            temperature during day as sinusoid curve,")
         print("                                     otherwise constant by maximum temperature")
         print("    -t <num>   --fast_test=<num>     box test with fast time, not real time;")
         print("                                     set time increment in hours during each step")
         print("    -c         --check_dev           perform initial test of LEDs and cooling device")
         print("")
         print("Example:")
         print("python3 box.py -r 7 -s 19 -m 5 -n 20 -e 15 -l 10,30,5,100,0,10,20 -i -j")
         print("Note: start PIGPIO daemon first using  `sudo pigpiod`")
         print("Note: set correct time using  `sudo date -s 9:05`")
         sys.exit()
      elif opt in ("-f"):
         useconf = True
         with open(conf,"r") as f_input:
            csv_input = csv.DictReader(f_input, delimiter='\t',quoting=csv.QUOTE_NONE)
            for row in csv_input:
                  sunrise = float(row['r'])
                  sunset = float(row['s'])
                  morn_t = float(row['m'])
                  noon_t = float(row['n'])
                  even_t = float(row['e'])
                  sin_l = float(row['i'])
                  sin_t = float(row['j'])
                  led = [float(i) for i in row['l'].split(',')]
      elif opt in ("--file"):
         useconf = True
         if arg != "":
            conf = arg
         with open(conf,"r") as f_input:
            csv_input = csv.DictReader(f_input, delimiter='\t',quoting=csv.QUOTE_NONE)
            for row in csv_input:
                  sunrise = float(row['r'])
                  sunset = float(row['s'])
                  morn_t = float(row['m'])
                  noon_t = float(row['n'])
                  even_t = float(row['e'])
                  sin_l = float(row['i'])
                  sin_t = float(row['j'])
                  led = [float(i) for i in row['l'].split(',')]
      elif opt in ("-r", "--sunrise"):
         sunrise = float(arg)
      elif opt in ("-s", "--sunset"):
         sunset = float(arg)
      elif opt in ("-m", "--morning_temp"):
         morn_t = float(arg)
      elif opt in ("-n", "--noon_temp"):
         noon_t = float(arg)
      elif opt in ("-e", "--evening_temp"):
         even_t = float(arg)
      elif opt in ("-l", "--LED_int"):
         led = [float(i) for i in arg.split(',')]
      elif opt in ("-i", "--sin_light"):
         sin_l = 1
      elif opt in ("-j", "--sin_temp"):
         sin_t = 1
      elif opt in ("-c", "--check_dev"):
         check_dev = 1
      elif opt in ("-t", "--fast_test"):
         fast_test = float(arg)
   print ('The file ', conf, 'will be used for configuration: ', useconf)   
   print ('Sunrise time is ', sunrise)
   print ('Sunset time is ', sunset)
   
   print ('Morning temp is ', morn_t)
   print ('Noon temp is ', noon_t)
   print ('Evening temp is ', even_t)
   print ("LED intensities for RED, GREEN, BLUE, WHITE, UV, PLANT, AQUARIUM are: ",led)
   print ("If >>1<< then modeled sinusoid illumination: ", sin_l)
   print ("If >>1<< then modeled sinusoid temperature: ", sin_t)
   print ("If >>1<< then devce check will proceed: ", check_dev)
   print ("If > 0, fast time test activated with time increment in hours:", fast_test)
   time.sleep(5.0)

# led - list with 7 items, numbers 0-100
# ilum - aactual intensisty of light
def LEDs( led, ilum ):
   #print ("setting RED, GREEN, BLUE, WHITE, UV, PLANT, AQUARIUM: ",led)
   #pwmR.ChangeDutyCycle(ilum*led[0])
   #pwmG.ChangeDutyCycle(ilum*led[1])
   #pwmB.ChangeDutyCycle(ilum*led[2])
   #pwmW.ChangeDutyCycle(ilum*led[3])
   #pwmU.ChangeDutyCycle(ilum*led[4])
   #pwmP.ChangeDutyCycle(ilum*led[5])
   #pwmA.ChangeDutyCycle(ilum*led[6])
   pi.set_PWM_dutycycle(R,round(2.55*ilum*led[0]))
   pi.set_PWM_dutycycle(G,round(2.55*ilum*led[1]))
   pi.set_PWM_dutycycle(B,round(2.55*ilum*led[2]))
   pi.set_PWM_dutycycle(W,round(2.55*ilum*led[3]))
   pi.set_PWM_dutycycle(U,round(2.55*ilum*led[4]))
   pi.set_PWM_dutycycle(P,round(2.55*ilum*led[5]))
   pi.set_PWM_dutycycle(A,round(2.55*ilum*led[6]))

def HWsetup():
   global t
   global b
   
   #global pwmR
   #global pwmG
   #global pwmB
   #global pwmW
   #global pwmU
   #global pwmP
   #global pwmA
   
   global pi
   
   # Relay
   #GPIO.setup(C, GPIO.OUT)
   #GPIO.setup(F, GPIO.OUT)
   
   print("Set cooling ON ...")
   #GPIO.output(C, False) #ON
   #GPIO.output(F, False) #ON
   pi.write(C,0)  #cooling
   pi.write(F,1)  #ON
   
   # LEDs
   
   #GPIO.setup(R, GPIO.OUT)
   #GPIO.setup(G, GPIO.OUT)
   #GPIO.setup(B, GPIO.OUT)
   #GPIO.setup(W, GPIO.OUT)
   #GPIO.setup(U, GPIO.OUT)
   #GPIO.setup(P, GPIO.OUT)
   #GPIO.setup(A, GPIO.OUT)
   #
   #pwmR = GPIO.PWM(R, fPWM)
   #pwmG = GPIO.PWM(G, fPWM)
   #pwmB = GPIO.PWM(B, fPWM)
   #pwmW = GPIO.PWM(W, fPWM)
   #pwmU = GPIO.PWM(U, fPWM)
   #pwmP = GPIO.PWM(P, fPWM)
   #pwmA = GPIO.PWM(A, fPWM)
   #
   #pwmR.start(0)
   #pwmG.start(0)
   #pwmB.start(0)
   #pwmW.start(0)
   #pwmU.start(0)
   #pwmP.start(0)
   #pwmA.start(0)
   
   # Initial the dht device, with data pin connected to:
   t = adafruit_dht.DHT22(board.D13)
   b = adafruit_dht.DHT22(board.D21)
   TempRead()


def TempRead():
    global t_temperature
    global b_temperature
    global t_humidity
    global b_humidity	
    try:
        # Print the values to the serial port
        t_temperature = t.temperature
        t_humidity = t.humidity
    except RuntimeError as error:
        # Errors happen fairly often, DHT's are hard to read, just keep going
        print(error.args[0])
        time.sleep(2.0)
        #continue
    except Exception as error:
        t.exit()
        raise error

    time.sleep(2.0)
    
    try:
        # Print the values to the serial port
        b_temperature = b.temperature
        b_humidity = b.humidity
    except RuntimeError as error:
        # Errors happen fairly often, DHT's are hard to read, just keep going
        print(error.args[0])
        time.sleep(2.0)
        #continue
    except Exception as error:
        b.exit()
        raise error



def Illum( hours, sin_l):
    sunlen = sunset - sunrise
    noon = (sunrise+sunset)/2
    #B is the value of sun curve at sunrise point
    B = math.cos(math.pi*(sunrise-noon)/12)
    sun = math.cos(math.pi*(hours-noon)/12) - B
    #from sun curve created normalized curve, each day between 0-1
    norm_light = sun/(1-B)
    # 0-1 function, 1 between sunrise and sunset
    day = (math.copysign(1,sun)+math.fabs(math.copysign(1,sun)))/2
    if sin_l == 0:
       return day
    else:
       return day*norm_light


def Optim_A():
    A = noon_t
    sunlen = sunset - sunrise
    noon = (sunrise+sunset)/2
    incr = -0.1*A
    rest = -1
    #print(sunrise, sunset, sunlen, even_t, morn_t, A)
    while True:
        hour_max = noon + 12/math.pi*math.asin(12*(even_t-morn_t)/A/math.pi/sunlen)
        rest_p = rest
        B = math.cos(math.pi*(sunrise-noon)/12)
        act_max = A*math.cos(math.pi*(hour_max-noon)/12) - A*B + (hour_max-sunrise)*(even_t-morn_t)/sunlen + morn_t
        rest = noon_t - act_max
        #print(hour_max, A, incr, rest)
        if math.fabs(rest) < 0.0001:
           break
        if rest*rest_p < 0: incr = -0.1*incr
        A = A + incr
        #time.sleep(0.5)
    print("Optimized temp curve parameter A = {:.3f}".format(A)) 
    print("Max temp {:.1f} °C reached at {:.2f} o'clock".format(act_max, hour_max))
    print("***************************************")
    time.sleep(3.0)
    return A

    
def Cool( hours, sin_t):
    global sin_A
    sunlen = sunset - sunrise
    noon = (sunrise+sunset)/2
    #B is the value of sun curve at sunrise point
    B = math.cos(math.pi*(sunrise-noon)/12)
    sun = math.cos(math.pi*(hours-noon)/12) - B
    #from sun curve created normalized curve, each day between 0-1
    # 0-1 function, 1: before sunset; between sunrise and sunset; after sunset
    morning = (math.copysign(1,sunrise - hours) + math.fabs(math.copysign(1,sunrise - hours)))/2
    day = (math.copysign(1,sun)+math.fabs(math.copysign(1,sun)))/2
    evening = (math.copysign(1,hours - sunset) + math.fabs(math.copysign(1,hours - sunset)))/2
    #print(B, sun, morning,day,evening)    
    morning_lin = (morn_t-even_t)/(24-sunlen)*(hours-sunrise) + morn_t 
    day_lin = (hours-sunrise)*(even_t-morn_t)/sunlen + morn_t
    evening_lin = (morn_t-even_t)/(24-sunlen)*(hours-sunset) + even_t

    if sin_t == 0:
       return day*noon_t + morning*morning_lin + evening*evening_lin
    else:
       if sin_A == 0: sin_A = Optim_A()
       return day*day_lin + day*sin_A*sun + morning*morning_lin + evening*evening_lin


#if __name__ == "__main__":
main(sys.argv[1:])
HWsetup()
print("Set LEDs OFF ...")
LEDs([0,0,0,0,0,0,0],1)
time.sleep(3.0)
   
if check_dev == 1:
  print("LED test:")
  print("LEDs ON...")
  LEDs([100,100,100,100,100,100,100],1)
  time.sleep(5.0)
  print("LEDs OFF...")
  LEDs([0,0,0,0,0,0,0],1)
  time.sleep(1.0)
  print("Relay test:")
  print("Relay ON...")
  #GPIO.output(C, False) #ON
  #GPIO.output(F, False) #ON
  pi.write(C,0)  #cooling
  pi.write(F,1)  #ON
   
  time.sleep(5.0)
  print("Relay OFF...")
  #GPIO.output(C, True) #OFF
  #GPIO.output(F, True) #OFF
  pi.write(C,0)  #cooling
  pi.write(F,0)  #OFF
   
  time.sleep(5.0)
  print("End of testing...")


while True:
   if fast_test == 0:
      localtime = time.localtime(time.time())
      hours = localtime.tm_hour + localtime.tm_min/60 + localtime.tm_sec/3600
   TempRead()
   print( "Bottom: {:.1f} °C Humidity: {}% ".format( b_temperature, b_humidity ) )
   print( "Top:    {:.1f} °C Humidity: {}% ".format( t_temperature, t_humidity ) )
   light = Illum(hours, sin_l)
   LEDs(led, light)
   #temperature fast security check
   if t_temperature < 2:
      #GPIO.output(C, True)
      #GPIO.output(F, True)
      pi.write(C,0)  #cooling
      pi.write(F,0)  #OFF
   
   if b_temperature < 2:
      #GPIO.output(C, True)
      #GPIO.output(F, True)
      pi.write(C,0)  #cooling
      pi.write(F,0)  #OFF
   
   if t_temperature > 28:
      LEDs(led, 0)
   if b_temperature > 28:
      LEDs(led, 0)
   temp = (t_temperature + b_temperature)/2
   # non-stably defined function for temperature modelling
   if hours == sunrise:
       hours = hours + fast_test
       continue
   if hours == sunset:
       hours = hours + fast_test
       continue
   t_set = Cool(hours,sin_t)
   dif = temp - t_set
   if dif0 == 100:  #initial state, no previous value
      if dif > 0.1:
         c = 0 #cooling
         f = 100    #ON
         cooling = "Cooling is ON"
      elif dif < -0.1:
         c = 0  #heating
         f = 100    #ON
         cooling = "Heating is ON"
      else:
         c = 0  #cooling
         f = 1       #OFF
         cooling = "Cooling is OFF"
      pi.write(C,c)
      pi.set_PWM_dutycycle(F,round(2.55*f))
      dif0 = dif
      
   else: ### ordinary cycle
      if dif != 0:
         pr = (dif0-dif)/dif # convergent if < 0
      else:
         pr = 0
      print(pr)
      if dif < 0:
         c = 1 #heating
         cooling = "Heating is ON"
      else:
         c = 0 #cooling
         cooling = "Cooling is ON"
      pi.write(C,c)  
      if pr > 0: #convergent situation
         if abs(dif) > 0.1: #otherwise f without change
            f = f/(20*pr) # decrease or increase power (convergence in 10 cycles)
            print("convergent")
            print(f)
         else:
            print("in range")
      else:       #divergent situation
         if pr != 0:
            if abs(dif) > 0.1: #otherwise f without change
               f = 1.2*f #increase power
               print("divergent")
               print(f)
            else:
               print("in range")
         else:
            if abs(dif) > 0.1: #otherwise f without change
               f = 1.1*f #increase power
               print("constant")
               print(f)
            else:
               print("in range")
      
      if dif*dif0 <= 0:  # overshoot
         f = f/4
         print("overshoot")
         print(f)
         
      if f > 100: f = 100
      if f < 0.1: f = 0.1
      pi.set_PWM_dutycycle(F,round(2.55*f))  #ON
      dif0 = dif
        
      
   print("Time is {:.1f}, temp set {:.2f}°C, actual {:.2f}°C, difference is {:.2f}°C , {}, power {:.2f}".format(hours, t_set, temp, dif, cooling, f))
   print("LEDs spectrum: {}, intensity {:.3f}".format(led, light))
   with open("/home/pi/Desktop/box_log","a") as blf:
       blf.write("{:.4f} {:.2f} {:.2f} {:.4f} {:.1f} {:.1f} {:.1f} {:.1f} {:.2f} {}\n".format(hours, t_set, temp, light, t_temperature, b_temperature, t_humidity, b_humidity, f, c))
   hours = hours + fast_test
   if hours >= 24: hours = 0
   if fast_test == 0:
      time.sleep(5)
   else:
      time.sleep(1.0)
