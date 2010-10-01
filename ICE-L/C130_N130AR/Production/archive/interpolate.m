function interpolate(folder)

%Created by Sean Stroble, Last Modified August 16 2010
%Function:
%	Interpolates Fast O3 data to the nearest second and outputs to file.
%Usage:
%	In matlab navigate to the folder that contains this file and run:
%		interpolate(DIR)
%	Where DIR is a directory containing the *.txt files that need to be interpolated
%	Interpolated files will be output to the same directory with i appended to the filename
%Example
%	interpolate('/scr/raf/Raw_Data/ICE_L/Prod_Data/FO3')

thisdir = pwd;
cd(folder);
Files = dir('*.txt');



%Main Loop
for n=1:numel(Files)
    %Vars
    Tin = [];
    O3in = [];
    
    f=Files(n);
    if (f.name(1) == 'i')
        continue;
    end
    disp(f.name)
    filenameIn = f.name;
    filenameOut = strcat('i', f.name);
    
    filein = fopen(filenameIn); %Open Input File
    header = fgetl(filein); %Get Header (First line)
    
    fileout = fopen(filenameOut, 'w'); %Open Output File
    fprintf(fileout, '%s\n',header); %Write Header
    fclose(fileout); %Close File
    
    fileout = fopen(filenameOut, 'a');
    line = fgetl(filein); %get first data line
    while (ischar(line))
       line = strrep(line, ',', ' ');
       split = sscanf(line, '%lg'); %look for floating point numbers
       
       if (numel(split) == 2) %Make sure there are only 2 values
           if (split(2) == -99999)
               
               if (numel(Tin) > 1)
                   Tout = round(Tin(1)):1:round(Tin(end)); %Create clean list of times
                   O3out = interp1(Tin, O3in, Tout, 'linear', 'extrap'); %Interpolate O3in to Tout  

                   dlmwrite(filenameOut, [Tout',O3out'], '-append'); %Save Data

               elseif (numel(Tin) == 1)
                   fprintf(fileout, '%g,%g\n',round(Tin(1)),-99999); %Write Line
                   
               end
               
               %fileout = fopen(filenameOut, 'a'); %Open Output File
               fprintf(fileout, '%g,%g\n',round(split(1)),-99999); %Write Line
               %fclose(fileout); %Close File
               
               Tin = [];
               O3in = [];
           else
               Tin(end+1) = split(1); %Save Time
               O3in(end+1) = split(2); %Save O3
           end
       else
           disp(strcat('UNKOWN LINE FORMAT: ', line));
       end
       line = fgetl(filein); %Get next Line
    end
    
    fclose(filein);
    
    if (numel(Tin) > 1)
        Tout = round(Tin(1)):1:round(Tin(end)); %Create clean list of times
        O3out = interp1(Tin, O3in, Tout, 'linear', 'extrap'); %Interpolate O3in to Tout  
 
        dlmwrite(filenameOut, [Tout',O3out'], '-append'); %Save Data
 
        Tin = [];
        O3in = [];
    elseif (numel(Tin) == 1)
        %fileout = fopen(filenameOut, 'a'); %Open Output File
        fprintf(fileout, '%g,%g\n',round(Tin(1)),-99999); %Write Line
        %fclose(fileout); %Close File
    end
    
    fclose(fileout); %Close File
    
end;

cd(thisdir);

return;
