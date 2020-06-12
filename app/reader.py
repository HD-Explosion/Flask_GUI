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
        if item == ['', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '']:
            break
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
            # Check the formart of the file is right
            if item != ['Protein', 'Start', 'End', 'Sequence', 'Modification', 'Fragment', 'MaxUptake', 'MHP', 'State', 'Exposure', 'Center', 'Center SD', 'Uptake', 'Uptake SD', 'RT', 'RT SD']:
                return 0
            n = n + 1

    csvFile.close()
    return (Proteins, States, Time_Points,Data1)





def filesread(filenames):
# Open csv file
    File_names = filenames
    Columns = []
    States = []
    Time_f = 's'
    Data1 = pd.DataFrame(columns=Columns)
    i = 0
    n = 0
    k = 0
    Protein = ''
    for File_name in File_names:
        k += 1
        csvFile = open(os.path.join(app.config['USER_FOLDER'],File_name), "r")
        reader = cs.reader(csvFile)
        Time_Points = []
        Columns = []
        if k == 1:
            Data1 = pd.DataFrame(columns=Columns)
            Sequence_number = ''
            for item in reader:
                if item == ['', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '']:
                    break
                if n != 0:
                    if item[0] == Protein:
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
                            if Time != '0':
                                if Time not in Time_Points:
                                    Time_Points.append(Time)
                                Data1.loc[i, Protein + '_' + State + '_' + Time] = item[12]
                                Data1.loc[i, Protein + '_' + State + '_' + Time + '_SD'] = item[13]
                    elif Protein == '':
                        Protein = item[0]
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
                            if Time != '0':
                                if Time not in Time_Points:
                                    Time_Points.append(Time)
                                Data1.loc[i, Protein + '_' + State + '_' + Time] = item[12]
                                Data1.loc[i, Protein + '_' + State + '_' + Time + '_SD'] = item[13]
                else:
                    if item != ['Protein', 'Start', 'End', 'Sequence', 'Modification', 'Fragment', 'MaxUptake', 'MHP', 'State', 'Exposure', 'Center', 'Center SD', 'Uptake', 'Uptake SD', 'RT', 'RT SD']:
                        return 0
                    n = n + 1
        else:
            i = 0
            n = 0
            Data2 = pd.DataFrame(columns=Columns)
            Sequence_number = ''
            for item in reader:
                if n != 0:
                    if item[0] == Protein:
                        if item[8] in States:
                            if Sequence_number != item[1] + '-' + item[2]:
                                i += 1
                                Sequence_number = item[1] + '-' + item[2]
                                Data2.loc[i, item[0]] = Sequence_number
                                Data2.loc[i, item[0] + '_' + 'MaxUptake'] = item[6]
                            if Time_f == 's':
                                Time = str(int(float(item[9]) * 60 + 0.5))
                            else:
                                Time = item[9]
                            State = item[8]
                            Protein = item[0]
                            if Time != '0':
                                if Time not in Time_Points:
                                    Time_Points.append(Time)
                                Data2.loc[i, Protein + '_' + State + '_' + Time] = item[12]
                                Data2.loc[i, Protein + '_' + State + '_' + Time + '_SD'] = item[13]
                        else:
                            States.append(item[8])
                            if Sequence_number != item[1] + '-' + item[2]:
                                i += 1
                                Sequence_number = item[1] + '-' + item[2]
                                Data2.loc[i, item[0]] = Sequence_number
                                Data2.loc[i, item[0] + '_' + 'MaxUptake'] = item[6]
                            if Time_f == 's':
                                Time = str(int(float(item[9]) * 60 + 0.5))
                            else:
                                Time = item[9]
                            State = item[8]
                            Protein = item[0]
                            if Time != '0':
                                if Time not in Time_Points:
                                    Time_Points.append(Time)
                                Data2.loc[i, Protein + '_' + State + '_' + Time] = item[12]
                                Data2.loc[i, Protein + '_' + State + '_' + Time + '_SD'] = item[13]
                else:
                    if item != ['Protein', 'Start', 'End', 'Sequence', 'Modification', 'Fragment', 'MaxUptake', 'MHP', 'State', 'Exposure', 'Center', 'Center SD', 'Uptake', 'Uptake SD', 'RT', 'RT SD']:
                        return 0
                    n = n + 1
            Data1 = Data1.merge(Data2, on=Protein)
        n = 0
    Data1.to_csv(os.path.join(app.config['USER_FOLDER'],"For_plot.csv"), index=False, sep=',')
    return ([Protein], States, Time_Points, Data1)
