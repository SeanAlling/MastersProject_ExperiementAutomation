#! /bin/python
# This script is vary similar to RunExperiments_Setup1.py 
# Except that this script is designed to use an HP6644A power supply 
# instead of a HP66311B source meter.
# 
# These experiments also focus testing these system and not the MCU. There are some 
# minor tweaks in the experimental scripts to achieve this goal. 

# Used to read files on the system.
# and to run system shell commands.
import os
# Used to interface with the many different instruments. 
import visa
# Used to track how long an experiment collects data and also to add delays to the program.
import time

# The root directory for each experiment executable is located in the 
# "Experiments" folder. 
directoryList=os.listdir("../Experiments")

# Informs the user that the script will now try and connect to the test equipment.
print("Connecting to test equipment")
# Create an instance of the python pyVISA object. This is required so that the installed VISA 
# bindings can be used within python. 
rm = visa.ResourceManager()
# The GPIB adapter that I used is assigned to GPIB0. The following assumes that your GPIB adapter
# will also be assigned GPIB0.

# HP3467A bench multimeter.
# The multimeter is fixed to be on address 22.
multimeter   = rm.open_resource('GPIB0::22::INSTR', read_termination='\r\n')
# This is an HP6644A DC power supply.
# The power supply is fixed to be on address 5.
powerSupply  = rm.open_resource('GPIB0::14::INSTR')


# Setup instruments. This needs to occur only once per instrument
#setup power supply
# Set output voltage to 3.7V
# Only one voltage needs to be used for all these experiments.
# System voltage is set to 3.7 since this is the battery voltage that will be 
# supplied to the system.
powerSupply.write("OUTP OFF")
powerSupply.write("VOLT 3.7")
# Set a current limit of 0.5A. The system should NEVER reach this and if it did then 
# there is a short. This value could probably be tuned to be under 100ma. 
powerSupply.write("CURR 0.5")
powerSupply.write("STAT:PRES 0x0100")

# Setup the multimeter
time.sleep(0.5)
# Puts multimeter into its default power on state.
multimeter.write("RESET")
# Disable multimeter beeping. 
multimeter.write("BEEP OFF")
time.sleep(0.1)
#mandatory for reading from instrument
multimeter.write("END ALWAYS") 
time.sleep(0.1)
# Set measurment mode to DC current. 
multimeter.write("DCI 0.03")
time.sleep(0.1)
#integration time, disable. Take instant measurements
multimeter.write("NPLC 0")
time.sleep(0.1)
# Disable auto zeroing. 
multimeter.write("AZERO 0")
time.sleep(0.1)
# Disable the display
multimeter.write("DISP OFF") 
time.sleep(0.1)
# Set output format to signed real numbers. 
multimeter.write("OFORMAT SREAL")
time.sleep(0.1)


time.sleep(0.1)
# Start measurements
multimeter.write("TARM AUTO") 


# Want to run experiments for every file in the experimental directory.
for d in directoryList:
    # Experiment folders have the following name format
    # EXP#-VOLTAGE-FREQUENCY-DCDC. Split the file name and extract each part. 
    # # these values will be used for saving experimental data 
    # and to also setup the experiment.
    expParams=d.split('-')
    
    # Extracts experiment settings
    expNumber = expParams[0]
    # The value for voltage will also be used to set the power supply.
    voltage   = expParams[1].replace('_','.')
    frequency = expParams[2]
    print("====================================================================================================")
    print("Experiment: " + d)
    print("====================================================================================================")
    # Creates a jlink script needed to flash a MSP432
    # The following script will allow the MSP432 to be flashed with the software thats required for the specified
    # experiment. 
    with open('jlinkScript.jlink', 'w') as file:  # Use file to refer to the file object
        # Use SDW interface
        file.write('If SWD\n')
        # SWD speed is 4k Hz
        file.write('speed 4000\n')
        # Connect to MSP432
        file.write('connect\n')
        # Reset MSP432
        file.write('r\n')
        # Erase flash on MSP432
        file.write("erase\n")
        # Flash experiment executable onto the MSP432
        file.write("loadfile ../Experiments/" + d + "/" + d + ".srec\n")
        # Reset the MSP432
        file.write('r\n')
        # Start MSP432
        file.write('g\n')
        # Exit flash script
        file.write('exit\n')

    # Turn on the power supply. Remember this is a system experiment, so the voltage is fixed
    # to 3.7V.
    powerSupply.write("OUTP ON")
    # Give time for the MSP432 to power up.
    time.sleep(5)

    # Start flashing process for the MSP432
    print("Flashing Target")
    # Inform the user what experiment is being flashed to the MSP432.
    print("Experiment: " + expParams[0] + "Voltage: " + expParams[1] + "\tFrequency: " + expParams[2])
    # Start the jlink program through the system shell. 
    # Two arguments are given. The first is the device, SEGGER recommends that device be provided
    #     jlink at the command line. The second arguet is the script that was generated earlier.
    os.system("jlink -device MSP432P401R -CommanderScript jlinkScript.jlink")
    # Wait a few seconds after the MSP432 has been flashed. This gives some time for the system to boot up
    # with the new firmware. The below power off -> power on cycle is just performing a hard power reset
    # of the system.
    time.sleep(5)
    # Turn off the power supply.
    powerSupply.write('OUTP OFF')
    # Delay added to make sure that MSP432 is truly off. 
    time.sleep(5)

    # Turn on the power supply again. 
    powerSupply.write("OUTP ON")

    print("Finished setting up power supply")
    # Give time for the micro controller to setup. Want the micro to be in the while(1) loop when we start taking measurements.
    # Sleep for 1 minutes to get the system into steady state.
    time.sleep(5)
    # Capture the time that the experiment is starting. 
    start = time.time()
    # Use file to refer to the file object
    with open("../Experiments/" + d + '/' + d + '.results', 'w',1) as results:  
        # Keep taking measurements for 30 seconds. 
        while (time.time() - start) < 30:
            # Sometimes the data returned from the source meter can be corrupted. The try and except blocks make sure that 
            # if corrupt data is received, then the system will skip. Without the try and catch the system would hard fault
            # and the xperiment would end. 
            try:
                # Convert the received signed binary number to a float. Write the data to the experiments results file. 
                results.write("{0:.6f}".format(multimeter.read_binary_values(datatype='f', is_big_endian=True,header_fmt='empty')[0]))
                # Add a newline to the output file.
                results.write("\n")
            except:
                # Inform the user that an error occured. If here then some corrupt data was received.
                print("Exception occurred")
    # Experiment is complete.
    # Delay here was added arbitrarily. Just provides a few seconds between experiments.
    time.sleep(5)
    print("Experiment Complete")
