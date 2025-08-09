#!/usr/bin/python3
# -*- coding: UTF-8 -*-
from __future__ import annotations
import sys
import os
import tkinter.messagebox as tkMessageBox
from tkinter import filedialog, simpledialog
import tkinter as tk
from typing import cast, override, Any
from idlelib.statusbar import MultiStatusBar

import numpy as np
import cv2
import PIL

from pyutilities.logit import pv
# from pyutilities.win_app import ImagePanelCtrl, WinApp
from pyutilities.tkwin import ImagePanelCtrl, tkWin
from pyutilities.utilities import legal_name


class App(tkWin):

    def __init__(self, path_: str, xmlfile: str):
        super().__init__(path_, xmlfile)

        # resize row 1 and column 0 with window
        _ = self._win.rowconfigure(1, weight=1)
        _ = self._win.columnconfigure(0, weight=1)
        # set minimum height for row 0 and 2
        _ = self._win.rowconfigure(0, minsize=20)
        _ = self._win.rowconfigure(2, minsize=20)

        self._image_list: list[str] = []

        self._image: cv2.typing.MatLike | None = None
        self._idx: int = -1

        self._image_panel: ImagePanelCtrl = cast(ImagePanelCtrl, self.get_control("pnlImage"))
        self._statusbar: MultiStatusBar = cast(MultiStatusBar, self.get_control("Statusbar"))

        # windows maximum
        # self._win.state('zoomed')
        # linux maximum
        # self._win.attributes('-zoomed', True)

    # FIXME: the order is not responding with the windows file order
    def _traverse_imgs(self, img: str):
        print(f"file: {img}")
        if len(self._image_list) > 0:
            self._image_list.clear()
        path, img_name = os.path.split(img)

        i: int = 0
        files = os.listdir(path)
        for file in files:
            file_path = os.path.join(path, file)
            if os.path.isfile(file_path):
                ext = os.path.splitext(file_path)[-1]
                ext = ext.lower()
                if ext in [".jpg", ".png"]:
                    self._image_list.append(file_path)
                    if img_name == file:
                        self._idx = i
                    i += 1
        print(f"there is {len(self._image_list)} images.")
        print(self._image_list)
        print(f"the index is {self._idx}.")

    # FIXME: 1) size of askstring is not proper
    # 2) left key doesn't work
    def _rename_image(self, init_val: str = ""):
        try:
            image_name = self._image_list[self._idx]
        except IndexError:
            return ""
        path, fname = os.path.split(image_name)
        name, ext = os.path.splitext(fname)
        if not init_val:
            init_val = name

        new_name = simpledialog.askstring(
            title="Rename " + name, prompt="rename to ", initialvalue=init_val
        )
        if new_name is not None:
            if len(new_name) > 0:
                new_name2 = legal_name(new_name)
                if len(new_name2) == len(new_name):
                    new_name = os.path.join(path, new_name + ext)
                    os.rename(image_name, new_name)
                    print(image_name + " is be renamed to " + new_name)
                    self._image_list[self._idx] = new_name
                    return new_name
                else:
                    # _ = messagebox.showerror("Error", "File name illegal")
                    _ = self.show_err("Error", f"File name '{new_name}' illegal")
        return ""

    def _delete_image(self):
        try:
            cur_image = self._image_list[self._idx]
        except IndexError:
            return ""
        image_name = os.path.split(cur_image)[1]
        res = tkMessageBox.askquestion(
            image_name, "Do you really want to delete?"
        )
        if res == "yes":
            os.remove(cur_image)
            del self._image_list[self._idx]
            return self._next_image()
        return ""

    # TODO: save
    def _rotate_image(self, image: cv2.typing.MatLike | None, degree: float):
        assert self._image_panel
        if image is not None:
            # Shape of image in terms of pixels.
            h, w = cast(tuple[int, int], image.shape[:2])

            ll: int = max(w, h)
            cx, cy = (ll // 2, ll // 2)
            padding_w: int = (ll - w) // 2  # 指定零填充的宽度
            padding_h: int = (ll - h) // 2  # 指定零填充的高度

            # 在原图像做对称的零填充，使得图片由矩形变为方形
            img_padded: cv2.typing.MatLike = np.zeros(shape=(ll, ll, 3), dtype=np.uint8)
            img_padded[padding_h : padding_h + h, padding_w : padding_w + w, :] = image

            # getRotationMatrix2D creates a matrix needed for transformation.
            # - (cX, cY): 旋转的中心点坐标
            # - degree: 旋转的度数，正度数表示逆时针旋转，而负度数表示顺时针旋转。
            # - 1.0：旋转后图像的大小，1.0原图，2.0变成原来的2倍，0.5变成原来的0.5倍
            M = cv2.getRotationMatrix2D((cx, cy), degree, 1)
            rotated_padded = cv2.warpAffine(img_padded, M, (ll, ll))

            image = rotated_padded[
                padding_w : padding_w + w, padding_h : padding_h + h, :
            ]
            return image

    def _next_image(self):
        if self._idx < len(self._image_list) - 1:
            self._idx += 1
        else:
            self._idx = 0
        return self._image_list[self._idx]

    def _prev_image(self):
        if self._idx >= 1:
            self._idx -= 1
        else:
            self._idx = len(self._image_list) - 1
        return self._image_list[self._idx]

    # TODO: center the dialog
    def _open_image(self):
        # open a file chooser dialog and allow the user to select an input image
        return filedialog.askopenfilename(filetypes=[("Image files", ".jpg .png")])

    def _scale_image(self, image: cv2.typing.MatLike, factor: float = 1):
        assert self._image_panel and self._statusbar
        # Get number of pixel horizontally and vertically.
        image_height, image_width = cast(tuple[int, int], image.shape[:2])
        print("img:", image_width, image_height)
        print("win w:", self._ww, ", win h:", self._hh)
        print(
            "panel x:",
            self._image_panel.control.winfo_x(),
            ", panel y:",
            self._image_panel.control.winfo_y(),
        )
        print(
            "statusbar x:",
            self._statusbar.winfo_x(),
            ", statusbar y:",
            self._statusbar.winfo_y(),
        )
        self._win.update()
        fram_width = self._image_panel.control.winfo_width()
        # fram_height = self._window_height - self._imgPanel.winfo_y() - 20
        fram_height = self._statusbar.winfo_y() - \
            self._image_panel.control.winfo_y()
        print("panel:", fram_width, fram_height)
        ratio_width = image_width / fram_width
        ratio_height = image_height / fram_height
        print("ratio:", ratio_width, ratio_height)
        ratio_image = image_height / image_width
        print("ratio of Image:", ratio_image)
        scale = 1 / max(ratio_width, ratio_height)
        print("scale:", scale)
        new_width = image_width * scale * factor
        new_height = new_width * ratio_image * factor
        print("new:", new_width, new_height)

        # display_width = self._img_panel.winfo_width()
        # pv(display_width)
        # display_height = self._

        self._statusbar.set_label("info", f"{image_width}*{image_height}\t\t{scale*100: .2f}%")
        self._statusbar.set_label("index", f"{self._idx+1} of {len(self._image_list)}", "right")

        return cv2.resize(
            image, (int(new_width), int(new_height)), interpolation=cv2.INTER_CUBIC
        )

    def _read_image(self, image_path: str):
        if os.path.exists(image_path):
            image_name = os.path.split(image_path)[1]
            self._win.title(image_name)

            # load the image from disk
            # image = cv2.imdecode(np.fromfile(imagepath, dtype=np.uint8), cv2.IMREAD_COLOR)
            image = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)

            return image
        return None

    def keypress_handler(self, **kwargs: Any):
        key = cast(str, kwargs["key"])
        match key:
            case "Left":
                return self.process_message("btnPrvImg")
            case "Right":
                return self.process_message("btnNxtImg")
            case "F2":
                return self.process_message("btnRnmImg")
            case "F3":
                return self.process_message("btnOpnImg")
            case "Delete":
                return self.process_message("bntDelImg")
            case _:
                return False

    @override
    def _before_go(self):
        self.process_message("btnOpnImg")

    @override
    def process_message(self, idmsg: str, **kwargs: Any):
        match idmsg:
            case "btnOpnImg":
                image_path = self._open_image()
                self._traverse_imgs(image_path)
                self._image = self._read_image(image_path)
            case "btnRnmImg":
                image_path = self._rename_image()
                self._image = self._read_image(image_path)
            case "btnNxtImg":
                image_path = self._next_image()
                self._image = self._read_image(image_path)
            case "btnPrvImg":
                image_path = self._prev_image()
                self._image = self._read_image(image_path)
            case "btnRotClkwis":
                self._image = self._rotate_image(self._image, -90)
            case "btnRotAticlkwis":
                self._image = self._rotate_image(self._image, 90)
            case "bntDelImg":
                image_path = self._delete_image()
                self._image = self._read_image(image_path)
            case "WindowResize":
                pass
            case "KeyPress":
                return self.keypress_handler(**kwargs)
            case _:
                return super().process_message(idmsg, **kwargs)

        if self._image is not None:
            image = self._scale_image(self._image)
            self._image_panel.display_image(image) 

        return True


def main():
    cur_path = os.path.dirname(os.path.abspath(__file__))
    if getattr(sys, "frozen", False):
        cur_path = os.path.dirname(os.path.abspath(sys.executable))
    proj_path = os.path.join(cur_path, "..")
    win_xml = os.path.join(proj_path, "resources", "window.xml")
    my_app = App(cur_path, win_xml)

    # kick off the app
    my_app.go()


if __name__ == "__main__":
    # execute only if run as a script
    main()
