#!/usr/bin/env python
###################################################
#  phase_scan_gif.py	                          #
#                                                 #
#  Produces a gif of the phase scan from the      #
#  output of iQiScan hcalraw plugin.              #
###################################################
import sys
import optparse
import ROOT
from ROOT import TFile, TCanvas, TH1D, gROOT, gStyle, gPad
import os
from datetime import datetime
from subprocess import call
# Number of fibers
FIBER_CNT = 24
# Number of channels per fiber
FIBCH_CNT = 8

# Crate (FNAL teststand: default 41)
CRATE = 41

# Slot number (FNAL teststand: default 1)
SLOT = 1

# Valid Gsel settings
GSEL_CODES = [0b00000, 0b00001, 0b00010, 0b00100, 0b01000, 0b10000, 0b10010, \
              0b10100, 0b11000, 0b11010, 0b11100, 0b11110, 0b11111]

FIBER = 21 
FIBCH = 7


#############################################
#  Quiet                                    #
#  Usage: Quiets info, warnings, or errors  #
#                                           #
#  Ex: TCanvas.c1.SaveAs("myplot.png")      #
#      Quiet(c1.SaveAs)("myplot.png")       #
#############################################
def Quiet(func, level = ROOT.kInfo + 1):
    def qfunc(*args,**kwargs):
        oldlevel = ROOT.gErrorIgnoreLevel
        ROOT.gErrorIgnoreLevel = level
        try:
            return func(*args,**kwargs)
        finally:
            ROOT.gErrorIgnoreLevel = oldlevel
    return qfunc

usage = 'usage: %prog [options]'
parser = optparse.OptionParser(usage)
parser.add_option('-i', '--inF', dest='inF', help='input file', default=None, type='string')
parser.add_option('-o', '--outF', dest='outF', help='output file name', default="", type='string')
parser.add_option('-s', '--scan', dest='scan', help='scan type (gsel or phase)', default="", type='string')
parser.add_option('-f', '--frames', dest='frames', help='frames to use', default=0, type='int')
parser.add_option('-e', '--fedId', dest='fedId', help='fed Id', default=1776, type='int')
parser.add_option('-w', '--warn', dest='warn', help='warn on errors (0 or 1)', default=0, type='int')
parser.add_option('-m', '--fiberMask', dest='fiberMask', help='fiber to inspect', default=-1, type='int')
(opt,args) = parser.parse_args()

f = TFile.Open(opt.inF, 'r')
try:
    if f.IsZombie():
        print "File %s is a zombie" % opt.inF
        sys.exit()
except: # Couldn't open file, exit
    sys.exit()

gROOT.SetBatch(True)  # True: Don't display canvas
c = TCanvas("c","c",1700,1200)


try:
    if opt.scan == "gsel":
	FRAMES = 13
    elif opt.scan == "phase":
	FRAMES = 114
    else:
	print "Unrecognized --scan option  (hint: gsel or phase)"
	sys.exit()

    if opt.frames > 0:
	FRAMES = opt.frames
except:
    sys.exit()

print "Loading histograms from file %s.." % opt.inF,
histos = []
for i in range(FRAMES):
    htemp = None
    #htemp = f.Get("ADC_vs_TS_ErrF0_%s_%d_FED_1776_Crate_41_Slot_1_Fib_4_Ch_4_2D" % (opt.scan, i if opt.scan != "gsel" else GSEL_CODES[i]))
    htemp = f.Get("ADC_vs_TS_ErrF0_%s_%d_FED_1776_Crate_41_Slot_1_Fib_%d_Ch_%d_2D" % (opt.scan, i if opt.scan != "gsel" else GSEL_CODES[i], FIBER, FIBCH))
    try:
	htemp.SetDirectory(0)
	histos.append(htemp)
    except:
	continue
if len(histos) == 0:
    print "Can't find %s scan data in %s" % (opt.scan, opt.inF)
    sys.exit()


#maxADC = -1
#for bin in range(histos[0].GetN
print "done!"
print "Drawing frames...",
sys.stdout.flush()
maxADC = 75 if opt.scan == "phase" else 150
#maxADC = 20000

tempdir = "_tmpGif_" + datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
os.mkdir(tempdir)
tempfiles = ""
for i, h in enumerate(histos):
    h.SetAxisRange(0., maxADC, "Y")
    h.Draw("COLZ")
    gPad.Update()
    
    st = h.FindObject("stats")	# TPaveStats object
    st.SetX1NDC(0.7)
    st.SetX2NDC(0.9)
    st.SetY2NDC(0.9)

#    if i < 10:
#	run = "00" + str(i)
#    elif i < 100:
#	run = "0" + str(i)
#    else:
#	run = str(i)
    #c.SaveAs("tmp/tmp_phase%s.png" % run)
    tempfiles += "tmp_%s.png\n" % i
    Quiet(c.SaveAs)(tempdir + "/tmp_%s.png" % i)
print "done!"

path,outf = os.path.split(opt.outF)
if opt.outF != "" and (path == "" or os.path.exists(path)):
    name = os.path.abspath(path) + "/" + outf
    if os.path.splitext(outf)[1] != ".gif":
	name += ".gif"

else:
    name = os.getcwd() + "/" + os.path.splitext(os.path.basename(opt.inF))[0] + "-%s_scan.gif" % opt.scan
    #name = os.path.splitext(os.path.abspath(os.path.split(opt.inF)[0]) + "/" + os.path.basename(opt.inF))[0] + "-%s_scan.gif" % opt.scan

print "Creating gif %s ..." % name, 
sys.stdout.flush()

if opt.scan == "phase":
    command = "convert -loop 0 -delay 20 @file.tx -delay 150 tmp_%d.png %s" % (FRAMES-1, name)
    os.system("cd %s" % tempdir + ";echo '%s' > file.tx" % tempfiles + ";" + command + ";cd ..")
elif opt.scan == "gsel":
    command = "convert -loop 0 -delay 50 @file.tx -delay 150 tmp_%d.png %s" % (FRAMES-1, name)
    os.system("cd %s" % tempdir + ";echo '%s' > file.tx" % tempfiles + ";" + command + ";cd ..")
print "done!"
os.system("rm -rf %s" % tempdir)
