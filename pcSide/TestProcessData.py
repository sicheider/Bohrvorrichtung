import ProcessData

"""
main process registers
property                unit                    initial value           upper           lower
position                steps                   0                       1024            1025
speed                   Hz                      1000                    1152            1153
mode                    inc(0)/abs(1)           0                       1280            1281
function                0-4                     0                       1408            1409
acceleration            s/kHz                   1000                    1536            1537
deceleration            s/kHz                   1000                    1664            1665
current                 %%                      200                     1792            1793
sequential              0/1                     0                       1920            1921
dwelltime               unknown                 0                       2048            2049
"""
def main():
    data = ProcessData.ProcessData()
    initList = [[1, 1024, 1025, 0, 1000],
                [2, 1024, 1025, 0, 3000],
                [2, 1026, 1027, 0, 500]]
    sequenceList = [[2, 1, 0],
                    [1, 0, 0],
                    [2, 0, 0],
                    [1, 0, 0],
                    [2, 0, 0],
                    [1, 1, 0]]
    data.writeProcessData(initList, sequenceList)

if __name__ == '__main__':
    main()
