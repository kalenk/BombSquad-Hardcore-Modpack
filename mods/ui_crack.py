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
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Dict, List, Any

from ba import _store, internal, Plugin

def get_store_layout() -> Dict[str, List[Dict[str, Any]]]:
    """Return what's available in the store at a given time.

        Categorized by tab and by section."""
    store_layout = _get_store_layout()
    if store_layout:
        items = store_layout['characters'][0]['items']
        if 'characters.santa' not in items:
            i = items.index('characters.wizard')
            if i:
                items = items[0: i - 1] + ['characters.santa'] + items[i:]
                store_layout['characters'][0]['items'] = items
        for key, val in [
            ('characters', [
                {
                    'title': 'store.holidaySpecialText',
                    'items': ['characters.bunny', 'characters.taobaomascot']
                }
                ]
            ),
            ('minigames', [
                {
                    'title': 'store.holidaySpecialText',
                    'items': ['games.easter_egg_hunt']
                }
                ]
            )
        ]:
            for v in val:
                if v not in store_layout[key]:
                    store_layout[key].append(v)
        return store_layout
    return {}

def main() -> None:
    globals()['_get_store_layout'] = _store.get_store_layout
    _store.get_store_layout = internal.get_store_layout = get_store_layout

# ba_meta export plugin
class HolidaySpecial(Plugin):
    def on_app_launch(self) -> None:
        main()