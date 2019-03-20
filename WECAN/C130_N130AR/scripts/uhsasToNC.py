# Python3
#
# Merge time shifted CVI UHSAS data into the netCDF files.
# Darin Toohy provided .csv files for each flight with the shifted data.

#Imports
import numpy as np
from netCDF4 import Dataset
import pandas
import math

#fileNames
flightNums = ['{:02d}'.format(x) for x in range(1,17)]
basePath = '/scr/raf_data/WECAN/cvi_merge/'
newDataFile = 'CVI_UHSAS_RF','_for_netcdf_merge.csv'

#Data to overwrite from .csv files
ncKeys = ['AUHSAS_CVIU', 'CUHSAS_CVIU','CONCU500_CVIU', 'CONCU100_CVIU', \
    'TCNTU_CVIU', 'CONCU_CVIU', 'CONCUD', 'CVINLET','CVCFACT']

#AUHSAS is all the raw bins starting at index 14 ON.
#CUHSAS is all the raw bins divided by UFLWC_CVIU
#CVINLET is column 114 in csv (self named)
#CVCFACT is column 115 in csv (self named)
#CONCU100_CVIU is derived... Sum of column 32:end THEN divided by UFLWC_CVIU)
#CONCU500_CVIU is derived... Sum of column 86:end THEN divided by UFLWC_CVIU)
#CONCUD is derived... TACTU_CVIU/(CVCFACT * USMPFLW_CVIU)  ... ONLY REPORT WHEN CVINLET == 0
#UFLWC is derived .... USMPFLW_CVIU * UPRESS_CVIU * 10.0 * (1.0 / (PSXC)) * (273.15 + ATX) / UTMP_CVIU
#CONCU_CVIU is derived ..... TACTU_CVIU / UFLWC_CVIU .... ONLY REPORT WHEN CVINLET != 0 mind the nan
#CUHSAS_CVIU is derived ..... is AUHSAS_CVIU / UFLWC_CVIU
#TCNTU_CVIU is ACTUALLY TACTU_CVIU is derived .... sum of AUHSAS columns

for flight in flightNums:
    ncData = Dataset(basePath+'WECANrf'+flight+'.nc','r+')
    #ncData.close
    ncTime = ncData['Time'][:].data

    #Open csvFile....
    #df = pandas.read_csv(basePath + newDataFile[0] + 'RF' + flight + newDataFile[1], sep='\t', lineterminator='\n')
    df = pandas.read_csv(basePath + newDataFile[0] + flight + newDataFile[1])
    fileTime = np.array(df['juldate'][1:],dtype='int')

    #Convert all relevant data in nc files to nans to allow calculations
    #   without "creating" data
    for key in ncKeys:
        ncData[key][:] = np.nan#-32767

    #Index initialization for csv dataframe
    dfStart = 1
    dfEnd = len(df['juldate'][:])

    #Conditional statements for lining up timestamps between files
    if max(ncTime) < max(fileTime):
        dfEnd = max(ncTime) - max(fileTime)

    if min(ncTime) > min(fileTime):
        dfStart = 1 + min(ncTime) - min(fileTime)
        csvOffset = 0
    else:
        csvOffset = min(fileTime) - min(ncTime)

    #Calculate length of fileData and use offset from nc file time
    csvLen = fileTime[dfEnd] - fileTime[dfStart] #max((fileTime)) - min((fileTime))

    try:
        ncData['CVINLET'][csvOffset : csvOffset + csvLen + 1] = \
            np.array(df['CVINLET'][dfStart:dfEnd], dtype = 'float32')
    except:
        ncData['CVINLET'][csvOffset : csvOffset + csvLen + 1] = \
            np.array(df[' CVINLET'][dfStart:dfEnd], dtype = 'float32')

    ncData['CVINLET'][ncData['CVINLET'] == -9999] = np.nan

    #Spurious
    try:
        ncData['CVCFACT'][csvOffset : csvOffset + csvLen + 1] = \
            np.array(df[' CVCFACT'][dfStart:dfEnd], dtype = 'float32')
    except:
        ncData['CVCFACT'][csvOffset : csvOffset + csvLen + 1] = \
            np.array(df['CVCFACT'][dfStart:dfEnd], dtype = 'float32')

    ncData['CVCFACT'][ncData['CVCFACT'] == -9999] = np.nan

    #Enhancement factor correction.
    ncData['CVCFACT'][csvOffset : csvOffset + csvLen + 1] /= 1.12

    AUHSAS = np.array(df.values[dfStart:dfEnd,14:14+99],dtype='float32')
    AUHSAS[AUHSAS == -9999] = np.nan

    ncData['AUHSAS_CVIU'][csvOffset : csvOffset + csvLen + 1 , 0 , :-1] = AUHSAS

    #sample is usmpflw, pres. is upres, temp. is utmp
    usmpflw = np.array(df['Sample'][dfStart:dfEnd], dtype='float32')
    usmpflw[usmpflw == -9999] = np.nan
    upres = np.array(df['Pres.'][dfStart:dfEnd], dtype = 'float32')
    upres[upres == -9999] = np.nan
    utmp = np.array(df['Box'][dfStart:dfEnd], dtype = 'float32')
    utmp[utmp == -9999] = np.nan

    UFLW =  (usmpflw/60.0) * \
        (upres * 10.0 / ncData['PSXC'][csvOffset : csvOffset + csvLen + 1]) * \
        ((273.15 + ncData['ATX'][csvOffset : csvOffset + csvLen + 1]) / utmp )

    #Sum up all the columns of AUHSAS
    ncData['TCNTU_CVIU'][csvOffset : csvOffset + csvLen + 1] =  \
        np.sum( AUHSAS, axis = 1 )

    #Divide each auhsas column by the calculated flow.
    ncData['CUHSAS_CVIU'][csvOffset : csvOffset + csvLen + 1 , 0 , :-1] = \
        AUHSAS / np.transpose([[UFLW]*99])[:,:,0]

    ncData['CONCU_CVIU'][csvOffset : csvOffset + csvLen + 1] = \
        ncData['TCNTU_CVIU'][csvOffset : csvOffset + csvLen + 1] / UFLW

    #Filter data when in cvi mode
    ncData['CONCU_CVIU'][np.where(ncData['CVINLET'][:] == 0)[0]] = np.nan

    ncData['CONCUD'][csvOffset : csvOffset + csvLen + 1] = \
        ncData['TCNTU_CVIU'][csvOffset : csvOffset + csvLen + 1]/\
        (ncData['CVCFACT'][csvOffset : csvOffset + csvLen + 1] * (usmpflw/60.0) )

    #Filter data when not in cvi mode
    ncData['CONCUD'][np.where(ncData['CVINLET'][:] != 0)[0]] = np.nan

    ncData['CONCU500_CVIU'][csvOffset : csvOffset + csvLen + 1] = \
        np.sum( AUHSAS[:,72:], axis = 1 ) / UFLW

    ncData['CONCU100_CVIU'][csvOffset : csvOffset + csvLen + 1] = \
        np.sum( AUHSAS[:,18:], axis = 1 ) / UFLW

    #Set np.nan values to fill value -32767
    for key in ncKeys[2:]:
        try:
            ncData[key][np.isnan(ncData[key])] = -32767
        except: pass
    for key in ncKeys[:2]:
        for i in range(len(ncData[key][0,0,:])):
            try:
                ncData[key][np.isnan(ncData[key][:,0,i]),0,i] = -32767
            except: pass

    #Save and close nc file.
    ncData.close
