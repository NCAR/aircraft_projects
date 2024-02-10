#!/usr/bin/env python3
#
#-------------------------------------------------------------------------------
# Name:        process_ads_data_veloc.py
# Purpose:     Transform engine velocimeter data from a real-time ADS data feed
#              and output a UDP feed of the processed data back to ADS server (or display)
#
# Author:      jcarnes
#
# Created:     06/02/2024
# Copyright:   (c) jcarnes 2024
# Licence:     <your licence>
#-------------------------------------------------------------------------------

# Description
#  Script reads data from stdin, performs Digital Signal Processing, and then outputs processed data.
#  - Data should be piped into stdin from a real-time ADS data feed (i.e. data_dump)
#      $ data_dump -i 19,160 | python process_ads_data_veloc.py -u -a 192.168.84.2 -p 56775
#  - or run on an existing .ads file to display the data (or route to file)
#      $ data_dump -i 19,160 {dataFile}.ads | python process_ads_data_veloc.py -d > saveFile.dat

#  More specifically, velocimeter data is sampled on 4 channels of a GP-DACQ unit(100SPS)
#  in the C130. This script accesses the data in real-time, parses, and performs the DSP.
#  The DSP includes FIR(len=61) bandpass filtering @ 17Hz, root-mean-square on a 1-2sec window,
#  and scales the signal to match the readout of the VXP propellor balancing system.
#  Most of the signal path operates on an (N_ch x M_samp) numpy array 'data'

import sys
import getopt
import numpy
import socket
import time
from datetime import datetime

# Get a specified # of lines from stdin. Reject lines of length less than minimum.
#   Return a list of lines. Terminations unmodified.
def get_stdin_lines(num_lines=1, min_len=2):
    count = 0
    lines_list = []
    while (count < num_lines):
        line = sys.stdin.readline()
        if (len(line) < 1): # end of file reached
            raise EOFError()
        if (len(line) < min_len): # throw out short lines and extra line terminations
            continue

        lines_list.append(line)
        count = count + 1
    #--- end while

    return lines_list
#--- end get_stdin_lines()


# Strip off data_dump formatting to retrieve just the sample data
def strip_ads_data_dump_line(line):
    return ''.join(line.strip().split()[6:]) # split by whitespace
#---end strip_data_dump_line()


# Parse data from GPDACQ. Throw away non-sample lines
#  Output 4xN numpy matrix for 4 GPDACQ channels
def parse_data_lines_gpdacq(lines_list):

    # Pre-allocate max array size
    data = numpy.zeros((4,len(lines_list)), dtype=float)

    data_index = 0
    for line in lines_list:

        try:
            sample_str = strip_ads_data_dump_line(line)
            if (sample_str[0] != '#'): # only consider sample lines
                continue
            parsed_str = sample_str[1:].split(',')
            data[0,data_index] = float(int(parsed_str[1],16)) # hex string to float
            data[1,data_index] = float(int(parsed_str[2],16))
            data[2,data_index] = float(int(parsed_str[3],16))
            data[3,data_index] = float(int(parsed_str[4],16))
            data_index = data_index + 1

        except:
            continue
        #---end try

    #---end for

    data = data[:,0:data_index] # remove unused allocation

    return data
#---end parse_data_lines_gpdacq


# Scale the GP-DACQ data
#   Assumes 20-bit output, +/-10V inumpyut range
def scale_data_gpdacq(data):
    return 19.073486e-6 * (data - 524288.0)
#---end scale_data_gpdacq


##  FIR BPF, Fc=0.165/Fs BW=0.062/Fs, len=61, window method (flattop)
##  Matlab Code:
##    N_filt = 10*6+1;
##    win = window(@flattopwin, N_filt)';
##    Gp_win = sqrt(sum(win.^2));
##    Gdc_win = sqrt(sum(win));
##    h_winsin = sin(2*pi*(0:1:N_filt-1)/6).* win;
##    h_winsin = h_winsin / 6.48 ;
##    freqz(h_winsin, 1, 1000)
##    figure
##    plot(h_winsin)
##    for i=0:1:length(h_winsin)-1
##        fprintf('h_imp[%d] = %.8f\n', i, h_winsin(i+1))
##    end
def get_fir_coefficients():
    # FIR impulse response coefficients
    h_imp = numpy.zeros(61, dtype=float)
    h_imp[0]  = -0.00000000
    h_imp[1]  = -0.00009456
    h_imp[2]  = -0.00021702
    h_imp[3]  = -0.00000000
    h_imp[4]  =  0.00081005
    h_imp[5]  =  0.00134671
    h_imp[6]  =  0.00000000
    h_imp[7]  = -0.00303722
    h_imp[8]  = -0.00419149
    h_imp[9]  = -0.00000000
    h_imp[10] =  0.00685111
    h_imp[11] =  0.00810476
    h_imp[12] =  0.00000000
    h_imp[13] = -0.00943018
    h_imp[14] = -0.00895443
    h_imp[15] = -0.00000000
    h_imp[16] =  0.00421734
    h_imp[17] = -0.00059222
    h_imp[18] = -0.00000000
    h_imp[19] =  0.01594376
    h_imp[20] =  0.02649002
    h_imp[21] =  0.00000000
    h_imp[22] = -0.05225096
    h_imp[23] = -0.06658993
    h_imp[24] = -0.00000000
    h_imp[25] =  0.09509579
    h_imp[26] =  0.10782781
    h_imp[27] =  0.00000000
    h_imp[28] = -0.12678507
    h_imp[29] = -0.13190416
    h_imp[30] = -0.00000000
    h_imp[31] =  0.13190416
    h_imp[32] =  0.12678507
    h_imp[33] = -0.00000000
    h_imp[34] = -0.10782781
    h_imp[35] = -0.09509579
    h_imp[36] = -0.00000000
    h_imp[37] =  0.06658993
    h_imp[38] =  0.05225096
    h_imp[39] =  0.00000000
    h_imp[40] = -0.02649002
    h_imp[41] = -0.01594376
    h_imp[42] = -0.00000000
    h_imp[43] =  0.00059222
    h_imp[44] = -0.00421734
    h_imp[45] =  0.00000000
    h_imp[46] =  0.00895443
    h_imp[47] =  0.00943018
    h_imp[48] =  0.00000000
    h_imp[49] = -0.00810476
    h_imp[50] = -0.00685111
    h_imp[51] = -0.00000000
    h_imp[52] =  0.00419149
    h_imp[53] =  0.00303722
    h_imp[54] =  0.00000000
    h_imp[55] = -0.00134671
    h_imp[56] = -0.00081005
    h_imp[57] = -0.00000000
    h_imp[58] =  0.00021702
    h_imp[59] =  0.00009456
    h_imp[60] =  0.00000000
    return h_imp

#---end get_fir_coefficients()


# Filter the data: convolve 2-D data[channel,samples] with fir_num_coeffs
#   Trims boundaries. Only returns (N_sample - N_fir + 1) data points.
def fir_filter_data(data, fir_coeffs):

    M_chan   = len(data)
    N_sample = len(data[0])
    N_fir    = len(fir_coeffs)

    if (N_sample < N_fir):
        print('ERROR fir_filter_data(): not enough points')
        return numpy.zeros((M_chan, N_sample), dtype=float)

    data_filtered = numpy.zeros((M_chan, N_sample - N_fir + 1), dtype=float)
    for m_ch in range(0,M_chan):
        conv = numpy.convolve(numpy.transpose(data[m_ch,:]), fir_coeffs, 'valid') # 'valid', 'full'
        data_filtered[m_ch,:] = conv

    return data_filtered

#---end fir_filter_data()


# Calculate RMS of data in 2-D (M_ch x N_samp) numpy array, scaled by g_float
#   Returns (M_ch x 1) array
def calc_scaled_rms(data, g_float):
    M_ch   = len(data)
    N_samp = len(data[0])
    rms_data = numpy.zeros((M_ch,1), dtype=float) # pre-allocate
    for m_ch in range(0,M_ch):
        rms_data[m_ch] = g_float * numpy.sqrt(sum(pow(data[m_ch,:],2.0)) / N_samp)

    return rms_data
#---end calc_scaled_rms()

def print_args_format():
    print('\n{file}.py [-d] [-u] [-a <ipaddr>] [-p <port>]')
    print('   -d           : Display data to stdout')
    print('   -u           : Send UDP Data')
    print('   -a <ipaddr>  : UDP ip address (default='+UDP_IP_DEFAULT+')')
    print('   -p <port>    : UDP destination port (default='+str(UDP_PORT_DEFAULT)+')')
    print('\n')
#---end print_args_format()


UDP_IP_DEFAULT   = "192.168.84.2"
UDP_PORT_DEFAULT = 56775

def main():

    udp_ip   = UDP_IP_DEFAULT
    udp_port = UDP_PORT_DEFAULT
    udp_send  = False
    disp_data = False

    fir_coeffs = get_fir_coefficients()

    try:
        opts, args = getopt.getopt(sys.argv[1:],"hdua:p:")
    except getopt.GetoptError:
        print_args_format()
        sys.exit(2)
    #---end try

    for opt, arg in opts:
        if opt == '-h':
            print_args_format()
            sys.exit()
        elif opt in ("-d"):
            disp_data = True
        elif opt in ("-u"):
            udp_send = True
        elif opt in ("-a"):
            udp_ip = arg
        elif opt in ("-p"):
            udp_port = int(arg)
    #---end for

    if (udp_send == True):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    else:
        sock = None
    #---end if

    lines_old = []
    while (True):
        try:
            # Get new batch of samples and process at least every second.
            # Append to previous batch to perform longer sequence analysis.
            lines_new = get_stdin_lines(num_lines = 90, min_len = 10)
            lines = lines_old + lines_new
            lines_old = lines_new

            data_parsed = parse_data_lines_gpdacq(lines)
            data_scaled = scale_data_gpdacq(data_parsed)
            data_filtered = fir_filter_data(data_scaled, fir_coeffs)
            #data_rms = calc_scaled_rms(data_filtered, 75.0) # scaling used on 2/7/2024 Engine Test Run from 2/1 data
            data_rms = calc_scaled_rms(data_filtered, 77.8) # scaling from 2/1 and 2/7 calibration data

            if (disp_data == True):
                print(str(datetime.now()) +
                       ", %.3f,%.3f,%.3f,%.3f" % (data_rms[0], data_rms[1], data_rms[2], data_rms[3]))
            #---end if

            if (udp_send == True):
                udp_payload = "VELOCIM,%.3f,%.3f,%.3f,%.3f\n" % (data_rms[0], data_rms[1], data_rms[2], data_rms[3])
                sock.sendto(udp_payload.encode(), (udp_ip, udp_port))
            #---end if

        except KeyboardInterrupt:
            sys.exit()
        except EOFError:
            sys.exit()
        except Exception as e:
            print('ERROR Exception')
            continue
        #---end try/except
    #---end while

#---end main()

if __name__ == '__main__':
    main()
