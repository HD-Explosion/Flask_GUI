import csv as cs
import os
from pathlib import Path
from app import app
import pandas as pd
from app.routes import app

def fileread(filename):
    Time_f = 's'
    # Open csv file
    File_name = str(filename)
    file_to_open = os.path.join(app.config['USER_FOLDER'],File_name)
    csvFile = open(file_to_open, "r")
    reader = cs.reader(csvFile)
    Columns = []
    Data1 = pd.DataFrame(columns=Columns)
    n, i = 0, 0
    Sequence = ''
    Sequence_number = ''
    Time_Points = []
    Proteins = []
    States = []
    # Read data form reader to Data
    for item in reader:
        if n != 0:
            if item[0] in Proteins:
                if item[8] in States:
                    if Sequence_number != item[1] + '-' + item[2]:
                        i += 1
                        Sequence_number = item[1] + '-' + item[2]
                        Data1.loc[i, item[0]] = Sequence_number
                        Data1.loc[i, item[0] + '_' + 'MaxUptake'] = item[6]
                    if Time_f == 's':
                        Time = str(int(float(item[9]) * 60 + 0.5))
                    else:
                        Time = item[9]
                    State = item[8]
                    Protein = item[0]
                    if Time != '0':
                        if Time not in Time_Points:
                            Time_Points.append(Time)
                        Data1.loc[i, Protein + '_' + State + '_' + Time] = item[12]
                        Data1.loc[i, Protein + '_' + State + '_' + Time + '_SD'] = item[13]
                else:
                    States.append(item[8])
                    if Sequence_number != item[1] + '-' + item[2]:
                        i += 1
                        Sequence_number = item[1] + '-' + item[2]
                        Data1.loc[i, item[0]] = Sequence_number
                        Data1.loc[i, item[0] + '_' + 'MaxUptake'] = item[6]
                    if Time_f == 's':
                        Time = str(int(float(item[9]) * 60 + 0.5))
                    else:
                        Time = item[9]
                    State = item[8]
                    Protein = item[0]
                    if Time != '0':
                        if Time not in Time_Points:
                            Time_Points.append(Time)
                        Data1.loc[i, Protein + '_' + State + '_' + Time] = item[12]
                        Data1.loc[i, Protein + '_' + State + '_' + Time + '_SD'] = item[13]
            else:
                i = 0
                Proteins.append(item[0])
                if item[8] in States:
                    if Sequence_number != item[1] + '-' + item[2]:
                        i += 1
                        Sequence_number = item[1] + '-' + item[2]
                        Data1.loc[i, item[0]] = Sequence_number
                        Data1.loc[i, item[0] + '_' + 'MaxUptake'] = item[6]
                    if Time_f == 's':
                        Time = str(int(float(item[9]) * 60 + 0.5))
                    else:
                        Time = item[9]
                    State = item[8]
                    Protein = item[0]
                    if Time != '0':
                        if Time not in Time_Points:
                            Time_Points.append(Time)
                        Data1.loc[i, Protein + '_' + State + '_' + Time] = item[12]
                        Data1.loc[i, Protein + '_' + State + '_' + Time + '_SD'] = item[13]
                else:
                    States.append(item[8])
                    if Sequence_number != item[1] + '-' + item[2]:
                        i += 1
                        Sequence_number = item[1] + '-' + item[2]
                        Data1.loc[i, item[0]] = Sequence_number
                        Data1.loc[i, item[0] + '_' + 'MaxUptake'] = item[6]
                    if Time_f == 's':
                        Time = str(int(float(item[9]) * 60 + 0.5))
                    else:
                        Time = item[9]
                    State = item[8]
                    Protein = item[0]
                    if Time != '0':
                        if Time not in Time_Points:
                            Time_Points.append(Time)
                        Data1.loc[i, Protein + '_' + State + '_' + Time] = item[12]
                        Data1.loc[i, Protein + '_' + State + '_' + Time + '_SD'] = item[13]
        else:
            n = n + 1
    csvFile.close()
    return (Proteins, States, Time_Points,Data1)