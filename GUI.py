
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
ID_SHOW_ALL = 8
RESTORE_TO_DEFAULT_ID = 9
ONLY_THIS_ID = 10
NEXT_INST_ID = 11
PREV_INST_ID = 12

UNDOS_ALLOWED = 10





class RichTextPanel(wx.Panel):

    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        self.my_text = rt.RichTextCtrl(self, style=wx.TE_MULTILINE | wx.VSCROLL |
                                       wx.HSCROLL | wx.richtext.RE_READONLY)
        self.parent = parent

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.my_text, 1, wx.ALL | wx.EXPAND)
        # sizer.Add(self.my_text, proportion=1, flag=wx.EXPAND)
        # self.SetSizer(sizer)

        self.menu = wx.Menu()
        # self.menu.Append(TAG_WORD_ID, "tag word")
        self.menu.Append(RESTORE_TO_DEFAULT_ID, "Restore to default")
        self.menu.Append(ONLY_THIS_ID, "Only this")
        self.menu.Append(NEXT_INST_ID, "Next inst")
        self.menu.Append(PREV_INST_ID, "Prev. inst")
        self.my_text.SetContextMenu(self.menu)

        # attr_fontsize = wx.richtext.RichTextAttr()
        # attr_fontsize.SetFontSize(wx.FONTSIZE_MEDIUM)
        # self.my_text.SetBasicStyle(attr_fontsize)
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
        # if event_id == TAG_PARAGRAPH_ID:
        #     paragraph = self.find_paragraph(caret_position)
        #     start = self.my_text.GetValue().find(paragraph)
        #     end = start + len(paragraph)
        #     self.apply_tag((start, end))
        # elif event_id == TAG_SENTENCE_ID:
        #     sentence, x, y = self.find_sentence(caret_position)
        #     start = self.my_text.GetValue().find(sentence.strip())
        #     end = start + len(sentence.strip())
        #     self.apply_tag((start, end))
        # elif event_id == TAG_WORD_ID:
        #     word = self.find_word(caret_position)
        #     if word is not None:
        #         clean_word = " ".join(re.findall("[a-zA-Z]+", word))
        #         start = self.my_text.GetValue()[caret_position - 5:].find(word.strip()) + caret_position - 5
        #         end = start + len(word.strip())
        #         self.apply_tag((start, end), clean_word)

        if event_id == TAG_WORD_ID:
            # TODO fix that we can also mark two words
            word = self.find_word_to_tag(caret_position)
            if word is not None:
                clean_word = " ".join(re.findall("[a-zA-Z]+", word))
                start = self.my_text.GetValue()[caret_position - 5:].find(word.strip()) + caret_position - 5
                end = start + len(word.strip())
                self.apply_tag((start, end), clean_word, wx.BLUE)

        elif event_id == ONLY_THIS_ID:
            exp = None
            position = None
            for pos in self.parent.indices_range_to_exp_dict:
                if pos[0] <= caret_position <= pos[1]:
                    exp = self.parent.indices_range_to_exp_dict[pos]
                    position = pos
                    break

            if exp is not None and exp in self.parent.expressions_to_highlight:
                self.parent.highlight_words("LIGHT GREY")
                self.apply_tag(position, exp, wx.YELLOW)

    def apply_tag(self, position, word=None, color=wx.YELLOW):
        if word.lower() in self.parent.expressions_to_highlight:
            self.my_text.SetStyle(position[0], position[1], wx.TextAttr(colText=wx.BLACK, colBack=color))

    def find_paragraph(self, caret_position):
        paragraphs = self.my_text.GetValue().split("\n\n")
        for paragraph in paragraphs:
            paragraph = paragraph.strip()
            start = self.my_text.GetValue().find(paragraph)
            end = start + len(paragraph)
            if start < caret_position < end:
                return paragraph

    def find_word_to_tag(self, caret_position):
        index = caret_position
        text = self.my_text.GetValue()
        while (('a' <= text[index] <= 'z') or ('A' <= text[index] <= 'Z')) and index >= 0:
            # TODO '!', '.' etc.
            index -= 1
        if index != 0:
            index += 1
        word = ""
        while ('a' <= text[index] <= 'z') or ('A' <= text[index] <= 'Z'):
            word += text[index]
            index += 1
        return word

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
                return sentence, start, end

    # def find_word(self, caret_position):
    #     sentence, start, end = self.find_sentence(caret_position)
    #     words = sentence[caret_position - start - 5:].split(" ")
    #     for word in words:
    #         word = word.strip()
    #         clean_word = " ".join(re.findall("[a-zA-Z]+", word))
    #         if clean_word.lower() in self.parent.words_to_highlight:
    #             start = self.my_text.GetValue()[caret_position - 5:].find(word) + caret_position - 5
    #             end = start + len(word)
    #             # append dot if applicable
    #             if self.my_text.GetValue()[end] == "!":
    #                 word += "!"
    #             elif self.my_text.GetValue()[end] == "?":
    #                 word += "?"
    #             if start < caret_position < end:
    #                 return word
    #     return None

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
        self.combo = None
        self.toolbar = self.CreateToolBar(style=wx.TB_TEXT)
        self.groups = None
        self.words_to_highlight = None
        self.expressions_to_highlight = None
        self.opened_text = ""
        self.patterns = None
        self.re_highlight = None
        self.pos_list = []
        self.groups_pos_list = []
        self.group_expressions_dict = dict()
        self.expressions_group_dict = dict()
        self.indices_range_to_exp_dict = dict()
        # self.timer = wx.Timer(self, TIMER_ID)
        self.init_ui()
        self.MakeToolBar()

    def init_ui(self):
        menu_bar = wx.MenuBar()
        file_menu = wx.Menu()

        self.text_panel.my_text.Bind(wx.EVT_LEFT_DCLICK, self.on_double_click)

        # self.undo_redo_n = UNDOS_ALLOWED

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
        self.Bind(wx.EVT_MENU, self.on_save, id=APP_SAVE)

        menu_bar.Append(file_menu, '&File')
        self.SetMenuBar(menu_bar)

        self.SetSize((700, 600))
        self.Centre()
        self.groups, self.words_to_highlight = get_expressions_from_json(self)

    def on_quit(self, e):
        self.Close()

    def on_finish(self, e):
        self.on_save(e)
        self.Close()

    def on_show_all(self, e):
        self.highlight_words("YELLOW")

    def find_word_to_tag(self, caret_position, text):
        index = caret_position
        text_size = len(text)
        if caret_position >= text_size - 1:
            return None
        while (('a' <= text[index] <= 'z') or ('A' <= text[index] <= 'Z')) and index >= 0:
            # TODO '!', '.' etc.
            index -= 1
        if index != 0:
            index += 1
        word = ""
        while ('a' <= text[index] <= 'z') or ('A' <= text[index] <= 'Z'):
            word += text[index]
            index += 1
        return word


    def on_open(self, event):
        wildcard = "TXT and DOC files (*.txt;*.docx;*.doc)|*.txt;*.docx;*.doc"
        dialog = wx.FileDialog(self, "Open Text Files", wildcard=wildcard,
                               style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)

        if dialog.ShowModal() == wx.ID_CANCEL:
            return

        path = dialog.GetPath()
        self.groups, self.words_to_highlight = get_expressions_from_json(self)
        if os.path.exists(path):
            convert_word_to_txt_and_open(self, path)

        # print(f'{self.text_panel.my_text.GetValue()}')
        # self.text_panel.my_text.WriteText(("\n" + "\n").join(self.groups))
        # self.text_panel.my_text.WriteText(("\n" + "\n").join(self.words_to_highlight))
        # self.text_panel.my_text.WriteText(self.opened_text + "\n" + "\n")
        # self.text_panel.my_text.WriteText(f"index is: {search_words_in_txt(self.opened_text)}")

        self.get_positions()
        self.highlight_words("YELLOW")
        self.mark_groups("RED")

    def on_save(self, evt):

        if not self.text_panel.my_text.GetFilename():
            self.on_save_as(evt)
            self.get_positions()
            return

        self.text_panel.my_text.SaveFile()
        self.get_positions()

    def on_save_as(self, evt):

        wildcard, types = rt.RichTextBuffer.GetExtWildcard(save=True)

        dlg = wx.FileDialog(self, "Choose a filename",
                            wildcard=wildcard,
                            style=wx.FC_SAVE)

        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            if path:
                file_type = types[dlg.GetFilterIndex()]
                ext = rt.RichTextBuffer.FindHandlerByType(file_type).GetExtension()
                if not path.endswith(ext):
                    path += '.' + ext
                self.text_panel.my_text.SaveFile(path, file_type)

        dlg.Destroy()

    def forward_event(self, evt):

        # The RichTextCtrl can handle menu and update events for undo,
        # redo, cut, copy, paste, delete, and select all, so just
        # forward the event to it.
        self.text_panel.my_text.ProcessEvent(evt)

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

    # def get_positions(self):
    #     self.pos_list = []
    #     pos = 0
    #     num_of_newline = 1
    #     raw_text = self.text_panel.my_text.GetValue()
    #     # raw_text = raw_text.split(" ")
    #     transformed_text = self.text_panel.my_text.GetValue().replace("\n", " ").split(" ")
    #     # transformed_text = list(filter(None, transformed_text))
    #
    #     # print(f'transformed_text is: {self.opened_text.rstrip("\n")} \n')
    #     # print(f'transformed_text is: {transformed_text} \n')
    #     for word in transformed_text:
    #         # if '\n' in word:
    #         #     num_of_newline = len(word.splitlines())
    #         #     words_after_split = word.replace("\n", " ").split(" ")
    #         if word != '':
    #             clean_word = " ".join(re.findall("[a-zA-Z]+", word))
    #             # print(f'word is: {clean_word} \n')
    #             if clean_word.lower() in self.words_to_highlight:
    #                 if clean_word == word:
    #                     t = (pos, pos + len(word))
    #                     self.pos_list.append(t)
    #                 else:
    #                     t = (pos, pos + len(clean_word))
    #                     self.pos_list.append(t)
    #         # print(f'word: {word} \n')
    #         # print(f'pos_init: {pos} \n')
    #         pos += len(word) + 1
    #         # num_of_newline = 1
    #         # print(f'pos_after: {pos} \n')

    def get_positions(self):
        self.pos_list = []
        self.groups_pos_list = []
        modified_text = ""
        raw_text = self.text_panel.my_text.GetValue()
        i = 0
        while i < len(raw_text):
            for exp in self.expressions_to_highlight:
                s = raw_text.lower()[i: i + len(exp)]
                if s == exp:
                    t = (i, i + len(exp))
                    self.pos_list.append(t)
                    i += len(exp) - 1
                    self.indices_range_to_exp_dict[t] = exp
                    break
            i += 1

        list_of_pos_tuples = list(self.indices_range_to_exp_dict)
        j = 0
        for t in list_of_pos_tuples:
            modified_text += raw_text[j: t[1]]
            j = t[1] + 1
            exp = raw_text[t[0]: t[1]]
            # print(modified_text)
            modified_text += " " + self.expressions_group_dict[exp.lower()] + " "
            # print(modified_text)

        self.pos_list = []
        i = 0
        while i < len(modified_text):
            for exp in self.expressions_to_highlight:
                s = modified_text.lower()[i: i + len(exp)]
                if s == exp:
                    t = (i, i + len(exp))
                    self.pos_list.append(t)
                    i += len(exp) - 1
                    group = self.expressions_group_dict[exp]
                    t2 = (i + 2, i + 2 + len(group))
                    self.groups_pos_list.append(t2)
                    i += len(group)  # - 1
                    self.indices_range_to_exp_dict[t] = exp
                    break
            i += 1
        self.text_panel.my_text.Clear()
        self.text_panel.my_text.WriteText(modified_text)

    def highlight_words(self, color):
        for t in self.pos_list:
            self.text_panel.my_text.SetStyle(t, rt.RichTextAttr(wx.TextAttr("BLACK", color)))

    def mark_groups(self, color):
        attr_super = wx.richtext.RichTextAttr()
        attr_super.SetTextEffects(wx.TEXT_ATTR_EFFECT_SUPERSCRIPT)
        attr_super.SetFlags(wx.TEXT_ATTR_EFFECTS)
        attr_super.SetTextColour(wx.RED)
        attr_super.SetTextEffectFlags(wx.TEXT_ATTR_EFFECT_SUPERSCRIPT)
        for t in self.groups_pos_list:
            self.text_panel.my_text.SetStyle(t, attr_super)


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

    def on_double_click(self, e):
        caret_pos = self.text_panel.my_text.GetCaretPosition()
        text = self.text_panel.my_text.GetValue()
        exp = None
        for position in self.indices_range_to_exp_dict:
            if position[0] <= caret_pos <= position[1]:
                exp = self.indices_range_to_exp_dict[position]
                break

        if exp in self.expressions_group_dict:
            belong_to_group = self.expressions_group_dict[exp]
            group_index_in_list = self.groups.index(belong_to_group)
            self.combo.SetSelection(group_index_in_list)
        else:
            return

    def MakeToolBar(self):

        def doBind(item, handler, updateUI=None):
            self.Bind(wx.EVT_TOOL, handler, item)
            if updateUI is not None:
                self.Bind(wx.EVT_UPDATE_UI, updateUI, item)

        open_icon = wx.Bitmap('Icons\\open.png')
        save_icon = wx.Bitmap('Icons\\save2.png')
        show_all_icon = wx.Bitmap('Icons\\show.png')
        finish_icon = wx.Bitmap('Icons\\finish.png')
        redo_icon = wx.Bitmap('Icons\\redo.png')
        undo_icon = wx.Bitmap('Icons\\undo.png')
        cancel_icon = wx.Bitmap('Icons\\cancel.png')

        tbar = self.toolbar
        doBind(tbar.AddTool(-1, 'Open', open_icon, shortHelp='Open File'), self.on_open)
        tbar.AddTool(-1, 'Save', save_icon, shortHelp='Save File')
        tundo = tbar.AddTool(wx.ID_UNDO, 'Undo', undo_icon, shortHelp='Undo')
        tredo = tbar.AddTool(wx.ID_REDO, 'Redo', redo_icon, shortHelp='Redo')
        show_all = tbar.AddTool(ID_SHOW_ALL, 'Show All', show_all_icon, shortHelp='Restore')

        # tbar.EnableTool(wx.ID_REDO, False)

        self.Bind(wx.EVT_TOOL, self.forward_event, tundo)
        self.Bind(wx.EVT_TOOL, self.forward_event, tredo)

        finish = tbar.AddTool(-1, 'Finish', finish_icon, shortHelp='Finish session')
        doBind(finish, self.on_finish)

        doBind(show_all, self.on_show_all)

        cancel = tbar.AddTool(-1, 'Cancel', cancel_icon, shortHelp='Cancel all changed made')
        doBind(cancel, self.on_quit)

        tbar.AddSeparator()


        # tbar.Bind(wx.EVT_COMBOBOX, self.on_combo_select)
        self.combo = wx.ComboBox(tbar, 555, value="", choices=self.groups)
        tbar.AddControl(self.combo)
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
    word_extensions = ["docx", "doc", "DOCX", "DOC"]
    if fileExtension in word_extensions:
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
    # print(f'{path}.{file_extension}')
    output = pypandoc.convert_file(f'{path}.{file_extension.lower()}', 'plain')
    return output
    # doc_extentions = ["doc", "DOC"]
    # docx_extentions = ["docx", "DOCX"]
    # if file_extension in docx_extentions:
    #
    # elif file_extension in doc_extentions:




def get_expressions_from_json(self):
    with open("json.txt") as json_file:
        data = json.load(json_file)
        expressions_list_items = data.items()
        expressions_list, groups, words = [], [], []
        for key, value in expressions_list_items:
            groups.append(key)
            expressions_list.append(value)
            self.group_expressions_dict[key] = value
            for expression in value:
                self.expressions_group_dict[expression.lower()] = key
        # print(self.expressions_group_dict)
        # print(self.group_expressions_dict)
        # print(f'expressions_list: {expressions_list} \n')
        list_text = [item for sublist in expressions_list for item in sublist]
        for text in list_text:
            words_temp = re.findall('[^\W\d_]+', text)
            words.extend(words_temp)
        self.expressions_to_highlight = [word for word in list_text]
        self.expressions_to_highlight = [x.lower() for x in self.expressions_to_highlight]
        words = [x.lower() for x in words]
        # list_text = [item for sublist in expressions_list for item in sublist]
        # print(f'groups are: {groups} \n words are: {words}')
        return groups, words

# def get_expressions_from_json(self):
#     with open("json.txt") as json_file:
#         data = json.load(json_file)
#         expressions_list_items = data.items()
#         expressions_list, groups, words = [], [], []
#         for key, value in expressions_list_items:
#             groups.append(key)
#             expressions_list.append(value)
#             self.group_expressions_dict[key] = value
#             for expression in value:
#                 self.expressions_group_dict[expression] = key
#         # print(self.expressions_group_dict)
#         # print(self.group_expressions_dict)
#         # print(f'expressions_list: {expressions_list} \n')
#         list_text = [item for sublist in expressions_list for item in sublist]
#         words = [word for word in list_text]
#         words = [x.lower() for x in words]
#         # list_text = [item for sublist in expressions_list for item in sublist]
#         # print(f'groups are: {groups} \n words are: {words}')
#         return groups, words


def start_app():
    # get_expressions_from_json()
    highlighter = wx.App()
    frame = Highlighter(None, title='Text Highlighter')
    frame.Show()
    highlighter.MainLoop()

start_app()



"""
Json Functions
"""

# json = '{“machine group“: [“coffee machine“, “product“, “machine“], “button group“: [“Power button“, “Control Knob”]}'



