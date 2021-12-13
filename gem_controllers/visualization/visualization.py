from .textbox import TextBox
import numpy as np
from pylatex import (Document, TikZ, TikZNode,
                     TikZDraw, TikZCoordinate,
                     TikZUserPath, TikZOptions,
                     Command, PageStyle)
from tkinter import filedialog
from tkinter import *
import os
import subprocess


class Visualization:

    def __init__(self, env, env_id, controller):
        self.env = env
        self.env_id = env_id
        self.controller_stages = controller
        self.stage_blocks = []
        self.doc = None
        self.path = None
        win = Tk()
        win.withdraw()
        self.path = filedialog.asksaveasfilename(initialdir='/',
                                                 title='Save as',
                                                 filetypes=(
                                                 ('Portable Document Format', '*.pdf'), ('All Files', '*.*')),
                                                 defaultextension='.pdf')

    def build(self):
        geometry_options = {
            'landscape': True,
            'includeheadfoot': False,
        }
        self.doc = Document(page_numbers=False, geometry_options=geometry_options)
        start = (0, 0)

        with self.doc.create(TikZ()) as pic:
            self.stage_blocks = self.controller_stages.visualize(pic, start)


        if self.path != '':
            path = self.path.split('.', 1)[0]
            self.doc.generate_pdf(path, compiler='pdflatex', clean_tex=True)


    def show(self):
        if self.path != '':
            os.system(self.path)
