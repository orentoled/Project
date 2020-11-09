
#This file implements the GUI of the HighLighter#

import os
import wx
import wx.richtext as rt


APP_EXIT = 1
APP_OPEN = 2
APP_SAVE = 3
APP_NEW = 4

UNDOS_ALLOWED = 10



class RichTextPanel(wx.Panel):

    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        self.my_text = rt.RichTextCtrl(self, style=wx.TE_MULTILINE | wx.VSCROLL | wx.HSCROLL)


        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.my_text, 1, wx.ALL | wx.EXPAND)

        self.SetSizer(sizer)

    def on_open(self, event):
        wildcard = "TXT files (*.txt)|*.txt"
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

    def init_ui(self):
        menu_bar = wx.MenuBar()
        file_menu = wx.Menu()

        # oren
        self.undo_redo_n = UNDOS_ALLOWED
        # oren

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
        wildcard = "TXT files (*.txt)|*.txt"
        dialog = wx.FileDialog(self, "Open Text Files", wildcard=wildcard,
                               style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)

        if dialog.ShowModal() == wx.ID_CANCEL:
            return

        path = dialog.GetPath()

        if os.path.exists(path):
            with open(path) as fobj:
                for line in fobj:
                    self.text_panel.my_text.WriteText(line)

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

        tbar = self.toolbar
        doBind(tbar.AddTool(-1, 'Open', open_icon, shortHelp='Open File'),self.on_open)
        tbar.AddTool(-1, 'Save', save_icon, shortHelp='Save File')
        tbar.AddTool(-1, 'Only This', only_this_icon, shortHelp='Focus on the selected feature')
        tbar.AddTool(-1, 'Show All', show_all_icon, shortHelp='Restore')

        tundo = tbar.AddTool(wx.ID_UNDO, 'Undo', undo_icon, shortHelp='Undo')
        tredo = tbar.AddTool(wx.ID_REDO, 'Redo', redo_icon, shortHelp='Redo')

        tbar.EnableTool(wx.ID_REDO, False)

        self.Bind(wx.EVT_TOOL, self.on_undo, tundo)
        self.Bind(wx.EVT_TOOL, self.on_redo, tredo)

        finish = tbar.AddTool(-1, 'Finish', finish_icon, shortHelp='Finish session')
        doBind(finish, self.on_quit)
        
        tbar.AddSeparator()
        tbar.Realize()




def start_app():
    highlighter = wx.App()
    frame = Highlighter(None, title='Text Highlighter')
    frame.Show()
    highlighter.MainLoop()


start_app()
