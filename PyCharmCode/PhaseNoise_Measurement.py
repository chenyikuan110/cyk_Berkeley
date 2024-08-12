import os
import time
import datetime
import csv

import pandas as pd
from Codebook.BeamCodebook import BeamCodebook
from SDX55.SDX import SDX
from data_processing.get_polarization import *
from data_processing.freq2arfcn import *
from instrument.signal_analyzer import *
from Instrument_Automation.Signal_Analyzer.SignalAnalyzerN9040B import SignalAnalyzerN9040B

from UXA_PN import uxa_pn_auto as upa

import pyvisa as visa

class PhaseNoise_Measurement:
    # Version 1.1
    # Yikuan Chen
    # Aug 2 2021

    def __init__(self, config_file_name="DEV3_PhaseNoise_Config.csv"):

        # File related
        self.use_Freq_File = 0; # default to be not using frequency file. Change to 1 if have a file.
        self.config_file_name = config_file_name
        self.results_file_name = "DEV3_PhaseNoise_"
        self.measurement_freq = "RF"
        self.freqList_file_name = "RF_freqList.csv"
        self.results_folder_path = "Z:/Documents/GitHub/venv/Mav22_FR2_Code/UXA_PN/UXA_PN_Results"

        # Path loss compensation
        self.Pcomp = 0

        # Instrument related parameters
        self.ip_signal_analyzer = 'TCPIP::192.164.100.11::INSTR'
        self.signal_analyzer = 'UXA'

        # DUT Connection parameters
        self.connectionType = 'QUTS'
        self.comPort = 'COM4'
        self.timeout_in_ms = 2000
        self.isPhoneConnected = [0x00]

        # DUT Setup Parameters
        self.power = 15  # not 1:1 to QRCT
        self.beamID = [128]
        self.freqList = [{"band": 260, "channel": [2237499, 2254167]}]
        self.bw = [100e3]  # kHz, aka here it is 100MHz BW
        self.carrier = 0
        self.numAvg = 10
        self.tRXMode = 'TX'
        self.txMode = 'CONT'  # 'CONT' or 'BURST' -- burst mode is default set to 50% DC
        self.waveformType = 'CW'  # for Phase Noise measurement
        self.modType = 'QPSK'  # doesn't matter when CW is chosen
        self.startRB = 0
        self.numRB = 66

        # Codebook parameters
        self.loadCBFlag = 1  # Load the codebook mapping from the cbDir directory file
        # TODO: make sure you have the correct path for the codebook
        self.cbDir = './Codebook/Codebook_Repo/Single_Element_Codebook_hwid2850.csv'  # Location of cdoebook mapping csv file
        self.bfFlag = 0  # Flag to load in BF codebook (1) from BBFW or single element codebook (0)

        # UXA Test config
        self.uxa_window_span = [100, 100e6]
        self.freq_pts = [12e3, 30e3,  50e6]
        self.power_attn = 20  # dB
        self.avg_count = 5  # averaging number
        self.smoothing = 5  # smoothing percentage
        self.spur_threshold = -85;  # dBc

        # Screen capture option
        self.scr_background = "FILL" # default to be black; can also be OUTL for transparent background

        # DUT
        self.sdxHandler = SDX(self.comPort, connectionType=self.connectionType)

        # UXA
        self.rm = visa.ResourceManager()
        self.UXA = SignalAnalyzerN9040B(self.rm,str(self.ip_signal_analyzer));
        self.freq_config = {'PN_fmin': self.freq_pts[0],  # 12KHz
                            'PN_fmax': self.freq_pts[-1]}  # 50MHz, this is the integration bound
        self.results = [];
        self.spur_table = [];



        # End of constructor


    # helper function: convert string to float or int properly
    def conv_to_num(self,num):
        try:
            a = int(num);
        except (TypeError, ValueError):
            return num; # it's a string
        else:
            if a == float(num): # it's an integer
                return a;
            else:
                return float(num); # it's a float but not int


    # Called to load attributes from a file
    def Read_Config(self):
        config_file_path = os.path.join(self.results_folder_path, self.config_file_name)
        # create results folder path & config file if it does not exist
        if not os.path.exists(self.results_folder_path):
            os.makedirs(self.results_folder_path)
        if not os.path.exists(config_file_path):
            self.Write_header(config_file_path, "",file_type='input');
            print("\nNo config file found. New config template created. \nProgram exits. Please re-run after finishing the config file.\n")
            return 1;

        # begin loading values from file
        print("Loading config from file at" + config_file_path);

        var_keys = list(vars(self).keys());
        config_keys = self.Clear_list(var_keys, 'sdxHandler')

        # set attributes according to the file
        with open(config_file_path, 'r') as config_file:
            for line in csv.reader(config_file):
                if line[0] in config_keys:
                    if line[1][0] == '{' or line[1][0] == '[': # parse dictionary and lists
                        setattr(self, line[0], eval(line[1]));
                    else:
                        setattr(self,line[0],self.conv_to_num(line[1]));
        return 0;


    # Called when band and channel are specified using a file
    def Load_freqList(self):

        freqList_file_path = os.path.join(self.results_folder_path, self.freqList_file_name)

        # if file doesn't exist, create a template
        if not os.path.exists(freqList_file_path):
            print("Creating a frequency list file template.\n")
            print("Example:")
            keys = ['band','channels']
            for each_value in keys:
                print("{:<10}".format(each_value), end='')
            print("")
            vals = [260,2254165,2254167,2254169]
            for each_value in vals:
                print("{:<10}".format(each_value), end='')
            print("\n")

            df = pd.DataFrame(['band','channels']).T
            df.to_csv(freqList_file_path, mode='a', header=False, index=False)
            df = pd.DataFrame(['', '']).T
            df.to_csv(freqList_file_path, mode='a', header=False, index=False)

            print("Please fill in the frequency list file and re-run.")
            return 1;

        # clear the default freqList
        self.freqList = [];
        with open(freqList_file_path, 'r') as freqList_file:
            for line in csv.reader(freqList_file):
                if line[0] == "band":
                    continue;
                else:
                    my_freqList = {"band":int(line[0]), "channel":[]};
                    for chn in line[1:]:
                        my_freqList["channel"].append(int(chn));
                    self.freqList.append(my_freqList);

        return 0;


    # Setting self.<attributes> with a file or keeping default
    def Setup_Config(self):
        while (1):
            user_input = input("\nDo you want to set up config using a file? (y/n)");
            if (user_input == "Y" or user_input == "y"):
                respond = self.Read_Config();
                if(respond == 1):
                    return 1;
                if (self.use_Freq_File == 1):
                    return self.Load_freqList();
                break;
            elif (user_input == "N" or user_input == "n"):
                print("Running with default settings...")
                break;
            print("Invalid input!")
        return 0;



    def Setup_Temp(self):
        # TODO
        return;



    # Establish connection to the DUT
    def Connect_DUT(self):
        # Connect to the DUT
        if self.connectionType == 'QPST' or self.connectionType == 'QUTS':
            self.sdxHandler.ListPorts()
            self.sdxHandler.ConnectSDX()
        else:
            self.sdxHandler.ConnectSerialSDX()

        response = self.sdxHandler.CheckConnection()
        print('\r\nEntering Verify Mode')
        response = self.sdxHandler.EnterVerifyMode(bfCB=self.bfFlag)



    # Called when there're multiple frequencies/bands, otherwise only runs once
    def Set_DUT(self, beamID, band, channel, bw):
        print("\nSetting up DUT\n")
        # loading codebook if flag is set to 1
        if self.loadCBFlag == 1:
            cb = BeamCodebook(codeBookDir=self.cbDir)
            beamMapping = cb.GetBeamMapping(band=band)
            polMapping = cb.GetPolMapping(band=band)

            # This line is for backward compatibility reason
            signalMapping = beamMapping
            self.sdxHandler.SetBeamMapping(signalMapping, polMapping, beamMapping)
            trxID = cb.GetModuleMapping(band=band, beamID=beamID)

        # Instrument related parameters
        RF_Freq = self.sdxHandler.GetRFFreq(channel)
        f_inst = str(float(RF_Freq / 1000000000)) + 'GHz'
        print("Frequency of signal is " + f_inst)
        # signal port is 9(V) or 1(H), corresponding beamID is 0-127 or 128-255
        signalPort = beamID  # not get_signalPort(beamID)
        print("BeamID is " + str(signalPort))

        print("Setting radio config for TX\n")
        response = self.sdxHandler.SetVerifyRadioConfig(band=band, channel=channel,
                                                   bw=bw,
                                                   signalPort=signalPort,
                                                   tRXMode=self.tRXMode,
                                                   mode=self.txMode)
        time.sleep(0.2)

        print("\r\nSetting tx control\n")
        response = self.sdxHandler.SetTXControl(signalPort=signalPort, startWaveform=1, power=self.power,
                                           waveformType=self.waveformType, modType=self.modType,
                                           startRB=self.startRB, numRB=self.numRB)

        time.sleep(0.5)
        powerDET, totalPowerDET = self.sdxHandler.GetVerifyTXMeasure(signalPort=signalPort, numAvg=self.numAvg)
        print("Reading PDET for beamID {0} --> powerDET = {1:2.1f} dBm, totalPowerDET = {2:2.1f} dBm".format(beamID,
                                                                                                             powerDET,
                                                                                                             totalPowerDET))
        time.sleep(0.2)
        return;



    def Setup_UXA(self):
        upa.uxa_setup(self.UXA,self.signal_analyzer, self.ip_signal_analyzer);
        return;



    def Get_UXA_Measurement(self, debugFlag,beamID=0, band=0, channel=0):
        return upa.uxa_pn_run(self.UXA, self.freq_pts, self.freq_config,
                              self.power_attn, self.avg_count, self.smoothing,
                              self.spur_threshold, self.uxa_window_span, debugFlag, beamID, band, channel, self.scr_background);



    def Compensate_UXA_Measurement(self,results, RF_Freq):
        # TODO: this is copied from Trishul's example, not using for now
        cmn_path_loss = round(common_path_loss[round(float(RF_Freq / 1000000000), 1)], 1);
        port_header = "BeamID_" + str(self.beamID[b]) + "_Loss(dB)";
        port_pat_loss = round(port_path_loss.loc[round(float(RF_Freq / 1000000000), 1), port_header], 1);
        results["Power(dBm)"] = round(results["Power(dBm)"] + cmn_path_loss + port_pat_loss, 1);
        return;



    def Stop_Tx(self,beamID=0):
        signalPort = beamID;
        # Turn off the signal power
        response = self.sdxHandler.SetTXControl(signalPort=signalPort, startWaveform=0, power=self.power,
                                                waveformType=self.waveformType, startRB=self.startRB, numRB=self.numRB)
        time.sleep(2.0)

        # Safe teardown of DUT settings and connection
        print("\r\nStopping TX")
        response = self.sdxHandler.SetTXControl(signalPort=signalPort, startWaveform=0, power=0,
                                           waveformType=self.waveformType, startRB=self.startRB, numRB=self.numRB)
        return;



    def End_Measurement(self):
        print("\nDropping all to stop or change channels/polarization or to TRX mode\n")
        response = self.sdxHandler.DropVerifyMode()
        return;



    def Update_results(self, spurs, measurement, beamID=128, band=260, channel=2254167, bw=100e3):

        # check data
        if(measurement == []):
            print("Empty measurement result!");
            return;
        # check spurs
        if(spurs == []):
            print("No spurs found for band "+str(band)+" channel "+str(channel)+".\n");
        else:
            for spur in spurs:
                self.spur_table.append({"band":band,
                                "channel":channel,
                                "beamID":beamID,
                                "spur_freq": spur["spur_freq"],
                                "spur_power": spur["spur_power"]});


        # unsmoothed
        num_pts = len(self.freq_pts);
        self.results.append({"band": band,"channel":channel,"beamID":beamID,"smoothed": 0})
        for i in range(num_pts):
            freq_offset_str = "PNoise at "+str(self.freq_pts[i])+" Hz";
            self.results[-1][freq_offset_str] = measurement[i];
        self.results[-1]["Integrated noise"] = measurement[num_pts];

        # smoothed
        self.results.append({"band": band,"channel":channel,"beamID":beamID,"smoothed": 1})
        for i in range(num_pts):
            freq_offset_str = "PNoise at "+str(self.freq_pts[i])+" Hz";
            self.results[-1][freq_offset_str] = measurement[num_pts+1+i]; # +1 for the int_noise
        self.results[-1]["Integrated noise"] = measurement[num_pts];

        return;


    # Print measurement results on the console in a tidy way
    def Print_results(self):
        # PN
        i = 0;
        keys = list(self.results[0].keys());
        values = self.results;
        for each_value in keys:
            print("{:<{length}}".format(each_value, length=(len(keys[i])+2)), end='')
            i = i+1;
        print("")

        for each_row in values:
            i = 0;
            for each_value in list(each_row.values()):
                print("{:<{length}}".format(each_value, length=(len(keys[i])+2)), end='')
                i = i+1;
            print("")

        # spurs
        if(self.spur_table == []):
            print("\nNo spurs found.");
        else:
            for each_value in list(self.spur_table[0].keys()):
                print("{:<13}".format(each_value), end='')
            print("")

            for each_row in self.spur_table:
                for each_value in list(each_row.values()):
                    print("{:<13}".format(each_value), end='')
                print("")
        return;


    # Remove some unused info from the list
    def Clear_list(self, list_a, element_e):
        new_list = []
        for element_x in list_a:
            if element_x == element_e:
                break
            else:
                new_list.append(element_x)
        return new_list;


    # Called by self.Write_file
    def Write_header(self, file_path, file_full_name, file_type='output'):

        # config header for all csv files
        var_keys = list(vars(self).keys());
        config_keys = self.Clear_list(var_keys,'sdxHandler')
        var_vals = list(vars(self).values());
        config_vals = var_vals[:len(config_keys)]

        # a little bit of extra processing...
        filename_idx = config_keys.index('results_file_name');
        if(file_type=='input'):
            del config_keys[filename_idx];
            del config_vals[filename_idx];
        if(file_type=='output'):
            config_vals[filename_idx] = file_full_name;
            if(self.use_Freq_File == 1):
                freqListIdx = config_keys.index('freqList');
                config_vals[freqListIdx] = "See "+self.freqList_file_name;

        # write config header
        for i in range(len(config_keys)):
            keys_vals = [];
            keys_vals.append(config_keys[i]);
            keys_vals.append(config_vals[i]);
            #print(keys_vals)
            df = pd.DataFrame(keys_vals).T
            df.to_csv(file_path, mode='a', header=False, index=False)
        return;


    # Called by self.Write_file
    def Write_result(self, list_to_write, file_path):

        # add space after header
        df = pd.DataFrame(['', '']).T
        df.to_csv(file_path, mode='a', header=False, index=False)

        # write data header
        data_header = list(list_to_write[0].keys());
        append_row = pd.DataFrame(data_header).T
        append_row.to_csv(file_path, mode='a', header=False, index=False)
        # then append each line
        for each_row in list_to_write:
            result_values = list(each_row.values())
            append_row = pd.DataFrame(result_values).T
            append_row.to_csv(file_path, mode='a', header=False, index=False)


    # The final step is to write result into .csv
    def Write_file(self):

        if(self.results == []):
            print("Empty results!");
            return;

        # add time stamp to the file name
        current_time = datetime.datetime.now().strftime("%H%M")
        today = datetime.datetime.now().strftime("%Y%m%d")

        # output file name
        results_file_full_name = self.results_file_name + self.measurement_freq + "_" + today + "_"+ current_time + ".csv";
        results_file_path = os.path.join(self.results_folder_path, results_file_full_name)

        # create results folder path if it does not exist
        if not os.path.exists(self.results_folder_path):
            os.makedirs(self.results_folder_path)

        # actual write
        self.Write_header(results_file_path, results_file_full_name,file_type='output');
        self.Write_result(self.results, results_file_path);

        # spur table to csv
        if(self.spur_table == []):
            return;
        else:
            # output file name
            spurs_file_full_name = self.results_file_name + self.measurement_freq + "_" + today + "_" + current_time + "_spurTable.csv";
            spurs_file_path = os.path.join(self.results_folder_path, spurs_file_full_name)

            # actual write
            self.Write_header(spurs_file_path, spurs_file_full_name, file_type='output');
            self.Write_result(self.spur_table, spurs_file_path);

        return



    # Executed upon wrap up
    def Exit(self):
        if(len(self.results) <= 100):
            self.Print_results();
        self.Write_file();
        print("\nPhase Noise measurement is done.")



    def Run(self, debugFlag=0):
        # common
        respond = self.Setup_Config();
        if(respond == 1):
            return;
        self.Connect_DUT();
        self.Setup_UXA();

        # for each frequency in the dictionary, organized by bands
        for bandIdx in self.freqList:
            print(bandIdx)
            _band = bandIdx["band"]
            for _channel in bandIdx["channel"]:
                for _beam in self.beamID:
                    _bw = self.bw[0]; # placeholder
                    self.Setup_Temp();
                    self.Set_DUT(beamID=_beam, band=_band, channel=_channel, bw=_bw);

                    spurs, measurement = self.Get_UXA_Measurement(debugFlag,beamID=_beam, band=_band, channel=_channel);

                    self.Stop_Tx(beamID=_beam);
                    self.End_Measurement();

                    if(spurs==[] and measurement == []): # timeout happens
                        if(self.results != []):
                            self.Exit();
                        else:
                            print("\nProgram terminated. No measurement was done.")

                    self.Update_results(spurs, measurement, beamID=_beam, band=_band, channel=_channel, bw=_bw)

        self.Exit();


        # self.sdxHandler.CloseConnection()



