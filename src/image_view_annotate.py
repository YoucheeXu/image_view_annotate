#!/usr/bin/python3
# -*- coding: UTF-8 -*-

# import the necessary packages
import os
import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox
from PIL import Image, ImageTk
import cv2
import numpy as np
import re

class App(tk.Frame):

	def __init__(self):
		super().__init__()

		# self.__window = tk.Tk()
		# 设置窗口标题
		# # self.__window.title('image View and Annotate')
		# self.__window.wm_title('image View and Annotate')

		# a reference to the image panels
		self.__imgPanel = None
		
		self.__imgLst = []

		self.__window_width = 0
		self.__window_height = 0

		self.__initUI()

		self.__img = None

	def __exit(self):
		self.quit()

	def __initUI(self):

		self.master.title("imgView&Annotation")

		toolbar = tk.Frame(self.master, bd = 1, relief = tk.RAISED)

		img = Image.open("resources\\icons8-add-file-16.png")
		eimg = ImageTk.PhotoImage(img)
		openImgButton = tk.Button(toolbar, image = eimg, relief = tk.FLAT, command = self.__selImage)
		openImgButton.image = eimg
		openImgButton.pack(side = tk.LEFT, padx = 2, pady = 2)

		img = Image.open("resources\\icons8-rename-16.png")
		eimg = ImageTk.PhotoImage(img)
		renameButton = tk.Button(toolbar, image = eimg, relief = tk.FLAT, command = self.__rename)
		renameButton.image = eimg
		renameButton.pack(side = tk.LEFT, padx = 2, pady = 2)

		img = Image.open("resources\\icons8-next-16.png")
		eimg = ImageTk.PhotoImage(img)
		nextImgButton = tk.Button(toolbar, image = eimg, relief = tk.FLAT, command = self.__nextImg)
		nextImgButton.image = eimg
		nextImgButton.pack(side = tk.LEFT, padx = 2, pady = 2)

		img = Image.open("resources\\icons8-previous-16.png")
		eimg = ImageTk.PhotoImage(img)
		privousImgButton = tk.Button(toolbar, image = eimg, relief = tk.FLAT, command = self.__previousImg)
		privousImgButton.image = eimg
		privousImgButton.pack(side = tk.LEFT, padx = 2, pady = 2)

		img = Image.open("resources\\icons8-rotate-right-16.png")
		eimg = ImageTk.PhotoImage(img)
		rotateRightButton = tk.Button(toolbar, image = eimg, relief = tk.FLAT, command = lambda: self.__rotateImg(-90))
		rotateRightButton.image = eimg
		rotateRightButton.pack(side = tk.LEFT, padx = 2, pady = 2)

		img = Image.open("resources\\icons8-rotate-left-16.png")
		eimg = ImageTk.PhotoImage(img)
		rotateLeftButton = tk.Button(toolbar, image = eimg, relief = tk.FLAT, command = lambda: self.__rotateImg(90))
		rotateLeftButton.image = eimg
		rotateLeftButton.pack(side = tk.LEFT, padx = 2, pady = 2)

		img = Image.open("resources\\icons8-delete-16.png")
		eimg = ImageTk.PhotoImage(img)
		delButton = tk.Button(toolbar, image = eimg, relief = tk.FLAT, command = self.__delImg)
		delButton.image = eimg
		delButton.pack(side = tk.LEFT, padx = 2, pady = 2)

		img = Image.open("resources\\icons8-close-window-16.png")
		eimg = ImageTk.PhotoImage(img)
		exitButton = tk.Button(toolbar, image = eimg, relief = tk.FLAT, command = self.__exit)
		exitButton.image = eimg
		exitButton.pack(side = tk.LEFT, padx = 2, pady = 2)

		toolbar.pack(side = tk.TOP, fill = tk.X)

		self.__imgPanel = tk.Label(text = "image View and Annotate", anchor = tk.CENTER)
		self.__imgPanel.pack()

		self.__statusbar = tk.Label(text = "on the way…", height=20, bd = 1, relief = tk.SUNKEN, anchor = tk.W)
		self.__statusbar.pack(side = tk.BOTTOM, fill = tk.X)

		# self.master.config(menu = menubar)
		self.pack()

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
	def __rename(self, initVal = None):
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
					self.__readAndshowImg(newName)
				else:
					messagebox.showerror("Error", "File name illegal")
					self.__rename(newName)

	def __delImg(self):
		curImg = self.__imgLst[self.__idx]
		os.remove(curImg)
		del self.__imgLst[self.__idx]

		self.__nextImg()

	# TODO: save
	def __rotateImg(self, degree):
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

			img = self.__scaleImg(self.__img)
			self.__displayImg(img)

	# FIXME: circulate
	def __nextImg(self):
		if self.__idx < len(self.__imgLst) - 1:
			self.__idx += 1
			imgPath = self.__imgLst[self.__idx]
			self.__readAndshowImg(imgPath)

	# FIXME: circulate
	def __previousImg(self):
		if self.__idx >= 1:
			self.__idx -= 1
			imgPath = self.__imgLst[self.__idx]
			self.__readAndshowImg(imgPath)

	def eventhandler(self, event):
		if event.keysym == "Left":
			self.__previousImg()
		elif event.keysym == 'Right':
			self.__nextImg()
		elif event.keysym == 'F2':
			self.__rename()
		elif event.keysym == 'F3':
			self.__selImage()
		elif event.keysym == 'Delete':
			self.__delImg()

	# FIXME: center the dialog
	def __selImage(self):

		# open a file chooser dialog and allow the user to select an input image
		imgPath = filedialog.askopenfilename(filetypes=[("Image files", ".jpg .png")])

		image = self.__readImg(imgPath)
		if image is not None:
			image = self.__scaleImg(image)
			self.__displayImg(image)

			self.__traverseImgs(imgPath)

	def __scaleImg(self, img, factor = 1):
		# Get number of pixel horizontally and vertically.
		(heightOfImg, widthOfImg) = img.shape[:2]
		print("img:", widthOfImg, heightOfImg)
		print("win w:", self.__window_width, ", win h:", self.__window_height)
		print("panel x:", self.__imgPanel.winfo_x(), ", panel y:", self.__imgPanel.winfo_y())
		print("statusbar x:", self.__statusbar.winfo_x(), ", statusbar y:", self.__statusbar.winfo_y())
		widthOfFram = self.__window_width
		heightOfFram = self.__window_height - self.__imgPanel.winfo_y() - 20
		# heightOfFram =  self.__statusbar.winfo_y() - self.__imgPanel.winfo_y()
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

		return cv2.resize(img, (int(newWidth), int(newHeight)), interpolation = cv2.INTER_CUBIC)	

	def __readImg(self, imgPath):
		if os.path.exists(imgPath):
			imgName = os.path.split(imgPath)[1]
			self.master.title(imgName)

			# load the image from disk
			# image = cv2.imread(imgPath)
			image = cv2.imdecode(np.fromfile(imgPath, dtype = np.uint8), cv2.IMREAD_COLOR)

			self.__img = image
			return image
		else:
			return None

	def __displayImg(self, image):

		# OpenCV represents images in BGR order; however PIL represents
		# images in RGB order, so we need to swap the channels
		image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

		# convert the images to PIL format...
		image = Image.fromarray(image)
		# ...and then to ImageTk format
		image = ImageTk.PhotoImage(image)

		self.__imgPanel.configure(image = image)
		self.__imgPanel.image = image

	def __readAndshowImg(self, imgPath):
		image = self.__readImg(imgPath)
		if image is not None:
			image = self.__scaleImg(image)
			self.__displayImg(image)

	# listen events of window resizing.
	def onWindowResize(self, event = None):
		if event is not None:
			if self.__window_width != self.master.winfo_width() or self.__window_height != self.master.winfo_height():
				if self.__window_width != self.master.winfo_width():
					self.__window_width = self.master.winfo_width()
				if self.__window_height != self.master.winfo_height():
					self.__window_height = self.master.winfo_height()


def main():
	# initialize the window toolkit along with the two image panels
	root = tk.Tk()

	# windows maximum
	root.state('zoomed')
	# linux maximum
	# root.attributes('-zoomed', True)

	app = App()
	root.bind_all('<KeyPress>', app.eventhandler)
	root.bind('<Configure>', app.onWindowResize)

	# kick off the GUI
	root.mainloop()


if __name__ == "__main__":
	# execute only if run as a script
	main()
