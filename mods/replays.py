# Copyright (c) 2020 Daniil Rakhov
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# ba_meta require api 6

from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Optional, Callable

from bastd.ui import watch
from bastd.ui.fileselector import FileSelectorWindow
import ba, os

def get_translate() -> dict:
    lang = ba.app.language
    if lang == 'Russian':
        return {
            'upload': 'Загрузить реплей',
            'save': 'Сохранить реплей'
        }
    # UPDATE THIS
    else:
        return {
            'upload': 'Upload replay',
            'save': 'Save replay'
        }

def open_fileselector(path: str, callback: Callable = None) -> None:
    with ba.Context('ui'):
        FileSelectorWindow(path, callback, True,
            ['brp'], False)

def get_save_path() -> str:
    path = ba.app.python_directory_user + os.path.sep + 'replays'
    if not os.path.exists(path):
        os.mkdir(path)
    return path

def get_upload_path() -> str:
    from _ba import get_replays_dir
    return get_replays_dir()

def copy_replay(src: str, dst: str, callback: Callable = None) -> None:
    from threading import Thread
    def run() -> None:
        if os.path.exists(src) and os.path.exists(dst):
            if not os.path.exists(dst + os.path.sep +
                  os.path.basename(src)):
                from shutil import copy
                try:
                    copy(src, dst)
                except:
                    pass 
                # pass permission errors
                if callback is not None:
                    ba.pushcall(ba.Call(callback, True), 
                        from_other_thread=True)
            elif callback is not None:
                ba.pushcall(ba.Call(callback, False),
                    from_other_thread=True)
    Thread(target=run).start()

def _watch_upload_replays(self) -> None:
    def on_copy(result: bool = False) -> None:
        if result:
            with ba.Context('ui'):
                self._my_replay_selected = None
                self._refresh_my_replays()
    def on_callback(path: str = None) -> None:
        if path:
            copy_replay(path, get_upload_path(), on_copy)
    open_fileselector(get_save_path(), on_callback)

def _watch_save_replays(self) -> None:
    def on_callback(path: str = None) -> None:
        if path:
            copy_replay(path, get_save_path(), None)
    open_fileselector(get_upload_path(), on_callback)

def _watch__set_tab(self, tab: str) -> None:
    if tab != 'my_replays':
        watch__set_tab(self, tab)
        return
    elif self._current_tab == tab:
        return

    uiscale = ba.app.ui.uiscale
    c_width = self._scroll_width
    c_height = self._scroll_height - 20

    b_width = 140 if uiscale is ba.UIScale.SMALL else 178
    b_height = (82 if uiscale is ba.UIScale.SMALL else
                80 if uiscale is ba.UIScale.MEDIUM else 80)
    b_space_extra = (0 if uiscale is ba.UIScale.SMALL else
                     2 if uiscale is ba.UIScale.MEDIUM else 3)
    btnv = (c_height - (48 if uiscale is ba.UIScale.SMALL else
                        55 if uiscale is ba.UIScale.MEDIUM else 50) -
            b_height)
    btnh = 40

    tscl = 1.0 if uiscale is ba.UIScale.SMALL else 1.2

    b_color = (0.6, 0.53, 0.63)
    b_textcolor = (0.75, 0.7, 0.8)

    watch__set_tab(self, tab)
    for child in self._tab_container.get_children():
        if child and child.get_widget_type() == 'button':
            ba.buttonwidget(edit=child, 
                position=(btnh, btnv),
                size=(b_width, b_height))
            btnv -= b_height + b_space_extra
    tr = get_translate()
    self._upload_replays_button = ba.buttonwidget(
        parent=self._tab_container,
        size=(b_width, b_height),
        position=(btnh, btnv),
        button_type='square',
        color=b_color,
        textcolor=b_textcolor,
        on_activate_call=self.upload_replays,
        text_scale=tscl,
        label=ba.Lstr(value = tr['upload']),
        autoselect=True)
    btnv -= b_height + b_space_extra
    self._save_replays_button = ba.buttonwidget(
        parent=self._tab_container,
        size=(b_width, b_height),
        position=(btnh, btnv),
        button_type='square',
        color=b_color,
        textcolor=b_textcolor,
        on_activate_call=self.save_replays,
        text_scale=tscl,
        label=ba.Lstr(value = tr['save']),
        autoselect=True)

def main() -> None:
    for attr in [
        '_set_tab']:
        globals().update({'watch_' + attr: getattr(watch.WatchWindow, attr)})
    for attr, obj in globals().items():
        if attr.startswith('_watch_'):
            setattr(watch.WatchWindow, attr[7:], obj)

# ba_meta export plugin
class SaveAneShareReplays(ba.Plugin):
    def on_app_launch(self) -> None:
        main()