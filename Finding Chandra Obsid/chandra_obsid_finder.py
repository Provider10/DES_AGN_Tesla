import os
from astropy.table import Table, hstack, vstack
import numpy as np
import glob


def finding_chandra_obsids(): ## This is what pings the Chandra Servers. 

    ## This code is configured for Ciao 4.10. Future versions may need to be updated. 
    ciao_check = input("Have you initialized Ciao? (y/n)")
    if ciao_check == "y":
        pass
    elif ciao_check == "n":
        print("Initialize Ciao then restart program")
        quit()
    else:
        print("Invalid entry. Ending program")
        quit()
    
    
    i = 1
    os.system('mkdir Locations_ch_fnd_obsid')
    t = Table.read('catalog_members_relevant.fits')## Obtained from the "Checking Sources" code
    RA, DEC = t['RA'],t['DEC']

    print("As it is written this program is not to be run as a background process. Estimated time of completion: " + str(len(t)*2.0/3600.0)+' hours')
    ## To run as a non parallelized background process, insert an time break of approximately two seconds per process. Forcing more requests can overload the Chandra server, so be careful!
    

    for ra,dec in zip(RA,DEC):
        comma = "find_chandra_obsid "+str(ra)+' ' +str(dec)+ ' >> Locations_ch_fnd_obsid/'+str(ra)+'_'+str(dec)+'.txt'
        os.system(comma)
        print(i)
        if i%50 == 0:
            ## Another option to run as a background process is to input a time break of 5 seconds or so right here, so that every fifty requests, it can catch up. I haven't tested it, but I think it'll work
            print(str(i*100.0/len(t))+' percent complete')
        i = i+1


finding_chandra_obsids() # Function to run 'find_chandra_obsid' on multiple sources. comment out to run analyis on gathered data

Locations = glob.glob('Locations_ch_fnd_obsid/*')

primary_table = Table(data=[[],[],[],[],[],[],[],[],[],[]],names = ['obsid','sepn','inst', 'grat', 'time','obsdate','pinname','target','RA','DEC'], dtype=['i8','f8','S6','S4','f8','S10','S20','S30','f8','f8']) # Table of a standard obsid result
no_match_table = Table(data=[[],[]],names=['RA', 'DEC'],dtype=['f8', 'f8']) #Table of no matches

i=0
    
for match in Locations:
    useful = match[23:-4] ## If you change the file names, this much change too.
    RA, DEC = float(useful.split('_')[0]), float(useful.split('_')[1]) ## Separates the textfiles into ra and dec values
    
    try:
        ls = Table.read(match, format='ascii')
        dummy_table = Table() ## Table to collect all RA and DEC values to easily add them to the existing table

        RA_Col = np.zeros([len(ls),1]) + RA
        dummy_table['RA'] = RA_Col.flatten() ## Maintains array size

        DEC_Col = np.zeros([len(ls),1]) + DEC
        dummy_table['DEC'] = DEC_Col.flatten() ## Maintains array size

        ls = hstack([ls,dummy_table])

        primary_table = vstack([primary_table,ls]) ## Table of all results from this search

    except:
        no_match_table.add_row([RA,DEC]) ## Table of all other results
    i +=1
    if i%1000 == 0:
        print(i)



## Final Table writings
primary_table.write('match_table.fits',overwrite=True) 
no_match_table.write('no_match_table.fits',overwrite=True)


## To delete files generated
# os.system('rm -r Locations_ch_fnd_obsid/')
