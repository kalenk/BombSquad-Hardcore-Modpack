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
from ba import Plugin, Call

V = '0.0.1'

def get_my_name() -> str:
    assert __file__

    from os.path import basename
    return basename(__file__)

def mods_path() -> str:
    from _ba import app
    return app.python_directory_user

def open_log() -> open:
    from os.path import sep
    return open(mods_path() +
        sep + 'mods_importer.log', 
        'w+')

def write_log() -> None:
    assert '_log' in globals()

    global _log
    _log = ('Mods Importer V.{} Log\n\n'.format(V) + _log)
    with open_log() as f:
        f.write(_log)
        f.flush()
        f.close()

def log(message: str) -> None:
    if '_log' not in globals():
        globals().update({'_log': ''})
    globals()['_log'] += (message + '\n')

def search() -> None:
    from time import time
    from os import walk
    from os.path import basename, sep
    start_time = time()
    result = set()
    path = mods_path()
    myname = get_my_name()
    log('Start search...')
    for root, dirs, files in walk(path):
        files = [i for i in files if i.endswith('.py')]
        if files:
            files = sorted(files, 
                key = lambda file : file != '__init__.py')
            module_name = root.replace(path, '')
            if module_name:
                if module_name.startswith(sep):
                    module_name = module_name[1:]
                module_name = module_name.replace(sep, '.')
            for file in files:
                if (file == '__init__.py'):
                    if module_name:
                        result.add(module_name)
                elif (file == myname):
                    continue
                elif (module_name not in result):
                    result.add('.'.join(file.split('.')[0:-1]))
    from _ba import pushcall
    for f in result:
        if f:
            try:
                pushcall(Call(__import__, f),
                    from_other_thread = True)
                # local imports
            except Exception as exc:
                log('Error while importing: {}'.format(exc))
            else:
                log('Successfull import: {}'.format(f))
    log('Complete in {} seconds.'.format(time() - start_time))
    write_log()

def main() -> None:
    from threading import Thread
    Thread(target = search, daemon = True).start()

# ba_meta export plugin
class ModsImporter(Plugin):
    def on_app_launch(self) -> None:
        main()