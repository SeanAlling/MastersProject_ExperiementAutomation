# Overview

The following project contains scripts for generating an executable to be loaded onto the target system along with a set of python scrips. The python scripts allow gully autonomous experimentation and data collection.

# Dependencies

## Virtual Instrument Software Architecture (VISA) Driver

A version of a VISA driver needs to be installed. This research used a VISA driver provided by National Instruments, [NI-VISA](https://www.ni.com/en-us/support/downloads/drivers/download.ni-visa.html#346210)

## pyVISA

pyVISA provided python bindings to a VISA driver. This allows VISA to be used within a python program.


# Files

## GenerateExperiments.py

When executed will generate an executable for each experiment. 

## RunExperiments_Setup1.py

Will run each experiment generated from GenerateExperiments.py using a HP66311B source meter and a HP3467A bench multimeter. 

Experimental data is stored in a plain text file with the extension "\*.results file.". The file is saved under the following directory path

```
Experiments/EXP#-VOLTAGE-FREQUENCY
```

* Where # in EXP is the experiment number. 
* VOLTAGE is the supply voltage used to run the experiment. 
* Frequency is the MCU core frequency used for the experiment. 


## RunExperiments_Setup2.py

Will run each experiment generated from GenerateExperiments.py using a HP6644A power supply and a HP3467A bench 
multimeter. 


Experimental data is stored in a plain text file with the extension "\*.results file.". The file is saved under the following directory path

```
Experiments/EXP#-VOLTAGE-FREQUENCY
```

* Where # in EXP is the experiment number. 
* VOLTAGE is the supply voltage used to run the experiment. 
* Frequency is the MCU core frequency used for the experiment. 

## PostProcess_SingleFile.py

Processes the experimental results file and generates a graph in PDF and PNG format along with a text file containing the statistics of the experimental measurements. 

The script takes three arguments
1. Root directory where experimental data is stored. 
2. The experimental name, following the format described in "RunExperiments_Setup1.py" and "RunExperiments_Setup2.py" sections. 
3. Flag that takes one of three values [PDF|PNG|STATS]. The flag selects what output is generated.





# Experiments
## Experiment Set 1: Power Modes
Experiment set 1 are used to characterize the MSP432 to met the datasheet specifications.When performing these experiments the following assumptions are made. 
1. Microcontroller is only device in system
1. All pins are configured as outputs defined to logic state 0. 
1. VCORE is set in mode 0 except for 48MHz operation. 

Under these assumptions all on board peripherals are held in reset, this means no internal clocking is done to the peripherals. As a result no dynamic losses are generated.

Each experiment is ran at 6 different frequencies unless otherwise noted. 
1. 15MHz
1. 3MHz
1. 6MHz
1. 12MHz
1. 24MHz
1. 48MHz

and at 3 different voltages 
1. 1.8V
1. 2.0V
1. 3.3V

In order to perform these experiments the PCB made for this project (V3), was modified so that a source meter could be attached t the microcontroller directly.

Current measurements are taken for thirty seconds using the automated test bench setup.


### Experiment 0: Active Mode
Microcontroller runs with an empty while loop.

```c
...
SYSTEM SETUP
...
while(1)
{

}
```

### Experiment 1: Low Frequency Active Mode
Low frequency active mode. This is one of four experiments in experiment 1 that is run at a single frequency.
As with experiment 0, this experiment measures current consumption using a while(1) loop. 

### Experiment 2: Low Power Mode 0
Microcontroller sets up then goes to LPM0 mode. 

```c
...
SYSTEM SETUP
...
while(1)
{
    PCM_gotoLPM0();
}
```

### Experiment 3: Low Frequency Low Power Mode 0
low frequency LPMO. Device set for low frequency and then transitions to LPM0. Current consumption is measured. 

The second low frequency experiment. The format is the same as experiment 2 but runs at a low frequency. 

### Experiment 4: Low Power Mode 3
Measures the current consumption in LPM3. 

```c
...
SYSTEM SETUP
...
while(1)
{
    PCM_gotoLPM3();
}
```

### Experiment 5: Low Power Mode 4
Device sets up then goes to LPM4. Current is measured. Nothing wakes the device from this operation. 
```c
...
SYSTEM SETUP
...
while(1)
{
    PCM_gotoLPM4();
}
```

### Experiment 6: Low Power Mode 3.5
Device is set up then goes to LPM3.5. Current consumption is measured. Nothing wakes the device from this operation. 

```c
...
SYSTEM SETUP
...
while(1)
{
    PCM_setPowerState(PCM_LPM35_VCORE0);
}
```

### Experiment 7: Low Power Mode 4.5
Measures the current consumption in LPM4.5, shutdown operation. Upon entering LPM45, nothing wakes he system from this mode of operation. 

```c
...
SYSTEM SETUP
...
while(1)
{
    PCM_shutdownDevice(PCM_LPM45_VCORE0);
}
```

This is a special operation in which everything on chip is shut down. Upon waking up, the system memory is corrupt and any static or global variable states is lost unless they were stored to flash for FRAM. If they were stored then the data could be restored by reading the data from memory. 



## Experiment Set 2: Power Modes With LED Toggle.
Experiment set 2 focuses on toggling a single RED led. TThe focus of this test set is to monitor the current consumption of the system and the systems response as it enters and exits different low power modes.

Each of these experiments also run at one of the 6 frequencies or one of three voltages that were used in experimental set 1 unless otherwise indicated.

### Experiment 8
Microcontroller configures itself to run at one of the six high frequencies. Then the microcontroller enters an empty while(1) loop and toggles an LED as fast as it can. 

### Experiment 9
GPO toggled as fast as possible in low frequency mode

### Experiment 10
GPO is toggled at a rate of 500ms. Delay is implemented by polling the systick timer. 


### Experiment 11
Microcontroller toggles a GPO at a rate of 500ms and goes to LPM zero when inactive. Delay is implemented with a 32 bit hardware timer. 32 bit timer is used for simplicity in experiments. In the worst case a 25 bit timer needed for a 500ms delay cycle when the clock rate is set 48MHz. By using the 32 bit counters the 16 bit counters, the same timer can be used for all of the experiments compared to having to use 1 16 bit for some and a 32 bit for the others. This helps keeping the experiments as close to the same as possible. 

### Experiment 12
GPO toggled every 500ms in low frequency mode. Delay is implemented by polling the systick timer.



## Experiment Set 3: System Peripherals
Experiment set 2 is used to measure the current  consumed by each peripheral and device in the system designed for this project. For these experiments the input voltage is held at 3.7V (voltage provided by a lipo battery) and the sweeped across the seven frequencies (six high frequency and one low frequency).

Experiments that read sensor data at timed intervals are also sweeped across the different power modes in order to characterize the power required from waking up from one of these modes and perform  an operation.

The power consumption for these will be higher compared to experiment set 1 because this is looking at current consumption at the system level and not the chip level. One major change compared to experiment set 1 is that for these experiments the system will configure multiple different peripherals. The peripherals will be setup to not run but since they are not in reset will consume some power. 

Another area where extra power is consumed is the DC/DC regulator for the MSP432. This DC/DC converter is a linear regulator which converts the input battery voltage of 3.7V to 3.3V. 

---
**NOTE**

Replacing the MSP432 regulator along with all other regulators to be high efficient switching regulators is an area for future research.

--- 

### Experiment 13A: Enable FRAM Only
MSP432 enables the FRAM and then enters shutdown mode (LPM4.5). Current measurements are then taken for thirty seconds.

The purpose of this experiment is to find the amount of static current that the FRAM subsystem will consume as it is left on.

### Experiment 13B: FRAM Write (I2C)
Writes to entire FRAM. Process is repeated 3 times with a delay of 500ms between write cycles. 
1. First write cycle with increasing numbers
2. Write all zeros
3. Write all ones

This experiment is measuring the current that is consumed to write to the FRAM using I2C.


### Experiment 14: FRAM Reads (I2C)
Read content of FRAM. Read cycle happens three times.

Similar to experiment 13B except only I2C reads are performed.

3 sets of reads are performed 3 times giving a total of 9 read operations from FRAM.

### Experiment 15: FRAM Read & Write (I2C)
Writes to entire FRAM. Process is repeated 3 times with a delay of 50ms between write cycles. 
1. First write cycle with increasing numbers
2. Write all zeros
3. Write all ones

A read is performed after each write. 50ms delay between reads.


### Experiment 16A: HDC1080 Enable Only
MSP432 enables HDC1080 and then enters shutdown mode (LPM4.5). Current measurements are then taken for thirty seconds.

The purpose of this experiment is to find the amount of static current that the HDC1080 subsystem will consume as it is on.

### Experiment 16B: HDC1080 Reads (I2C)
non stop reads performed from the HDC1080 for 30 seconds.  This effectively the following.

```c
...
SYSTEM SETUP
...
while(1)
{
    HDC1080_Read()
}
```

The MSP432 never enters sleep mode, it just always requests data from the HDC1080.


### Experiment 17: HDC1080 Timed Reads (I2C)
A hardware timer is used to signal a I2C read from the HDC1080. Reads are requested at 500 millisecond intervals. While not performing an I2C read, the system will enter a low power mode of operations. 


```c
...
SYSTEM SETUP
...
while(1)
{
    HDC1080_Read()
    ENTER LOW POWER MODE
}
```

This experiment is ran once for each of the different low power modes. The above line "ENTER LOW POWER MODE" will be swapped out for each of the low power modes of operation.


### Experiment 18: HDC1080 Timed Reads wakeup from LPM0 (I2C)
See experiment 17
### Experiment 19: HDC1080 Timed Reads wakeup from LPM3 (I2C)
See experiment 17
### Experiment 20: HDC1080 Timed Reads wakeup from LPM3.5 (I2C)
See experiment 17
### Experiment 21: HDC1080 Timed Reads wakeup from LPM4 (I2C)
See experiment 17
### Experiment 22: HDC1080 Timed Reads wakeup from LPM4.5 (I2C)
See experiment 17


### Experiment 23A: OPT3001 Enable Only (I2C)
Format is same as 16A except using the OPT301 instead of the HDC1080. See Experiment 16A for more information. 
### Experiment 23: OPT3001 Reads (I2C)
non stop reads performed from the OPT3001. Format of experiment is same as 16B. See Experiment 16B for more information.

### Experiment 24: OPT3001 Timed Reads (I2C)
Timer used to signal that a read operation should happen.  Format of experiment is same as 17. See Experiment 16B for more information.

### Experiment 25: OPT3001 Timed Reads wakeup from LPM0 (I2C)
Format of experiment is same as 18. See Experiment 18 for more information.
### Experiment 26: OPT3001 Timed Reads wakeup from LPM3 (I2C)
Format follows experiment 19. See Experiment 19 for more details.
### Experiment 27: OPT3001 Timed Reads wakeup from LPM3.5 (I2C)
Format follows experiment 20. See Experiment 20 for more details.
### Experiment 28: OPT3001 Timed Reads wakeup from LPM4 (I2C)
Format follows experiment 21. See Experiment 21 for more details.
### Experiment 29: OPT3001 Timed Reads wakeup from LPM4.5 (I2C)
Format follows experiment 22. See Experiment 22 for more details.
### Experiment 30: XBee Idle
Format follows experiment 23. See Experiment 23 for more details.
### Experiment 31: XBee Constant Transmission
Format follows experiment 23. See Experiment 23 for more details.
### Experiment 32: XBee Transmission After Wakeup from LPM0 (UART)
Format follows experiment 18. See Experiment 18 for more details.
### Experiment 33: XBee Transmission After Wakeup from LPM3 (UART)
Format follows experiment 19. See Experiment 19 for more details.
### Experiment 34: XBee Transmission After Wakeup from LPM3.5 (UART)
Format follows experiment 20. See Experiment 20 for more details.
### Experiment 35: XBee Transmission After Wakeup from LPM4 (UART)
Format follows experiment 21. See Experiment 21 for more details.
### Experiment 36: XBee Transmission After Wakeup from LPM4.5 (UART)
Format follows experiment 22. See Experiment 22 for more details.
### Experiment 37: Timed Reads OPT3001 Then HDC1080 Then XBee Transmit
MSP432 will iterate taking data measurements from the OPT3001, then the HDC1080, and then transmit collected data over XBee.
### Experiment 38: Display Constant refresh White -> Black -> White
MSP432 toggled E-Ink display between being fully white to fully black and then back to fully white. Measures the current required to update the screen for one cycle.
### Experiment 39: Display Partial Update Numbers
Updates only a portion of the E-Ink display. Measurement the current consumed to do a partial update. 
### Experiment 40: Display Image Update
Multiple pre defined images are stored in flash. Displayed image is changed every 30 seconds after completion of last update. Current consumption is measured per image change.

### Experiment 41: Sending Uncompressed FRAM Data Over XBee Bad Data
No two sequential bytes are the same. Sends 1kB worth of data.

### Experiment 42: Sending Uncompressed FRAM Data Over XBee Good Data
Each byte is the same value. Sends 1kB worth of data.


### Experiment 43: Sending Run Length Encoded Data Over XBee (Worst Case)
No adjacent bytes are the same. So no benefit of actually using RLE as nothing will be compressed. Sends 1kB worth of data.

### Experiment 44: Sending Run Length Encoded Data Over XBee (Best Case)
All data i same value. Transmitted data will benefit from encoded data due to repetition. Input is 1kB of uncoded data.

### Experiment 45: Sending Delta Compressed Data Over XBee
Sends 1kB of data that is ONLY delta encoded. 

### Experiment 46: Sending Delta Compressed And Run Length Encoded Data Over XBee (Worst Case)
Performs DRLE on input data and sends data. Input data is 1kB and sequential values have random values. 

### Experiment 47: Sending Delta Compressed And Run Length Encoded Data Over XBee (Best Case)
Performs DRLE on input data and sends data. Input data is 1kB Where data is linearly increasing.

### Experiment 48: Sending Real Data Over XBee Uncompressed
Sends measured data uncompressed over XBee. Experiment will measure and then send 1kB worth of temperature measurements followed by 1kB of humidity measurements.

### Experiment 49: Sending Real Data Over XBee Run Length Encoded
Sends measured data that is run length encoded over XBee. Experiment will measure and then send 1kB worth of temperature measurements followed by 1kB of humidity measurements.

### Experiment 50: Sending Real Data Over XBee Delta Compressed
Sends measured data that has been delta compressed over XBee. Experiment will measure and then send 1kB worth of temperature measurements followed by 1kB of humidity measurements.

### Experiment 51: Sending Real Data Over XBee Delta Compressed and Run Length Encoded
Sends measured data DRLE over XBee. Experiment will measure and then send 1kB worth of temperature measurements followed by 1kB of humidity measurements.




## Experiment Set 4: Power Modes With LED Toggle With System CConfiguration
The following are a a repeat of experiment sets 0 and 1 (experiments 00 - 12). The main difference here is that the configuration of the microprocessor. Where in experiments sets 0 and 1 all pins are set as output and also set to low, this configuration uses the configuration that will be used "In System". What this means is that I2C, SPI, and UART peripherals are active, the associated pins are also active. As can easily be seen with the results is that a significant amount of extra current is drawn. In some cases it can be more than a 10x increase in current draw. 

A surprising observation is that over time the current increases until it reaches a steady state. Steady state is reached about 2/3 minuets after applying power. 

For example, an empty while loop will consume 900uA under ideal conditions (all pins set to output, no internal periphs enabled), but in the configuration of the system I am working on the default current starts at 1.4mA and increases overtime to 2.4mA. That is a 90% increase in current consumption by just having the IO in non defined states ans periphs enabled.



## Experiment set 5: XBee Tx
These experiments send the # of bytes specified, then goes to sleep.
500ms between sending # of bytes. These experiments are all performed at 9600 & 115200 baud with Vin 3.7 volts. 
System will be swept across the frequency range as used in Experiment Set 1.

### Experiment 70
Transmit 1 byte over Xbee communication
### Experiment 71
Transmit  2 byte over Xbee communication
### Experiment 72
Transmit  4 byte over Xbee communication
### Experiment 73
Transmit  8 byte over Xbee communication
### Experiment 74
Transmit  16 byte over Xbee communication
### Experiment 75
Transmit  32 byte over Xbee communication
### Experiment 76
Transmit  64 byte over Xbee communication
### Experiment 77
Transmit  128 byte over Xbee communication
### Experiment 78
Transmit  256 byte over Xbee communication
### Experiment 79
Transmit  512 byte over Xbee communication
### Experiment 80
Transmit  1024 byte over Xbee communication
### Experiment 81
Transmit  2048 byte over Xbee communication
### Experiment 82
Transmit  4096 byte over Xbee communication



# Special Thanks

<table><tr>
<td> <img src="./UCD_EEC.png"  style="width: 250px;"/> </td>
<td> <img src="./MCSG.bmp"  style="width: 250px;"/> </td>
</tr></table>