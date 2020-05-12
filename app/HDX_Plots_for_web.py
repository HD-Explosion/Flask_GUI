import csv as cs
from numpy import *
import numpy as np
import pandas as pd
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.gridspec as gridspec
import matplotlib.colors as colors
from scipy import stats
from matplotlib.patches import Polygon
from matplotlib.ticker import ScalarFormatter
import os
from pathlib import Path

from matplotlib import rcParams
rcParams['font.family'] = 'sans-serif'
rcParams['font.sans-serif'] = ['Arial']


def wood(df, State1, State2, Time_point):
    df[State1 + '_' + Time_point] = df[State1 + '_' + Time_point].astype('float')
    df[State2 + '_' + Time_point] = df[State2 + '_' + Time_point].astype('float')
    df['dif'] = df[State2 + '_' + Time_point] - df[State1 + '_' + Time_point]
    df[State1 + '_' + Time_point + '_SD'] = df[State1 + '_' + Time_point + '_SD'].astype('float')
    df[State2 + '_' + Time_point + '_SD'] = df[State2 + '_' + Time_point + '_SD'].astype('float')
    df['dif_err'] = df[State2 + '_' + Time_point + '_SD'] + df[State1 + '_' + Time_point + '_SD']
    df['dif_err'] = df['dif_err'].astype('float')
    x = []
    len = []
    for se in df['Sequence Number']:
        s = se.split('-')
        while '' in s:
            s.remove('')
        x.append((float(s[0]) + float(s[1])) / 2)
        len.append(float(s[1]) - float(s[0]))
    fig, ax = plt.subplots(figsize=(20, 10))
    ax.errorbar(x, df['dif'], xerr=len, marker='o', linestyle='', markersize=4, capsize=2)
    ax.grid(True)
    ax.axhline(0, color='black', lw=1)
    ax.set_xlabel('Sequence')
    ax.set_title('dif' + '_' + State1 + '_' + State2 + '_' + Time_point)
    plt.savefig('dif' + '_' + State1 + '_' + State2 + '_' + Time_point + '.eps', format='eps', dpi=1000)
    plt.show()
    return ax


def uptakeplot(df, proteins, Time_points1=[], States=[], cols=1, rows=1, file_name='Multi-page.pdf',
               color=['k', 'b', 'r', 'g', 'y']):
    # Crate grid for plot
    gs = gridspec.GridSpec(rows, cols)
    gs.update(hspace=0.5)
    pp = PdfPages(file_name)
    for protein in proteins:
        x = []
        y = []
        yerr = []
        ax = []
        df.index = df[protein]
        i = 0
        # Plot the uptake plot and save as pdf file
        fig = plt.figure(figsize=(7, 5))
        sec = list(df[protein])
        while np.core.numeric.NaN in sec:
            sec.remove(np.core.numeric.NaN)
        for Sequence_number in sec:
            print(Sequence_number)
            n = 0
            row = (i // cols)
            col = i % cols
            print(row, col)
            ax.append(fig.add_subplot(gs[row, col]))  # Crate the subplot
            ax[-1].set_xscale("log", nonposx='clip')  # Set up log x
            ax[-1].set_ylim([0, float(df.loc[Sequence_number, protein + '_' + 'MaxUptake'])])  # Set up y scale
            ax[-1].set_title(protein + '_' + Sequence_number, fontdict={'fontsize': 6}, pad=-6, loc='right')  # Set title of plot
            ax[-1].tick_params(axis='both', labelsize=4, pad=1.2)
            if int(float(df.loc[Sequence_number, protein + '_' + 'MaxUptake'])) // 5 == 0:
                stp = 1
            else:
                stp = int(float(df.loc[Sequence_number, protein + '_' + 'MaxUptake'])) // 5
            ax[-1].set_yticklabels(list(range(0, int(float(df.loc[Sequence_number, protein + '_' + 'MaxUptake'])) + stp * 2, stp)))
            print(list(range(0, int(float(df.loc[Sequence_number, protein + '_' + 'MaxUptake'])), stp)))
            if row == rows - 1:
                ax[-1].set_xlabel('Time (s)', {'fontsize': 6})
            if col == 0:
                ax[-1].set_ylabel('Uptake (Da)', {'fontsize': 6})
                ax[-1].yaxis.set_label_coords(-0.2, 0.5)
            for State in States:
                n += 1
                for time in Time_points1:  # For 4 time points
                    Line = protein + '_' + State + '_' + time
                    x.append(float(df.loc[Sequence_number, Line]))  # Get y number from df
                    y.append(int(time))
                    yerr.append(2 * float(df.loc[Sequence_number, Line + '_SD']))
                ax[-1].errorbar(y, x, yerr=yerr, marker='o', label=State, linewidth=0.7, markersize=0,
                                elinewidth=0.3, capsize=1, capthick=0.3, color=color[n - 1])
                # Plot one state on the subplot
                y = []
                x = []
                yerr = []
            if row == 0 and col == 0:
                ax[-1].legend(fontsize=4, loc='lower right', bbox_to_anchor=(0, 1.05))  # Set figure legend
            if i == cols * rows - 1:
                plt.savefig(pp, format='pdf')  # Save figure in pdf
                plt.close()  # Close the figure
                fig = plt.figure(figsize=(7, 5))  # Crate new figure
                ax = []
                i = -1
            i = i + 1
        if i == 0:
            plt.close()
        else:
            plt.savefig(pp, format='pdf')  # Save figure in pdf
            plt.close()  # Close the figure

    pp.close()  # Close the pdf file
    text = []
    return text


def v(UserFolder, df, times, proteins, state1, state2, size, colors, file_name, md=0.5, ma=0.01, msi=0.5, xmin=-1.0, xmax=2.0, ymin=5.0, sizeX=6.0, sizeY=6.0, lif=False, tsize=6):
    df1 = pd.DataFrame(columns=['Time point', 'Sequence', 'Difference', 'p-Value'])
    fig, ax = plt.subplots(figsize=(sizeX, sizeY))
    ax.set_yscale("log")
    ax.set_xlim(xmin, xmax)
    ax.set_ylim(0.5, 10** ymin)
    ax.xaxis.set_ticks(list(np.arange(xmin, xmax, msi)), minor=True)
    formatter = ScalarFormatter()
    ax.yaxis.set_major_formatter(formatter)
    y = []
    for i in range(1, (-ymin)):
        y.append(1/10**i)
    print(y)
    ax.set_yticks(y)
    ax.set_xlabel(chr(916) + 'HDX', fontsize=12)
    ax.set_xticklabels(np.arange(xmin, xmax, msi), fontsize=10)
    ax.set_yticklabels(y, fontsize=10)
    ax.set_ylabel('p-Value', fontsize=12)
    verts = [(-11, ma), (-md, ma), (-md, 0.000000001), (-11, 0.000000001)]
    poly = Polygon(verts, fill=False, edgecolor='0', linestyle='--', lw='2', zorder=0)
    ax.add_patch(poly)
    verts = [(11, ma), (md, ma), (md, 0.000000001), (11, 0.000000001)]
    poly = Polygon(verts, fill=False, edgecolor='0', linestyle='--', lw='2', zorder=0)
    ax.add_patch(poly)
    for protein in [proteins]:
        print(protein)
        sec = list(df[protein])
        while np.core.numeric.NaN in sec:
            sec.remove(np.core.numeric.NaN)
        for i, time in enumerate(times):
            print(time)
            try:
                x1 = list(df[protein + '_' + state1 + '_' + time])
                s1 = list(df[protein + '_' + state1 + '_' + time + '_SD'])
                x2 = list(df[protein + '_' + state2 + '_' + time])
                s2 = list(df[protein + '_' + state2 + '_' + time + '_SD'])
            except:
                continue
            while np.core.numeric.NaN in x1:
                x1.remove(np.core.numeric.NaN)
            while np.core.numeric.NaN in s1:
                s1.remove(np.core.numeric.NaN)
            while np.core.numeric.NaN in x2:
                x2.remove(np.core.numeric.NaN)
            while np.core.numeric.NaN in s2:
                s2.remove(np.core.numeric.NaN)
            x2 = np.array(x2).astype(float)
            s2 = np.array(s2).astype(float)
            x1 = np.array(x1).astype(float)
            s1 = np.array(s1).astype(float)
            d = x1 - x2
            t = (x1 - x2) / np.sqrt(s1 * s1 / 3 + s2 * s2 / 3)
            p = stats.t.sf(abs(t), 3)
            d_in_n = []
            p_in_n = []
            d_in_p = []
            p_in_p = []
            d_out = []
            p_out = []
            for a, di in enumerate(d):
                if di >= md and p[a] <= ma:
                    d_in_p.append(di)
                    p_in_p.append(p[a])
                    if lif and di <= xmax and di >= xmin and p[a] >= 10 ** ymin:
                        ax.text(di, p[a], sec[a], fontsize=tsize)
                elif di <= -1 * md and p[a] <= ma:
                    d_in_n.append(di)
                    p_in_n.append(p[a])
                    if lif and di <= xmax and di >= xmin and p[a] >= 10 ** ymin:
                        ax.text(di, p[a], sec[a], fontsize=tsize)
                else:
                    d_out.append(di)
                    p_out.append(p[a])
            ax.scatter(d_out, p_out, s=size, linewidths=size/3, zorder=(i+1)*5, color='None', edgecolor='0.8')
            ax.scatter(d_in_n, p_in_n, s=size, linewidths=size/3, zorder=(i + 1) * 5, color='None', edgecolor=colors[i])
            ax.scatter(d_in_p, p_in_p, s=size, linewidths=size/3, zorder=(i + 1) * 5, color='None', edgecolor=colors[i])
            # ax.vlines(d1.mean(), 0, 1, transform=ax.get_xaxis_transform(), colors=colors[i])
    plt.savefig(os.path.join(UserFolder,file_name + ".eps"), format='eps', dpi=100)
    plt.savefig(os.path.join(UserFolder,file_name + ".png"), format='png', dpi=500)
    #plt.show()
    #df1.to_csv("SSRP1.csv", index=False, sep=',')
    return 0





def heatmap(UserFolder,df, protien, State1, State2, Time_points,f = None,pp = 0.5, min=0., rotation = 'H', max=2.5, step=10, color="Blues", file_name='Heatmap.eps', step2=0):
    k = 0
    sec = list(df[protien])
    print(sec)
    while np.core.numeric.NaN in sec or nan in sec:
        sec.remove(np.core.numeric.NaN)
    sec = [x for x in sec if str(x) != 'nan']
    for time in Time_points:
        # Check tiem points is readable
        try:
            t1 = list(df[protien + '_' + State1 + '_' + time])[0:len(sec)]
            t2 = list(df[protien + '_' + State2 + '_' + time])[0:len(sec)]
            s1 = list(df[protien + '_' + State1 + '_' + time + '_SD'])[0:len(sec)]
            s2 = list(df[protien + '_' + State2 + '_' + time + '_SD'])[0:len(sec)]
        except:
            return 0
        s1 = np.nan_to_num(s1)
        s2 = np.nan_to_num(s2)
        t1 = np.nan_to_num(t1)
        t2 = np.nan_to_num(t2)
        s1 = np.array(s1).astype(float)
        s2 = np.array(s2).astype(float)
        t1 = np.array(t1).astype(float)
        t2 = np.array(t2).astype(float)
        dif = t1 - t2
        tv = dif / np.sqrt(s1 * s1 / 3 + s2 * s2 / 3)
        p = stats.t.sf(abs(tv), 3)
        if k == 0:
            t = copy(dif)
            pv = copy(p)
            k = k + 1
        else:
            print(dif.shape, t.shape)
            t = np.vstack((t, dif))
            pv = np.vstack((pv, p))
            print(t.mean())
    [rows, cols] = t.shape
    if f:
        for i in range(rows):
            for j in range(cols):
                if pv[i, j] >= pp:
                    t[i, j] = 0

    # plt.rcParams['xtick.bottom'] = plt.rcParams['xtick.labelbottom'] = False
    # plt.rcParams['xtick.top'] = plt.rcParams['xtick.labeltop'] = True
    if rotation == 'H':
        fig, ax = plt.subplots(figsize=(len(sec)*0.0612318+1.3243, 3))
    else:
        fig, ax = plt.subplots(figsize=(3, len(sec)*0.0612318+1.3243))
    clmap = [(1.0, 1.0, 1.0)]
    if color == 'r':
        for c in range(step - 1):
            clmap.append((1.0 - (c + 1) * (1.0 / step) / 3, 1.0 - (c + 1) * (1.0 / step), 1.0 - (c + 1) * (1.0 / step)))
    elif color == 'g':
        for c in range(step - 1):
            clmap.append(
                (1.0 - (c + 1) * (1.0 / step), 1.0 - (c + 1) * (1.0 / step) / 1.5, 1.0 - (c + 1) * (1.0 / step)))
    elif color == 'b':
        for c in range(step - 1):
            clmap.append(
                (1.0 - (c + 1) * (1.0 / step), 1.0 - (c + 1) * (1.0 / step), 1.0 - (c + 1) * (1.0 / step) / 1.5))
    elif color == 'rb':
        clmap = [(1.0, 1.0, 1.0), (1.0, 1.0, 1.0)]
        for c in range(step - 1):
            clmap.append((1.0 - (c + 1) * (1.0 / step) / 3, 1.0 - (c + 1) * (1.0 / step), 1.0 - (c + 1) * (1.0 / step)))
        for c in range(step2 - 1):
            clmap.insert(0,
                    (1.0 - (c + 1) * (1.0 / step), 1.0 - (c + 1) * (1.0 / step), 1.0 - (c + 1) * (1.0 / step) / 1.5))
    elif color == 'br':
        clmap = [(1.0, 1.0, 1.0), (1.0, 1.0, 1.0)]
        for c in range(step - 1):
            clmap.append(
                (1.0 - (c + 1) * (1.0 / step), 1.0 - (c + 1) * (1.0 / step), 1.0 - (c + 1) * (1.0 / step) / 1.5))
        for c in range(step2 - 1):
            clmap.insert(0, (1.0 - (c + 1) * (1.0 / step) / 3, 1.0 - (c + 1) * (1.0 / step), 1.0 - (c + 1) * (1.0 / step)))
    elif color == 'gr':
        clmap = [(1.0, 1.0, 1.0), (1.0, 1.0, 1.0)]
        for c in range(step - 1):
            clmap.append(
                (1.0 - (c + 1) * (1.0 / step), 1.0 - (c + 1) * (1.0 / step) / 1.5, 1.0 - (c + 1) * (1.0 / step)))
        for c in range(step2 - 1):
            clmap.insert(0, (1.0 - (c + 1) * (1.0 / step) / 3, 1.0 - (c + 1) * (1.0 / step), 1.0 - (c + 1) * (1.0 / step)))
    elif color == 'o':
        for c in range((step - 1)//2):
            clmap.append(
                (1, 1.0 - ((255-102) / ((step - 1)//2) * (c+1))/255, 1.0 - (255 / ((step - 1)//2) * (c+1))/255))
        for c in range(step - 1 - (step - 1) // 2):
            clmap.append(((255-(230-51)/step*(c+1))/255, (102-(102-20)/step*(c+1))/255, 0))
    elif color == 'ob':
        clmap = [(1.0, 1.0, 1.0), (1.0, 1.0, 1.0)]
        for c in range((step - 1)//2):
            clmap.append(
                (1, 1.0 - ((255-102) / ((step - 1)//2) * (c+1))/255, 1.0 - (255 / ((step - 1)//2) * (c+1))/255))
        for c in range(step - 1 - (step - 1) // 2):
            clmap.append(((255-(230-128)/step*(c+1))/255, (102-(102-51)/step*(c+1))/255, 0))
        for c in range(step2 - 1):
            clmap.insert(0,
                    (1.0 - (c + 1) * (1.0 / step), 1.0 - (c + 1) * (1.0 / step), 1.0 - (c + 1) * (1.0 / step) / 1.5))
    elif color == 'y':
        for c in range((step - 1)//2):
            clmap.append(
                (1, 1, 1.0 - (255 / ((step - 1)//2) * (c+1))/255))
        for c in range(step - 1 - (step - 1) // 2):
            clmap.append(((255-(255-77)/step*(c+1))/255, (255-(255-77)/step*(c+1))/255, 0))
    elif color == 'gr':
        for c in range(step - 1):
            clmap.append((1.0 - (c + 1) * (1.0 / step), 1.0 - (c + 1) * (1.0 / step), 1.0 - (c + 1) * (1.0 / step)))
    elif color == 'bp':
        clmap = [(1.0, 1.0, 1.0), (1.0, 1.0, 1.0)]
        for c in range((step - 1)//2):
            clmap.append(
                (1.0 - ((255-100) / ((step - 1)//2) * (c+1))/255, 1.0 - ((255-149) / ((step - 1)//2) * (c+1))/255, 1.0 - ((255-235) / ((step - 1)//2) * (c+1))/255))
        for c in range(step - 1 - (step - 1) // 2):
            clmap.append(
                ((100-100/step*(c+1))/255, (149-149/step*(c+1))/255,
                 1.0 - ((255 - 150) / ((step - 1)//2) * (c + 1)) / 255))
        for c in range((step - 1)//2):
            clmap.insert(0,
                (1, 1.0 - ((255-0) / ((step - 1)//2) * (c+1))/255, 1))
        for c in range(step - 1 - (step - 1) // 2):
            clmap.insert(0,
                         ((255-(225-23)/(step - 1)//2*(c+1))/255, 0, (255-(225-23)/(step - 1)//2*(c+1))/255))
    elif color == 'bg':
        clmap = [(1.0, 1.0, 1.0), (1.0, 1.0, 1.0)]
        for c in range((step - 1)//2):
            clmap.append(
                (1.0 - ((255-100) / ((step - 1)//2) * (c+1))/255, 1.0 - ((255-149) / ((step - 1)//2) * (c+1))/255, 1.0 - ((255-235) / ((step - 1)//2) * (c+1))/255))
        for c in range(step - 1 - (step - 1) // 2):
            clmap.append(
                ((100-100/step*(c+1))/255, (149-149/step*(c+1))/255,
                 1.0 - ((255 - 150) / ((step - 1)//2) * (c + 1)) / 255))
        for c in range(step - 1):
            clmap.insert(0,
                         (1.0 - (c + 1) * (1.0 / step), 1.0 - (c + 1) * (1.0 / step) / 1.5, 1.0 - (c + 1) * (1.0 / step)))
    else:
        clmap = [(1.0, 1.0, 1.0), (1.0, 1.0, 1.0)]
        for c in range(step - 1):
            clmap.append((1.0 - (c + 1) * (1.0 / step) / 3, 1.0 - (c + 1) * (1.0 / step), 1.0 - (c + 1) * (1.0 / step)))
        for c in range(step2-1):
            clmap.insert(0, (75/255, 140/255, 97/255))
    cmap = mpl.colors.ListedColormap(clmap)
    if rotation == 'H' or rotation == 'h':
        im = ax.imshow(t, aspect=3, cmap=cmap, vmin=min, vmax=max)
        cbar = ax.figure.colorbar(im, ax=ax, orientation='horizontal', fraction=.12, pad=0.4)
        if 10.8 > len(sec)*0.0612318+1.3243:
            cbar.ax.tick_params(labelsize=len(sec)*0.0612318+1.3243/(step+step2+1)*20)
        else:
            cbar.ax.tick_params(labelsize=10)
        cbar.ax.set_xlabel(protien + '_' + State1 + '-' + State2, labelpad=15, va="bottom")
        cbar.set_ticks(np.linspace(min, max, step + step2 + 1))
        cbar.set_ticklabels(np.linspace(min, max, step + step2 + 1))
        ax.set_xticks(np.arange(len(sec)))
        ax.set_yticks(np.arange(len(Time_points)))
        ax.set_xticklabels(sec)
        ax.set_yticklabels(Time_points)
        ax.set_ylabel('Time')
        ax.set_xlabel('Peptide Number')
        ax.set_facecolor('white')
        ax.tick_params(axis='x', labelsize=3.5, pad=0.9, length=3.2)
        ax.tick_params(axis='y', labelsize=10)
        plt.setp(ax.get_xticklabels(), rotation=90, ha="right", va='center', rotation_mode="anchor")
        fig.tight_layout()
        plt.savefig(os.path.join(UserFolder,file_name + ".eps"), format='eps', dpi=100)
        plt.savefig(os.path.join(UserFolder,file_name + ".png"), format='png', dpi=500)

        #plt.show()
    else:
        im = ax.imshow(t.T, aspect=0.33333333, cmap=cmap, vmin=min, vmax=max)
        cbar = ax.figure.colorbar(im, ax=ax, orientation='horizontal', pad=0.02)
        cbar.ax.set_xlabel(protien + '_' + State1 + '-' + State2, labelpad=15, va="bottom")
        cbar.ax.tick_params(labelsize=3/(step+step2+1)*30)
        cbar.set_ticks(np.linspace(min, max, step + step2 + 1))
        cbar.set_ticklabels(np.linspace(min, max, step + step2 + 1))
        ax.xaxis.tick_top()
        ax.xaxis.set_label_position('top')
        ax.set_yticks(np.arange(len(sec)))
        ax.set_xticks(np.arange(len(Time_points)))
        ax.set_yticklabels(sec)
        ax.set_xticklabels(Time_points)
        ax.set_xlabel('Time')
        ax.set_ylabel('Peptide Number')
        ax.set_facecolor('white')
        ax.tick_params(axis='y', labelsize=3.5, pad=0.9, length=3.2)
        ax.tick_params(axis='x', labelsize=10, labelrotation=90)
        plt.setp(ax.get_yticklabels(), rotation=0, ha="right", va='center', rotation_mode="anchor")
        fig.tight_layout()
        plt.savefig(os.path.join(UserFolder,file_name + ".eps"), format='eps', dpi=100)
        plt.savefig(os.path.join(UserFolder,file_name + ".png"), format='png', dpi=500)
        #plt.show()
    return k
