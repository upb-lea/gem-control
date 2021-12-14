from pylatex import Document, TikZ
from tkinter import filedialog
from tkinter import *
import os
from .point import Point


class Visualization:

    def __init__(self, env_id, controller_stages, data_type=('pdf',)):
        self._env_id = env_id
        self._controller_stages = controller_stages
        self._stage_boxes = []
        self._data_type = tuple(data_type)
        geometry_options = {'landscape': True, 'includeheadfoot': False}
        self._doc = Document(page_numbers=False, geometry_options=geometry_options)
        self._filenames = None
        self._pdf_name = None

    def build(self):
        start = Point(0, 0)
        self._stage_boxes = self._controller_stages.visualize(start)

        with self._doc.create(TikZ()) as pic:
            for sb in self._stage_boxes:
                sb.build(pic)

        self._filenames = self._get_filename()

        for filename in self._filenames:
            name, data_type = filename.split('.', 1)

            if data_type == 'pdf':
                self._doc.generate_pdf(name, compiler='pdflatex', clean_tex=True)
                self._pdf_name = filename
            elif data_type == 'tex':
                self._doc.generate_tex(name)

    def show(self):
        if self._pdf_name is not None:
            os.system(self._pdf_name)

    def _get_filename(self):
        win = Tk()
        win.withdraw()
        for data_type in self._data_type:
            if 'pdf' == data_type:
                filetypes = (('Portable Document Format (*.pdf)', '*.pdf'), ('All Files', '*.*'))
                yield filedialog.asksaveasfilename(initialdir='/', title='Save as', filetypes=filetypes, defaultextension='.pdf')
            elif 'tex' == data_type:
                filetypes = (('TeX Document (*.tex)', '*.tex'), ('All Files', '*.*'))
                yield filedialog.asksaveasfilename(initialdir='/', title='Save as', filetypes=filetypes, defaultextension='.tex')
            else:
                raise ValueError()

