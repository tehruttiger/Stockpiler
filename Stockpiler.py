import os
import os.path
import time
from tkinter import *
from tkinter import ttk

import numpy
from PIL import ImageTk, ImageGrab, Image
import logging
import datetime
from pynput.mouse import Button, Controller
import glob
import cv2
import numpy as np
from global_hotkeys import *
import csv
import re
from requests.sessions import Request
import xlsxwriter
from tksheet import Sheet
import win32gui
import requests
import threading

global stockpilename
global PopupWindow
global NewStockpileName
global StockpileNameEntry
global IconEntry
global IconName
global CurrentStockpileName
global IconPickerWindow
global IndOrCrateWindow
global FilterFrame
global LastStockpile
global tempicon

class items(object):
	data = []
	numbers = (('CheckImages//num0.png', "0"), ('CheckImages//num1.png', "1"), ('CheckImages//num2.png', "2"),
			   ('CheckImages//num3.png', "3"), ('CheckImages//num4.png', "4"), ('CheckImages//num5.png', "5"),
			   ('CheckImages//num6.png', "6"), ('CheckImages//num7.png', "7"), ('CheckImages//num8.png', "8"),
			   ('CheckImages//num9.png', "9"), ('CheckImages//numk.png', "k+"))
	stockpilecontents = []
	sortedcontents = []
	slimcontents = []
	ThisStockpileName = ""
	FoundStockpileTypeName = ""
	UIimages = []


mouse = Controller()
current_mouse_position = mouse.position

if not os.path.exists("./logs"):
	os.makedirs("./logs")

logfilename = datetime.datetime.now().strftime("%Y-%m-%d-%H%M%S")
logfilename = "logs/Stockpiler-log-" + logfilename + ".txt"
logging.basicConfig(filename=logfilename, format='%(name)s - %(levelname)s - %(message)s', level=logging.INFO)
print("Log file created: " + logfilename)
logging.info(str(datetime.datetime.now()) + ' Log Created')


def get_file_directory(file):
	return os.path.dirname(os.path.abspath(file))


# Log cleanup of any contents of logs folder older than 7 days
now = time.time()
cutoff = now - (7 * 86400)
files = os.listdir(os.path.join(get_file_directory(__file__), "logs"))
file_path = os.path.join(get_file_directory(__file__), "logs/")
for xfile in files:
	if os.path.isfile(str(file_path) + xfile):
		t = os.stat(str(file_path) + xfile)
		c = t.st_ctime
		if c < cutoff:
			os.remove(str(file_path) + xfile)
			logging.info(str(datetime.datetime.now()) + " " + str(xfile) + " log file deleted")


Version = "1.2"

StockpilerWindow = Tk()
StockpilerWindow.title('Stockpiler ' + Version)
# Window width is based on generated UI.  If buttons change, width should change here.
StockpilerWindow.geometry("537x600")
# Width locked since button array doesn't adjust dynamically
StockpilerWindow.resizable(width=False, height=False)


class menu(object):
	iconrow = 1
	iconcolumn = 0
	lastcat = 0
	itembuttons = []
	icons = []
	category = [[0, 0], [1, 0], [2, 0], [3, 0], [4, 0], [5, 0], [6, 0], [7, 0], [8, 0]]
	faction = [0, 0]
	topscroll = 0
	BotHost = StringVar()
	BotPassword = StringVar()
	BotGuildID = StringVar()
	CSVExport = IntVar()
	updateBot = IntVar()
	XLSXExport = IntVar()
	ImgExport = IntVar()
	Set = IntVar()
	Learning = IntVar()
	FoxWinX = 0
	FoxWinY = 0
	FoxWinW = 0
	FoxWinH = 0


s = ttk.Style()
s.theme_use('alt')
s.configure("EnabledButton.TButton", background="gray")
s.configure("DisabledButton.TButton", background="red2")
# Manually disabled button is different color because it is retained regardless of category/faction disable/enable
s.configure("ManualDisabledButton.TButton", background="red4")
s.configure("EnabledCategory.TButton", background="gray")
s.configure("DisabledCategory.TButton", background="red2")
s.configure("EnabledFaction.TButton", background="gray")
s.configure("DisabledFaction.TButton", background="red2")
s.configure("TScrollbar", troughcolor="grey20", arrowcolor="grey20", background="gray", bordercolor="grey15")
s.configure("TFrame", background="black")
s.configure("TCanvas", background="black")
s.configure("TCheckbutton", background="black", foreground="grey75")
s.configure("TWindow", background="black")
s.map("TCheckbutton", foreground=[('!active', 'grey75'),('pressed', 'black'),
								  ('active', 'black'), ('selected', 'green'), ('alternate', 'purple')],
	  background=[ ('!active','black'),('pressed', 'grey75'), ('active', 'white'),
				   ('selected', 'cyan'), ('alternate', 'pink')],
	  indicatorcolor=[('!active', 'black'),('pressed', 'black'), ('selected','grey75')],
	  indicatorbackground=[('!active', 'green'),('pressed', 'pink'), ('selected','red')])
s.configure('TNotebook', background="grey25", foreground="grey15", borderwidth=0)
s.map('TNotebook.Tab', foreground=[('active', 'black'), ('selected', 'black')],
			background=[('active', 'grey80'), ('selected', 'grey65')])
s.configure("TNotebook.Tab", background="grey40", foreground="black", borderwidth=0)
s.configure('TRadiobutton', background='black', indicatorbackground='blue',
			indicatorcolor='grey20', foreground='grey75', focuscolor='grey20')
s.map("TRadiobutton", foreground=[('!active', 'grey75'),('pressed', 'black'), ('active', 'black'),
								  ('selected', 'green'), ('alternate', 'purple')],
	  background=[ ('!active','black'),('pressed', 'grey15'), ('active', 'white'),
				   ('selected', 'cyan'), ('alternate', 'pink')])
s.configure("TLabel", background="black", foreground="grey75")


global hotkey
global listener
global vkclean
global vkorchar
global keyname
global justkey
global counter
global TargetDistanceEntry
global threadnum

counter = 1
threadnum = 1

filter = []

# Load contents of ItemNumbering.csv into items.data
# Adds all fields (columns) even though only a few are used
with open('ItemNumbering.csv', 'rt') as f_input:
	csv_input = csv.reader(f_input, delimiter=',')
	# Skips first line
	header = next(csv_input)
	# Skips reserved line
	reserved = next(csv_input)
	for rowdata in csv_input:
		items.data.append(rowdata)
		if os.path.exists("UI//" + str(rowdata[0]) + ".png"):
			items.UIimages.append((rowdata[0], "UI//" + str(rowdata[0]) + ".png"))

# Load filter values into new array
with open('Filter.csv', 'rt') as f_input:
	csv_input = csv.reader(f_input, delimiter=',')
	# Skips first line
	header = next(csv_input)
	for rowdata in csv_input:
		filter.append(rowdata)

# Matches up filter value with appropriate items in items.data
# for filteritem in range(len(filter)):
for item in range(len(items.data)):
	items.data[item].append(0)

for filteritem in range(len(filter)):
	# print(filter[filteritem])
	try:
		# print(filter[filteritem])
		for item in range(len(items.data)):
			if filter[filteritem][0] == items.data[item][0]:
				items.data[item][17] = filter[filteritem][1]
				# items.data[item].extend(filter[filteritem][1])
	except:
		print("failed to apply filters to items.data")


print(items.data[1])


### For troubleshooting
# data[item].extend(filter[item][1])
# print(data)
# Names = [item[3] for item in data]
# print(Names)


class CreateToolTip(object):
	"""
	create a tooltip for a given widget
	"""
	def __init__(self, widget, text='widget info'):
		self.waittime = 100     #miliseconds before popup appear
		self.wraplength = 180   #pixels
		self.widget = widget
		self.text = text
		self.widget.bind("<Enter>", self.enter)
		self.widget.bind("<Leave>", self.leave)
		self.widget.bind("<ButtonPress>", self.leave)
		self.id = None
		self.tw = None

	def enter(self, event=None):
		self.schedule()

	def leave(self, event=None):
		self.unschedule()
		self.hidetip()

	def schedule(self):
		self.unschedule()
		self.id = self.widget.after(self.waittime, self.showtip)

	def unschedule(self):
		id = self.id
		self.id = None
		if id:
			self.widget.after_cancel(id)

	def showtip(self, event=None):
		x = y = 0
		x, y, cx, cy = self.widget.bbox("insert")
		x, y = mouse.position
		# have popup slightly offset from mouse
		x += 15
		y += 15
		# creates a toplevel window
		self.tw = Toplevel(self.widget)
		# Leaves only the label and removes the app window
		self.tw.wm_overrideredirect(True)
		self.tw.wm_geometry("+%d+%d" % (x, y))
		label = ttk.Label(self.tw, text=self.text, justify='left',
						relief='ridge', borderwidth=5, background="grey25", foreground="white",
						wraplength = self.wraplength)
		label.pack(ipadx=1)

	def hidetip(self):
		tw = self.tw
		self.tw= None
		if tw:
			tw.destroy()


def winEnumHandler( hwnd, ctx ):
	# if win32gui.IsWindowVisible( hwnd ):
	# 	print (hex(hwnd), win32gui.GetWindowText( hwnd ))
	if win32gui.GetWindowText(hwnd) == "War  ":
		print("Found Foxhole")
		rect = win32gui.GetWindowRect(hwnd)
		menu.FoxWinX = rect[0]
		menu.FoxWinY = rect[1]
		menu.FoxWinW = rect[2] - menu.FoxWinX
		menu.FoxWinH = rect[3] - menu.FoxWinY
		print(menu.FoxWinX, menu.FoxWinY, menu.FoxWinW, menu.FoxWinH)
		if menu.FoxWinX < 0:
			menu.FoxWinX = 0
			# menu.FoxWinW = 1
		if menu.FoxWinY < 0:
			menu.FoxWinY = 0
			# menu.FoxWinH = 1


# Function used simply for grabbing cropped stockpile images
# Helpful for grabbing test images for assembling missing icons or new sets of icons (for modded icons)
def GrabStockpileImage():
	global counter
	win32gui.EnumWindows(winEnumHandler, None)
	######### Remove if multi-monitor works as expected #########
	# grab whole screen and prepare for template matching
	# screen = np.array(ImageGrab.grab(bbox=None))
	# screen = cv2.cvtColor(screen, cv2.COLOR_BGR2GRAY)

	# OKAY, so you'll have to grab the whole screen, detect that thing in the upper left, then use that as a basis
	# for cropping that full screenshot down to just the foxhole window

	screen = np.array(ImageGrab.grab(bbox=None, include_layered_windows=False, all_screens=True))
	screen = cv2.cvtColor(screen, cv2.COLOR_BGR2GRAY)

	numbox = cv2.imread('CheckImages//StateOf.png', cv2.IMREAD_GRAYSCALE)
	res = cv2.matchTemplate(screen, numbox, cv2.TM_CCOEFF_NORMED)
	threshold = .95
	stateloc = np.where(res >= threshold)
	statey = stateloc[0].astype(int) - 35
	statex = stateloc[1].astype(int) - 35

	screen = screen[int(statey):int(statey) + menu.FoxWinH, int(statex):int(statex) + menu.FoxWinW]

	# cv2.imshow("asdf", screen)
	# cv2.waitKey(0)

	# Shirts are always in the same spot in every stockpile, but might be single or crates
	if menu.Set.get() == 0:
		findshirtC = cv2.imread('CheckImages//Default//86C.png', cv2.IMREAD_GRAYSCALE)
		findshirt = cv2.imread('CheckImages//Default//86.png', cv2.IMREAD_GRAYSCALE)
	else:
		findshirtC = cv2.imread('CheckImages//Modded//86C.png', cv2.IMREAD_GRAYSCALE)
		findshirt = cv2.imread('CheckImages//Modded//86.png', cv2.IMREAD_GRAYSCALE)
	try:
		resC = cv2.matchTemplate(screen, findshirtC, cv2.TM_CCOEFF_NORMED)
	except:
		print("Maybe you don't have the shirt crate")
	try:
		res = cv2.matchTemplate(screen, findshirt, cv2.TM_CCOEFF_NORMED)
	except:
		print("Maybe you don't have the individual shirt")
	threshold = .99
	FoundShirt = False
	try:
		if np.amax(res) > threshold:
			print("Found Shirts")
			y, x = np.unravel_index(res.argmax(), res.shape)
			FoundShirt = True
	except:
		print("Don't have the individual shirts icon or not looking at a stockpile")
	try:
		if np.amax(resC) > threshold:
			print("Found Shirt Crate")
			y, x = np.unravel_index(resC.argmax(), resC.shape)
			FoundShirt = True
	except:
		print("Don't have the shirt crate icon or not looking at a stockpile")
	if not FoundShirt:
		print("Found nothing.  Either don't have shirt icon(s) or not looking at a stockpile")
		y = 0
		x = 0

	# If no stockpile was found, don't bother taking a screenshot
	if x == 0 and y == 0:
		print("Both 0's")
		pass
	else:
		stockpile = np.array(ImageGrab.grab(bbox=(x-11,y-32,x+389,1080)))
		stockpile = cv2.cvtColor(stockpile, cv2.COLOR_BGR2RGB)
		imagename = datetime.datetime.now().strftime("%Y-%m-%d-%H%M%S")
		cv2.imwrite('test_' + imagename + '.png', stockpile)


def Learn(LearnInt, image):
	global counter
	global IconName
	global LastStockpile
	# grab whole screen and prepare for template matching
	# COMMENT OUT THESE TWO LINES IF YOU ARE TESTING A SPECIFIC IMAGE
	TestImage = False
	win32gui.EnumWindows(winEnumHandler, None)

	# OKAY, so you'll have to grab the whole screen, detect that thing in the upper left, then use that as a basis
	# for cropping that full screenshot down to just the foxhole window
	screen = np.array(ImageGrab.grab(bbox=None, include_layered_windows=False, all_screens=True))
	screen = cv2.cvtColor(screen, cv2.COLOR_BGR2GRAY)

	numbox = cv2.imread('CheckImages//StateOf.png', cv2.IMREAD_GRAYSCALE)
	res = cv2.matchTemplate(screen, numbox, cv2.TM_CCOEFF_NORMED)
	threshold = .95
	stateloc = np.where(res >= threshold)
	statey = stateloc[0].astype(int) - 35
	statex = stateloc[1].astype(int) - 35

	screen = screen[int(statey):int(statey) + menu.FoxWinH, int(statex):int(statex) + menu.FoxWinW]

	# UNCOMMENT AND MODIFY LINE BELOW IF YOU ARE TESTING A SPECIFIC IMAGE
	# screen = cv2.cvtColor(np.array(Image.open("test_2021-11-25-110247.png")), cv2.COLOR_RGB2GRAY)
	# TestImage = True

	# WHEN USING OTHER RESOLUTIONS, GRAB THEM HERE
	resx = 1920
	resy = 1080

	if LearnInt != "":
		pass
	else:
		screen = LastStockpile

	numbox = cv2.imread('CheckImages//NumBox.png', cv2.IMREAD_GRAYSCALE)
	res = cv2.matchTemplate(screen, numbox, cv2.TM_CCOEFF_NORMED)
	threshold = .99
	numloc = np.where(res >= threshold)
	print("found them here:", numloc)
	print(len(numloc[0]))
	for spot in range(len(numloc[0])):
		# Stockpiles never displayed in upper left under State of the War area
		# State of the War area throws false postives for icons
		if numloc[1][spot] < (resx * .2) and numloc[0][spot] < (resy * .24) and not TestImage:
			pass
		else:
			print("x:", numloc[1][spot], " y:",numloc[0][spot])
			# cv2.imshow('icon', screen[int(numloc[0][spot]+2):int(numloc[0][spot]+36), int(numloc[1][spot]-38):numloc[1][spot]-4])
			# cv2.waitKey(0)
			currenticon = screen[int(numloc[0][spot]+2):int(numloc[0][spot]+36), int(numloc[1][spot]-38):numloc[1][spot]-4]
			print("currenticon:", currenticon.shape)
			if menu.Set.get() == 0:
				folder = "CheckImages//Default//"
			else:
				folder = "CheckImages//Modded//"
			Found = False
			for imagefile in os.listdir(folder):
				checkimage = cv2.imread(folder + imagefile, cv2.IMREAD_GRAYSCALE)
				result = cv2.matchTemplate(currenticon, checkimage, cv2.TM_CCOEFF_NORMED)
				threshold = .99
				if np.amax(result) > threshold:
					#print("Found:", imagefile)
					Found = True
					break
			if not Found:
				print("Not found, should launch IconPicker")
				IconPicker(currenticon)
	# cv2.imshow('blah', screen)
	# cv2.waitKey(0)
	SearchImage(1, screen)
	CreateButtons("blah")


# def WhichItem(image):
# 	global PopupWindow
# 	global IconEntry
# 	root_x = StockpilerWindow.winfo_rootx()
# 	root_y = StockpilerWindow.winfo_rooty()
# 	if root_x == root_y == -32000:
# 		win_x = 100
# 		win_y = 100
# 	else:
# 		win_x = root_x - 20
# 		win_y = root_y + 125
# 	location = "+" + str(win_x) + "+" + str(win_y)
# 	PopupWindow = Toplevel(StockpilerWindow)
# 	PopupWindow.geometry(location)
# 	PopupFrame = ttk.Frame(PopupWindow)
# 	PopupWindow.resizable(False, False)
# 	PopupFrame.pack()
# 	PopupWindow.grab_set()
# 	PopupWindow.focus_force()
# 	im = Image.fromarray(image)
# 	tkimage = ImageTk.PhotoImage(im)
# 	NewIconLabel = ttk.Label(PopupFrame, image=tkimage, style="TLabel")
# 	NewIconLabel.image = tkimage
# 	NewIconLabel.grid(row=5, column=0)
# 	WhatLabel = ttk.Label(PopupFrame, text="What is it?", style="TLabel")
# 	WhatLabel.grid(row=7, column=0)
# 	IconEntry = ttk.Entry(PopupFrame)
# 	IconEntry.grid(row=8, column=0)
# 	OKButton = ttk.Button(PopupFrame, text="OK", command=lambda: SaveIconAndDestroy(image), style="EnabledButton.TButton")
# 	PopupWindow.bind('<Return>', lambda event, a=image: SaveIconAndDestroy(a))
# 	IconEntry.focus()
# 	OKButton.grid(row=10, column=0, sticky="NSEW")
# 	PopupWindow.wait_window()


def SearchImage(Pass, LearnImage):
	global stockpilename
	global NewStockpileName
	global PopupWindow
	global CurrentStockpileName
	global threadnum

	if Pass != "":
		screen = LearnImage
		# cv2.imshow('blah', screen)
		# cv2.waitKey(0)
	else:
		try:
			win32gui.EnumWindows(winEnumHandler, None)

			# OKAY, so you'll have to grab the whole screen, detect that thing in the upper left, then use that as a basis
			# for cropping that full screenshot down to just the foxhole window
			screen = np.array(ImageGrab.grab(bbox=None, include_layered_windows=False, all_screens=True))
			screen = cv2.cvtColor(screen, cv2.COLOR_BGR2GRAY)

			numbox = cv2.imread('CheckImages//StateOf.png', cv2.IMREAD_GRAYSCALE)
			res = cv2.matchTemplate(screen, numbox, cv2.TM_CCOEFF_NORMED)
			threshold = .95
			stateloc = np.where(res >= threshold)
			statey = stateloc[0].astype(int) - 35
			statex = stateloc[1].astype(int) - 35
			print(statey, statex)

			screen = screen[int(statey):int(statey) + menu.FoxWinH, int(statex):int(statex) + menu.FoxWinW]
		except:
			screen = np.array(ImageGrab.grab(bbox=None, include_layered_windows=False, all_screens=True))
	garbage = "blah"
	args = (screen, garbage)
	# Threading commands are generated via text since each thread needs a distinct name, created using threadcounter
	threadcounter = "t" + str(threadnum)
	# print(threadcounter)
	threadingthread = threadcounter + " = threading.Thread(target = ItemScan, args = args)"
	threadingdaemon = threadcounter + ".daemon = True"
	threadingstart = threadcounter + ".start()"
	# print(threadnum)
	exec(threadingthread)
	exec(threadingdaemon)
	exec(threadingstart)
	threadnum += 1


def ItemScan(screen, garbage):
	global LastStockpile

	# UNCOMMENT IF TESTING A SPECIFIC IMAGE
	# screen = cv2.cvtColor(np.array(Image.open("test_2021-11-25-101723.png")), cv2.COLOR_RGB2GRAY)

	# cv2.imshow("test", screen)
	# cv2.waitKey(0)

	if menu.Set.get() == 0:
		findshirtC = cv2.imread('CheckImages//Default//86C.png', cv2.IMREAD_GRAYSCALE)
		findshirt = cv2.imread('CheckImages//Default//86.png', cv2.IMREAD_GRAYSCALE)
	else:
		try:
			findshirtC = cv2.imread('CheckImages//Modded//86C.png', cv2.IMREAD_GRAYSCALE)
		except:
			print("You don't have the Shirt crate yet")
		try:
			findshirt = cv2.imread('CheckImages//Modded//86.png', cv2.IMREAD_GRAYSCALE)
		except:
			print("You don't have the individual Shirt yet")
	try:
		resC = cv2.matchTemplate(screen, findshirtC, cv2.TM_CCOEFF_NORMED)
	except:
		print("Looks like you're missing the shirt crate")
	try:
		res = cv2.matchTemplate(screen, findshirt, cv2.TM_CCOEFF_NORMED)
	except:
		print("Looks like you're missing the individual shirts")
	threshold = .99
	FoundShirt = False
	try:
		if np.amax(res) > threshold:
			print("Found Shirts")
			y, x = np.unravel_index(res.argmax(), res.shape)
			FoundShirt = True
	except:
		print("Don't have the individual shirts icon or not looking at a stockpile")
	try:
		if np.amax(resC) > threshold:
			print("Found Shirt Crate")
			y, x = np.unravel_index(resC.argmax(), resC.shape)
			FoundShirt = True
	except:
		print("Don't have the shirt crate icon or not looking at a stockpile")
	if not FoundShirt:
		print("Found nothing.  Either don't have shirt icon(s) or not looking at a stockpile")
		y = 0
		x = 0

	# COMMENT OUT IF TESTING A SPECIFIC IMAGE
	if y == x == 0:
		stockpile = screen
	else:
		stockpile = screen[y - 32:1080, x - 11:x + 389]

	# UNCOMMENT IF TESTING A SPECIFIC IMAGE
	# stockpile = screen

	# Grab this just in case you need to rerun the scan from Results tab
	# LastStockpile = stockpile
	LastStockpile = screen

	# Image clips for each type of stockpile should be in this array below
	StockpileTypes = (('CheckImages//Seaport.png', 'Seaport', 0), ('Checkimages//StorageDepot.png', 'Storage Depot', 1),
					  ('Checkimages//Outpost.png', 'Outpost', 2), ('Checkimages//Townbase.png', 'Town Base', 3),
					  ('Checkimages//RelicBase.png', 'Relic Base', 4),
					  ('Checkimages//BunkerBase.png', 'Bunker Base', 5),
					  ('Checkimages//Encampment.png', 'Encampment', 6),
					  ('Checkimages//SafeHouse.png', 'Safe House', 7))
	# Check cropped stockpile image for each location type image
	for image in StockpileTypes:
		try:
			findtype = cv2.imread(image[0], cv2.IMREAD_GRAYSCALE)
			# cv2.imshow("asdf",findtype)
			# cv2.waitKey(0)
			res = cv2.matchTemplate(stockpile, findtype, cv2.TM_CCOEFF_NORMED)
			# Threshold is a bit lower for types as they are slightly see-thru
			typethreshold = .95
			# print("Checking:", image[1])
			if np.amax(res) > typethreshold:
				y, x = np.unravel_index(res.argmax(), res.shape)
				FoundStockpileType = image[2]
				FoundStockpileTypeName = image[1]
				# print(image[1])
				if image[1] == "Seaport" or image[1] == "Storage Depot":
					findtab = cv2.imread('CheckImages//Tab.png', cv2.IMREAD_GRAYSCALE)
					res = cv2.matchTemplate(stockpile, findtab, cv2.TM_CCOEFF_NORMED)
					tabthreshold = .99
					if np.amax(res) > tabthreshold:
						print("Found the Tab")
						y, x = np.unravel_index(res.argmax(), res.shape)
						# Seaports and Storage Depots have the potential to have named stockpiles, so grab the name
						stockpilename = stockpile[y - 5:y + 17, x - 150:x - 8]
						# Make a list of all current stockpile name images
						currentstockpiles = glob.glob("Stockpiles/*.png")
						# print(currentstockpiles)
						found = 0
						for image in currentstockpiles:
							stockpilelabel = cv2.imread(image, cv2.IMREAD_GRAYSCALE)
							if not image.endswith("image.png"):
								res = cv2.matchTemplate(stockpilename, stockpilelabel, cv2.TM_CCOEFF_NORMED)
								threshold = .99
								flag = False
								if np.amax(res) > threshold:
									# Named stockpile is one already seen
									found = 1
									ThisStockpileName = (image[11:(len(image) - 4)])
						if found != 1:
							newstockpopup(stockpilename)
							PopupWindow.wait_window()
							# NewStockpileFilename = 'Stockpiles//' + NewStockpileName + '.png'
							# It's a new stockpile, so save an images of the name as well as the cropped stockpile itself
							cv2.imwrite('Stockpiles//' + NewStockpileName + '.png', stockpilename)
							if menu.ImgExport.get() == 1:
								cv2.imwrite('Stockpiles//' + NewStockpileName + ' image.png', stockpile)
							ThisStockpileName = NewStockpileName
					else:
						# It's not a named stockpile, so just call it by the type of location (Bunker Base, Encampment, etc)
						ThisStockpileName = FoundStockpileTypeName
				else:
					# It's not a named stockpile, so just call it by the type of location (Bunker Base, Encampment, etc)
					ThisStockpileName = FoundStockpileTypeName
				# StockpileName = StockpileNameEntry.get()
				# cv2.imwrite('Stockpiles//' + StockpileName + '.png', stockpilename)
				break
			else:
				# print("Didn't find",image[1])
				FoundStockpileType = "None"
				ThisStockpileName = "None"
				pass
		except:
			print("Probably not looking at a stockpile or don't have the game open")
			FoundStockpileType = "None"
			ThisStockpileName = "None"
			pass

	# These stockpile types allow for crates (ie: Seaport)
	CrateList = [0, 1]
	# These stockpile types only allow individual items (ie: Bunker Base)
	SingleList = [2, 3, 4, 5, 6, 7]

	start = datetime.datetime.now()

	print(ThisStockpileName)
	if menu.Set.get() == 0:
		folder = "CheckImages//Default//"
	else:
		folder = "CheckImages//Modded//"
	if ThisStockpileName != "None":
		if menu.ImgExport.get() == 1:
			cv2.imwrite('Stockpiles//' + ThisStockpileName + ' image.png', stockpile)
		if FoundStockpileType in CrateList:
			print("Crate Type")
			# Grab all the crate CheckImages
			StockpileImages = [(str(item[0]), folder + str(item[0]) + "C.png", (item[3] + " Crate"), item[8], item[17]) for item in items.data if str(item[17]) == "0"]
			# Grab all the individual vehicles and shippables
			StockpileImagesAppend = [(str(item[0]), folder + str(item[0]) + ".png", item[3], item[8], item[17]) for item in items.data if (str(item[9]) == "7" and str(item[17]) == "0") or (str(item[9]) == "8" and str(item[17]) == "0")]
			StockpileImages.extend(StockpileImagesAppend)
			#print("Checking for:", StockpileImages)
		elif FoundStockpileType in SingleList:
			print("Single Type")
			# Grab all the individual items
			# for item in range(len(items.data)):
			# 	print(item)
			StockpileImages = [(str(item[0]), folder + str(item[0]) + ".png", item[3], item[8], item[17]) for item in items.data]
			#print("Checking for:", StockpileImages)
		else:
			print("No idea what type...")


		stockpilecontents = []
		checked = 0
		#print("StockpileImages", StockpileImages)
		for image in StockpileImages:
			checked += 1
			try:
				findimage = cv2.imread(image[1], cv2.IMREAD_GRAYSCALE)
				res = cv2.matchTemplate(stockpile, findimage, cv2.TM_CCOEFF_NORMED)
				threshold = .99
				flag = False
				if np.amax(res) > threshold:
					flag = True
					y, x = np.unravel_index(res.argmax(), res.shape)
					# Found a thing, now find amount
					numberlist = []
					for number in items.numbers:
						findnum = cv2.imread(number[0], cv2.IMREAD_GRAYSCALE)
						# Clip the area where the stock number will be
						numberarea = stockpile[y+8:y+28, x+45:x+87]
						resnum = cv2.matchTemplate(numberarea, findnum, cv2.TM_CCOEFF_NORMED)
						threshold = .90
						numloc = np.where(resnum >= threshold)
						# It only looks for up to 3 of each number for each item, since after that it would be a "k+" scenario, which never happens in stockpiles
						# This will need to be changed to allow for more digits whenever it does in-person looks at BB stockpiles and such, where it will show up to 5 digits
						if len(numloc[1]) > 0:
							numberlist.append(tuple([numloc[1][0],number[1]]))
						if len(numloc[1]) > 1:
							numberlist.append(tuple([numloc[1][1],number[1]]))
						if len(numloc[1]) > 2:
							numberlist.append(tuple([numloc[1][2],number[1]]))
						# Sort the list of numbers by position closest to the left, putting the numbers in order by extension
						numberlist.sort(key=lambda y: y[0])

					# If the number ends in a K, it just adds 000 since you don't know if that's 1001 or 1999
					# k+ never happens in stockpiles, so this only affects town halls, bunker bases, etc
					if len(numberlist) == 1:
						quantity = int(str(numberlist[0][1]))
					elif len(numberlist) == 2:
						if numberlist[1][1] == "k+":
							quantity = int(str(numberlist[0][1]) + "000")
						else:
							quantity = int(str(numberlist[0][1]) + (str(numberlist[1][1])))
					elif len(numberlist) == 3:
						if numberlist[2][1] == "k+":
							quantity = int(str(numberlist[0][1]) + (str(numberlist[1][1])) + "000")
						else:
							quantity = int(str(numberlist[0][1]) + (str(numberlist[1][1])) + str(numberlist[2][1]))
					elif len(numberlist) == 4:
						if numberlist[3][1] == "k+":
							quantity = int(str(numberlist[0][1]) + (str(numberlist[1][1])) + str(numberlist[2][1]) + "000")
						else:
							quantity = int(str(numberlist[0][1]) + (str(numberlist[1][1])) + str(numberlist[2][1]) + str(numberlist[3][1]))
					# place shirts first, since they're always at the top of every stockpile
					if image[0] == "86":
						itemsort = 0
					# bunker supplies next
					elif image[0] == "93":
						itemsort = 1
					# garrison supplies last
					elif image[0] == "90":
						itemsort = 2
					elif image[3] != "Vehicle" and image[3] != "Shippables":
						itemsort = 5
					elif image[3] == "Vehicle":
						itemsort = 10
					else:
						itemsort = 15
					if image[1][(len(image[1])-5):(len(image[1])-4)] == "C":
						stockpilecontents.append(list((image[0], image[2], quantity, itemsort, 1)))
					else:
						stockpilecontents.append(list((image[0], image[2], quantity, itemsort, 0)))
			except:
				# print("Exception for some reason")
				pass
				# print(len(numberlist))

		#print("Stockpile Contents:", stockpilecontents)
		items.sortedcontents = list(sorted(stockpilecontents, key=lambda x: (x[3], x[4], -x[2])))
		#print("Sorted Contents:", items.sortedcontents)
		# Here's where we sort stockpilecontents by category, then number, so they spit out the same as screenshot
		# Everything but vehicles and shippables first, then single vehicle, then crates of vehicles, then single shippables, then crates of shippables
		if ThisStockpileName in ("Seaport","Storage Depot","Outpost","Town Base","Relic Base","Bunker Base","Encampment","Safe House"):
			ThisStockpileName = "Public"

		if menu.CSVExport.get() == 1:
			stockpilefile = open("Stockpiles//" + ThisStockpileName + ".csv", 'w')
			stockpilefile.write(ThisStockpileName + ",\n")
			stockpilefile.write(FoundStockpileTypeName + ",\n")
			stockpilefile.write(str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")) + ",\n")
			stockpilefile.close()

			# Writing to both csv and xlsx, only the quantity and name is written
			# If more elements from items.data are added to stockpilecontents, they could be added to these exports as fields
			with open("Stockpiles//" + ThisStockpileName + ".csv", 'a') as fp:
				# fp.write('\n'.join('{},{},{}'.format(x[0],x[1],x[2]) for x in stockpilecontents))
				############### THIS ONE DOES IN REGULAR ORDER ############
				# fp.write('\n'.join('{},{}'.format(x[1],x[2]) for x in stockpilecontents))
				############### THIS ONE DOES IN SORTED ORDER #############
				fp.write('\n'.join('{},{}'.format(x[1], x[2]) for x in items.sortedcontents))
			fp.close()
		

		if menu.updateBot.get() == 1 and ThisStockpileName != "Public":
			requestObj = {
				"password": menu.BotPassword.get(),
				"name": ThisStockpileName,
				"guildID": menu.BotGuildID.get()
			}
			data = []
			for x in items.sortedcontents:
				data.append([x[1], x[2]])
			requestObj["data"] = data

			try:
				r = requests.post(menu.BotHost.get(), json=requestObj)
				response = r.json()

				storemanBotPrefix = "[Storeman Bot Link]: "
				if (response["success"]): print(storemanBotPrefix + "Sent to server successfully")
				elif (response["error"] == "empty-stockpile-name"): print(storemanBotPrefix + "Stockpile name is invalid. Perhaps the stockpile name was not detected or empty.")
				elif (response["error"] == "invalid-password"): print(storemanBotPrefix + "Invalid password, check that the Bot Password is correct.")
				elif (response["error"] == "invalid-guild-id"): print(storemanBotPrefix + "The Guild ID entered was not found on the Storeman Bot server. Please check that it is correct.")
				else: print(storemanBotPrefix + "An unhandled error occured: " + response["error"])
			except Exception as e:
				print("There was an error connecting to the Bot")
				print(e)


		if menu.XLSXExport.get() == 1:
			workbook = xlsxwriter.Workbook("Stockpiles//" + ThisStockpileName + ".xlsx")
			worksheet = workbook.add_worksheet()
			worksheet.write(0, 0, ThisStockpileName)
			worksheet.write(1, 0, FoundStockpileTypeName)
			worksheet.write(2, 0, str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
			row = 3
			for col, data in enumerate(items.sortedcontents):
				# print("col", col, " data", data)
				worksheet.write(row + col, 0, data[1])
				worksheet.write(row + col, 1, data[2])
			workbook.close()
		print(datetime.datetime.now()-start)
		print("Items Checked:",checked)
		items.slimcontents = items.sortedcontents
		for sublist in items.slimcontents:
			del sublist[3:5]
		ResultSheet.set_sheet_data(data=items.slimcontents)
	else:
		popup("NoStockpile")


def on_activate():
	# print("Button Hit")
	GrabStockpileImage()


def on_activate_two():
	# print("Second Button Hit")
	LearnOrNot()


def LearnOrNot():
	if menu.Learning.get() == 0:
		SearchImage("", "")
	else:
		Learn(0, "img")


def newstockpopup(image):
	# global stockpilename
	global PopupWindow
	global StockpileNameEntry
	root_x = StockpilerWindow.winfo_rootx()
	root_y = StockpilerWindow.winfo_rooty()
	if root_x == root_y == -32000:
		win_x = 100
		win_y = 100
	else:
		win_x = root_x - 20
		win_y = root_y + 125
	location = "+" + str(win_x) + "+" + str(win_y)
	PopupWindow = Toplevel(StockpilerWindow)
	PopupWindow.geometry(location)
	PopupFrame = ttk.Frame(PopupWindow)
	PopupWindow.resizable(False, False)
	PopupFrame.pack()
	PopupWindow.grab_set()
	PopupWindow.focus_force()
	im = Image.fromarray(image)
	tkimage = ImageTk.PhotoImage(im)
	NewStockpileLabel = ttk.Label(PopupFrame, text="Looks like a new stockpile.", style="TLabel")
	NewStockpileLabel.grid(row=2, column=0)
	StockpileNameImage = ttk.Label(PopupFrame, image=tkimage, style="TLabel")
	StockpileNameImage.image = tkimage
	StockpileNameImage.grid(row=5, column=0)
	StockpileNameLabel = ttk.Label(PopupFrame, text="What is the name of the stockpile?", style="TLabel")
	StockpileNameLabel.grid(row=7, column=0)
	StockpileNameEntry = ttk.Entry(PopupFrame)
	StockpileNameEntry.grid(row=8, column=0)
	OKButton = ttk.Button(PopupFrame, text="OK", command=lambda: NameAndDestroy("blah"))
	PopupWindow.bind('<Return>', NameAndDestroy)
	StockpileNameEntry.focus()
	OKButton.grid(row=10, column=0, sticky="NSEW")


def popup(type):
	global PopupWindow
	root_x = StockpilerWindow.winfo_rootx()
	root_y = StockpilerWindow.winfo_rooty()
	if root_x == root_y == -32000:
		win_x = 100
		win_y = 100
	else:
		win_x = root_x - 20
		win_y = root_y + 125
	location = "+" + str(win_x) + "+" + str(win_y)
	PopupWindow = Toplevel(StockpilerWindow)
	PopupWindow.geometry(location)
	PopupFrame = ttk.Frame(PopupWindow)
	PopupWindow.resizable(False, False)
	PopupFrame.pack()
	PopupWindow.grab_set()
	PopupWindow.focus_force()
	if type == "NoFox":
		NoFoxholeLabel = ttk.Label(PopupFrame, text="Foxhole isn't running.\nLaunch Foxhole and retry.", style="TLabel")
		NoFoxholeLabel.grid(row=2, column=0)
	elif type == "NoStockpile":
		NoStockpileLabel = ttk.Label(PopupFrame, text="Didn't detect stockpile.\nHover over a stockpile on the map and retry.", style="TLabel")
		NoStockpileLabel.grid(row=2, column=0)
	OKButton = ttk.Button(PopupFrame, text="OK", command=lambda: Destroy("blah"))
	PopupWindow.bind('<Return>', Destroy)
	OKButton.grid(row=10, column=0, sticky="NSEW")


def NameAndDestroy(event):
	global PopupWindow
	global NewStockpileName
	global StockpileNameEntry
	NewStockpileName = StockpileNameEntry.get()
	PopupWindow.destroy()



def SaveIconAndDestroy(image):
	global PopupWindow
	global IconEntry
	global IconName
	IconName = IconEntry.get()
	if IconName != "":
		if menu.Set.get() == 0:
			folder = "CheckImages//Default//"
		else:
			folder = "CheckImages//Modded//"
		cv2.imwrite(folder + IconName + '.png', image)
	PopupWindow.destroy()


def CancelIcon(event):
	global PopupWindow


def Destroy(event):
	global PopupWindow
	PopupWindow.destroy()


def CSVExport():
	if items.stockpilecontents != []:
		stockpilefile = open("Stockpiles//" + items.ThisStockpileName + ".csv", 'w')
		stockpilefile.write(items.ThisStockpileName + ",\n")
		stockpilefile.write(items.FoundStockpileTypeName + ",\n")
		stockpilefile.write(str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")) + ",\n")
		stockpilefile.close()

		# Writing to both csv and xlsx, only the quantity and name is written
		# If more elements from items.data are added to stockpilecontents, they could be added to these exports as fields
		with open("Stockpiles//" + items.ThisStockpileName + ".csv", 'a') as fp:
			# fp.write('\n'.join('{},{},{}'.format(x[0],x[1],x[2]) for x in stockpilecontents))
			############### THIS ONE DOES IN REGULAR ORDER ############
			# fp.write('\n'.join('{},{}'.format(x[1],x[2]) for x in stockpilecontents))
			############### THIS ONE DOES IN SORTED ORDER #############
			fp.write('\n'.join('{},{}'.format(x[1], x[2]) for x in items.sortedcontents))
		fp.close()


def XLSXExport():
	if items.stockpilecontents != []:
		workbook = xlsxwriter.Workbook("Stockpiles//" + items.ThisStockpileName + ".xlsx")
		worksheet = workbook.add_worksheet()
		worksheet.write(0, 0, items.ThisStockpileName)
		worksheet.write(1, 0, items.FoundStockpileTypeName)
		worksheet.write(2, 0, str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
		row = 3
		for col, data in enumerate(items.sortedcontents):
			# print("col", col, " data", data)
			worksheet.write(row + col, 0, data[1])
			worksheet.write(row + col, 1, data[2])
		workbook.close()


# Created this function in order to test changing the hotkey while the program is running
# def changehotkey():
# 	print("That hotkey hit")
# 	newhotkey = "f8"
# 	clear_hotkeys()
# 	bindings = [
# 		[["f2"], None, on_activate],
# 		[["f3"], None, on_activate_two],
# 		[[newhotkey], None, changehotkey],
# 	]
#
# 	register_hotkeys(bindings)
#
# 	start_checking_hotkeys()


################################################
### Potentially can be used to detect new hotkey
################################################
# def on_press_detect(key):
# 	global NewHotkeyDetected
# 	# global ArtyLocHotkey
# 	# global TargetLocHotkey
# 	global vkclean
# 	global vkorchar
# 	global keyname
# 	global CurrentHotkeyLabel
# 	global justkey
# 	global vkfinal
# 	# print('press ', key.__dict__)
# 	arglist = dict(key.__dict__)
# 	saved_args = locals()
# 	# print(saved_args)
# 	# print(type(arglist))
# 	dirtyvk = list(arglist.items())[0]
# 	# print(dirtyvk)
# 	# print(type(dirtyvk))
# 	(vk, vkmiddle) = dirtyvk
# 	vktemp = str(vkmiddle)
# 	# print("Here" + str(vktemp))
# 	# print(type(vktemp))
# 	if vktemp[0] == "<":
# 		# print("found <")
# 		vklength = len(vktemp) - 1
# 		vkclean = vktemp[1:vklength]
# 		chartemp = list(arglist.items())[1]
# 		(label, char) = chartemp
# 		chartemp2 = str(char)
# 		keyname = chartemp2
# 		vkorchar = "vk"
# 		justkey = keyname
# 	else:
# 		# print("no <")
# 		chartemp = list(arglist.items())[1]
# 		(label, char) = chartemp
# 		chartemp2 = str(char)
# 		vkclean = chartemp2
# 		keyname = chartemp2
# 		vkorchar = "char"
# 		justkey = keyname
# 	if keyname == "None":
# 		justkey = keyname
# 		vkclean = "145"
# 		vkorchar = "vk"
# 	elif keyname in ("shift", "ctrl_l", "ctrl_r", "alt_l", "alt_r", "ctrl", "alt"):
# 		justkey = keyname
# 		vkclean = "145"
# 		vkorchar = "vk"
# 	# print("vkclean: " + vkclean)
# 	if vkorchar == "vk":
# 		vkfinal = "<" + vkclean + ">"
# 	else:
# 		vkfinal = vkclean
# 	NewHotkeyDetected = True
# 	return False


# def on_release_detect(key):
# 	# print('{0} released'.format(key))
# 	if key == keyboard.Key.esc:
# 		return False


# def DetectHotkey(whichhotkey):
# 	global NewHotkeyDetected
# 	global SkipHotkey
# 	global hotkey
# 	global listener
# 	global vkclean
# 	global vkorchar
# 	global keyname
# 	global SkipFrame
# 	global SkipKeySelectWindow
# 	NewHotkeyDetected = False
# 	listener.stop()
# 	with keyboard.Listener(
# 			on_press=on_press_detect,
# 			on_release=on_release_detect) as listener:
# 		while NewHotkeyDetected == False:
# 			listener.join()
# 	listener.stop()
# 	# print("Found a key and I'm back")
# 	if vkorchar == "vk":
# 		vkfinal = "<" + vkclean + ">"
# 	elif vkorchar == "char":
# 		vkfinal = vkclean
# 	SkipBuilt = vkfinal
# 	# print("Printing SkipBuilt")
# 	# print(SkipBuilt)
# 	# print("keyname is " + keyname)
# 	listener.stop
# 	if whichhotkey == 1:
# 		Hotkeys.ArtyLocHotkey = SkipBuilt
# 		Hotkeys.ArtyLocKeyname = keyname
# 	elif whichhotkey == 2:
# 		Hotkeys.TargetLocHotkey = SkipBuilt
# 		Hotkeys.TargetLocKeyname = keyname
#
# 	######### WILL NEED TO FIX THIS IF HOTKEYS ARE CONFIGURABLE #########m
#
# 	# CurrentArtyLocHotkey.configure(text=str(Hotkeys.ArtyLocKeyname))
# 	# CurrentTargetLocHotkey.configure(text=str(Hotkeys.TargetLocKeyname))
# 	# hotkey = keyboard.HotKey(keyboard.HotKey.parse(ArtyLocHotkey), on_activate)
# 	# print(hotkey)
# 	print(SkipBuilt)
# 	listener = keyboard.GlobalHotKeys({
# 		Hotkeys.ArtyLocHotkey: on_activate,
# 		Hotkeys.TargetLocHotkey: on_activate_two})
# 	listener.start()


def _on_mousewheel(event):
	FilterCanvas.yview_scroll(int(-1*(event.delta/120)), "units")


# OuterFrame = ttk.Frame(StockpilerWindow)
# OuterFrame.pack(fill=BOTH, expand=1)
# canvas = Canvas(OuterFrame)
# canvas.bind_all("<MouseWheel>", _on_mousewheel)
# canvas.pack()
# scrollbar = ttk.Scrollbar(OuterFrame, orient="vertical", command=canvas.yview)
# StockpileFrame = ttk.Frame(canvas, style="TFrame")

OuterFrame = ttk.Frame(StockpilerWindow)
OuterFrame.pack(fill=BOTH, expand=1)
TabControl = ttk.Notebook(OuterFrame)
FilterTab = ttk.Frame(TabControl)
TabControl.add(FilterTab, text="Filter")
TableTab = ttk.Frame(TabControl)
TabControl.add(TableTab, text="Results")
SettingsTab = ttk.Frame(TabControl)
TabControl.add(SettingsTab, text="Settings")
TabControl.pack(expand=1, fill=BOTH)

FilterCanvas = Canvas(FilterTab)
TableCanvas = Canvas(TableTab)
SettingsCanvas = Canvas(SettingsTab)

FilterCanvas.bind_all("<MouseWheel>", _on_mousewheel)
scrollbar = ttk.Scrollbar(FilterTab, orient=VERTICAL, command=FilterCanvas.yview)
scrollbar.pack(side="right", fill="y")
# StockpileFrame = ttk.Frame(FilterCanvas, style="TFrame")

FilterCanvas.configure(scrollregion=FilterCanvas.bbox('all'), yscrollcommand=scrollbar.set)
FilterCanvas.bind('<Configure>', lambda e: FilterCanvas.configure(scrollregion=FilterCanvas.bbox('all')))


# If enough items are added, then the height below will have to be modified to account for any new button rows
# Remember to make sure the Quit button is displayed
# FilterCanvas.create_window((0, 0), window=StockpileFrame, anchor="nw", height="1691p", width="550p")
# FilterCanvas.configure(yscrollcommand=scrollbar.set)
# OuterFrame.pack()
# scrollbar.pack(side="right", fill="y")
# FilterCanvas.pack(side="left", fill="both", expand=1)


FilterCanvas.pack(side=LEFT, fill=BOTH, expand=1)
TableCanvas.pack(side=TOP, fill=BOTH, expand=1)
SettingsCanvas.pack(side=TOP, fill=BOTH, expand=1)

FilterFrame = ttk.Frame(FilterCanvas)
TableFrame = ttk.Frame(TableCanvas)
SettingsFrame = ttk.Frame(SettingsCanvas)

FilterCanvas.create_window((0, 0), window=FilterFrame, anchor="nw", height="1837p", width="550p")
TableCanvas.create_window((0, 0), window=TableFrame, anchor="nw", height="410p", width="402p")
SettingsCanvas.create_window((0, 0), window=SettingsFrame, anchor="nw", height="500p", width="402p")

FilterFrame.bind(
	"<Configure>",
	lambda e: FilterCanvas.configure(
		scrollregion=FilterCanvas.bbox("all")
	)
)

fillerdata = (0)
TableBottom = ttk.Frame(TableCanvas)
TableBottom.columnconfigure(0, weight=1)
TableBottom.columnconfigure(1, weight=1)
TableBottom.columnconfigure(2, weight=1)
# REMOVED TO FIX BUG WITH THREADING FOR NOW
# CSVButton = ttk.Button(TableBottom, text="Re-Export CSV", command=CSVExport, style="EnabledButton.TButton")
# CSVButton.grid(row=0, column=0, pady=5, sticky=NSEW)
# XSLXButton = ttk.Button(TableBottom, text="Re-Export XLSX", command=XLSXExport, style="EnabledButton.TButton")
# XSLXButton.grid(row=0, column=1, pady=5, sticky=NSEW)
# ReRunLearn = ttk.Button(TableBottom, text="Re-Run w/ Learn", command=lambda: Learn(1, LastStockpile))
# ReRunLearn.grid(row=0, column=2, pady=5, sticky=NSEW)


# TableBottom.pack(expand=True, fill='x', side=BOTTOM)
TableBottom.pack(fill='x', side=BOTTOM)


ResultSheet = Sheet(TableFrame, data=fillerdata)
ResultSheet.enable_bindings()
ResultSheet.pack(expand=True, fill='both')
ResultSheet.set_options(table_bg="grey75", header_bg="grey55", index_bg="grey55", top_left_bg="grey15", frame_bg="grey15")

def SaveFilter():
	os.remove("Filter.csv")
	with open("Filter.csv", "w") as filterfile:
		filterfile.write("Number,Filter\n")
		for line in range(len(items.data)):
			try:
				filterfile.write(str(items.data[line][0]) + "," + str(items.data[line][17]) + "\n")
			except:
				print("Fail", line)
	with open("Config.txt", "w") as exportfile:
		exportfile.write(str(menu.CSVExport.get()) + "\n")
		exportfile.write(str(menu.XLSXExport.get()) + "\n")
		exportfile.write(str(menu.ImgExport.get()) + "\n")
		exportfile.write(str(menu.Set.get()) + "\n")
		exportfile.write(str(menu.Learning.get()) + "\n")
		exportfile.write(str(menu.updateBot.get()) + "\n")
		exportfile.write(str(menu.BotHost.get()) + "\n")
		exportfile.write(str(menu.BotPassword.get()) + "\n")
		exportfile.write(str(menu.BotGuildID.get()) + "\n")
	CreateButtons("")


def CreateButtons(self):
	global FilterFrame

	for widgets in FilterFrame.winfo_children():
		widgets.destroy()
	menu.iconrow = 1
	menu.iconcolumn = 0
	menu.lastcat = 0
	menu.itembuttons = []
	menu.icons = []
	sortedicons = []
	counter = 0
	if menu.Set.get() == 0:
		folder = "CheckImages//Default//"
	else:
		folder = "CheckImages//Modded//"
	# print("fresh menu", menu.icons)
	# print("fresh sorted", sortedicons)
	# print(items.data[1])
	for i in range(len(items.data)+1):
		# print("i",i)
		for x in items.data:
			# print("x",x)
			if x[0] == str(i):
				# print("Found",i)
				if os.path.exists(folder + str(i) + ".png") or os.path.exists(folder + str(i) + "C.png"):
					try:
						menu.icons.append((i, folder + str(i) + ".png", int(x[9]), int(x[10]), int(x[17]), str(x[3]), str(x[8])))
					except:
						print(x[17])
						print("oops", i)
			# filter.append((i, 0))
			# print(x[3],x[9],x[10])

	# print("icons", menu.icons)
	sortedicons = sorted(menu.icons, key=lambda x: (x[2], x[3]))

	# print("full menu", menu.icons)
	# print("full sorted", sortedicons)

	# CSVExport = IntVar()
	# XLSXExport = IntVar()
	# ImgExport = IntVar()

	SettingsFrame.columnconfigure(0, weight=1)
	SettingsFrame.columnconfigure(7, weight=1)
	SetLabel = ttk.Label(SettingsFrame, text="Icon set?", style="TLabel")
	SetLabel.grid(row=menu.iconrow, column=0)
	DefaultRadio = ttk.Radiobutton(SettingsFrame, text="Default", variable=menu.Set, value=0)
	DefaultRadio.grid(row=menu.iconrow, column=1)
	ModdedRadio = ttk.Radiobutton(SettingsFrame, text="Modded", variable=menu.Set, value=1)
	ModdedRadio.grid(row=menu.iconrow, column=2)
	menu.iconrow += 1
	catsep = ttk.Separator(SettingsFrame, orient=HORIZONTAL)
	catsep.grid(row=menu.iconrow, columnspan=8, sticky="ew", pady=10)
	menu.iconrow += 1
	LearningCheck = ttk.Checkbutton(SettingsFrame, text="Learning Mode?", variable=menu.Learning)
	LearningCheck.grid(row=menu.iconrow, column=0, columnspan=2)
	menu.iconrow += 1
	catsep = ttk.Separator(SettingsFrame, orient=HORIZONTAL)
	catsep.grid(row=menu.iconrow, columnspan=8, sticky="ew", pady=10)
	menu.iconrow += 1
	CSVCheck = ttk.Checkbutton(SettingsFrame, text="CSV?", variable=menu.CSVExport)
	CSVCheck.grid(row=menu.iconrow, column=0)
	XLSXCheck = ttk.Checkbutton(SettingsFrame, text="XLSX?", variable=menu.XLSXExport)
	XLSXCheck.grid(row=menu.iconrow, column=1)
	ImgCheck = ttk.Checkbutton(SettingsFrame, text="Image?", variable=menu.ImgExport)
	ImgCheck.grid(row=menu.iconrow, column=2)
	menu.iconrow += 1
	catsep = ttk.Separator(SettingsFrame, orient=HORIZONTAL)
	catsep.grid(row=menu.iconrow, columnspan=8, sticky="ew", pady=10)
	menu.iconrow += 1
	SendBotCheck = ttk.Checkbutton(SettingsFrame, text="Send To Bot?", variable=menu.updateBot)
	SendBotCheck.grid(row=menu.iconrow, column=0, rowspan=2, padx=5)
	SendBotCheck_ttp = CreateToolTip(SendBotCheck, 'Send results to Storeman-Bot Discord Bot?')
	BotHostLabel = ttk.Label(SettingsFrame, text="Bot Host:")
	BotHostLabel.grid(row=menu.iconrow, column=2)
	BotHost = ttk.Entry(SettingsFrame, textvariable=menu.BotHost)
	BotHost.grid(row=menu.iconrow, column=3, columnspan=2)
	BotHost_ttp = CreateToolTip(BotHost, 'Host is http://<your Storeman-Bot server IP>:8090')
	menu.iconrow += 1
	BotPasswordLabel = ttk.Label(SettingsFrame, text="Password:")
	BotPasswordLabel.grid(row=menu.iconrow, column=2)
	BotPassword = ttk.Entry(SettingsFrame, textvariable=menu.BotPassword)
	BotPassword.grid(row=menu.iconrow, column=3, columnspan=2)
	BotPassword.config(show="*")
	BotPassword_ttp = CreateToolTip(BotPassword, 'Password is set with bot using /spsetpassword command in Discord')
	menu.iconrow += 1
	BotGuildIDLabel = ttk.Label(SettingsFrame, text="GuildID (if you are using a multi-server instance):")
	BotGuildIDLabel.grid(row=menu.iconrow, column=2)
	BotGuildID = ttk.Entry(SettingsFrame, textvariable=menu.BotGuildID)
	BotGuildID.grid(row=menu.iconrow, column=3, columnspan=2)
	BotGuildID_ttp = CreateToolTip(BotGuildID, 'If you are using a public instance of Storeman Bot, this is your Discord\'s "Guild ID"')
	menu.iconrow += 1
	catsep = ttk.Separator(SettingsFrame, orient=HORIZONTAL)
	catsep.grid(row=menu.iconrow, columnspan=8, sticky="ew", pady=10)
	menu.iconrow += 3
	SaveImg = PhotoImage(file="UI/Save.png")
	SaveButton = ttk.Button(FilterFrame, image=SaveImg, command=SaveFilter)
	
	SaveButton.image = SaveImg
	SaveButton.grid(row=menu.iconrow, column=7, columnspan=1, pady=5)
	SaveButton_ttp = CreateToolTip(SaveButton, 'Save Current Filter and Export Settings')

	SaveImg2 = PhotoImage(file="UI/Save.png")
	SaveButton2 = ttk.Button(SettingsFrame, image=SaveImg2, command=SaveFilter)

	SaveButton2.image = SaveImg2
	SaveButton2.grid(row=menu.iconrow, column=0, columnspan=8, pady=5)
	SaveButton_ttp2 = CreateToolTip(SaveButton2, 'Save Current Filter and Export Settings')
	# menu.iconrow += 1

	if menu.faction[0] == 0:
		Wimg = PhotoImage(file="UI//W0.png")
		WardenButton = ttk.Button(FilterFrame, image=Wimg, style="EnabledFaction.TButton")
		WardenButton.image = Wimg
	else:
		Wimg = PhotoImage(file="UI//W1.png")
		WardenButton = ttk.Button(FilterFrame, image=Wimg, style="DisabledFaction.TButton")
		WardenButton.image = Wimg
	WardenButton["command"] = lambda WardenButton=WardenButton: open_this("W", WardenButton)
	WardenButton.grid(row=menu.iconrow, column=0, columnspan=1, pady=5)
	WardenButton_ttp = CreateToolTip(WardenButton, 'Enable/Disable Warden-only Items')
	if menu.faction[1] == 0:
		Cimg = PhotoImage(file="UI//C0.png")
		ColonialButton = ttk.Button(FilterFrame, image=Cimg, style="EnabledFaction.TButton")
		ColonialButton.image = Cimg
	else:
		Cimg = PhotoImage(file="UI//C1.png")
		ColonialButton = ttk.Button(FilterFrame, image=Cimg, style="DisabledFaction.TButton")
		ColonialButton.image = Cimg
	ColonialButton["command"] = lambda ColonialButton=ColonialButton: open_this("C", ColonialButton)
	ColonialButton.grid(row=menu.iconrow, column=1, columnspan=1, pady=5)
	ColonialButton_ttp = CreateToolTip(ColonialButton, 'Enable/Disable Colonial-only Items')
	menu.iconrow += 1
	for i in range(len(sortedicons)):
		# print("comparison", str(icons[i][2]), str(menu.lastcat))
		if str(sortedicons[i][2]) != str(menu.lastcat):
			menu.lastcat = int(sortedicons[i][2])
			menu.iconrow += 1
			try:
				catsep = ttk.Separator(FilterFrame, orient=HORIZONTAL)
				catsep.grid(row=menu.iconrow, columnspan=8, sticky="ew", pady=10)
				menu.iconrow += 1
				catimg = PhotoImage(file="UI//cat" + str(menu.lastcat) + ".png")
				if menu.category[menu.lastcat][1] == 0:
					catbtn = ttk.Button(FilterFrame, image=catimg, style="EnabledCategory.TButton")
				else:
					catbtn = ttk.Button(FilterFrame, image=catimg, style="DisabledCategory.TButton")
				catbtn.image = catimg
				counter += 1
				catbtn["command"] = lambda i=i, catbtn=catbtn: open_this(str("cat-" + str(sortedicons[i][2])), catbtn)
				menu.iconcolumn = 0
				catbtn.grid(row=menu.iconrow, column=menu.iconcolumn, sticky="NSEW", columnspan=8)
				menu.iconrow += 1
				menu.itembuttons.extend((catbtn, "category", sortedicons[i][2]))
				catbtnttp = ("cat" + str(counter) + "_ttp = CreateToolTip(catbtn, '" + str(sortedicons[i][6]) + "')")
				exec(catbtnttp)
			except:
				print("Category exception")
		if os.path.exists("UI//" + str(sortedicons[i][0]) + ".png"):
			img = PhotoImage(file="UI//" + str(sortedicons[i][0]) + ".png")
			if sortedicons[i][4] == 0:
				btn = ttk.Button(FilterFrame, image=img, style="EnabledButton.TButton")
			elif sortedicons[i][4] == 1:
				btn = ttk.Button(FilterFrame, image=img, style="ManualDisabledButton.TButton")
			else:
				btn = ttk.Button(FilterFrame, image=img, style="DisabledButton.TButton")
			counter += 1


			btn.image = img
			# This stuff after the lambda makes sure they're set to the individual values, if I add more, have to be blah=blah before it
			btn["command"] = lambda i=i, btn=btn: open_this(sortedicons[i][0],btn)
			if menu.iconcolumn < 8:
				btn.grid(row=menu.iconrow, column=menu.iconcolumn, sticky="W", padx=2, pady=2)
				menu.iconcolumn += 1
			else:
				menu.iconrow += 1
				menu.iconcolumn = 0
				btn.grid(row=menu.iconrow, column=menu.iconcolumn, sticky="W", padx=2, pady=2)
				menu.iconcolumn += 1
			# print(btn, sortedicons[i][2])
			tooltiptext = re.sub('\'', '', sortedicons[i][5])
			# itembtnttp = ("item" + str(counter) + "_ttp = CreateToolTip(btn, '" + str(sortedicons[i][5]) + "')")
			itembtnttp = ("item" + str(counter) + "_ttp = CreateToolTip(btn, '" + tooltiptext + "')")
			exec(itembtnttp)
			menu.itembuttons.extend((btn, sortedicons[i][0], sortedicons[i][2]))
	QuitButton = ttk.Button(FilterFrame, text="Quit", style="EnabledButton.TButton", command=lambda: StockpilerWindow.quit())
	QuitButton.grid(row=500, column=0, columnspan=10, sticky="NSEW")
	FilterFrame.update()
	try:
		print("create_window height for Filter canvas should be roughly:", str(btn.winfo_y()-505))
	except:
		print("Might not be any buttons")


def IconPicker(image):
	global IconPickerWindow
	global tempicon
	tempicon = image
	root_x = StockpilerWindow.winfo_rootx()
	root_y = StockpilerWindow.winfo_rooty()
	if root_x == root_y == -32000:
		win_x = 90
		win_y = 90
	elif root_x < 20:
		win_x = 90
		win_y = 90
	else:
		win_x = root_x - 20
		win_y = root_y + 125

	location = "+" + str(win_x) + "+" + str(win_y)
	IconPickerWindow = Toplevel(StockpilerWindow)
	IconPickerWindow.geometry(location)
	IconPickerFrame = ttk.Frame(IconPickerWindow)
	IconPickerWindow.resizable(False, False)
	IconPickerFrame.pack()
	# IconPickerWindow.grab_set()
	# IconPickerWindow.focus_force()

	IconPickerFrame.grid_forget()
	NewIconLabel = ttk.Label(IconPickerFrame, text="What's this?")
	NewIconLabel.grid(row=0, column=0, columnspan=2)
	im = Image.fromarray(image)
	tkimage = ImageTk.PhotoImage(im)
	NewIconImage = ttk.Label(IconPickerFrame, image=tkimage)
	NewIconImage.image = image
	NewIconImage.grid(row=0, column=2)
	iconcolumn = 0
	iconrow = 1
	counter = 0
	temptime = datetime.datetime.now()
	for x in range(len(items.data)):
		# print(x)
		if os.path.exists("UI//" + str(items.data[x][0]) + ".png"):
			img = PhotoImage(file="UI//" + str(items.data[x][0]) + ".png")
			btn = ttk.Button(IconPickerFrame, image=img, style="EnabledButton.TButton")
			# btn = ttk.Button(IconPickerFrame, text=str(items.data[x][3]))
			counter += 1
			btn.image = img
			# This stuff after the lambda makes sure they're set to the individual values, if I add more, have to be blah=blah before it
			btn["command"] = lambda x=x, btn=btn: IndividualOrCrate(items.data[x][0])
			if iconcolumn < 18:
				btn.grid(row=iconrow, column=iconcolumn, sticky="W", padx=2, pady=2)
				# print("item:", items.data[x][3], "row:", iconrow, "column:", iconcolumn)
				iconcolumn += 1
			else:
				iconrow += 1
				iconcolumn = 0
				btn.grid(row=iconrow, column=iconcolumn, sticky="W", padx=2, pady=2)
				# print("item:", items.data[x][3], "row:", iconrow, "column:", iconcolumn)
				iconcolumn += 1
				# print(items.data[x][3])
			# print(btn, sortedicons[i][2])
			tooltiptext = re.sub('\'', '', items.data[x][3])
			# itembtnttp = ("item" + str(counter) + "_ttp = CreateToolTip(btn, '" + str(sortedicons[i][5]) + "')")
			itembtnttp = ("item" + str(counter) + "_ttp = CreateToolTip(btn, '" + tooltiptext + "')")
			exec(itembtnttp)

	# IconPickerFrame.update()
	# IconPickerWindow.focus_force()
	print("Took this long to make icon picker window:", datetime.datetime.now() - temptime)
	IconPickerWindow.wait_window()


def IndividualOrCrate(num):
	global tempicon
	print(num)
	IconPickerWindow.destroy()
	global IndOrCrateWindow
	root_x = StockpilerWindow.winfo_rootx()
	root_y = StockpilerWindow.winfo_rooty()
	if root_x == root_y == -32000:
		win_x = 90
		win_y = 90
	else:
		win_x = root_x - 20
		win_y = root_y + 125

	location = "+" + str(win_x) + "+" + str(win_y)
	IndOrCrateWindow = Toplevel(StockpilerWindow)
	IndOrCrateWindow.geometry(location)
	IndOrCrateWindow.resizable(False, False)
	# IndOrCrateWindow.grab_set()
	# IndOrCrateWindow.focus_force()
	IndOrCrateFrame = ttk.Frame(IndOrCrateWindow, style="TFrame")
	IndOrCrateFrame.pack()
	ForLabel = ttk.Label(IndOrCrateFrame, text="For:")
	ForLabel.grid(row=0, column=0)
	YouSelectedLabel = ttk.Label(IndOrCrateFrame, text="You\nSelected:")
	YouSelectedLabel.grid(row=0, column=1)
	im = Image.fromarray(tempicon)
	tkimage = ImageTk.PhotoImage(im)
	NewIconImage = ttk.Label(IndOrCrateFrame, image=tkimage)
	NewIconImage.image = tempicon
	NewIconImage.grid(row=1, column=0)
	UIimage = PhotoImage(file="Compare//" + str(num) + ".png")
	SelectedImage = ttk.Label(IndOrCrateFrame, image=UIimage)
	SelectedImage.image = UIimage
	SelectedImage.grid(row=1, column=1)
	IndividualButton = ttk.Button(IndOrCrateFrame, text="Individual", style="EnabledButton.TButton", command=lambda: SaveIcon(num,0,tempicon))
	IndividualButton.grid(row=5, column=0)
	CrateButton = ttk.Button(IndOrCrateFrame, text="Crate", style="EnabledButton.TButton", command=lambda: SaveIcon(num,1,tempicon))
	CrateButton.grid(row=5, column=1)
	TryAgainButton = ttk.Button(IndOrCrateFrame, text="Pick a different icon?", style="EnabledButton.TButton", command=lambda: BackToPicker(tempicon))
	TryAgainButton.grid(row=10, column=0, columnspan=2)
	IndOrCrateWindow.wait_window()


def BackToPicker(image):
	global IndOrCrateWindow
	IndOrCrateWindow.destroy()
	IconPicker(image)


def SaveIcon(num, type, image):
	global IndOrCrateWindow
	IndOrCrateWindow.destroy()
	if type == 0:
		name = str(num) + ".png"
	else:
		name = str(num) + "C.png"
	if menu.Set.get() == 0:
		save = 'CheckImages//Default//' + name
	else:
		save = 'CheckImages//Modded//' + name
	print("save:", save)
	cv2.imwrite(save, image)


def open_this(myNum,btn):
	# print(myNum,btn)
	# print(str(btn['style']))
	if str(btn['style']) == "EnabledButton.TButton":
		btn.configure(style="ManualDisabledButton.TButton")
		# print(len(items.data))
		for item in range(len(items.data)):
			# print(item[0])
			if str(items.data[item][0]) == str(myNum):
				items.data[item][17] = 1
				print(items.data[item][17])
	elif str(btn['style']) == "ManualDisabledButton.TButton":
		btn.configure(style="EnabledButton.TButton")
		for item in range(len(items.data)):
			# print(item[0])
			if str(items.data[item][0]) == str(myNum):
				items.data[item][17] = 0
				print(items.data[item][17])
	elif str(btn['style']) == "EnabledCategory.TButton":
		btn.config(style="DisabledCategory.TButton")
		menu.category[int(myNum[4:5])][1] = 1
		print("category number was 0")
		for item in range(len(items.data)):
			# print(item[0])
			# print(str(myNum[4:5]))
			# print("before test", items.data[item][17])
			if str(items.data[item][9]) == str(myNum[4:5]):
				if str(items.data[item][17]) == str(0):
					# print("yes")
					items.data[item][17] = 2
				# print(items.data[item][17])
			# print("after test", items.data[item][17])
		CreateButtons("blah")
	elif str(btn['style']) == "DisabledCategory.TButton":
		btn.config(style="EnabledCategory.TButton")
		menu.category[int(myNum[4:5])][1] = 0
		print("category number was 1")
		for item in range(len(items.data)):
			# print(item[0])
			# print(str(myNum[4:5]))
			if str(items.data[item][9]) == str(myNum[4:5]):
				if str(items.data[item][17]) == str(2):
					# print("yes")
					items.data[item][17] = 0
		CreateButtons("blah")
	elif myNum == str("W"):
		if str(btn['style']) == "EnabledFaction.TButton":
			btn.config(style="DisabledFaction.TButton")
			menu.faction[0] = 1
			for item in range(len(items.data)):
				if items.data[item][7] == "Warden" and str(items.data[item][17]) == "0":
					items.data[item][17] = 3
		else:
			btn.config(style="EnabledFaction.TButton")
			menu.faction[0] = 0
			for item in range(len(items.data)):
				if items.data[item][7] == "Warden" and str(items.data[item][17]) == "3":
					items.data[item][17] = 0
		CreateButtons("blah")
	elif myNum == str("C"):
		if str(btn['style']) == "EnabledFaction.TButton":
			btn.config(style="DisabledFaction.TButton")
			menu.faction[1] = 1
			for item in range(len(items.data)):
				# print(items.data[item][17])
				if items.data[item][7] == "Colonial" and str(items.data[item][17]) == "0":
					items.data[item][17] = 3
					# print("should be disabling", items.data[item])
		else:
			btn.config(style="EnabledFaction.TButton")
			menu.faction[1] = 0
			for item in range(len(items.data)):
				# print(items.data[item][7])
				if items.data[item][7] == "Colonial" and str(items.data[item][17]) == "3":
					items.data[item][17] = 0
					# print("should be enabling", items.data[item])
		CreateButtons("blah")

if os.path.exists("Config.txt"):
	with open("Config.txt") as file:
		content = file.readlines()
	content = [x.strip() for x in content]
	try:
		logging.info(str(datetime.datetime.now()) + ' Attempting to load from config.txt')
		menu.CSVExport.set(int(content[0]))
		menu.XLSXExport.set(int(content[1]))
		menu.ImgExport.set(int(content[2]))
		menu.Set.set(int(content[3]))
		menu.Learning.set(int(content[4]))
		menu.updateBot.set(int(content[5]))
		menu.BotHost.set(content[6])
		menu.BotPassword.set(content[7])
		menu.BotGuildID.set(content[8])
	except:
		logging.info(str(datetime.datetime.now()) + ' Loading from config.txt failed, setting defaults')
		menu.CSVExport.set(1)
		menu.XLSXExport.set(1)
		menu.ImgExport.set(1)
		menu.Set.set(0)
		menu.Learning.set(0)
else:
	menu.CSVExport.set(1)
	menu.XLSXExport.set(1)
	menu.ImgExport.set(1)
	menu.Set.set(0)
	menu.Learning.set(0)

CreateButtons("")

# hotkey = keyboard.HotKey(keyboard.HotKey.parse(ArtyLocHotkey), on_activate)
# hotkeytwo = keyboard.HotKey(keyboard.HotKey.parse(TargetLocHotkey), on_activate_two)

# listener = keyboard.GlobalHotKeys({
# 	Hotkeys.ArtyLocHotkey: on_activate,
# 	Hotkeys.TargetLocHotkey: on_activate_two})
# listener.start()


bindings = [
	[["f2"], None, on_activate],
	[["f3"], None, on_activate_two],
]

register_hotkeys(bindings)

start_checking_hotkeys()

StockpilerWindow.mainloop()