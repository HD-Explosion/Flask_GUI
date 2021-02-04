import csv as cs
from numpy import *
import numpy as np
import pandas as pd
import matplotlib as mpl

mpl.use('Agg')

import sys

sys.path.append('/root/new_daily/dialy-test/notes/program/newGit/lib/python/')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.gridspec as gridspec
import matplotlib.colors as colors
from scipy import stats
from matplotlib.patches import Polygon
from matplotlib.ticker import ScalarFormatter
import os
from pathlib import Path
import matplotlib.ticker as ticker
from matplotlib import rcParams
rcParams['font.family'] = 'sans-serif'
rcParams['font.sans-serif'] = ['Arial']
from pymol import cmd
from pymol import stored
import matplotlib.path as mpath
import matplotlib.patches as mpatches


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


def v(UserFolder, df, times, proteins, state1, state2, size, colors, file_name, md=0.5, ma=0.01, msi=0.5, xmin=-1.0, xmax=2.0, ymin=5.0, sizeX=6.0, sizeY=6.0, lif=False, tsize=6, nsize=3):
    df1 = pd.DataFrame(columns=['Time point', 'Sequence', 'Difference', 'p-Value'])
    fig, ax = plt.subplots(figsize=(sizeX, sizeY))
    ax.set_yscale("log")
    ax.set_xlim(xmin, xmax)
    ax.set_ylim(0.5, 10** ymin)
    xt = []
    sp = xmin
    while sp <= xmax:
        xt.append(sp)
        sp = sp + msi
    print(sp)
    ax.xaxis.set_ticks(xt, minor=False)
    formatter = ScalarFormatter()
    ax.yaxis.set_major_formatter(formatter)
    y = []
    for i in range(1, (-ymin)):
        y.append(1/10**i)
    ax.set_yticks(y)
    ax.set_xlabel(chr(916) + 'HDX', fontsize=12)
    ax.set_xticklabels(xt, fontsize=10)
    ax.xaxis.set_major_formatter(ticker.FormatStrFormatter('%0.' + str(len(str(msi).split('.')[-1])) + 'f'))
    print(np.linspace(xmin, xmax, num=int((xmax - xmin)/msi) + 1))
    ax.set_yticklabels(y, fontsize=10)
    ax.set_ylabel('$\it{p}$'+'-value', fontsize=12)
    ax.set_title(proteins + '(' + state1 + ')' + '-' + '(' + state2 +')')
    ax.yaxis.set_major_formatter(ticker.FormatStrFormatter('%0.0e'))
    verts = [(-11, ma), (-md, ma), (-md, 0.000000001), (-11, 0.000000001)]
    poly = Polygon(verts, fill=False, edgecolor='0', linestyle='--', lw='1', zorder=0)
    ax.add_patch(poly)
    verts = [(11, ma), (md, ma), (md, 0.000000001), (11, 0.000000001)]
    poly = Polygon(verts, fill=False, edgecolor='0', linestyle='--', lw='1', zorder=0)
    ax.add_patch(poly)
    slist = []
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
            t = (x1 - x2) / np.sqrt(s1 * s1 / nsize + s2 * s2 / nsize)
            p = stats.t.sf(abs(t), nsize)
            d_in_n = []
            p_in_n = []
            d_in_p = []
            p_in_p = []
            d_out = []
            p_out = []
            slist.append(time + 's')
            for a, di in enumerate(d):
                if di >= md and p[a] <= ma:
                    d_in_p.append(di)
                    p_in_p.append(p[a])
                    slist.append(sec[a])
                    if lif and di <= xmax and di >= xmin and p[a] >= 10 ** ymin:
                        ax.text(di, p[a], sec[a], fontsize=tsize)
                elif di <= -1 * md and p[a] <= ma:
                    d_in_n.append(di)
                    p_in_n.append(p[a])
                    slist.append(sec[a])
                    if lif and di <= xmax and di >= xmin and p[a] >= 10 ** ymin:
                        ax.text(di, p[a], sec[a], fontsize=tsize)
                else:
                    d_out.append(di)
                    p_out.append(p[a])
            ax.scatter(d_out, p_out, s=size, linewidths=size/3, zorder=(i+1)*5, color='None', edgecolor='0.8')
            ax.scatter(d_in_n, p_in_n, s=size, linewidths=size/3, label=time + 's', zorder=(i + 1) * 5, color='None', edgecolor=colors[i])
            ax.scatter(d_in_p, p_in_p, s=size, linewidths=size/3, zorder=(i + 1) * 5, color='None', edgecolor=colors[i])
            # ax.vlines(d1.mean(), 0, 1, transform=ax.get_xaxis_transform(), colors=colors[i])
    ax.legend()
    fig.tight_layout()
    df = pd.DataFrame(data={'List':slist})
    df.to_csv(os.path.join(UserFolder, 'list' + ".csv"), sep=',', index=False)
    plt.savefig(os.path.join(UserFolder, file_name + ".eps"), format='eps', dpi=100)
    plt.savefig(os.path.join(UserFolder, file_name + ".png"), format='png', dpi=500)
    #plt.show()
    #df1.to_csv("SSRP1.csv", index=False, sep=',')
    return 0





def heatmap(UserFolder,df, protien, State1, State2, Time_points,f = None,pp = 0.5, min=0., rotation = 'H', max=2.5, step=10, color="Blues", file_name='Heatmap.eps', step2=0, nsize=3):
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
        tv = dif / np.sqrt(s1 * s1 / nsize + s2 * s2 / nsize)
        p = stats.t.sf(abs(tv), nsize)
        if k == 0:
            t = copy(dif)
            pv = copy(p)
            k = k + 1
        else:
            print(dif.shape, t.shape)
            t = np.vstack((t, dif))
            pv = np.vstack((pv, p))
            print(t.mean())
    try:
        [rows, cols] = t.shape
        if f:
            for i in range(rows):
                for j in range(cols):
                    if pv[i, j] >= pp:
                        t[i, j] = 0
    except:
        for i in range(len(t)):
            if pv[i] >= pp:
                t[i] = 0
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
        for c in range(step2 - 1):
            clmap.insert(0,
                         (1.0 - (c + 1) * (1.0 / step2), 1.0 - (c + 1) * (1.0 / step2) / 1.5, 1.0 - (c + 1) * (1.0 / step2)))
    else:
        clmap = [(1.0, 1.0, 1.0), (1.0, 1.0, 1.0)]
        for c in range(step - 1):
            clmap.append((1.0 - (c + 1) * (1.0 / step) / 3, 1.0 - (c + 1) * (1.0 / step), 1.0 - (c + 1) * (1.0 / step)))
        for c in range(step2-1):
            clmap.insert(0, (75/255, 140/255, 97/255))
    cmap = mpl.colors.ListedColormap(clmap)
    if rotation == 'H' or rotation == 'h':
        try:
            im = ax.imshow(t, aspect=3, cmap=cmap, vmin=min, vmax=max)
        except:
            im = ax.imshow(np.vstack([t,t]), aspect=3, cmap=cmap, vmin=min, vmax=max)
        cbar = ax.figure.colorbar(im, ax=ax, orientation='horizontal', fraction=0.12, pad=0.4)
        if 10.8 > len(sec)*0.0612318+1.3243:
            cbar.ax.tick_params(labelsize=len(sec)*0.0612318+1.3243/(step+step2+1)*20)
        else:
            cbar.ax.tick_params(labelsize=10)
        cbar.ax.set_xlabel(protien + ' ' + '(' + State1 + ')' + '-' + '(' + State2 + ')', labelpad=15, va="bottom")
        cbar.set_ticks(np.linspace(min, max, step + step2 + 1))
        cbar.set_ticklabels(np.around(np.linspace(min, max, step + step2 + 1), decimals=3))
        ax.set_xticks(np.arange(len(sec)))
        ax.set_yticks(np.arange(len(Time_points)))
        ax.set_xticklabels(sec)
        ax.set_yticklabels(Time_points)
        ax.set_ylabel('Time (s)', fontsize=8)
        ax.set_xlabel('Peptide Number', fontsize=8)
        ax.set_facecolor('white')
        ax.tick_params(axis='x', labelsize=3.5, pad=0.9, length=3.2)
        ax.tick_params(axis='y', labelsize=10)
        plt.setp(ax.get_xticklabels(), rotation=90, ha="right", va='center', rotation_mode="anchor")
        fig.tight_layout()
        plt.savefig(os.path.join(UserFolder,file_name + ".eps"), format='eps', dpi=100)
        plt.savefig(os.path.join(UserFolder,file_name + ".png"), format='png', dpi=500)

        #plt.show()
    else:
        try:
            im = ax.imshow(t.T, aspect=0.33333333, cmap=cmap, vmin=min, vmax=max)
        except:
            im = ax.imshow(np.vstack([t,t]).T, aspect=3, cmap=cmap, vmin=min, vmax=max)
        cbar = ax.figure.colorbar(im, ax=ax, orientation='horizontal', pad=0.02)
        cbar.ax.set_xlabel(protien + ' ' + '(' + State1 + ')' + '-' + '(' + State2 + ')', labelpad=15, va="bottom")
        cbar.ax.tick_params(labelsize=3/(step+step2+1)*30)
        cbar.set_ticks(np.linspace(min, max, step + step2 + 1))
        cbar.set_ticklabels(np.around(np.linspace(min, max, step + step2 + 1), decimals=3))
        ax.xaxis.tick_top()
        ax.xaxis.set_label_position('top')
        ax.set_yticks(np.arange(len(sec)))
        ax.set_xticks(np.arange(len(Time_points)))
        ax.set_yticklabels(sec)
        ax.set_xticklabels(Time_points)
        ax.set_xlabel('Time', fontsize=6)
        ax.set_ylabel('Peptide Number', fontsize=6)
        ax.set_facecolor('white')
        ax.tick_params(axis='y', labelsize=3.5, pad=0.9, length=3.2)
        ax.tick_params(axis='x', labelsize=10, labelrotation=90)
        plt.setp(ax.get_yticklabels(), rotation=0, ha="right", va='center', rotation_mode="anchor")
        fig.tight_layout()
        plt.savefig(os.path.join(UserFolder,file_name + ".eps"), format='eps', dpi=100)
        plt.savefig(os.path.join(UserFolder,file_name + ".png"), format='png', dpi=500)
        #plt.show()
    return k


def get_ss(id, file_n=''):
    cmd.fetch(file_n)
    cmd.remove('not chain ' + id)
    stored.resi = []
    stored.ss = []
    cmd.dss()
    cmd.iterate("all and n. ca", "stored.resi.append(resi)")
    cmd.iterate("all and n. ca", "stored.ss.append(ss)")
    resi = list.copy(stored.resi)
    resi = list(map(int, resi))
    ss = dict(zip(resi, stored.ss))
    rid = []
    for a, b in ss.items():
        if b == '':
            rid.append(a)
    for r in rid:
        ss.pop(r)
    cmd.remove('chain ' + id)
    return ss

def get_coverage(df, sec, protein):
    peps = list(df[protein])
    while np.core.numeric.NaN in peps:
        peps.remove(np.core.numeric.NaN)
    while nan in peps:
        peps.remove(nan)
    peps = [pep for pep in peps if str(pep) != 'nan']
    coverage = [0] * len(sec)
    le = []
    for pep in peps:
        if len(pep.split('-')) == 4: continue
        if len(pep.split('-')) == 3: pep = '1-' + pep.split('-')[-1]
        for n in range(int(pep.split('-')[0]) - 1, int(pep.split('-')[1])):
            coverage[n] += 1
        le.append(int(pep.split('-')[1]) - int(pep.split('-')[0]))
    red = np.array(coverage).mean()
    avle = np.array(le).mean()
    k = 0
    for c in coverage:
        if c != 0:
            k += 1
    cov = k / len(sec)
    return cov, red, avle


def cm(UserFolder, df, pdb_fn, chianid, protein, sec_h,
       sec, wi, bh, ssp, state1, state2, timepoint, timepoints, file_name,
       min=-1, max=1):
    print(get_coverage(df, sec, protein), len(sec))
    crv = 0.05  # Set the curve for cylinders
    ss = get_ss(chianid, pdb_fn)  # Get secondary structure from PDB file
    ss_w = 0.1
    space = 0.01  # Set space between peptide
    num = 0  # Setting the sequence number
    py = 1  # Setting the position of y
    t_p = True  # Use for take position
    sec_end = len(sec)  # Getting the num of res
    emp_x = 0.2  # White space on left and right
    hps = 0.08  # Height of the num or seq
    peps = list(df[protein])  # Getting the peptides draw on the cm
    ot = True  # The control of the the sequence on top or bottom
    # sec_h = True  # The control of if hide the sequence
    camp = mpl.cm.get_cmap('RdBu')  # Function for get color
    norml = mpl.colors.Normalize(vmin=min, vmax=max)  # Function for normalize data
    # Get difference between two states
    if timepoint == 'avg':
        dif = np.empty((0, len(peps)), float)
        for t in timepoints:
            dif = np.append(dif, [(np.array(float(df[protein + '_' + state2 + '_' + t])) - np.array(float(df[protein + '_' + state1 + '_' + t])))
                       / np.array(float(df[protein + '_MaxUptake']))], axis=0)
        dif = np.mean(dif, axis=0)
    elif timepoint == 'all':
        dif = np.zeros(len(peps), float)
        for t in timepoints:
            dif = dif + (np.array(df[protein + '_' + state2 + '_' + t], dtype=np.float) - np.array(df[protein + '_' + state1 + '_' + t], dtype=np.float))/np.array(df[protein + '_MaxUptake'], dtype=np.float)
    else:
        dif = (np.array(df[protein + '_' + state2 + '_' + timepoint], dtype=np.float) - np.array(df[protein + '_' + state1 + '_' + timepoint], dtype=np.float))/np.array(df[protein + '_MaxUptake'], dtype=np.float)
    dif = dict(zip(peps, list(dif)))
    while np.core.numeric.NaN in peps or nan in peps:
        peps.remove(np.core.numeric.NaN)
    peps = [x for x in peps if str(x) != 'nan']  # Getting ride of space
    # Get the row number
    if sec_end % wi == 0:
        rows = int(sec_end / wi)
    else:
        rows = int(sec_end / wi) + 1
    wx = wi * ssp + emp_x * 2  # Setting the length of the x
    hy = len(peps) * bh + rows * (hps * 2 + 0.1) + 5
    # Creating the figure
    fig = plt.figure(figsize=(wx, hy))
    ax = fig.add_axes([0, 0, 1, 1])
    peps_cr = []  # Creating a list for cross peptides
    # Draw the map row by row
    for row in range(rows):
        path1 = mpath.Path
        # Draw ss
        # Pick ss in this row
        ss_in = ''  # Store ss in the row
        ss_st = 0  # Record the start of the ss
        ss_ed = 0  # Record the edn of the ss
        for ss_res in ss:
            if row * wi < ss_res <= (row + 1) * wi:
                # The start of the ss
                if ss_in == '':
                    ss_in = ss[ss_res]
                    ss_st = ss_res
                    ss_ed = ss_res
                # Draw the ss
                elif ss_in != ss[ss_res] or ss_res == (row + 1) * wi:
                    # Draw loop with line
                    if ss_in == 'L':
                        ax.add_artist(lines.Line2D([emp_x / wx + ((ss_st - 1) % wi) * ssp / wx,
                                                     emp_x / wx + (ss_ed % wi) * ssp / wx],
                                                    [py - ss_w / 2 / hy, py - ss_w / 2 / hy],
                                                    linewidth=1.2, color='k', zorder=1.0))
                    # Draw sheet with arrow
                    if ss_in == 'S':
                        ax.arrow(emp_x / wx + ((ss_st - 1) % wi) * ssp / wx, py - ss_w / 2 / hy,
                                  (ss_ed - ss_st + 1) * ssp / wx, 0,
                                  width=0.0015, color='k', length_includes_head=True, zorder=2.0)
                    # Draw helix with cylinders
                    if ss_in == 'H':
                        # Make sure the helix in row
                        path_data = [
                            (path1.MOVETO, (emp_x / wx + ((ss_st - 1) % wi) * ssp / wx, py - ss_w / hy)),
                            (path1.CURVE4, (emp_x / wx + ((ss_st - 1) % wi) * ssp / wx - crv / wx, py - ss_w / hy)),
                            (path1.CURVE4, (emp_x / wx + ((ss_st - 1) % wi) * ssp / wx - crv / wx, py)),
                            (path1.CURVE4, (emp_x / wx + ((ss_st - 1) % wi) * ssp / wx, py)),
                            (path1.LINETO, (emp_x / wx + ((ss_st - 1) % wi) * ssp / wx +
                                            (ss_ed - ss_st + 1) * ssp / wx, py)),
                            (path1.CURVE4, (emp_x / wx + ((ss_st - 1) % wi) * ssp / wx +
                                            (ss_ed - ss_st + 1) * ssp / wx + crv / wx, py)),
                            (path1.CURVE4, (emp_x / wx + ((ss_st - 1) % wi) * ssp / wx +
                                            (ss_ed - ss_st + 1) * ssp / wx + crv / wx, py - ss_w / hy)),
                            (path1.CURVE4, (emp_x / wx + ((ss_st - 1) % wi) * ssp / wx +
                                            (ss_ed - ss_st + 1) * ssp / wx, py - ss_w / hy)),
                            (path1.CLOSEPOLY, (emp_x / wx + ((ss_st - 1) % wi) * ssp / wx, py - ss_w / hy)),
                        ]
                        codes, verts = zip(*path_data)
                        path2 = mpath.Path(verts, codes)
                        p = mpatches.PathPatch(path2, facecolor='1', zorder=3.0)
                        ax.add_patch(p)
                        path_data = [
                            (path1.MOVETO, (emp_x / wx + ((ss_st - 1) % wi) * ssp / wx +
                                            (ss_ed - ss_st + 1) * ssp / wx, py - ss_w / hy)),
                            (path1.CURVE4, (emp_x / wx + ((ss_st - 1) % wi) * ssp / wx +
                                            (ss_ed - ss_st + 1) * ssp / wx + crv / wx, py - ss_w / hy)),
                            (path1.CURVE4, (emp_x / wx + ((ss_st - 1) % wi) * ssp / wx +
                                            (ss_ed - ss_st + 1) * ssp / wx + crv / wx, py)),
                            (path1.CURVE4, (emp_x / wx + ((ss_st - 1) % wi) * ssp / wx +
                                            (ss_ed - ss_st + 1) * ssp / wx, py)),
                            (path1.CURVE4, (emp_x / wx + ((ss_st - 1) % wi) * ssp / wx +
                                            (ss_ed - ss_st + 1) * ssp / wx - crv / wx, py)),
                            (path1.CURVE4, (emp_x / wx + ((ss_st - 1) % wi) * ssp / wx +
                                            (ss_ed - ss_st + 1) * ssp / wx - crv / wx, py - ss_w / hy)),
                            (path1.CURVE4, (emp_x / wx + ((ss_st - 1) % wi) * ssp / wx +
                                            (ss_ed - ss_st + 1) * ssp / wx, py - ss_w / hy)),
                        ]
                        codes, verts = zip(*path_data)
                        path2 = mpath.Path(verts, codes)
                        p = mpatches.PathPatch(path2, facecolor='1', zorder=3.0)
                        ax.add_patch(p)
                    ss_in = ss[ss_res]
                    ss_st = ss_res
                    ss_ed = ss_res
                else:
                    ss_ed = ss_res
        if ss_ed != (row + 1) * wi:
            if ss_in == 'L':
                ax.add_artist(lines.Line2D([emp_x / wx + ((ss_st - 1) % wi) * ssp / wx,
                                             emp_x / wx + (ss_ed % wi) * ssp / wx],
                                            [py - ss_w / 2 / hy, py - ss_w / 2 / hy],
                                            linewidth=1.2, color='k', zorder=1.0))
            if ss_in == 'S':
                ax.arrow(emp_x / wx + ((ss_st - 1) % wi) * ssp / wx, py - ss_w / 2 / hy,
                          (ss_ed - ss_st + 1) * ssp / wx, 0,
                          width=0.0015, color='k', length_includes_head=True, zorder=2.0)
            if ss_in == 'H':
                path_data = [
                    (path1.MOVETO, (emp_x / wx + ((ss_st - 1) % wi) * ssp / wx, py - ss_w / hy)),
                    (path1.CURVE4, (emp_x / wx + ((ss_st - 1) % wi) * ssp / wx - crv / wx, py - ss_w / hy)),
                    (path1.CURVE4, (emp_x / wx + ((ss_st - 1) % wi) * ssp / wx - crv / wx, py)),
                    (path1.CURVE4, (emp_x / wx + ((ss_st - 1) % wi) * ssp / wx, py)),
                    (path1.LINETO, (emp_x / wx + ((ss_st - 1) % wi) * ssp / wx +
                                                (ss_ed - ss_st + 1) * ssp / wx, py)),
                    (path1.CURVE4, (emp_x / wx + ((ss_st - 1) % wi) * ssp / wx +
                                    (ss_ed - ss_st + 1) * ssp / wx + crv / wx, py)),
                    (path1.CURVE4, (emp_x / wx + ((ss_st - 1) % wi) * ssp / wx +
                                    (ss_ed - ss_st + 1) * ssp / wx + crv / wx, py - ss_w / hy)),
                    (path1.CURVE4, (emp_x / wx + ((ss_st - 1) % wi) * ssp / wx +
                                    (ss_ed - ss_st + 1) * ssp / wx, py - ss_w / hy)),
                    (path1.CLOSEPOLY, (emp_x / wx + ((ss_st - 1) % wi) * ssp / wx, py - ss_w / hy)),
                ]
                codes, verts = zip(*path_data)
                path2 = mpath.Path(verts, codes)
                p = mpatches.PathPatch(path2, facecolor='1', zorder=3.0)
                ax.add_patch(p)
                path_data = [
                    (path1.MOVETO, (emp_x / wx + ((ss_st - 1) % wi) * ssp / wx +
                                    (ss_ed - ss_st + 1) * ssp / wx, py - ss_w / hy)),
                    (path1.CURVE4, (emp_x / wx + ((ss_st - 1) % wi) * ssp / wx +
                                    (ss_ed - ss_st + 1) * ssp / wx + crv / wx, py - ss_w / hy)),
                    (path1.CURVE4, (emp_x / wx + ((ss_st - 1) % wi) * ssp / wx +
                                    (ss_ed - ss_st + 1) * ssp / wx + crv / wx, py)),
                    (path1.CURVE4, (emp_x / wx + ((ss_st - 1) % wi) * ssp / wx +
                                    (ss_ed - ss_st + 1) * ssp / wx, py)),
                    (path1.CURVE4, (emp_x / wx + ((ss_st - 1) % wi) * ssp / wx +
                                    (ss_ed - ss_st + 1) * ssp / wx - crv / wx, py)),
                    (path1.CURVE4, (emp_x / wx + ((ss_st - 1) % wi) * ssp / wx +
                                    (ss_ed - ss_st + 1) * ssp / wx - crv / wx, py - ss_w / hy)),
                    (path1.CURVE4, (emp_x / wx + ((ss_st - 1) % wi) * ssp / wx +
                                    (ss_ed - ss_st + 1) * ssp / wx, py - ss_w / hy)),
                ]
                codes, verts = zip(*path_data)
                path2 = mpath.Path(verts, codes)
                p = mpatches.PathPatch(path2, facecolor='1', zorder=3.0)
                ax.add_patch(p)
        py -= ss_w / hy  # Take the position of ss
        if ot:  # Make judgement if the sequence on top
            # Draw the sec and sec num on the top of the row
            while num <= wi * (row + 1) - 1 and num <= sec_end - 1:
                # Draw sec num
                if (num + 1) % 5 == 0 or num % wi == 0:
                    ax.text(emp_x / wx + (num % wi) * ssp / wx, py - (hps / hy), str(num + 1), size=8)
                # Draw sec or sticks
                if sec_h:
                    if (num + 1) % 5 == 0 or num % wi == 0:
                        x_p = emp_x / wx + (num % wi) * ssp / wx
                        ax.add_artist(lines.Line2D([x_p, x_p], [py - hps * 1.8 / hy, py - hps * 1.1 / hy],
                                                    linewidth=0.5, color='k'))
                else:
                    ax.text(emp_x / wx + (num % wi) * ssp / wx, py - (hps * 2 / hy), sec[num], size=8)
                num += 1
            py -= (hps * 2 + 0.04) / hy  # Set the position for the sec
        ind = np.array([np.zeros(wi)])  # Setting up indicator for peptide position
        pp = 0  # Setting the peptide position
        # Drawing cross peptides
        for pep in peps_cr:
            # Draw the box
            p = plt.Rectangle((emp_x / wx, py - pp * (bh + space) / hy), (int(pep.split('-')[1]) - row * wi) * ssp / wx,
                              bh / hy, facecolor=camp(norml(dif[pep])), edgecolor='k', lw=0.5)
            ax.add_patch(p)
            for x in range(int(pep.split('-')[1]) - row * wi):
                ind[pp][x] = 1  # Take the position of the peptide
            # Creating new line in the indicator
            pp += 1
            ind = np.append(ind, [np.zeros(wi)], axis=0)
        peps_cr = []  # Empty the list for cross peptides
        # Get peps in the sec range
        pep_row = [x for x in peps if row * wi < int(x.split('-')[0]) <= (row+1) * wi]
        # Draw the peptide in row
        for pep in pep_row:
            if len(pep.split('-')) == 4: continue
            if len(pep.split('-')) == 3: pep = '0-'+pep.split('-')[-1]
            if int(pep.split('-')[1]) <= (row + 1) * wi:  # Find out if the peptide is cross rows
                # Make sure the peptide can take the position
                for pp in range(len(ind)):
                    t_p = True  # Use for take position
                    for res in range(int(pep.split('-')[0]) - 1, int(pep.split('-')[1])):
                        if ind[pp][res % wi] == 1:
                            t_p = False
                            break
                    if t_p:
                        break
                # Make sure if need to add a new row
                if not t_p:
                    pp += 1
                    ind = np.append(ind, [np.zeros(wi)], axis=0)
                p = plt.Rectangle((emp_x / wx + ((int(pep.split('-')[0]) - 1) % wi) * ssp / wx, py - pp * (bh + space) / hy),
                                  (int(pep.split('-')[1]) - int(pep.split('-')[0])) * ssp / wx, bh / hy,
                                  facecolor=camp(norml(dif[pep])), edgecolor='k', lw=0.5)
                ax.add_patch(p)
                # Take the position
                for res in range(int(pep.split('-')[0]) - 1, int(pep.split('-')[1])):
                    ind[pp][res % wi] = 1
            else:
                peps_cr.append(pep)
                # Make sure the peptide can take the position
                for pp in range(len(ind)):
                    t_p = True  # Use for take position
                    for res in range(int(pep.split('-')[0]) - 1, wi * (row + 1)):
                        if ind[pp][res % wi] == 1:
                            t_p = False
                            break
                    if t_p:
                        break
                # Make sure if need to add a new row
                if not t_p:
                    pp += 1
                    ind = np.append(ind, [np.zeros(wi)], axis=0)
                p = plt.Rectangle((emp_x / wx + ((int(pep.split('-')[0]) - 1) % wi) * ssp / wx, py - pp * (bh + space) / hy),
                                  (wi * (row + 1) + 1 - int(pep.split('-')[0])) * ssp / wx, bh / hy,
                                  facecolor=camp(norml(dif[pep])), edgecolor='k', lw=0.5)
                ax.add_patch(p)
                # Take the position
                for res in range(int(pep.split('-')[0]) - 1, wi * (row + 1)):
                    ind[pp][res % wi] = 1
        # Add space for peptide
        py -= (len(ind) + 1) * (bh + space) / hy
        if not ot:  # Make judgement if the sequence on bottom
            # Draw the sequence on bottom
            while num <= wi * (row + 1) - 1 and num <= sec_end - 1:
                if (num + 1) % 5 == 0 or num % wi == 0:
                    ax.text(emp_x / wx + (num % wi) * ssp / wx, py - hps * 2 / hy, str(num + 1), size=8)
                if sec_h:
                    if (num + 1) % 5 == 0 or num % wi == 0:
                        x_p = emp_x / wx + (num % wi) * ssp / wx
                        ax.add_artist(lines.Line2D([x_p, x_p], [py - hps * 0.5 / hy, py - hps / hy],
                                                    linewidth=0.5, color='k'))
                else:
                    ax.text(emp_x / wx + (num % wi) * ssp / wx, py - hps / hy, sec[num], size=8)
                num += 1
            py -= (hps * 2 + 0.04) / hy  # Set the position for the sec
    p0 = os.path.join(UserFolder, file_name + ".eps")
    p1 = os.path.join(UserFolder, file_name + ".png")
    plt.savefig(p0, format='eps', dpi=100)
    plt.savefig(p1, format='png', dpi=500)
    return 0
