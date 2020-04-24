# -*- coding: utf-8 -*-
import bs
import bsInternal

#writed by drov.drov, test version

env = bs.getEnvironment()
platform = env['platform']
usr_scr_dir = env['userScriptsDirectory']
debug = 0
gInfo = []

replays_dirs_names = {
    "Russian": {
        "savedReplays": "Сохраненные реплеи",
        "uploadReplays": "Загрузить реплеи",
        "saveReplays": "Сохранить реплеи"
    },
    "English": {
        "savedReplays": "Saved Replays",
        "uploadReplays": "Replays Upload",
        "saveReplays": "Save Replays"
    }
}
replays_dirs_names = replays_dirs_names.get(bs.getLanguage(), replays_dirs_names.get("English", {}))

if platform == "android":
    import os, shutil
    replays_internal = bsInternal._getReplaysDir()
    dirs = [replays_dirs_names.get("uploadReplays", "ReplaysIn"), \
        replays_dirs_names.get("savedReplays", "ReplaysOut")]

    replays_in_path = usr_scr_dir+os.path.sep+dirs[0]
    replays_out_path = usr_scr_dir+os.path.sep+dirs[1]

    log_file_path = os.path.join(usr_scr_dir, 'replaysInfo.txt')
    f = open(log_file_path, 'w+') 
    f.write('Replays Mod v.0.1 log file\n\n')
    f.flush()
    f.close()
    for i in [replays_in_path, replays_out_path]:
        if not os.path.exists(i): os.makedirs(i)

    def info(msgs=['']):
        if not os.path.exists(log_file_path): f = open(log_file_path, 'w+') 
        else: f = open(log_file_path, 'a')
        for msg in msgs: 
            msg = str(bs.Lstr(value=msg).evaluate().encode('utf-8'))
            f.write(msg)
            f.flush()
        f.close()

    def exception(error=None):
        if debug < 1: return 
        path = os.path.join(env['userScriptsDirectory'], 'errors')
        f = open(path, "w+") if not os.path.exists(path) else open(path, "a")
        f.write(str(error)+'\n')
        f.flush()
        f.close()

    def get_info_replays(path):
        files = []
        for i in os.listdir(path):
            i = str(bs.Lstr(value=i).evaluate().encode('utf-8'))
            pt = path + str(os.path.sep.encode('utf-8')) + i
            if i.endswith('.brp'): files.append([i, pt])
        return files
    
    def get_replays(replace_files=True):
        global gInfo
        for filename, path in get_info_replays(str(replays_internal.encode('utf-8'))):
            temp = replays_out_path + os.path.sep + filename
            if replace_files and os.path.exists(temp): 
               try: os.remove(temp)
               except: pass
            try: shutil.copy(path, replays_out_path)
            except Exception as e: 
                exception("get")
                exception(e)
            gInfo.append("Successfully saved: "+filename+'\n')
    
    def upload_replays(search_path=None, replace_files=True):
        global gInfo
        if search_path is None: search_path = replays_in_path
        for filename, path in get_info_replays(path=search_path): 
            temp = str(replays_internal.encode('utf-8')) + os.path.sep + filename
            if replace_files and os.path.exists(temp): 
               try: os.remove(temp)
               except: pass
            try: shutil.copy(path, str(replays_internal.encode('utf-8')))
            except Exception as e: 
                exception("upload")
                exception(e)
            try: os.remove(path)
            except: pass
            gInfo.append("Successfully uploaded: "+filename+'\n')

    def get_net_replays():
        pass

    def uploadReplays(self):
        upload_replays()
        self._refreshMyReplays()

    def getReplays(self):
        get_replays()
        self._refreshMyReplays()

    import bsUI

    bsUI.WatchWindow.uploadReplays = uploadReplays
    bsUI.WatchWindow.getReplays = getReplays

    from bsUI import _updateTabButtonColors, gSmallUI, gToolbars, gMedUI

    def _setTab(self, tab):
        if self._current_tab == tab: return

        self._current_tab = tab
        bs.getConfig()['Watch Tab'] = tab
        bs.writeConfig()

        _updateTabButtonColors(self._tab_buttons, tab)

        if self._tabContainer is not None and self._tabContainer.exists(): self._tabContainer.delete()
        scrollLeft = (self._width-self._scrollWidth)*0.5
        scrollBottom = self._height-self._scrollHeight-79-48

        self._tabData = {}
        if tab == 'myReplays':
            cWidth = self._scrollWidth
            cHeight = self._scrollHeight-20
            sub_scroll_height = cHeight - 63

            self._myReplaysScrollWidth = sub_scroll_width = (680 if gSmallUI else 640)

            self._tabContainer = c = bs.containerWidget(
                parent=self._rootWidget,
                position=(scrollLeft, scrollBottom +
                          (self._scrollHeight - cHeight) * 0.5),
                size=(cWidth, cHeight),
                background=False, selectionLoopToParent=True)

            v = cHeight - 30
            t = bs.textWidget(
                parent=c, position=(cWidth * 0.5, v),
                color=(0.6, 1.0, 0.6),
                scale=0.7, size=(0, 0),
                maxWidth=cWidth * 0.9, hAlign='center', vAlign='center',
                text=bs.Lstr(
                    resource='replayRenameWarningText',
                    subs=[('${REPLAY}', bs.Lstr(
                        resource='replayNameDefaultText'))]))

            bWidth = 140 if gSmallUI else 178
            bHeight = 64 if gSmallUI else 83 if gMedUI else 107
            bSpaceExtra = 3 if gSmallUI else 1 if gMedUI else 5

            bColor = (0.6, 0.53, 0.63)
            bTextColor = (0.75, 0.7, 0.8)
            bv = cHeight-(48 if gSmallUI else 45 if gMedUI else 40)-bHeight
            bh = 40 if gSmallUI else 40
            sh = 190 if gSmallUI else 225
            ts = 1.0 if gSmallUI else 1.2
            self._myReplaysWatchReplayButton = b1 = bs.buttonWidget(
                parent=c, size=(bWidth, bHeight),
                position=(bh, bv),
                buttonType='square', color=bColor, textColor=bTextColor,
                onActivateCall=self._onMyReplayPlayPress, textScale=ts,
                label=bs.Lstr(resource=self._r + '.watchReplayButtonText'),
                autoSelect=True)
            bs.widget(edit=b1, upWidget=self._tab_buttons[tab])
            if gSmallUI and gToolbars: bs.widget(edit=b1, leftWidget=bsInternal._getSpecialWidget('backButton'))
            bv -= bHeight+bSpaceExtra
            b2 = bs.buttonWidget(
                parent=c, size=(bWidth, bHeight),
                position=(bh, bv),
                buttonType='square', color=bColor, textColor=bTextColor,
                onActivateCall=self._onMyReplayRenamePress, textScale=ts,
                label=bs.Lstr(resource=self._r + '.renameReplayButtonText'),
                autoSelect=True)
            bv -= bHeight+bSpaceExtra
            b3 = bs.buttonWidget(
                parent=c, size=(bWidth, bHeight),
                position=(bh, bv),
                buttonType='square', color=bColor, textColor=bTextColor,
                onActivateCall=self._onMyReplayDeletePress, textScale=ts,
                label=bs.Lstr(resource=self._r + '.deleteReplayButtonText'),
                autoSelect=True)
            bv -= bHeight+bSpaceExtra
            b4 = bs.buttonWidget(
                parent=c, size=(bWidth, bHeight),
                position=(bh, bv),
                buttonType='square', color=bColor, textColor=bTextColor,
                onActivateCall=self.getReplays, textScale=ts,
                label=bs.Lstr(value=replays_dirs_names.get("saveReplays", "Save Replays")),
                autoSelect=True)
            bv -= bHeight+bSpaceExtra
            b5 = bs.buttonWidget(
                parent=c, size=(bWidth, bHeight),
                position=(bh, bv),
                buttonType='square', color=bColor, textColor=bTextColor,
                onActivateCall=self.uploadReplays, textScale=ts,
                label=bs.Lstr(value=replays_dirs_names.get("uploadReplays", "Upload Replays")),
                autoSelect=True)

            v -= sub_scroll_height+23
            self._scrollWidget = sw = bs.scrollWidget(
                parent=c, position=(sh, v),
                size=(sub_scroll_width, sub_scroll_height))
            bs.containerWidget(edit=c, selectedChild=sw)
            self._columnWidget = bs.columnWidget(parent=sw, leftBorder=10)

            bs.widget(edit=sw, autoSelect=True, leftWidget=b1,
                      upWidget=self._tab_buttons[tab])
            bs.widget(edit=self._tab_buttons[tab], downWidget=sw)

            self._myReplaySelected = None
            self._refreshMyReplays()
    bsUI.WatchWindow._setTab = _setTab
del env
        