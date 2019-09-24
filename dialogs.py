#! /usr/bin/env python
# -*- coding: utf8 -*-

###################################################################################################
# RuleUser
# dialogs.py
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
from gi.repository import GdkPixbuf

from util import *

_ = gettext.gettext


####################################################################################################

def message_dialog(window, text, list, buttons_ok=None, list_type="list"):
    # Возвращает True если нажата OK
    if list_type == "list":
        for z in list:
            if len(z) > 9:
                if z[9] == "server":
                    name = z[0] + "(" + z[4] + ")"
                else:
                    name = z[0] + "(" + z[9] + ")"
            else:
                name = z[0]
            text = text + "\n" + name
    elif list_type == "str":
        for item in list:
            text = text + "\n" + item

    dialog = Gtk.MessageDialog(
        window, 0, Gtk.MessageType.INFO, Gtk.ButtonsType.NONE, text)
    if buttons_ok:
        dialog.add_button(_("Ok"), Gtk.ButtonsType.OK)
    dialog.add_button(_("Cancel"), Gtk.ButtonsType.CANCEL)
    if dialog.run() == Gtk.ButtonsType.OK:
        dialog.destroy()
        return True
    else:
        dialog.destroy()
        return False


####################################################################################################

def about_dialog(data=None):
    about = Gtk.AboutDialog()
    about.set_name("RuleUser")
    about.set_comments(_("Computer management and monitoring users") + "\n"+_(
        "Developed specially for ALT Linux School") + "\n"+_("Поддерживается в Школе №830 г. Москва"))

    about.set_version("1.1.0")
    about.set_copyright("\n(c) 2013 " + _("Andrey Burbovskiy") + "\n" +
                        "Email: xak-altsp@yandex.ru""\n(c) 2017 " + _("Артем Проскурнев") + "\n"+"Email: tema@proskurnev.name")
    about.set_website("http://www.altlinux.org/LTSP/")
    about.set_authors(
        ["Тестирование:" + "\n" + "	Александр Шеметов berkut_174@mail.ru" + "\n"])
    about.set_license("GPLv3")
    about.set_logo(GdkPixbuf.Pixbuf.new_from_file(
        os.path.expanduser("icons/ruleuser2_48.png")))
    about.run()
    about.destroy()

####################################################################################################
