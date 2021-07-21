#!/usr/python3

import ROOT as root
import numpy as np
import sys
from os import system, name, get_terminal_size
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
    while len(temp) > n:
        temp = np.trim_zeros(temp)
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
    return np.pad(temp, (int(diff / 2), int(diff / 2) + 1))

def pixelate(bins: np.ndarray, n: int):
    fullblocks = np.zeros_like(bins)
    remainder = np.zeros_like(bins)
    scaled = np.interp(bins, (0, bins.max()), (0, 8 * n))
    for i, b in enumerate(scaled):
        fullblocks[i] = int(b // 8)
        remainder[i] = int(b % 8)
    return fullblocks, remainder


def preview_hist(tkeyname: str):
    global tfile
    global preview
    term_size = get_terminal_size()
    if preview:
        X_SCALE = term_size.columns - 9
        Y_SCALE = int(term_size.lines * 0.75) - 5
    else:
        X_SCALE = term_size.columns - 6
        Y_SCALE = term_size.lines - 5
    hist = tfile.Get(tkeyname)
    bincontent = np.zeros(hist.GetNbinsX())
    for i in range(hist.GetNbinsX()):
        bincontent[i] = int(hist.GetBinContent(i))
    Y_MAX_STR = str(int(bincontent.max()))
    Y_LABELS = [str(int(y)) for y in np.linspace(0, int(bincontent.max()), Y_SCALE)]
    X_SCALE -= len(Y_MAX_STR)
    bincontent = rebin(bincontent, X_SCALE)
    fullblocks, remainder = pixelate(bincontent, Y_SCALE)
    grid = np.zeros((X_SCALE, Y_SCALE))
    for i in range(X_SCALE):
        for j in range(int(fullblocks[i])):
            grid[i][j] = 8
            if remainder[i]:
                grid[i][j+1] = remainder[i]
    if preview:
        line = "╔" + "═" * (len(Y_MAX_STR) + 2) + "╦" + "═" * (X_SCALE + 1) + "╗\n"
    else:
        line = " " + tkeyname + "\n"
        line += "╔" + "═" * (len(Y_MAX_STR) + 2) + "╦" + "═" * (X_SCALE + 1) + "╗\n"
    for j in range(Y_SCALE):
        if j == 0:
            line += "║ " + Y_MAX_STR + " ╢"
        elif j == Y_SCALE - 1:
            line += "║" + " " * (len(Y_MAX_STR)) + "0 ╢"
        else:
            length_diff = len(Y_MAX_STR) - len(Y_LABELS[Y_SCALE - j - 1])
            line += "║ " + " " * length_diff + f"{Y_LABELS[Y_SCALE - j - 1]}" + " ╢"
        for i in range(X_SCALE):
            line += getBlock(grid[i][Y_SCALE - j - 1])
        line += " ║\n"
    line += "╚" + "═" * (len(Y_MAX_STR) + 2) + "╩" + "═" * (X_SCALE + 1) + "╝"

    return line

clear()
fpath = sys.argv[1]
preview = False
tfile = root.TFile.Open(fpath, "READ")
if len(sys.argv) == 3:
    keylist = [key for key in list_keys(tfile)]
    if sys.argv[2] in keylist:
        print(preview_hist(sys.argv[2]))
    else:
        print('Key not found, run without a second argument to list available keys!')
else:
    preview = True
    terminal_menu = TerminalMenu(list_keys(tfile), preview_command=preview_hist, preview_size=0.75)
    menu_entry_index = terminal_menu.show()
