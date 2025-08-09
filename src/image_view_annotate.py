#!/usr/bin/python3
# -*- coding: UTF-8 -*-
from __future__ import annotations
import sys
import os
import tkinter.messagebox as tkMessageBox
from tkinter import filedialog, simpledialog
# import tkinter as tk
from typing import cast, override, Any
from idlelib.statusbar import MultiStatusBar

import numpy as np
import cv2
# import PIL
from PIL import Image, ImageSequence

from pyutilities.logit import pv, po
import pyutilities.cv2_utilities as cv2u
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

        self._image: cv2.typing.MatLike | list[cv2.typing.MatLike] | None = None
        self._idx: int = -1

        self._image_panel: ImagePanelCtrl = cast(ImagePanelCtrl, self.get_control("pnlImage"))
        self._statusbar: MultiStatusBar = cast(MultiStatusBar, self.get_control("Statusbar"))

        # windows maximum
        # self._win.state('zoomed')
        # linux maximum
        # self._win.attributes('-zoomed', True)

        self._support_exts: list[str] = [".jpg", ".jpeg", ".bmp", ".png",
            ".webp", ".tiff", ".tif", ".ppm",
            ".gif"]

        self._timer: str = ""

    # FIXME: the order is not responding with the windows file order
    def _traverse_imgs(self, img: str):
        po(f"file: {img}")
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
                if ext in self._support_exts:
                    self._image_list.append(file_path)
                    if img_name == file:
                        self._idx = i
                    i += 1
        po(f"there is {len(self._image_list)} images.")
        po(self._image_list)
        po(f"the index is {self._idx}.")

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
                    po(image_name + " is be renamed to " + new_name)
                    self._image_list[self._idx] = new_name
                    return new_name
                else:
                    _ = self.show_err("Error", f"File name '{new_name}' illegal")
        return ""

    def _delete_image(self):
        cur_image = self._image_list[self._idx]

        image_name = os.path.split(cur_image)[1]
        res = tkMessageBox.askquestion(
            image_name, "Do you really want to delete?"
        )
        if res == "yes":
            os.remove(cur_image)
            del self._image_list[self._idx]
            return self._next_image()
        return cur_image

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

    def _open_image(self):
        # open a file chooser dialog and allow the user to select an input image
        return filedialog.askopenfilename(filetypes=[("Image files", self._support_exts)])

    def _calc_sacle(self, image: cv2.typing.MatLike, factor: float = 1):
        assert self._image_panel and self._statusbar
        # Get number of pixel horizontally and vertically.
        image_height, image_width = cast(tuple[int, int], image.shape[:2])
        po("img:", image_width, image_height)
        po("win w:", self._ww, ", win h:", self._hh)
        po(
            "panel x:",
            self._image_panel.control.winfo_x(),
            ", panel y:",
            self._image_panel.control.winfo_y(),
        )
        po(
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
        po("panel:", fram_width, fram_height)
        ratio_width = image_width / fram_width
        ratio_height = image_height / fram_height
        po("ratio:", ratio_width, ratio_height)
        ratio_image = image_height / image_width
        po("ratio of Image:", ratio_image)
        scale = 1 / max(ratio_width, ratio_height)
        po("scale:", scale)
        new_width = image_width * scale * factor
        new_height = new_width * ratio_image * factor
        po("new:", new_width, new_height)

        # display_width = self._img_panel.winfo_width()
        # pv(display_width)
        # display_height = self._

        self._statusbar.set_label("info", f"{image_width}*{image_height}\t\t{scale*100: .2f}%")
        self._statusbar.set_label("index", f"{self._idx+1} of {len(self._image_list)}", "right")

        return int(new_width), int(new_height)

    def _read_image(self, image_path: str):
        if os.path.exists(image_path):
            image_name = os.path.split(image_path)[1]
            self._win.title(image_name)

            _, fename = os.path.splitext(image_name)

            match fename.lower():
                case ".tiff" | ".tif":
                    image = cv2u.read_image(image_path, cv2.IMREAD_COLOR)
                case ".gif":
                    images = Image.open(image_path)
                    image = [cv2.cvtColor(np.asarray(frame), cv2.COLOR_RGB2BGR) for frame in \
                        ImageSequence.Iterator(images)]
                case _:
                    # load the image from disk
                    image = cv2u.read_image(image_path)

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
    def go(self):
        _ = self.process_message("btnOpnImg")
        super().go()

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
                if self._image is not None:
                    if isinstance(self._image, list):
                        for i in range(len(self._image)):
                            self._image[i] = cv2u.rotate_image(self._image[i], -90)
                    else:
                        self._image = cv2u.rotate_image(self._image, -90)
                else:
                    return
            case "btnRotAticlkwis":
                if self._image is not None:
                    if isinstance(self._image, list):
                        for i in range(len(self._image)):
                            self._image[i] = cv2u.rotate_image(self._image[i], 90)
                    else:
                        self._image = cv2u.rotate_image(self._image, -90)
                else:
                    return
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
            if self._timer:
                self.win.after_cancel(self._timer)
                self._timer = ""
            if isinstance(self._image, list):
                if idmsg == "WindowResize":
                    return
                def update_frame(frames: list[cv2.typing.MatLike], index: int):
                    frame = frames[index]
                    next_index = (index + 1) % len(frames)
                    # image = self._scale_image(frame)
                    new_width, new_height = self._calc_sacle(frame)
                    image = cv2u.scale_image(frame, new_width, new_height, cv2.INTER_CUBIC)
                    self._image_panel.display_image(image)
                    self._timer = self.win.after(50, update_frame, frames, next_index)
                update_frame(self._image, 0)
            else:
                # image = self._scale_image(self._image)
                new_width, new_height = self._calc_sacle(self._image)
                image = cv2u.scale_image(self._image, new_width, new_height, cv2.INTER_CUBIC)
                self._image_panel.display_image(image)

        return True


def main():
    file_path = os.path.dirname(os.path.abspath(__file__))
    if getattr(sys, "frozen", False):
        file_path = os.path.dirname(os.path.abspath(sys.executable))
    proj_path = os.path.join(file_path, "..")
    win_xml = os.path.join(proj_path, "resources", "window.xml")
    my_app = App(proj_path, win_xml)

    # kick off the app
    my_app.go()


if __name__ == "__main__":
    # execute only if run as a script
    main()
