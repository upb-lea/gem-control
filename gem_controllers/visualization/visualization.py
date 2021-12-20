from pylatex import Document, TikZ
from tkinter import filedialog
from tkinter import *
import os


class Visualization:

    def __init__(self, env_id, controller_stages, data_type=('pdf', 'tex')):
        self._env_id = env_id
        self._controller_stages = controller_stages
        self._data_type = tuple(data_type)
        self._pdf_name = None

    def build(self):
        stage_boxes = self._controller_stages.visualize()
        doc = Document(page_numbers=False, geometry_options={'landscape': True, 'includeheadfoot': False})
        with doc.create(TikZ()) as pic:
            for stage_box in stage_boxes:
                stage_box.build(pic)

        for filename in self._get_filename():
            name, data_type = filename.split('.', 1)
            if data_type == 'pdf':
                doc.generate_pdf(name, compiler='pdflatex', clean_tex=True)
                self._pdf_name = filename
            elif data_type == 'tex':
                doc.generate_tex(name)

    def show(self):
        if self._pdf_name is not None:
            os.system(self._pdf_name)

    def _get_filename(self):
        win = Tk()
        win.withdraw()
        for data_type in self._data_type:
            if 'pdf' == data_type:
                filetypes = (('Portable Document Format (*.pdf)', '*.pdf'), ('All Files', '*.*'))
                yield filedialog.asksaveasfilename(initialdir='/', title='Save as', filetypes=filetypes,
                                                   defaultextension='.pdf')
            elif 'tex' == data_type:
                filetypes = (('TeX Document (*.tex)', '*.tex'), ('All Files', '*.*'))
                yield filedialog.asksaveasfilename(initialdir='/', title='Save as', filetypes=filetypes,
                                                   defaultextension='.tex')
            else:
                raise ValueError(
                    f'The file type {data_type} is not supported. Use the Portable Document Format (pdf) or Tex Document (tex) file type.')
