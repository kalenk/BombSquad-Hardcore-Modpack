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
    from typing import Dict

from ba import _lobby, Plugin
from ba._profile import get_player_profile_colors
from ba._error import print_exception
from ba._enums import SpecialChar
import _ba

def _lobby___init__(self, vpos: float, sessionplayer: _ba.SessionPlayer,
             lobby: 'Lobby') -> None:
    self._markers = ['"',"'","^","%",";","`"]
    self._glowing = {}
    lobby___init__(self, vpos, sessionplayer, lobby)
    
def _lobby_get_glowing(self) -> Dict[str, list]:
    for profile_name in self._profilenames:
        for m in self._markers:
            if m in profile_name and len(profile_name.split(',')) > 3:
                s = profile_name.split(',')
                if s[0] != m:
                    s = [m, s[0].replace(m, '')] + s[1:]
                result = []
                
                for i, c in enumerate(s[1:5]):
                    try:
                        result.append(float(c) if i in range(2) else int(c))
                    except ValueError:
                        break

                if len(result) == 4:    
                    self._glowing[m] = result
    return self._glowing

def _lobby_update_from_profile(self) -> None:
    """Set character/colors based on the current profile."""
    self._profilename = self._profilenames[self._profileindex]
    self.get_glowing()
    if self._profilename[0] in self._glowing:
        m = self._profilename[0]
        character = self._profiles[self._profilename]['character']

        if (character not in self._character_names
                and character in _ba.app.spaz_appearances):
            self._character_names.append(character)
        self._character_index = self._character_names.index(character)

        color_multiple = self._glowing[m][0]
        highlight_multiple = self._glowing[m][1]

        self._color, self._highlight = (get_player_profile_colors(
            self._profilename, profiles=self._profiles))
        
        if not (self._glowing[m][2] > 0):
            self._color = tuple([i * color_multiple for i in list(self._color)])
        else:
            self._color = list(self._color)
            val = max(self._color)
            
            for i, c in enumerate(self._color):
                if c == val:
                    self._color[i] *= color_multiple
            self._color = tuple(self._color)
                    
        if not (self._glowing[m][3] > 0):
            self._highlight = tuple([i * highlight_multiple for i in list(self._highlight)])
        else:
            self._highlight = list(self._highlight)
            val = max(self._highlight)
            
            for i, c in enumerate(self._highlight):
                if c == val:
                    self._highlight[i] *= highlight_multiple
            self._highlight = tuple(self._highlight)

        self._update_icon()
        self._update_text()
    else:
        return lobby_update_from_profile(self)

def _lobby__getname(self, full: bool = False) -> str:
    name_raw = name = self._profilenames[self._profileindex]
    if name[0] in self._glowing:
        name = name[1:]
        clamp = False
        if full:
            try:
                if self._profiles[name_raw].get('global', False):
                    icon = (self._profiles[name_raw]['icon']
                            if 'icon' in self._profiles[name_raw] else
                            _ba.charstr(SpecialChar.LOGO))
                    name = icon + name
            except Exception:
                print_exception('Error applying global icon.')
        else:
            clamp = True

        if clamp:
            if len(name) > 10:
                name = name[:10] + '...'
        return name
    return lobby__getname(self, full)

def main() -> None:
    for attr in [
        '__init__',
        'update_from_profile',
        '_getname']:
        globals().update({'lobby_' + attr: getattr(_lobby.Chooser, attr)})
    for attr, obj in globals().items():
        if attr.startswith('_lobby_'):
            setattr(_lobby.Chooser, attr[7:], obj)

# ba_meta export plugin
class GlowingProfiles(Plugin):
    def on_app_launch(self) -> None:
        main()