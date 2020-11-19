
#This file implements the GUI of the HighLighter#

import re
import os
import json
import wx
import wx.richtext as rt
from docx import Document
import io
import textract
import pypandoc
from bs4 import BeautifulSoup

# from docx.shared import Inches
# from docx.enum.text import WD_COLOR_INDEX
from idna import unicode

# event handling
APP_EXIT = 1
APP_OPEN = 2
APP_SAVE = 3
APP_NEW = 4
TAG_SENTENCE_ID = 5
TAG_PARAGRAPH_ID = 6
TAG_WORD_ID = 7


UNDOS_ALLOWED = 10




class RichTextPanel(wx.Panel):

    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        self.my_text = rt.RichTextCtrl(self, style=wx.TE_MULTILINE | wx.VSCROLL | wx.HSCROLL)


        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.my_text, 1, wx.ALL | wx.EXPAND)
        # sizer.Add(self.my_text, proportion=1, flag=wx.EXPAND)
        # self.SetSizer(sizer)

        self.menu = wx.Menu()
        self.menu.Append(TAG_SENTENCE_ID, "tag sentence")
        self.menu.Append(TAG_PARAGRAPH_ID, "tag paragraph")
        self.menu.Append(TAG_WORD_ID, "tag word")
        self.my_text.SetContextMenu(self.menu)
        self.SetSizerAndFit(sizer)

        self.Bind(wx.EVT_MENU, self.menu_event)

    def menu_event(self, event):
        """ handle context menu events """
        event_id = event.GetId()
        self.tag(event_id)

    def tag(self, event_id):
        # get caret position
        caret_position = self.my_text.GetCaretPosition() + 1
        # tag by event
        if event_id == TAG_PARAGRAPH_ID:
            paragraph = self.find_paragraph(caret_position)
            start = self.my_text.GetValue().find(paragraph)
            end = start + len(paragraph)
            self.apply_tag((start, end))
        elif event_id == TAG_SENTENCE_ID:
            sentence = self.find_sentence(caret_position)
            start = self.my_text.GetValue().find(sentence.strip())
            end = start + len(sentence.strip())
            self.apply_tag((start, end))
        elif event_id == TAG_WORD_ID:
            word = self.find_word(caret_position)
            start = self.my_text.GetValue().find(word.strip())
            end = start + len(word.strip())
            self.apply_tag((start, end))

    def apply_tag(self, position):
        self.my_text.SetStyle(position[0], position[1], wx.TextAttr(colText=wx.WHITE, colBack=wx.BLUE))

    def find_paragraph(self, caret_position):
        paragraphs = self.my_text.GetValue().split("\n\n")
        for paragraph in paragraphs:
            paragraph = paragraph.strip()
            start = self.my_text.GetValue().find(paragraph)
            end = start + len(paragraph)
            if start < caret_position < end:
                return paragraph

    def find_sentence(self, caret_position):
        sentences = self.find_paragraph(caret_position).split(".")
        for sentence in sentences:
            sentence = sentence.strip()
            start = self.my_text.GetValue().find(sentence)
            end = start + len(sentence)
            # append dot if applicable
            if self.my_text.GetValue()[end] == ".":
                sentence += "."
            if start < caret_position < end:
                return sentence

    def find_word(self, caret_position):
        words = self.find_sentence(caret_position).split(" ")
        for word in words:
            word = word.strip()
            start = self.my_text.GetValue().find(word)
            end = start + len(word)
            # append dot if applicable
            if self.my_text.GetValue()[end] == "!":
                word += "!"
            elif self.my_text.GetValue()[end] == "?":
                word += "?"
            if start < caret_position < end:
                return word



    def on_open(self, event):
        wildcard = "TXT files (*.txt)|*.txt|*.docx"
        dialog = wx.FileDialog(self, "Open Text Files", wildcard=wildcard,
                               style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)

        if dialog.ShowModal() == wx.ID_CANCEL:
            return

        path = dialog.GetPath()

        if os.path.exists(path):
            with open(path) as fobj:
                for line in fobj:
                    self.my_text.WriteText(line)


class Highlighter(wx.Frame):

    def __init__(self, *args, **kwargs):
        super(Highlighter, self).__init__(*args, **kwargs)
        self.SetTitle(kwargs['title'])
        self.text_panel = RichTextPanel(self)
        self.toolbar = self.CreateToolBar(style=wx.TB_TEXT)
        self.MakeToolBar()
        self.init_ui()
        self.groups = None
        self.words_to_highlight = None
        self.opened_text = ""
        self.patterns = None
        self.re_highlight = None
        self.pos_list = []



        # self.text_panel.my_text.WriteText("This is BLUE background with WHITE text, This is RED background with BLACK text")
        # self.text_panel.my_text.SetStyle((0, 41), rt.RichTextAttr(wx.TextAttr("WHITE", "BLUE")))
        # self.text_panel.my_text.SetStyle((42, 79), rt.RichTextAttr(wx.TextAttr("BLACK", "RED")))






    def init_ui(self):
        menu_bar = wx.MenuBar()
        file_menu = wx.Menu()

        self.undo_redo_n = UNDOS_ALLOWED

        new_menu_item = wx.MenuItem(file_menu, APP_NEW, '&New\tCtrl+N')
        open_menu_item = wx.MenuItem(file_menu, APP_OPEN, '&Open\tCtrl+O')
        save_menu_item = wx.MenuItem(file_menu, APP_SAVE, '&Save\tCtrl+S')

        new_icon = wx.Bitmap('Icons\\new.png')
        open_icon = wx.Bitmap('Icons\\open.png')
        save_icon = wx.Bitmap('Icons\\save2.png')
        exit_icon = wx.Bitmap('Icons\\exit.png')

        new_menu_item.SetBitmap(new_icon)
        open_menu_item.SetBitmap(open_icon)
        save_menu_item.SetBitmap(save_icon)

        file_menu.Append(new_menu_item)
        file_menu.Append(open_menu_item)
        file_menu.Append(save_menu_item)

        file_menu.AppendSeparator()

        # imp_menu = wx.Menu()
        # imp_menu.Append(wx.ID_ANY, 'Import newsfeed list...')
        # imp_menu.Append(wx.ID_ANY, 'Import bookmarks...')
        # imp_menu.Append(wx.ID_ANY, 'Import mail...')
        #
        # file_menu.Append(wx.ID_ANY, '&Import', imp_menu)

        quit_menu_item = wx.MenuItem(file_menu, APP_EXIT, '&Quit\tCtrl+Q')

        quit_menu_item.SetBitmap(exit_icon)

        file_menu.Append(quit_menu_item)

        self.Bind(wx.EVT_MENU, self.on_quit, id=APP_EXIT)
        self.Bind(wx.EVT_MENU, self.on_open, id=APP_OPEN)

        menu_bar.Append(file_menu, '&File')
        self.SetMenuBar(menu_bar)

        self.SetSize((700, 600))
        self.Centre()

    def on_quit(self, e):
        self.Close()

    def on_open(self, event):

        wildcard = "TXT and DOC files (*.txt;*.docx;*.doc)|*.txt;*.docx;*.doc"
        dialog = wx.FileDialog(self, "Open Text Files", wildcard=wildcard,
                               style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)

        if dialog.ShowModal() == wx.ID_CANCEL:
            return

        path = dialog.GetPath()
        print(path)
        self.groups, self.words_to_highlight = get_expressions_from_json()
        if os.path.exists(path):
            convert_word_to_txt_and_open(self, path)

        # self.text_panel.my_text.WriteText(("\n" + "\n").join(self.groups))
        # self.text_panel.my_text.WriteText(("\n" + "\n").join(self.words_to_highlight))
        # self.text_panel.my_text.WriteText(self.opened_text + "\n" + "\n")
        # self.text_panel.my_text.WriteText(f"index is: {search_words_in_txt(self.opened_text)}")

        self.get_positions()
        self.highlight_words()



    #     self.do_regex()
    #
    # def do_regex(self):
    #     # Setup regex
    #     self.patterns = [r'\b' + word + r'\b' for word in self.words_to_highlight]
    #     self.re_highlight = re.compile('(' + '|'.join(p for p in self.patterns) + ')+', re.IGNORECASE)
    #
    #     print(f'patterns: {self.patterns}')
    #     print(f're_highlight: {self.re_highlight}')

    # def highlight_words(self):
    #     for para in self.opened_text:
    #         text_item = para.text
    #         if len(self.re_highlight.findall(text_item)) > 0:
    #             matches = self.re_highlight.finditer(text_item)
    #             para.text = ''
    #             p3 = 0
    #             for match in matches:
    #                 p1 = p3
    #                 p2, p3 = match.span()
    #                 para.add_run(text_item[p1:p2])
    #                 run = para.add_run(text_item[p2:p3])
    #                 run.font.highlight_color = WD_COLOR_INDEX.YELLOW
    #             para.add_run(text_item[p3:])

    def get_positions(self):
        pos = 0
        transformed_text = self.opened_text.replace("\n", " ").split(" ")
        transformed_text = filter(None, transformed_text)
        # print(f'transformed_text is: {self.opened_text.rstrip("\n")} \n')
        print(f'transformed_text is: {transformed_text} \n')
        for word in transformed_text:
            clean_word = " ".join(re.findall("[a-zA-Z]+", word))
            # print(f'word is: {clean_word} \n')
            if clean_word.lower() in self.words_to_highlight:
                if clean_word == word:
                    t = (pos + 1, pos + len(word) + 1)
                    self.pos_list.append(t)
                else:
                    t = (pos + 1, pos + len(clean_word) + 1)
                    self.pos_list.append(t)
            print(f'word: {word} \n')
            print(f'pos_init: {pos} \n')
            pos += len(word) + 1
            print(f'pos_after: {pos} \n')




    def highlight_words(self):
        for t in self.pos_list:
            self.text_panel.my_text.SetStyle(t, rt.RichTextAttr(wx.TextAttr("BLACK", "YELLOW")))

        self.text_panel.my_text.SetStyle((0, 3), rt.RichTextAttr(wx.TextAttr("BLACK", "YELLOW")))

    def on_undo(self, e):
        if 1 < self.undo_redo_n <= UNDOS_ALLOWED:
            self.undo_redo_n = self.undo_redo_n - 1

        if self.undo_redo_n == 1:
            self.toolbar.EnableTool(wx.ID_UNDO, False)

        if self.undo_redo_n == UNDOS_ALLOWED - 1:
            self.toolbar.EnableTool(wx.ID_REDO, True)

    def on_redo(self, e):
        if UNDOS_ALLOWED > self.undo_redo_n >= 1:
            self.undo_redo_n = self.undo_redo_n + 1
            self.toolbar.EnableTool(wx.ID_UNDO, True)

        if self.undo_redo_n == UNDOS_ALLOWED:
            self.toolbar.EnableTool(wx.ID_REDO, False)

    def MakeToolBar(self):

        def doBind(item, handler, updateUI=None):
            self.Bind(wx.EVT_TOOL, handler, item)
            if updateUI is not None:
                self.Bind(wx.EVT_UPDATE_UI, updateUI, item)

        open_icon = wx.Bitmap('Icons\\open.png')
        save_icon = wx.Bitmap('Icons\\save2.png')
        only_this_icon = wx.Bitmap('Icons\\spotlight.png')
        show_all_icon = wx.Bitmap('Icons\\show.png')
        finish_icon = wx.Bitmap('Icons\\finish.png')
        redo_icon = wx.Bitmap('Icons\\redo.png')
        undo_icon = wx.Bitmap('Icons\\undo.png')
        cancel_icon = wx.Bitmap('Icons\\cancel.png')

        tbar = self.toolbar
        doBind(tbar.AddTool(-1, 'Open', open_icon, shortHelp='Open File'),self.on_open)
        tbar.AddTool(-1, 'Save', save_icon, shortHelp='Save File')
        tundo = tbar.AddTool(wx.ID_UNDO, 'Undo', undo_icon, shortHelp='Undo')
        tredo = tbar.AddTool(wx.ID_REDO, 'Redo', redo_icon, shortHelp='Redo')
        tbar.AddTool(-1, 'Only This', only_this_icon, shortHelp='Focus on the selected feature')
        tbar.AddTool(-1, 'Show All', show_all_icon, shortHelp='Restore')

        tbar.EnableTool(wx.ID_REDO, False)

        self.Bind(wx.EVT_TOOL, self.on_undo, tundo)
        self.Bind(wx.EVT_TOOL, self.on_redo, tredo)

        finish = tbar.AddTool(-1, 'Finish', finish_icon, shortHelp='Finish session')
        doBind(finish, self.on_quit)

        cancel = tbar.AddTool(-1, 'Cancel', cancel_icon, shortHelp='Cancel all changed made')
        doBind(cancel, self.on_quit)
        
        tbar.AddSeparator()
        tbar.Realize()


def search_words_in_txt(text):

    word = 'machine'
    index = text.split().index(word)

    position = 0
    for i, word in enumerate(text):
        position += (1 + len(word))
        if i >= index:
            break
    return position

def convert_word_to_txt_and_open(self, path):
    relevant_path = path.split("\\")[-1]
    filename = relevant_path.split(".")[-2]
    fileExtension = relevant_path.split(".")[-1]
    path_without_type = path.split(".")[-2]
    word_extenstions = ["docx", "doc", "DOCX", "DOC"]
    if fileExtension in word_extenstions:
        output = handle_files(self, path_without_type, fileExtension)
        # text = BeautifulSoup(output, features="lxml").get_text('\n')
        # self.text_panel.my_text.WriteText(text)
        self.text_panel.my_text.WriteText(output)
        for line in output:
            self.opened_text += line + "\n"
            # self.text_panel.my_text.WriteText(line)
        # content = textract.process(f'{path}', encoding='utf-8')
        # textFilename = path_without_type + ".txt"
        # write_text_file = open(textFilename, "wb")
        # write_text_file.write(content)
        # write_text_file.close()
        # with open(textFilename, encoding='utf-8') as fobj:
        #     for line in fobj:
        #         self.opened_text += line + "\n"
        #         self.text_panel.my_text.WriteText(line)


        # docxFilename = path
        # # print(docxFilename)
        # document = Document(docxFilename)
        # textFilename = path_without_type + ".txt"
        # with io.open(textFilename, "w", encoding="utf-8") as textFile:
        #     for para in document.paragraphs:
        #         textFile.write(unicode(para.text))
        # with open(textFilename, encoding='utf-8', errors='ignore') as fobj:
        #     for line in fobj:
        #         self.opened_text += line + "\n"
        #         self.text_panel.my_text.WriteText(line)

        # if os.path.exists(textFilename):
        #     os.remove(textFilename)
    else:
        with open(path, encoding='utf-8', errors='ignore') as fobj:
            for line in fobj:
                self.opened_text += line + "\n"
                self.text_panel.my_text.WriteText(line)

def handle_files(self, path, file_extension):
    print(f'{path}.{file_extension}')
    output = pypandoc.convert_file(f'{path}.{file_extension.lower()}', 'plain')
    return output
    # doc_extentions = ["doc", "DOC"]
    # docx_extentions = ["docx", "DOCX"]
    # if file_extension in docx_extentions:
    #
    # elif file_extension in doc_extentions:




def get_expressions_from_json():
    with open("json.txt") as json_file:
        data = json.load(json_file)
        expressions_list_items = data.items()
        expressions_list, groups, words = [], [], []
        for key, value in expressions_list_items:
            groups.append(key)
            expressions_list.append(value)
        # print(f'expressions_list: {expressions_list} \n')
        list_text = [item for sublist in expressions_list for item in sublist]
        for text in list_text:
            words_temp = re.findall('[^\W\d_]+', text)
            words.extend(words_temp)
        words = [x.lower() for x in words]
        # list_text = [item for sublist in expressions_list for item in sublist]
        print(f'groups are: {groups} \n words are: {words}')
        return groups, words


def start_app():
    get_expressions_from_json()
    highlighter = wx.App()
    frame = Highlighter(None, title='Text Highlighter')
    frame.Show()
    highlighter.MainLoop()

start_app()



"""
Json Functions
"""

# json = '{“machine group“: [“coffee machine“, “product“, “machine“], “button group“: [“Power button“, “Control Knob”]}'



