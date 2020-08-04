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
from threading import Thread
from copy import copy

import ba

V = '0.0.2'

def get_search_query() -> str:
    return ba.app.config.get('internet_search_query', '')

def format_spaces(msg: str = '') -> str:
    while '  ' in msg:
        msg = msg.replace("  ", " ")
    if msg.startswith(" "): 
        msg = msg[1:]
    if msg.endswith(" "): 
        msg = msg[:-1]
    return msg

def __init__(self,
      transition: Optional[str] = 'in_right',
      origin_widget: ba.Widget = None) -> None:
    self._internet_search_field: Optional[ba.Widget] = None
    self._internet_search_activate_button: Optional[ba.Widget] = None
    self._internet_search_query: Optional[str] = None
    self._public_parties_reserve: Dict[str, Dict[str, Any]] = {}
    return self.__init___old(
        transition = transition, 
        origin_widget = origin_widget
    )

def set_search_query(self, query: str) -> None:
    self._internet_search_query = query
    ba.app.config.update({'internet_search_query': query})
    ba.app.config.commit()

def search(self, called_by_button: bool = False) -> None:
    if self._internet_search_field:
        query = cast(str, 
            ba.textwidget(query=self._internet_search_field))
        query = format_spaces(query).lower()
        if query:
            if query != self._internet_search_query:
                self.set_search_query(query)
            if isinstance(self._internet_search_query, str):
                can_rebuild = False
                self._public_parties = {}
                for key, party in self._public_parties_reserve.items():
                    if query in party['name'].lower():
                        self._public_parties.update({key: party})
                        can_rebuild = True
                if can_rebuild:
                    self._rebuild_public_party_list(1)
        elif called_by_button:
            self._public_parties = copy(self._public_parties_reserve)
            self._rebuild_public_party_list(2)

def _on_public_party_query_result(
          self, result: Optional[Dict[str, Any]]) -> None:
    self._on_public_party_query_result_old(result)
    self._public_parties_reserve = copy(self._public_parties)
    self.search()

def _rebuild_public_party_list(self, force: int = 0) -> None:
    if not force:
        return
    elif force == 2:
        self._last_public_party_list_rebuild_time = 0.0
    self._rebuild_public_party_list_old()

def _ping_callback(self, address: str, port: Optional[int],
          result: Optional[int]) -> None:
    party = self._public_parties.get(address + '_' + str(port))
    if party and party.get('ping_widget', None):
        self._rebuild_public_party_list(1)
    return self._ping_callback_old(address, port, result)

def _set_internet_tab(self, value: str, playsound: bool = False) -> None:
    self._set_internet_tab_old(value, playsound)

    for widget in [
        self._internet_search_field,
        self._internet_search_activate_button
          ]:
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
        self._internet_search_query = query = get_search_query()
        if query:
            ba.textwidget(edit=self._internet_search_field, text=query)
            self.search(True)
        self._internet_search_activate_button = ba.buttonwidget(
            parent=self._tab_container,
            size=(25, 25),
            on_activate_call=ba.WeakCall(self.search, True),
            position=(740, y + 9),
            label='',
            color=(0.9, 0.9, 0.9),
            autoselect=True)

def redefine(methods: Dict[str, Callable]) -> None:
    for n, func in methods.items():
        if hasattr(gather.GatherWindow, n):
            setattr(gather.GatherWindow, n + '_old', 
                getattr(gather.GatherWindow, n))
        setattr(gather.GatherWindow, n, func)

def am_i_imported() -> bool:
    return getattr(ba.app, 'server_search_enabled', False)

def i_was_imported() -> bool:
    if not am_i_imported():
        ba.app.server_search_enabled = True
        return True
    return False

def main() -> None:
    if i_was_imported():
        redefine({
            '__init__': __init__,
            'set_search_query': set_search_query,
            'search': search,
            '_on_public_party_query_result': _on_public_party_query_result,
            '_rebuild_public_party_list': _rebuild_public_party_list,
            '_ping_callback': _ping_callback,
            '_set_internet_tab': _set_internet_tab
        })

# ba_meta export plugin
class ServerSearch(ba.Plugin):
    def on_app_launch(self) -> None:
        main()