#! /bin/python
# Required to read files on the system.
# And to call the system shell.
import os
# Used for working with file.
import shutil

# arg 1 EXP0-${v}-${f}
# arg 2 is frequency
# arg 3 is experiment define
def CompileExperiment(fullExperimentName, frequency, experimentNumber):
    # Create the name for output files. 
    # Two output files will be created. The first is an AXF file. An AXF is needed for debugging 
    # as it contains all debug information.
    outputAXF  = "../Experiments/" + fullExperimentName + "/" + fullExperimentName + ".axf"
    # The srec file is used for flashing. An srec contains no debugging information.hjj
    outputSREC = "../Experiments/" + fullExperimentName + "/" + fullExperimentName + ".srec"

    # Creates directory with for experiments.
    # Experiments folder will be created in the root folder an found under 
    # the directory "Experiments"
    directoryCMD = "../Experiments/" + fullExperimentName
    if not os.path.exists(directoryCMD):
        os.mkdir(directoryCMD)

    # Each experiment generates its own executable. To make it simple to generate 
    # the executables, compile time defines are used so that one and only one experiment is included in the executable.
    #
    # To force a compile, touch the Experiments.c file. This is the file that takes the compile time defines
    # and enables or disables features that are to be used or not used during the experiment.
    # The following command will execute in the system shell
    os.system("touch ../Firmware/Firmware/L5_Application/Experiments/Experiments.c")
    # Generate the command that will be used to compile.
    # The software is built by using make build tool along with the frequency and voltage settings that are provided for the 
    # experiment. The following make command that is generated informs make where the executable should be built and passes
    # the experiment configurations as compile time defines. 
    makeCommand = "make -C  ../Firmware/ build -j CMD_LINE_DEFINED_FREQUENCY=EXP_DCO_" + frequency + " CMD_LINE_DEFINED_EXPERIMENT=" + experimentNumber
    # Actually issue the make command in the system shell.
    os.system(makeCommand)
    # Move the generated axf and srec to the appropriate experiment folder. The move will rename the executable to have the 
    # name calculated earlier so that the default axf and srec names are not used. 
    shutil.move("../Firmware/Build/Debug/MastersProject.axf ", outputAXF)
    shutil.move("../Firmware/Build/Debug/MastersProject.srec", outputSREC)

# Range of frequencies that the MCU will be tested at.
frequency = ['1500000', '3000000', '6000000', '12000000', '24000000', '48000000']
# Range of voltages that the MCU will be tested at.
voltage   = ['1_85', '2_0', '3_3']




# Active and low power mode tests
experimentSet1 = ['00', '02', '04', '05', '06', '07', '08', '10', '11']
#Low frequency just runs at different voltages
experimentSet2 = ['01', '03', '09', '12']


# The following two experiments generators look at just the MCU performance.
for f in frequency:
    for v in voltage:
        for exp in experimentSet1:
            fullExperimentName = "EXP"+exp+"-"+v+"-"+f
            CompileExperiment(fullExperimentName,f, "USER_EXPERIMENT_"+exp)

for v in voltage:
    for exp in experimentSet2:
        fullExperimentName = "EXP"+exp+"-"+v+"-LF"
        CompileExperiment(fullExperimentName, str(3000000), "USER_EXPERIMENT_"+exp)

# The following two experiment generators look at the whole system performance.
for f in frequency:
    for v in voltage:
        for exp in experimentSet1:
            fullExperimentName = "EXP"+exp+"-"+v+"-"+f+"-MyConfig"
            CompileExperiment(fullExperimentName,f, "USER_EXPERIMENT_"+exp)

#Low frequency just runs at different voltages
for v in voltage:
    for exp in experimentSet2:
        fullExperimentName = "EXP"+exp+"-"+v+"-LF-MyExperiment"
        CompileExperiment(fullExperimentName, str(3000000), "USER_EXPERIMENT_"+exp)



# Experiments for XBee, HDC1080, and OPT3001 timed reads
experimentSetSensors = ['13A', '13B', '14', '15', 
                        '16A', '16B', '17', '18', '19', '20', '21', '22',
                        '23A', '23B', '24', '25', '26', '27', '28', '29',
                        '37'
                        ]
for exp in experimentSetSensors:
    for f in frequency:    
        fullExperimentName = "EXP"+exp+"-"+"3_7"+"-"+f+"-MyConfig"
        CompileExperiment(fullExperimentName,f, "USER_EXPERIMENT_"+exp)

# Active and low power mode tests with XBee
experimentSetXBee = ['30A','30B', '31', '32', '33', '34', '35', '36']
for f in frequency:
        for exp in experimentSetXBee:
            fullExperimentName = "EXP"+exp+"-"+"3_7"+"-"+f+"-MyConfig"
            CompileExperiment(fullExperimentName,f, "USER_EXPERIMENT_"+exp)


 # XBee tests at 9600 baud
experimentSetXBee1 = ['70','71', '72', '73', '74', '75', '76', '77', '78', '79', '80', '81', '82']
for exp in experimentSetXBee1:
    for f in frequency:
        fullExperimentName = "EXP"+exp+"-"+"3_7"+"-"+f+"-MyConfig"
        CompileExperiment(fullExperimentName,f, "USER_EXPERIMENT_"+exp)

# XBee tests at 115200 baud
experimentSetXBee2 = ['83','84', '85', '86', '87', '88', '89', '90', '91', '92', '93', '94', '95']
for exp in experimentSetXBee2:
    for f in frequency:    
        fullExperimentName = "EXP"+exp+"-"+"3_7"+"-"+f+"-MyConfig"
        CompileExperiment(fullExperimentName,f, "USER_EXPERIMENT_"+exp)


