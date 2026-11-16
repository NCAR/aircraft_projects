#!/bin/bash
# The following *preliminary* core chemistry variables in the production HRT data file
# were released: H2O_QCL, CO_QCL, N2O_QCL, H2O_PIC, CO_PIC, CO2C_PIC, CH4C_PIC. The
# same data in the LRT file has been updated to final data and the two files no longer 
# agree. To avoid confusion, these variables are set to missing until the final HRT
# data can be merged in.
# -O overwrites an existing output file
INDIR=/scr/raf/Prod_Data/GOTHAAM/HRT/V1.1
OUTDIR=/scr/raf/Prod_Data/GOTHAAM/HRT/V1.2

for file in ${INDIR}/GOTHAAM*h.nc
do
    file=$(basename "$file")
    ncap2 -O -s "H2O_QCL(:)=H2O_QCL.get_miss(); CO_QCL(:)=CO_QCL.get_miss(); N2O_QCL(:)=N2O_QCL.get_miss(); H2O_PIC(:)=H2O_PIC.get_miss(); CO_PIC(:)=CO_PIC.get_miss(); CO2C_PIC(:)=CO2C_PIC.get_miss(); CH4C_PIC(:)=CH4C_PIC.get_miss();" ${INDIR}/$file ${OUTDIR}/$file
done
