from pylatex import Document, TikZ
from tkinter import filedialog
from tkinter import *
import os
from .point import Point


class Visualization:

    def __init__(self, env_id, controller_stages):
        self._env_id = env_id
        self._controller_stages = controller_stages
        self._stage_boxes = []
        geometry_options = {
                            'landscape': True,
                            'includeheadfoot': False,
                            }
        self._doc = Document(page_numbers=False, geometry_options=geometry_options)
        self._filename = None

    def build(self):
        start = Point(0, 0)
        self._stage_boxes, end = self._controller_stages.visualize(start)

        with self._doc.create(TikZ()) as pic:
            for sb in self._stage_boxes:
                sb.build(pic)

        self._filename = self._get_filename()

        if self._filename != '':
            name = self._filename.split('.', 1)[0]
            self._doc.generate_pdf(name, compiler='pdflatex', clean_tex=True)

    def show(self):
        os.system(self._filename)

    def _get_filename(self):
        win = Tk()
        win.withdraw()
        return filedialog.asksaveasfilename(initialdir='/',
                                            title='Save as',
                                            filetypes=(('Portable Document Format', '*.pdf'), ('All Files', '*.*')),
                                            defaultextension='.pdf')
