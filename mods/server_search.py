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
#

# ba_meta require api 6

from __future__ import annotations
from typing import TYPE_CHECKING, cast

if TYPE_CHECKING:
    from typing import Optional, Dict, Any

from bastd.ui import gather
import _ba, ba, copy

def format_spaces(msg: str = '') -> str:
    while True:
        msg = msg.replace("  ", " ")
        if "  " not in msg: 
            break
    if msg.endswith(" "): 
        msg = msg[0:-1]
    if msg.startswith(" "): 
        msg = msg[1:]
    elif msg.startswith("/"):
        if len(msg.split("/")) > 1 and msg.split("/")[1].startswith(" "): 
            msg = msg[0] + msg[2:]
    return msg

def _gather_search(self) -> None:
    if not getattr(self, '_internet_search_field', None):
        return
    query = cast(str, ba.textwidget(query=self._internet_search_field))
    query = format_spaces(query).lower()
    def rebuild():
        self._rebuild_public_party_list(2)
        _ba.app.config['internet_search_query'] = query
        _ba.app.config.commit()
    if not query:
        self._public_parties = copy.copy(self._public_parties_all)
        rebuild()
        return
    self._public_parties = {}
    for key, party in self._public_parties_all.items():
        if query in party['name'].lower():
            self._public_parties.update({key: party})
    rebuild()

def _gather__on_public_party_query_result(
        self, result: Optional[Dict[str, Any]]) -> None:
    gather__on_public_party_query_result(self, result)
    self._public_parties_all = copy.copy(self._public_parties)
    self.search()

def _gather__rebuild_public_party_list(self, force: int = 0) -> None:
    if not force:
        return
    elif force == 2:
        self._last_public_party_list_rebuild_time = 0.0
    return gather__rebuild_public_party_list(self)

def _gather__ping_callback(self, address: str, port: Optional[int],
                   result: Optional[int]) -> None:
    party = self._public_parties.get(address + '_' + str(port))
    if party is not None:
        current_ping = party.get('ping')
        if (current_ping is not None and result is not None
                and result < 150):
            smoothing = 0.7
            party['ping'] = int(smoothing * current_ping +
                                (1.0 - smoothing) * result)
        else:
            party['ping'] = result

        if 'ping_widget' not in party:
            pass
        elif party['ping_widget']:
            self._rebuild_public_party_list(1)

def _gather__set_internet_tab(self, value: str, playsound: bool = False) -> None:
    gather__set_internet_tab(self, value, playsound)
    for attr in [
        '_internet_search_field',
        '_internet_search_activate_button']:
        widget = getattr(self, attr, None)
        if widget:
            widget.delete()
    y = self._scroll_height - 70
    if value == 'join':
        self._internet_search_field = ba.textwidget(
            parent=self._tab_container,
            size=(120, 40),
            editable=True,
            position=(760, y),
            maxwidth=494,
            scale=0.6,
            color=(1.0, 1.0, 1.0),
            flatness=1.0,
            shadow=0.3,
            v_align='center')
        query = _ba.app.config.get('internet_search_query', '')
        if query:
            ba.textwidget(edit = self._internet_search_field,
                text = query)
        self._internet_search_activate_button = ba.buttonwidget(
            parent=self._tab_container,
            size=(25, 25),
            on_activate_call=ba.WeakCall(self.search),
            position=(740, y + 9),
            label='',
            color=(0.9, 0.9, 0.9),
            autoselect=True)
        self._rebuild_public_party_list(2)

def main() -> None:
    for attr in [
        '_set_internet_tab',
        '_on_public_party_query_result',
        '_rebuild_public_party_list',
        '_set_internet_tab']:
        globals().update({'gather_' + attr: getattr(gather.GatherWindow, attr)})
    for attr, obj in globals().items():
        if attr.startswith('_gather_'):
            setattr(gather.GatherWindow, attr[8:], obj)

# ba_meta export plugin
class ServerSearch(ba.Plugin):
    def on_app_launch(self) -> None:
        main()