#!/usr/python3

import ROOT as root
import numpy as np
import sys
from os import system, name
from simple_term_menu import TerminalMenu

def clear():
    if name == 'nt':
        system('cls')
    else:
        system('clear')

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
    nrebins = 0
    if len(temp) > n:
        while len(temp) > n:
            if len(temp) % 2: # if odd
                temp = np.pad(temp, (0, 1))
            half = np.zeros(int(len(temp) / 2))
            for i in range(0, int(len(temp) / 2)):
                half[i] += temp[2 * i]
                half[i] += temp[2 * i + 1]
            temp = half
    diff = n - len(temp)
    return np.pad(temp, (0, diff))

def pixelate(bins: np.ndarray, n: int):
    fullblocks = np.zeros_like(bins)
    remainder = np.zeros_like(bins)
    scaled = np.interp(bins, (bins.min(), bins.max()), (0, 8 * n))
    for i, b in enumerate(scaled):
        fullblocks[i] = int(b // 8)
        remainder[i] = int(b % 8)
    return fullblocks, remainder


def preview_hist(tkeyname: str):
    global tfile
    X_SCALE = 180
    Y_SCALE = 40
    hist = tfile.Get(tkeyname)
    bincontent = np.zeros(hist.GetNbinsX())
    for i in range(hist.GetNbinsX()):
        bincontent[i] = int(hist.GetBinContent(i))
    bincontent = rebin(bincontent, X_SCALE)
    fullblocks, remainder = pixelate(bincontent, Y_SCALE)
    grid = np.zeros((X_SCALE, Y_SCALE))
    for i in range(X_SCALE):
        for j in range(int(fullblocks[i])):
            grid[i][j] = 8
            if remainder[i]:
                grid[i][j+1] = remainder[i]
    line = ""
    for j in range(Y_SCALE):
        for i in range(X_SCALE):
            line += getBlock(grid[i][Y_SCALE - j - 1])
        line += "\n"

    return line

clear()
fpath = sys.argv[1]
tfile = root.TFile.Open(fpath, "READ")
if len(sys.argv) == 3:
    keylist = [key for key in list_keys(tfile)]
    if sys.argv[2] in keylist:
        print(preview_hist(sys.argv[2]))
    else:
        print('Key not found, run without a second argument to list available keys!')
else:
    terminal_menu = TerminalMenu(list_keys(tfile), preview_command=preview_hist, preview_size=0.75)
    menu_entry_index = terminal_menu.show()
