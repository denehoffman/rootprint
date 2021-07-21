#!/usr/python3

import ROOT as root
import numpy as np
import sys
from simple_term_menu import TerminalMenu

def list_keys(tfile: root.TFile):
    return (tkey.GetName() for tkey in tfile.GetListOfKeys() if (isinstance(tfile.Get(tkey.GetName()), root.TH1I) or isinstance(tfile.Get(tkey.GetName()), root.TH1F) or isinstance(tfile.Get(tkey.GetName()), root.TH1D)))


def getBlock(i: int):
    if i == 0:
        return " "
    elif i == 1:
        return "▁"
    elif i == 2:
        return "▂"
    elif i == 3:
        return "▃"
    elif i == 4:
        return "▄"
    elif i == 5:
        return "▅"
    elif i == 6:
        return "▆"
    elif i == 7:
        return "▇"
    else:
        return "█"

def rebin(bins: np.ndarray, n: int):
    temp = bins.copy()
    temp = np.trim_zeros(temp)
    while len(temp) > n:
        if (len(temp) / 3) > (len(temp) / 2):
            div2 = True
        else:
            div2 = False
        if div2:
            if len(temp) % 2: # if odd
                temp = np.pad(temp, (0, 1))
            half = np.zeros(int(len(temp) / 2))
            for i in range(int(len(temp) / 2)):
                half[i] += temp[2 * i]
                half[i] += temp[2 * i + 1]
            temp = half
        else:
            if len(temp) % 3: # if doesn't divide by 3
                temp = np.pad(temp, (0, len(temp) % 3))
            third = np.zeros(int(len(temp) / 3))
            for i in range(int(len(temp) / 3)):
                third[i] += temp[3 * i]
                third[i] += temp[3 * i + 1]
                third[i] += temp[3 * i + 2]
            temp = third
    diff = n - len(temp)
    return np.pad(temp, (0, diff))

def pixelate(bins: np.ndarray, n: int):
    fullblocks = np.zeros_like(bins)
    remainder = np.zeros_like(bins)
    for i, b in enumerate(bins):
        fullblocks[i] = b // n
        remainder[i] = b % n
    return fullblocks, remainder


def preview_hist(tkeyname: str):
    global tfile
    hist = tfile.Get(tkeyname)
    bincontent = np.zeros(hist.GetNbinsX())
    for i in range(hist.GetNbinsX()):
        bincontent[i] = int(hist.GetBinContent(i))
    bincontent = rebin(bincontent, 100) # now there are 100 bins
    # TODO needs to be // (maxbin // 100) or something
    fullblocks, remainder = pixelate(bincontent, 100) # // for fullblocks, %8 for remainder
    grid = np.zeros((100, 100))
    for i in range(100):
        for j in range(int(fullblocks[i])):
            grid[i][j] = 8
            grid[i][j+1] = remainder[i]
    line = ""
    for j in range(100):
        for i in range(100):
            line += getBlock(grid[i][j])
        line += "\n"

    return line

fpath = sys.argv[1]
tfile = root.TFile.Open(fpath, "READ")
terminal_menu = TerminalMenu(list_keys(tfile), preview_command=preview_hist, preview_size=0.75)
menu_entry_index = terminal_menu.show()
