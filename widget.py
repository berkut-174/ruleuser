#! /usr/bin/env python
# -*- coding: utf8 -*-

###################################################################################################
# RuleUser
# widget.py
#
# Copyright (C) 2012,2013 Andrey Burbovskiy <xak-altsp@yandex.ru>
# Copyright (C) 2017 Артем Проскурнев (Artem Proskurnev) <tema@proskurnev.name>
# Поддерживается в Школе №830 г. Москва
#
# Developed specially for ALT Linux School.
# http://www.altlinux.org/LTSP
#
# Computer management and monitoring of users:
# - LTSP servers
# - Linux standalone clients
# - Windows standalone clients(only VNC)
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###################################################################################################

import gi
from gi.repository import Pango

import shlex
import shutil
import urllib
from dialogs import *
from tree import *
from util import *
import gettext

_ = gettext.gettext


####################################################################################################

def toolbar_button(pixbuf=None, tooltips=None, tooltip=None, toggle=None):
    image = Gtk.Image()
    image.set_from_pixbuf(pixbuf)
    if toggle:
        button = Gtk.ToggleToolButton()
    else:
        button = Gtk.ToolButton()
    button.set_icon_widget(image)
    button.set_property('can-focus', True)
    if tooltips and tooltip:
        # if GObject.pygobject_version < (2, 12, 0):
        #     button.set_tooltip(tooltips, tooltip)
        # else:
        button.set_tooltip_text(tooltip)
    return button


####################################################################################################

def menu_image_button(pixbuf, label):
    button = Gtk.ImageMenuItem(label)
    image = Gtk.Image()
    image.set_from_pixbuf(pixbuf)
    button.set_image(image)
    return button


####################################################################################################

def image_button(pixbuf=None, label=None, tooltips=None, tooltip=None, toggle=None):
    if toggle:
        button = Gtk.ToggleButton(label)
    else:
        button = Gtk.Button(label)
    button.set_property('can-focus', True)
    # button.set_can_focus(False)
    image = Gtk.Image()
    image.set_from_pixbuf(pixbuf)
    button.set_image(image)
    if tooltips and tooltip:
        # if GObject.pygobject_version < (2, 12, 0):
        #     tooltips.set_tip(button, tooltip)
        # else:
        button.set_tooltip_text(tooltip)
    return button


####################################################################################################

class menu_tool_button(Gtk.ToolButton):
    def __init__(self, pixbuf, tooltips, tooltip=None):
        Gtk.ToolButton.__init__(self, None)

        image = Gtk.Image()
        image.set_from_pixbuf(pixbuf)
        self.set_icon_widget(image)
        # if GObject.pygobject_version < (2, 12, 0):
        #     self.set_tooltip(tooltips, tooltip)
        # else:
        self.set_tooltip_text("")

        self.button = self.get_child()
        self.button.connect("button-press-event", self.event)

        self.menu = Gtk.Menu()

    def append(self, item):
        self.menu.append(item)

    def context_menu(self, event):
        self.menu.popup(None, None, None, None, event.button, event.time)
        self.menu.show_all()

    def event(self, data, event):
        if event.button == 1:
            self.context_menu(event)


####################################################################################################

class label_entry(Gtk.Fixed):
    def __init__(self, label_text, entry_text, width, length, x1, x2, editable=True, visibility=True):
        Gtk.Fixed.__init__(self)

        self.set_size_request(int(width * 7.4), 26)
        label = Gtk.Label(label_text)
        label.set_alignment(0, 0.5)
        self.entry = Gtk.Entry()
        self.entry.set_max_length(length)
        self.entry.set_text(entry_text)
        self.entry.set_property('width-chars', width)
        #~ self.entry_base_color = self.entry.get_style().copy().base[Gtk.StateFlags.NORMAL]
        self.set_editable(editable)
        if visibility == False:
            self.entry.set_visibility(False)
        self.put(label, x1, 0)
        self.put(self.entry, x2, 0)

    def get_text(self):
        return self.entry.get_text()

    def set_editable(self, editable):
        if editable == False:
            self.entry.set_property("editable", False)
            self.entry.modify_base(Gtk.StateFlags.NORMAL,
                                   Gdk.color_parse("light gray"))
        else:
            self.entry.set_property("editable", True)
            #~ self.entry.modify_base(Gtk.StateFlags.NORMAL, self.entry_base_color)


####################################################################################################

class file_entry(Gtk.Fixed):
    def __init__(self, pixbuf, label_text, entry_text, width, x1, x2, editable=True, folder=None):
        Gtk.Fixed.__init__(self)

        self.set_size_request(int(width * 7.4), 26)
        label = Gtk.Label(label_text)
        label.set_alignment(0, 0.5)
        self.entry = Gtk.Entry()
        self.entry.set_text(entry_text)
        self.entry.set_property('width-chars', width)
        self.button = image_button(pixbuf, "")
        self.button.set_size_request(25, 25)
        self.button.connect("clicked", file_chooser_dialog,
                            self.entry, label_text)

        if editable == False:
            self.entry.set_property("editable", False)
            self.entry.modify_base(Gtk.StateFlags.NORMAL,
                                   Gdk.color_parse("light gray"))

        self.put(label, x1, 0)
        self.put(self.entry, x2, 0)
        self.put(self.button, x2 + int(width * 7.4), 0)

    def get_text(self):
        return self.entry.get_text()


####################################################################################################

def file_chooser_dialog(self, entry, label_text, folder=None, action=None):
    dialog = Gtk.FileChooserDialog(label_text, None, Gtk.FileChooserAction.OPEN,
                                   (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OPEN, Gtk.ResponseType.OK))
    dialog.set_default_response(Gtk.ResponseType.OK)
    if folder:
        dialog.set_current_folder(os.path.expanduser(folder))
    else:
        dialog.set_current_folder(os.path.expanduser("~"))
    if action:
        dialog.set_action(action)
    response = dialog.run()
    if response == Gtk.ResponseType.OK:
        if "Gtk.Entry" in str(entry):
            entry.set_text(dialog.get_filename())
        elif "Gtk.ComboBox" in str(entry):
            entry.insert_text(0, dialog.get_filename())
            entry.set_active(0)
    dialog.destroy()


####################################################################################################

class file_browser(Gtk.VBox):
    def __init__(self, cfg, folder, folder_name):
        Gtk.VBox.__init__(self, False, 1)

        self.cfg = cfg
        self.folder = folder
        self.folder_name = folder_name
        self.current_folder = self.folder
        self.show_hidden = False
        self.file = None

        vbox = self

        # pb, file, filestat.st_size, modified, type_, sort_key
        self.fileList = Gtk.ListStore(
            GdkPixbuf.Pixbuf, str, str, str, str, str)
        self.fileList.set_default_sort_func(None)

        self.treeView = Gtk.TreeView(self.fileList)
        self.treeView.set_rules_hint(True)
        self.treeView.set_headers_visible(True)
        self.treeView.set_headers_clickable(True)
        self.treeView.set_grid_lines(Gtk.TreeViewGridLines.VERTICAL)
        self.treeView.modify_font(Pango.FontDescription(self.cfg.fontTree))
        self.treeView.connect("button-press-event",
                              self.tree_button_press_event)
        self.TARGETS = [
            ('application/x-kde-urilist', 0, 0),
            ('x-special/gnome-copied-files', 0, 0),
            ('text/uri-list', 0, 0), ]

        self.treeView.connect(
            "drag_data_get", self.drag_data_get_data, self.cfg)
        self.treeView.enable_model_drag_source(
            Gdk.ModifierType.BUTTON1_MASK, self.TARGETS, Gdk.DragAction.COPY)

        self.treeView.connect("drag_data_received",
                              self.drag_data_received_data, self.cfg)
        self.treeView.enable_model_drag_dest(self.TARGETS, Gdk.DragAction.COPY)

        self.treeSelection = self.treeView.get_selection()
        self.treeSelection.set_mode(Gtk.SelectionMode.MULTIPLE)

        ######################

        self.cellpb = Gtk.CellRendererPixbuf()
        self.cell1 = Gtk.CellRendererText()
        self.cell1.connect('edited', self.rename_file)
        self.cell2 = Gtk.CellRendererText()
        self.cell3 = Gtk.CellRendererText()

        column = Gtk.TreeViewColumn(_("Name"))
        column.set_expand(True)
        column.set_resizable(True)
        column.set_sizing(Gtk.TreeViewColumnSizing.FIXED)
        column.pack_start(self.cellpb, False)
        column.pack_start(self.cell1, True)
        column.set_attributes(self.cellpb, pixbuf=0)
        column.set_attributes(self.cell1, text=1)
        self.treeView.append_column(column)

        column = Gtk.TreeViewColumn(_("Size"))
        column.set_expand(False)
        column.pack_start(self.cell2, True)
        column.set_attributes(self.cell2, text=2)
        self.treeView.append_column(column)

        column = Gtk.TreeViewColumn(_("Modified"))
        column.set_expand(False)
        column.pack_start(self.cell3, True)
        column.set_attributes(self.cell3, text=3)
        self.treeView.append_column(column)

        sw = Gtk.ScrolledWindow()
        sw.set_shadow_type(Gtk.ShadowType.ETCHED_IN)
        sw.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        sw.add(self.treeView)

        ##########################################

        self.label = Gtk.Label(self.folder_name)
        self.label.set_alignment(0, 0.5)
        vbox.pack_start(self.label, expand=False, fill=False, padding=5)

        toolbar = Gtk.Toolbar()
        toolbar.set_orientation(Gtk.Orientation.HORIZONTAL)
        toolbar.set_style(Gtk.ToolbarStyle.ICONS)
        toolbar.set_border_width(0)
        #~ toolbar.set_tooltips(True)

        button = toolbar_button(
            self.cfg.pixbuf_action_refresh_16, self.cfg.tooltips, _("Refresh"))
        button.connect('clicked', self.refresh)
        toolbar.insert(button, -1)

        button = toolbar_button(
            self.cfg.pixbuf_list_up_16, self.cfg.tooltips, _("Up"))
        button.connect('clicked', self.up)
        toolbar.insert(button, -1)

        separator = Gtk.SeparatorToolItem()
        toolbar.insert(separator, -1)

        button = toolbar_button(
            self.cfg.pixbuf_list_folder_add_16, self.cfg.tooltips, _("New folder"))
        button.connect('clicked', self.new_folder)
        toolbar.insert(button, -1)

        button = toolbar_button(
            self.cfg.pixbuf_list_file_copy_16, self.cfg.tooltips, _("Copy"))
        button.connect('clicked', self.copy)
        toolbar.insert(button, -1)

        button = toolbar_button(
            self.cfg.pixbuf_list_file_paste_16, self.cfg.tooltips, _("Paste"))
        button.connect('clicked', self.paste)
        toolbar.insert(button, -1)

        button = toolbar_button(
            self.cfg.pixbuf_list_file_edit_16, self.cfg.tooltips, _("Rename"))
        button.connect('clicked', self.rename)
        toolbar.insert(button, -1)

        button = toolbar_button(
            self.cfg.pixbuf_list_file_remove_16, self.cfg.tooltips, _("Remove"))
        button.connect('clicked', self.remove)
        toolbar.insert(button, -1)

        space = Gtk.SeparatorToolItem()
        space.set_draw(False)
        space.set_expand(Gtk.AttachOptions.EXPAND)
        toolbar.insert(space, -1)

        button = toolbar_button(self.cfg.pixbuf_list_file_hide_16, self.cfg.tooltips, _(
            "Show hidden files"), True)
        button.connect('clicked', self.hidden)
        toolbar.insert(button, -1)

        vbox.pack_start(toolbar, expand=False, fill=False, padding=0)
        vbox.pack_start(sw, expand=True, fill=True, padding=0)

        vbox.set_homogeneous(False)
        vbox.set_spacing(0)
        vbox.show_all()

        self.create_fileList()

    ##############################################

    def create_fileList(self, data=None):
        self.label.set_text("   " + self.folder_name +
                            self.current_folder[len(self.folder):])
        self.fileList.clear()
        try:
            listdir = os.listdir(self.current_folder)
        except:
            self.fileList.append([None, "..", "", "", "", ""])
            return

        list = []
        for f in listdir:
            if f[0] == '.' and self.show_hidden == False:
                continue

            try:
                file = self.current_folder + "/" + f
                type_ = "1"
                if os.path.islink(file):
                    pb = self.cfg.pixbuf_list_link_16
                elif os.path.ismount(file):
                    pb = self.cfg.pixbuf_list_mount_16
                elif os.path.isdir(file):
                    pb = self.cfg.pixbuf_list_folder_16
                elif os.path.isfile(file):
                    type_ = "2"
                    pb = self.cfg.pixbuf_list_file_16
                filestat = os.stat(self.current_folder + "/" + f)
            except:
                continue

            modified = time.strftime(
                "%d.%m.%y %H:%M:%S ", time.gmtime(filestat.st_mtime))
            sort_key = ""
            for c in unicode(f, 'utf-8').lower():
                if c != " ":
                    sort_key += c
                    if c != ".":
                        break
            list.append([pb, f, filestat.st_size, modified, type_, sort_key])
        list.sort(key=lambda tup: (tup[4], tup[5]))
        self.fileList.append([None, "..", "", "", "", ""])
        for z in list:
            self.fileList.append(z)

    ##############################################

    def get_filenames(self, mode=None):
        model, rows = self.treeSelection.get_selected_rows()
        if rows == []:
            return []
        if mode == "first":
            # Раскрыть и выделить первую позицию
            row = rows[0]
            self.treeView.scroll_to_cell(
                row, None, use_align=True, row_align=0.5, col_align=0.0)
            self.treeView.expand_to_path(Gtk.TreePath(row))
            self.treeSelection.unselect_all()
            self.treeSelection.select_path(Gtk.TreePath(row))
            model, rows = self.treeSelection.get_selected_rows()
        list = []
        for row in rows:
            if mode == "name":
                list.append(self.fileList[row][1])
            else:
                list.append(self.current_folder + self.fileList[row][1])
        return list

    ##############################################

    def copy(self, data=None):
        clipboard = Gtk.clipboard_get()
        clipboard.set_with_data(
            self.TARGETS, self.copy_files, self.clear_files)

    def copy_files(self, clipboard, selectiondata, info, data):
        txt = ""
        # print selectiondata.target
        if selectiondata.target == "x-special/gnome-copied-files":
            txt = txt + "copy\n"

        for file in self.get_filenames():
            txt = txt + "file://" + urllib.quote(file) + "\n"
        selectiondata.set(selectiondata.target, 8, txt)

    def clear_files(self, clipboard, data):
        pass

    ##############################################

    def paste(self, data=None):
        clipboard = Gtk.clipboard_get()
        # clipboard.request_targets(self.get_targets, user_data=None)
        clipboard.request_contents(
            "x-special/gnome-copied-files", self.paste_files)
        clipboard.request_contents(
            "application/x-kde-urilist", self.paste_files)

    def get_targets(self, d1, d2, d3):
        print(d1, d2, d3)

    def paste_files(self, clipboard, selectiondata, udata):
        if selectiondata.data is None:
            return
        # print selectiondata.target
        files = selectiondata.data.splitlines()
        action = "copy"
        if selectiondata.target == "x-special/gnome-copied-files":
            action = files[0]
            del files[0]
        elif selectiondata.target == "application/x-kde-urilist":
            del files[len(files) - 1]

        for file in files:
            file = urllib.unquote(file)[7:]
            try:
                if os.path.isfile(file) == False:
                    continue
                if action == "copy":
                    shutil.copy(unicode(file), self.current_folder)
                elif action == "cut":
                    shutil.move(unicode(file), self.current_folder)
            except:
                continue
        self.create_fileList()

    ##############################################

    def new_folder(self, data=None):
        try:
            os.makedirs(self.current_folder + "Новая папка")
        except:
            return
        self.create_fileList()

        row = False
        for i in range(len(self.fileList)):
            if self.fileList[i][1] == "Новая папка":
                row = (i,)
                break

        if row == False:
            return
        col = self.treeView.get_column(0)
        cell = col.get_cells()[1]
        cell.set_property('editable', True)
        self.file = self.current_folder + "Новая папка"
        self.treeView.set_cursor_on_cell(row, col, cell, start_editing=True)

    def rename(self, data=None):
        # Выделить первую позицию
        f_list = self.get_filenames("first")
        model, rows = self.treeSelection.get_selected_rows()
        if rows == []:
            return
        row = rows[0]
        col = self.treeView.get_column(0)
        cell = col.get_cells()[1]
        cell.set_property('editable', True)
        self.file = f_list[0]
        self.treeView.set_cursor_on_cell(row, col, cell, start_editing=True)

    def rename_file(self, cell, path, new_text):
        cell.set_property('editable', False)
        if not self.file or self.file == self.current_folder + new_text:
            return False
        try:
            os.rename(self.file, self.current_folder + new_text)
        except:
            return False
        self.create_fileList()

    ##############################################

    def hidden(self, data=None):
        if self.show_hidden:
            self.show_hidden = False
        else:
            self.show_hidden = True
        self.create_fileList()

    ##############################################

    def remove(self, data=None):
        dialog_list = self.get_filenames("name")
        file_list = self.get_filenames()
        window = self.get_toplevel()
        if message_dialog(window, _("Remove") + " ?\n", dialog_list, True, "str") != True:
            return
        for file in file_list:
            try:
                if os.path.isfile(file) == True:
                    os.remove(file)
                elif os.path.isdir(file) == True:
                    os.rmdir(file)
            except:
                continue
        self.create_fileList()

    ##############################################

    def up(self, data=None):
        if self.current_folder == self.folder:
            return
        current = self.current_folder.split("/")
        up = ""
        for x in range(len(current) - 2):
            up = up + current[x] + "/"
        self.current_folder = up
        self.create_fileList()

    ##############################################

    def refresh(self, data=None):
        self.create_fileList()

    ##############################################

    def selection_changed(self, data=None, event=None):
        pass

    ##############################################

    def tree_button_press_event(self, data=None, event=None):
        if event.button == 3:
            self.context_menu(event)
        if event.type == Gdk.EventType._2BUTTON_PRESS:
            self.open_file()

    def open_file(self, data=None):
        f_list = self.get_filenames()
        if f_list[0][len(self.current_folder):] == "..":
            self.up()
            return
        try:
            isdir = os.path.isdir(f_list[0])
        except:
            return
        if isdir == True:
            self.current_folder = f_list[0] + "/"
            self.create_fileList()
            return
        try:
            isfile = os.path.isfile(f_list[0])
        except:
            return
        if isfile == True:
            cmd = "xdg-open " + f_list[0].replace(" ", "\\ ")
            proc = popen_sub(self.cfg, shlex.split(cmd))
            return

    def context_menu(self, event):
        mouseMenu = Gtk.Menu()

        item = menu_image_button(self.cfg.pixbuf_list_file_up_16, _("Open"))
        item.connect('activate', self.open_file)
        mouseMenu.append(item)

        item = Gtk.SeparatorMenuItem()
        mouseMenu.append(item)

        item = menu_image_button(
            self.cfg.pixbuf_list_folder_add_16, _("New folder"))
        item.connect('activate', self.new_folder)
        mouseMenu.append(item)

        item = menu_image_button(self.cfg.pixbuf_list_file_copy_16, _("Copy"))
        item.connect('activate', self.copy)
        mouseMenu.append(item)

        item = menu_image_button(
            self.cfg.pixbuf_list_file_paste_16, _("Paste"))
        item.connect('activate', self.paste)
        mouseMenu.append(item)

        item = menu_image_button(
            self.cfg.pixbuf_list_file_edit_16, _("Rename"))
        item.connect('activate', self.rename)
        mouseMenu.append(item)

        item = menu_image_button(
            self.cfg.pixbuf_list_file_remove_16, _("Remove"))
        item.connect('activate', self.remove)
        mouseMenu.append(item)

        mouseMenu.popup(None, None, None, event.button, event.time, None)
        mouseMenu.show_all()

    def callback(self, data1=None, data2=None, data3=None):
        pass

    ##############################################

    def drag_data_get_data(self, treeview, context, selection, target_id, etime, cfg):
        # print selection.target
        pass

    def drag_data_received_data(self, treeview, context, x, y, selection, info, etime, cfg):
        # print selection.target
        pass


####################################################################################################


class tooltips_(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, Gtk.WindowType.POPUP)
        self.set_resizable(False)
        self.set_border_width(5)
        self.set_app_paintable(True)

        self.label = label = Gtk.Label()
        label.set_line_wrap(True)
        label.set_alignment(0.5, 0.5)
        self.add(label)

        self.visible = False

    def set_text(self, x=None, y=None, text=None):
        if not x or not y or not text:
            if self.visible:
                self.hide_all()
                self.visible = False
        else:
            self.label.set_text(text)
            self.move(int(x + 10), int(y))
            if not self.visible:
                self.show_all()
                self.visible = True

    def show(self):
        self.show_all()

    def hide(self):
        self.hide()


####################################################################################################

def entry_error(cfg, entry):
    if cfg.entry_error_busy == True:
        return
    cfg.entry_error_busy = True
    thread_messageBox = thread_gfunc(
        cfg, False, True, entry_error_t, cfg, entry)
    thread_messageBox.start()


####################################################################################################

def entry_error_t(cfg, entry):
    #~ base_color = entry.child.get_style().copy().base[Gtk.StateFlags.NORMAL]
    for i in range(3):
        Gdk.threads_enter()
        #~ entry.child.modify_base(Gtk.StateFlags.NORMAL, Gdk.color_parse("gray"))
        Gdk.threads_leave()
        time.sleep(0.3)
        Gdk.threads_enter()
        #~ entry.child.modify_base(Gtk.StateFlags.NORMAL, base_color)
        Gdk.threads_leave()
        time.sleep(0.3)
    cfg.entry_error_busy = False

####################################################################################################
