# Processes raw results from an experiment into one of three file formats, PDF, PNG, and STATS.    #
# PDF and PNG are plots of the experimental results in either PDF or PNG format.                   #
#                                                                                                  #
# STATS file contains the statistical data the experimental results.                               #


                                                  ##################################################
                                                  #                  IMPORTS                       #
                                                  ##################################################
from os import path                               # Path required for accessing files located in   #
                                                  #      system.                                   #
import matplotlib.pyplot as plt                   # Required for plotting data in PDF and PNG.     #
import numpy as np                                # Required for extracting statistical data.      #
from scipy import stats                           # Used for extracting command line parameters.   #
import sys

                                                  #######################################################
                                                  #                 COMMAND LINE PROCESSING             #
                                                  #######################################################
ROOT_DIR        = sys.argv[1]                     # Extract root directory from command line argument 1 #
EXPERIMENT_NAME = sys.argv[2]                     # Extract experiment name which is be stored as       #
                                                  #      command line argument 2.                       #
MODE            = sys.argv[3]                     # Extract type of output that should be generated.    #
                                                  # This is stored as the third command line argument   #

# Internal variable decelerations
# The full file path to the experiments results file
expResultFile  = ROOT_DIR + "/" + EXPERIMENT_NAME + "/" + EXPERIMENT_NAME + '.results'
# Full path to where the experiments stats file will be places. 
expStatsFile   = ROOT_DIR + "/" + EXPERIMENT_NAME + "/" + EXPERIMENT_NAME + '.stats'
# Full path to where the pdf plot will be saved.
pdfFilePath    = ROOT_DIR + "/" + EXPERIMENT_NAME + "/" + EXPERIMENT_NAME + '.pdf'
# Full path to where the png plot file will be saved. 
pngFilePath    = ROOT_DIR + "/" + EXPERIMENT_NAME + "/" + EXPERIMENT_NAME + '.png'

# Check that the experiments result file exists. 
# No need to process the results file if it does not exist.
if(path.exists(expResultFile)):
    # IF here, the the experiment results file exists. 
    # Extract the experimental parameters. 
    # These parameters are stored in the fie name separated by '-' character.
    expParams=EXPERIMENT_NAME.split('-')
    # First parameter is the experiment number.
    exp       = expParams[0]
    # Second parameter is voltage the experiment ran at.
    voltage   = expParams[1].replace('_','.')
    # Third parameter is the frequency the experiment ran at.
    frequency = expParams[2]

    # Open the experimental results file. 
    with open(expResultFile, "r") as filestream:
        # corresponding y axis values 
        # Default this to an empty list. 
        y = [] 
        # For every value in the results file, append the value to the y list.
        # The results file only contains a single measurement, with one entry per line.
        for line in filestream:
            # Measurements are in milliamps. Convert the number to amps. 
            y.append(float(line)*1000)

        # If the user selected to generate a PDF
        if MODE == "PDF":
            # Inform user PDF is being generated.
            print("Generating PDF file")
            # Below is a simple way to implement a rolling average. Its a 1D convolution. 
            # See the following link for the explanation on why this works. 
            # https://stackoverflow.com/questions/13728392/moving-average-or-running-mean
            numPointsToAverage=2
            y = np.convolve(y, np.ones((numPointsToAverage,))/numPointsToAverage, mode='valid')
            sample=range(len(y))

            # plotting the points  
            plt.plot(sample, y, label = "HP3457A") 
            plt.ticklabel_format(axis="y", style="sci", scilimits=(0,0))
            # naming the x axis 
            plt.xlabel('Sample') 
            # naming the y axis 
            plt.ylabel('Current') 

            # giving a title to my graph 
            # Title will be EXP#: VOLATGE: XXX Frequency: YYY
            # Where # is the experiment number, XXX is te experiment voltage, ad YYY is the 
            # experiment frequency.
            pltTitle  = exp + ": "
            pltTitle += "Voltage: " + voltage + " "
            pltTitle += "Frequency: " + frequency

            # Add the plot title created above to the plot. 
            plt.title(pltTitle)
            # Add a legend to the plot.
            plt.legend()
            # Generate the plot and saves the plot in pdf format
            plt.savefig(pngFilePath, format='pdf')
            plt.close()
        # USer is requesting a PNG output plot.
        elif MODE == "PNG":
            # Below code is the same as the PDF case. See notes from the PDF case as they are the same 
            # here unless otherwise noted.
            print("Generating PNG file")
             # Below is a simple way to implement a rolling average. Its a 1D convolution. 
            # See the following link for the explanation on why this works. 
            # https://stackoverflow.com/questions/13728392/moving-average-or-running-mean
            numPointsToAverage=2
            y = np.convolve(y, np.ones((numPointsToAverage,))/numPointsToAverage, mode='valid')
            sample=range(len(y))
            
            # plotting the points  
            plt.plot(sample, y, label = "HP3457A") 
            plt.ticklabel_format(axis="y", style="sci", scilimits=(0,0))
            # naming the x axis 
            plt.xlabel('Sample') 
            # naming the y axis 
            plt.ylabel('Current') 
              
            # giving a title to my graph 
            pltTitle  = exp + ": "
            pltTitle += "Voltage: " + voltage + " "
            pltTitle += "Frequency: " + frequency
            
            plt.title(pltTitle) 
            plt.legend()
            # function to show the plot 
            # Generate and save the plot in PNG format.
            plt.savefig(pngFilePath, format='png')
            plt.close()
        # Generates a plain text file with the statistics of the experimental readings. 
        elif MODE == "STATS":
            # Inform the user that the stats file is being generated. 
            print("Generating STATS file")
            # Generate a file with statistics about the data
            # Open the stats file for teh experiment in write mode. 
            with open(expStatsFile, "w") as statstream:
                # First item printed to sats file is the experiment number
                statstream.write(exp + ",")
                # The next item printed to the output file is either MCU or SYSTEM.
                # Some experiments focus on just the MCU performance, while others focus on the 
                # system performance. This here just prints if the experiment is a system or MCU
                # type experiment.
                if len(expParams) == 3:
                    statstream.write("MCU,")
                else:
                    statstream.write("SYSTEM,")
                # Print the frequency the experiment was run at
                statstream.write(frequency + ",")
                # Print the voltage the experiment was run at
                statstream.write(voltage + ",")
                # The following entries perform statistical calculations on the 
                # experimental data. The statistical values once calculated are
                # then printed to the output file.
                
                # Calculate and print the mean
                statstream.write("{0:.4f},".format(np.mean(y)))
                # Calculate and print the median
                statstream.write("{0:.4f},".format(np.median(y)))
                # Calculate and print the mode
                statstream.write("{0:.4f},".format(stats.mode(y)[0][0]))
                # Calculate and print the range
                statstream.write("{0:.4f},".format(np.ptp(y)))
                # Calculate and print the variance
                statstream.write("{0:.6f},".format(np.var(y)))
                # Calculate and print the standard deviation
                statstream.write("{0:.6f},".format(np.std(y)))
                # Calculate and print the minimum
                statstream.write("{0:.4f},".format(np.min(y)))
                # Calculate and print the maximum
                statstream.write("{0:.4f}\n".format( np.max(y)))