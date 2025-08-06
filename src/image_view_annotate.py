#!/usr/bin/python3
# -*- coding: UTF-8 -*-
import sys
import os
import re

import tkinter as tk
import tkinter.ttk as ttk
from tkinter import filedialog, simpledialog, messagebox

import numpy as np
import cv2

from pyutilities.logit import pv
from pyutilities.tkwin import tkWin


class StatusBar(tk.Frame):
	def __init__(self, _frmApp):
		tk.Frame.__init__(self, _frmApp)
		self.__label = tk.Label(self, bd = 1, relief = tk.SUNKEN, anchor = "w")
		self.__label.pack(fill = tk.X)
	def set(self, format0, *args):
		self.__label.config(text = format0 % args)
		self.__label.update_idletasks()
	def clear(self):
		self.__label.config(text="")
		self.__label.update_idletasks()


class App(tkWin):

	def __init__(self):
		super().__init__()
		# self._frmApp = root

		# resize row 1 and column 0 with window
		self._frmApp.rowconfigure(1, weight = 1)
		self._frmApp.columnconfigure(0, weight = 1)
		# set minimum height for row 0 and 2
		self._frmApp.rowconfigure(0, minsize = 20)
		self._frmApp.rowconfigure(2, minsize = 20)

		self.__imgLst = []

		self.__window_width = 0
		self.__window_height = 0

		# self._frmApp.title("imgView&Annotation")

		# toolbar = ToolBar(self._frmApp, self)
		# toolbar.grid(row=0, sticky="ew")

		# self.__imgPanel = tk.Label(text = "image View and Annotate", anchor = tk.CENTER)
		# self.__imgPanel.grid(row = 1, sticky = "ewsn")

		self.__imgPanel = None

		self.__statusbar = StatusBar(self._frmApp)
		self.__statusbar.grid(row=2, sticky="ew")

		self.__img = None

	def go(self):
		self.__imgPanel = self.get_control("ImageViewandAnnotate")

		# windows maximum
		# self._frmApp.state('zoomed')
		# linux maximum
		# self._frmApp.attributes('-zoomed', True)

		self._frmApp.bind_all('<KeyPress>', self.eventhandler)
		self._frmApp.bind('<Configure>', self.onWindowResize)
		self._frmApp.mainloop()

	# FIXME: the order is not responding with the windows file order
	def __traverseImgs(self, img):
		print("file:", img)
		if len(self.__imgLst) > 0:
			self.__imgLst.clear()
		# self.__imgLst.append(img)
		# self.__idx = 0;
		path, imgName = os.path.split(img)

		i = 0
		files = os.listdir(path)
		for file in files:
			filePath = os.path.join(path, file)
			if os.path.isfile(filePath):
				ext = os.path.splitext(filePath)[-1]
				ext = ext.lower()
				if ext in [".jpg", ".png"]:
					self.__imgLst.append(filePath)
					if imgName == file:
						self.__idx = i
					i += 1
		print("there is %d images." %len(self.__imgLst))
		print(self.__imgLst)
		print("the order is %d." %self.__idx)

	# FIXME: 1) size of askstring is not proper
	# 2) left key doesn't work
	def __rename_image(self, initVal = None):
		curImg = self.__imgLst[self.__idx]
		path, fName = os.path.split(curImg)
		name, ext = os.path.splitext(fName)
		if not initVal:
			initVal = name

		newName = simpledialog.askstring(title = "Rename " + name,
			prompt = "rename to ", initialvalue = initVal)
		if newName is not None:
			if len(newName) > 0:
				newName2 = re.sub('[\/:*?"<>|]', '', newName)
				if len(newName2) == len(newName):
					newName = os.path.join(path, newName + ext)
					os.rename(curImg, newName)
					print(curImg + " is be renamed to " + newName)
					self.__imgLst[self.__idx] = newName
					self.__read_show_image(newName)
				else:
					messagebox.showerror("Error", "File name illegal")
					self.__rename(newName)

	def __delete_image(self):
		curImg = self.__imgLst[self.__idx]
		os.remove(curImg)
		del self.__imgLst[self.__idx]

		self.__next_image()

	# TODO: save
	def __rotate_image(self, degree):
		if self.__img is not None:
			# Shape of image in terms of pixels.
			(h, w) = self.__img.shape[:2]

			l = max(w, h)
			(cX, cY) = (l // 2, l // 2)
			paddingW = (l - w) // 2	# 指定零填充的宽度
			paddingH = (l - h) // 2	# 指定零填充的高度

			# 在原图像做对称的零填充，使得图片由矩形变为方形
			img_padded = np.zeros(shape = (l, l, 3), dtype = np.uint8)
			img_padded[paddingH: paddingH + h, paddingW: paddingW + w, :] = self.__img

			# getRotationMatrix2D creates a matrix needed for transformation.
			# - (cX, cY): 旋转的中心点坐标
			# - degree: 旋转的度数，正度数表示逆时针旋转，而负度数表示顺时针旋转。
			# - 1.0：旋转后图像的大小，1.0原图，2.0变成原来的2倍，0.5变成原来的0.5倍
			M = cv2.getRotationMatrix2D((cX, cY), degree, 1)

			rotated_padded = cv2.warpAffine(img_padded, M, (l, l))

			self.__img = rotated_padded[paddingW: paddingW + w, paddingH: paddingH + h, :]

			img = self.__scale_image(self.__img)
			self.__imgPanel.display_image(img)

	# FIXME: circulate
	def __next_image(self):
		if self.__idx < len(self.__imgLst) - 1:
			self.__idx += 1
			imgPath = self.__imgLst[self.__idx]
			self.__read_show_image(imgPath)

	# FIXME: circulate
	def __prev_image(self):
		if self.__idx >= 1:
			self.__idx -= 1
			imgPath = self.__imgLst[self.__idx]
			self.__read_show_image(imgPath)

	# FIXME: center the dialog
	def __open_image(self):
		# open a file chooser dialog and allow the user to select an input image
		imgPath = filedialog.askopenfilename(filetypes=[("Image files", ".jpg .png")])

		image = self.__read_image(imgPath)
		if image is not None:
			self.__traverseImgs(imgPath)

			image = self.__scale_image(image)
			self.__imgPanel.display_image(image)

	def __scale_image(self, img, factor = 1):
		# Get number of pixel horizontally and vertically.
		(heightOfImg, widthOfImg) = img.shape[:2]
		print("img:", widthOfImg, heightOfImg)
		print("win w:", self.__window_width, ", win h:", self.__window_height)
		print("panel x:", self.__imgPanel.winfo_x(), ", panel y:", self.__imgPanel.winfo_y())
		print("statusbar x:", self.__statusbar.winfo_x(), ", statusbar y:", self.__statusbar.winfo_y())
		widthOfFram = self.__window_width
		# heightOfFram = self.__window_height - self.__imgPanel.winfo_y() - 20
		heightOfFram =  self.__statusbar.winfo_y() - self.__imgPanel.winfo_y()
		print("panel:", widthOfFram, heightOfFram)
		ratioOfWidth = widthOfImg / widthOfFram
		ratioOfHeight = heightOfImg / heightOfFram
		print("ratio:", ratioOfWidth, ratioOfHeight)
		ratioOfImg = heightOfImg / widthOfImg
		print("ratioOfImg:", ratioOfImg)
		scale = 1 / max(ratioOfWidth, ratioOfHeight)
		print("scale:", scale)
		newWidth = widthOfImg * scale * factor
		newHeight = newWidth * ratioOfImg * factor
		print("new:", newWidth, newHeight)

		self.__statusbar.set("%d*%d\t\t%.2f%%%%\t\t%d/%d" %(widthOfImg, heightOfImg, scale * 100, self.__idx + 1, len(self.__imgLst)))

		return cv2.resize(img, (int(newWidth), int(newHeight)), interpolation = cv2.INTER_CUBIC)	

	def __read_image(self, imgPath):
		if os.path.exists(imgPath):
			imgName = os.path.split(imgPath)[1]
			self._frmApp.title(imgName)

			# load the image from disk
			# image = cv2.imread(imgPath)
			image = cv2.imdecode(np.fromfile(imgPath, dtype = np.uint8), cv2.IMREAD_COLOR)

			self.__img = image
			return image
		else:
			return None

	def __read_show_image(self, imgPath):
		image = self.__read_image(imgPath)
		if image is not None:
			image = self.__scale_image(image)
			# self.__displayImg(image)
			self.__imgPanel.display_image(image)

	# listen events of window resizing.
	def onWindowResize(self, event = None):
		if event is not None:
			if self.__window_width != self._frmApp.winfo_width() or self.__window_height != self._frmApp.winfo_height():
				if self.__window_width != self._frmApp.winfo_width():
					self.__window_width = self._frmApp.winfo_width()
				if self.__window_height != self._frmApp.winfo_height():
					self.__window_height = self._frmApp.winfo_height()

	def eventhandler(self, event):
		if event.keysym == "Left":
			self.__prev_image()
		elif event.keysym == 'Right':
			self.__next_image()
		elif event.keysym == 'F2':
			self.__rename_image()
		elif event.keysym == 'F3':
			self.__open_image()
		elif event.keysym == 'Delete':
			self.__delete_image()

	def process_message(self, idCtrl, msg, extMsg=""):
		if idCtrl == "OpenImage":
			self.__open_image()
		elif idCtrl == "RenameImage":
			self.__rename_image()
		elif idCtrl == "NextImage":
			self.__next_image()
		elif idCtrl == "PreviousImage":
			self.__prev_image()
		elif idCtrl == "RotateClockwise":
			self.__rotate_image(-90)
		elif idCtrl == "RotateAnticlockwise":
			self.__rotate_image(90)
		elif idCtrl == "DeleteImage":
			self.__delete_image()
		elif idCtrl == "ExitApplication":
			super().exit_window()
		else:
			super().process_message(idCtrl, msg, extMsg)

def main():
	myApp = App()

	curPath = os.path.dirname(os.path.abspath(__file__))
	if getattr(sys, 'frozen', False):
		# print("script is packaged!")
		curPath = os.path.dirname(os.path.abspath(sys.executable))
	proj_path = os.path.join(curPath, "..")
	winXml = os.path.join(proj_path, 'resources', 'window.xml')
	myApp.create_window(winXml)

	# kick off the GUI
	myApp.go()


if __name__ == "__main__":
	# execute only if run as a script
	main()
