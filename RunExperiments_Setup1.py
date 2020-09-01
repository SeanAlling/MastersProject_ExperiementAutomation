#! /bin/python
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
# This is an HP66311B DC source meter.
# The source meter is fixed to be on address 5.
powerSupply = rm.open_resource('GPIB0::5::INSTR')
# HP3467A bench multimeter.
# The multimeter is fixed to be on address 22.
multimeter   = rm.open_resource('GPIB0::22::INSTR', read_termination='\r\n')



# Setup instruments. This needs to occur only once per instrument
# A small time delay is used after each command sent to the power supply. This is required 
# so that the GPIB commands can finish. before executing the next command. 
# The delay here of 100ms was chosen because it worked. 

# Perform power on reset sequence. The following commands will reset the source meter so that 
# all registers are put into there power on state.
# See user manual page 75 for more information.
powerSupply.write('*RST')
time.sleep(0.1)
powerSupply.write('*CLS')
time.sleep(0.1)
powerSupply.write('STAT:PRES')
time.sleep(0.1)
powerSupply.write('*SRE 0')
time.sleep(0.1)
powerSupply.write('*ESE 0')
time.sleep(0.1)

# Set the number of points to use for a measurement. 
# Use full size of buffer for data measurements
powerSupply.write('SENS:SWE:POIN 4096');
time.sleep(0.1)
# Use the fastest sample rate
powerSupply.write('SENS:SWE:TINT 15.6E-6');
time.sleep(0.1)


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
multimeter.write("DCI")
time.sleep(0.1)
# Set the integration time to 1 cycle
multimeter.write("NPLC 1")
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

    # Set power supply voltage to 3.3V. For flashing to work, the device MUST run at 3.3V
    powerSupply.write('VOLT 3.3')
    # Turn on the power supply output.
    powerSupply.write('OUTP ON')
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
    # with the new firmware. 
    time.sleep(5)
    # Turn off the power supply.
    powerSupply.write('OUTP OFF')
    # Delay added to make sure that MSP432 is truly off. 
    time.sleep(5)
    # Set up the experiment based on the parameters.
    print("Setting Up Experiment")
    print("Setting up power supply")
    # Set the power suply to the voltage requested for the experiment. 
    powerSupply.write('VOLT ' + voltage)
    time.sleep(0.1)
    # Turn the power supply output on.
    powerSupply.write('OUTP ON')
    time.sleep(0.1)
    print("Finished setting up power supply")
    # Give time for the micro controller to setup. Want the micro to be in the while(1) loop when we start taking measurements.
    time.sleep(5)
    # Capture the time that the experiment is starting. 
    start = time.time()
    with open("../Experiments/" + d + '/' + d + '.results', 'w',1) as results:  # Use file to refer to the file object
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

