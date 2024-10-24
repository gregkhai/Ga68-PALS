import ROOT
import sys
import os
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

def oneexp_positron_lifetime(x, A1, tau1):
    return A1 * np.exp(-x / tau1)

START_LLD = 0.600 #MeV
START_ULD = 1.050 #MeV
STOP_LLD = 0.050 #MeV
STOP_ULD = 0.340 #MeV

blocking_width = 500e-9 #s
coincidence_window = 20e-9 #s

dir = "output"
name = "3_pPs_H2O_digi_0.22_0.44_2.2_clean_123"
name = "3_pPs_H2O_digi_0.22_0.44_2_cyl_21"



if sys.argv[1] == "1":
    time_df = pd.read_csv(f"{name}_time_df.csv")
    times = np.array(time_df)
    diff = times[:,1] - times[:,0]

    counts, bins = np.histogram(diff*1e9, bins= np.arange(0, coincidence_window*1e9, 0.1)) 
    bin_centers = (bins[1:] + bins[:-1])/2
    print(bin_centers)
    bkg = np.mean(counts[bin_centers>15])
    # bkg = 0
    plt.scatter(bin_centers, (counts-bkg)/max(counts), s = 1)
    y = oneexp_positron_lifetime(bin_centers[bin_centers<15], 1, 1.9)
    plt.plot(bin_centers[bin_centers<15]-6, y/max(y))
    plt.yscale("log")
    # plt.ylim([0, 0.2])
    # plt.scatter(bin_centers, counts)
    print(len(diff))
    plt.show()

else:
    filename = f'{dir}/{name}.root'
    inFile = ROOT.TFile.Open(filename, "READ")
    singles = inFile.Get("Singles")

    max_num = singles.GetEntries()
    entryNum = 0

    E = []
    T = []
    E_block = []
    T_block = []

    flag = True
    while flag:
        singles.GetEntry(entryNum)
        # print(getattr(singles, "energy"), getattr(singles, "time"))

        #check that energy is between START CFD ranges. If not continue
        energy1 = getattr(singles, "energy")
        time1 = getattr(singles, "time")
        d1 = getattr(singles, "level1ID")
        #make detector 0 our START detector

        
        if energy1 < START_ULD and energy1 > START_LLD and d1 ==1:#change to 1 if no result
            for i in range(entryNum+1, max_num):
                singles.GetEntry(i)
                energy2 = getattr(singles, "energy")
                time2 = getattr(singles, "time")
                d2 = getattr(singles, "level1ID")
                co_flag = time2 - time1

                if d1 == d2:
                    continue

                if co_flag > coincidence_window:
                    entryNum += 1
                    break
                else:
                    if energy2 < STOP_ULD and energy2 > STOP_LLD:
                        E.append((energy1, energy2))
                        T.append((time1, time2))
                        print((energy1, energy2))
                        entryNum = i

                        # if len(T) == 0:
                        #     break

                        # if abs(time1-T[-1]) < blocking_width:
                        #     E_block.append((energy1, energy2))
                        #     T_block.append((time1, time2))

                        # break          
    
        else:
            entryNum += 1
        if max_num - 1 == entryNum:
            flag = False
        # print(entryNum)
        

    time_df = pd.DataFrame(T)
    energy_df = pd.DataFrame(E)
    time_df.to_csv(f"{name}_time_df.csv", index=False, header= ["time1", "time2"])
    energy_df.to_csv(f"{name}_energy_df.csv", index=False, header= ["energy1", "energy2"])


    times = np.array(T)
    print(times)
    diff = times[:,1] - times[:,0]


    plt.hist(diff*1e9, bins= 100)


    # time_df_block = pd.DataFrame(T_block)
    # energy_df_block = pd.DataFrame(E_block)
    # time_df_block.to_csv(f"{name}_time_df_block.csv", index=False, header= ["time1", "time2"])
    # energy_df_block.to_csv(f"{name}_energy_df_block.csv", index=False, header= ["energy1", "energy2"])
    plt.show()




    #find the first event that is within STOP CFD and within blocking with





    