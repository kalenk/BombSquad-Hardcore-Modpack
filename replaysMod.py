# -*- coding: utf-8 -*-
import bs
import bsInternal
import os

#writed by drov.drov, test version

env = bs.getEnvironment()
platform = env['platform']
usr_scr_dir = env['userScriptsDirectory']
basepath = (os.path.sep).join(usr_scr_dir.split(os.path.sep)[0:-1])
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
    import shutil
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
    
    def get_replays(paths=[], replace_files=True):
        global gInfo
        for path in paths:
            filename = path.split(os.path.sep)[-1]
            temp = replays_out_path + os.path.sep + filename
            if replace_files and os.path.exists(temp): 
               try: os.remove(temp)
               except: pass
            try: shutil.copy(path, replays_out_path)
            except Exception as e: 
                exception("get")
                exception(e)
            gInfo.append("Successfully saved: "+filename+'\n')
    
    def upload_replays(paths=[], replace_files=True):
        global gInfo
        for path in paths:
            filename = path.split(os.path.sep)[-1]
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

    import bsUI

    def uploadReplays(self):
        bsUI.uiGlobals['watch_window'] = self
        select_replays(basepath, callback=checkForUploadReplays)

    def getReplays(self):
        bsUI.uiGlobals['watch_window'] = self
        select_replays(replays_internal, callback=checkForSavedReplays)

    bsUI.WatchWindow.uploadReplays = uploadReplays
    bsUI.WatchWindow.getReplays = getReplays

    from bsUI import _updateTabButtonColors, gSmallUI, gToolbars, gMedUI

    def refreshReplays():
        if bsUI.uiGlobals.get('watch_window', None) is not None:
            bsUI.uiGlobals['watch_window']._refreshMyReplays()
            bsUI.uiGlobals['watch_window'] = None

    def checkForUploadReplays(result=None):
        if result is not None and len(result) > 0: 
            upload_replays(paths=result)
            refreshReplays()
    
    def checkForSavedReplays(result=None):
        if result is not None and len(result) > 0: 
            get_replays(paths=result)
            refreshReplays()

    def fileCheckBox(parent, name, position, scale=None, maxWidth=None, valueChangeCall=None):
        def _valueChanged(val):
            if valueChangeCall is not None: valueChangeCall(name, val)
    
        return bs.checkBoxWidget(parent=parent, autoSelect=True,
                                 position=position, size=(50, 50), text='',
                                 textColor=(0.8, 0.8, 0.8),
                                 value=False,
                                 onValueChangeCall=_valueChanged, scale=scale,
                                 maxWidth=maxWidth)

    class ReplaySelector(bsUI.FileSelectorWindow):
        def __init__(self, path, callback=None):
            bsUI.FileSelectorWindow.__init__(self, path=path, callback=callback, 
                showBasePath=True, validFileExtensions=['brp'], allowFolders=False)
            xInset = 87 if gSmallUI else 40
            self._doneButton = b = bs.buttonWidget(
                parent=self._rootWidget, position=(self._width - xInset - self._buttonWidth, self._height - 67),
                autoSelect=True, size=(self._buttonWidth, 50),
                label=bs.Lstr(resource='doneText'),
                onActivateCall=self._done)
        def _done(self):
            if self._callback is not None: 
                result = getattr(self, 'result', [])
                self._callback(result)
            bs.containerWidget(edit=self._rootWidget, transition='outRight')
        def on_entry_request(self, entry, delete=False):
            if entry is not None:
                result = getattr(self, 'result', [])
                if not delete and entry not in result:
                    result.append(entry)
                    self.result = result
                elif delete and entry in result:
                    result.remove(entry)
                    self.result = result
        def fileSelectCallback(self, entry, val=False):
            self.on_entry_request(entry=entry, delete=not val)
        def _select_dir(self, path):
            if path is not None: self._setPath(path, True)
        def _refresh(self, fileNames=None, error=None):
            if not self._rootWidget.exists(): return
    
            scrollWidgetSelected = (self._scrollWidget is None or self._rootWidget.getSelectedChild() == self._scrollWidget)
    
            inTopFolder = (self._path == self._basePath)
            hideTopFolder = inTopFolder and self._showBasePath is False
    
            if hideTopFolder: folderName = ''
            elif self._path == '/': folderName = '/'
            else: folderName = os.path.basename(self._path)
    
            bColor = (0.6, 0.53, 0.63)
            bColorDisabled = (0.65, 0.65, 0.65)
    
            if len(self._recentPaths) < 2:
                bs.buttonWidget(
                    edit=self._backButton, color=bColorDisabled,
                    textColor=(0.5, 0.5, 0.5))
            else:
                bs.buttonWidget(edit=self._backButton, color=bColor,
                                textColor=(0.75, 0.7, 0.8))
    
            maxStrWidth = 300
            strWidth = min(maxStrWidth, bsInternal._getStringWidth(
                folderName, suppressWarning=True))
            bs.textWidget(edit=self._pathText, text=folderName,
                          maxWidth=maxStrWidth)
            bs.imageWidget(edit=self._folderIcon, position=(
                self._folderCenter-strWidth*0.5-40,
                self._height-117), opacity=0.0 if hideTopFolder else 1.0)
    
            if self._scrollWidget is not None:
                self._scrollWidget.delete()
    
            if self._useFolderButton is not None:
                self._useFolderButton.delete()
                bs.widget(edit=self._cancelButton, rightWidget=self._backButton)
    
            self._scrollWidget = bs.scrollWidget(
                parent=self._rootWidget,
                position=((self._width-self._scrollWidth)*0.5,
                          self._height-self._scrollHeight-119),
                size=(self._scrollWidth,self._scrollHeight))
    
            if scrollWidgetSelected:
                bs.containerWidget(edit=self._rootWidget,
                                   selectedChild=self._scrollWidget)
    
            # show error case..
            if error is not None:
                self._subContainer = bs.containerWidget(
                    parent=self._scrollWidget,
                    size=(self._scrollWidth, self._scrollHeight),
                    background=False)
                bs.textWidget(
                    parent=self._subContainer, color=(1, 1, 0, 1),
                    text=error, maxWidth=self._scrollWidth * 0.9,
                    position=(self._scrollWidth * 0.48, self._scrollHeight * 0.57),
                    size=(0, 0),
                    hAlign='center', vAlign='center')
    
            else:
                fileNames = [f for f in fileNames if not f.startswith('.')]
                fileNames.sort(key=lambda x: x[0].lower())
    
                entries = fileNames
                entryHeight = 35
    
                folderEntryHeight = 100
                showFolderEntry = False
    
                showUseFolderButton = (self._allowFolders and not inTopFolder)
    
                self._subContainerHeight = entryHeight*len(entries) + (
                    folderEntryHeight if showFolderEntry else 0)
                v = self._subContainerHeight - (folderEntryHeight
                                                if showFolderEntry else 0)
    
                self._subContainer = bs.containerWidget(
                    parent=self._scrollWidget,
                    size=( self._scrollWidth, self._subContainerHeight),
                    background=False)
    
                bs.containerWidget(edit=self._scrollWidget,
                                   claimsLeftRight=False, claimsTab=False)
                bs.containerWidget(
                    edit=self._subContainer, claimsLeftRight=False, claimsTab=False,
                    selectionLoops=False, printListExitInstructions=False)
                bs.widget(edit=self._subContainer, upWidget=self._backButton)
    
                if showUseFolderButton:
                    self._useFolderButton = b = bs.buttonWidget(
                        parent=self._rootWidget,
                        position=(
                            self._width - self._buttonWidth - 35 - self._xInset,
                            self._height - 67),
                        size=(self._buttonWidth, 50),
                        label=bs.Lstr(
                            resource=self._r + '.useThisFolderButtonText'),
                        onActivateCall=self._onFolderEntryActivated)
                    bs.widget(edit=b, leftWidget=self._cancelButton,
                              downWidget=self._scrollWidget)
                    bs.widget(edit=self._cancelButton, rightWidget=b)
                    bs.containerWidget(edit=self._rootWidget, startButton=b)
    
                folderIconSize = 35
                for num, entry in enumerate(entries):
                    try: entryPath = str(self._path.encode('utf-8'))+os.path.sep+str(entry.encode('utf-8'))
                    except: entryPath = self._path + os.path.sep + str(entry.encode('utf-8'))
                    isValidFilePath = self._isValidFilePath(entry)
                    isDir = os.path.isdir(entryPath)
                    c = bs.containerWidget(
                        parent=self._subContainer, position=(0, v - entryHeight),
                        size=(self._scrollWidth, entryHeight),
                        rootSelectable=True if isDir else False, background=False, clickActivate=True if isDir else False,
                        onActivateCall=bs.Call(self._select_dir, entryPath) if isDir else None)
                    if num == 0:
                        bs.widget(edit=c, upWidget=self._backButton)
                    if isDir:
                        i = bs.imageWidget(
                            parent=c, size=(folderIconSize, folderIconSize),
                            position=(10, 0.5 * entryHeight - folderIconSize * 0.5),
                            drawController=c, texture=self._folderTex,
                            color=self._folderColor)
                    else:
                        i = bs.imageWidget(
                            parent=c, size=(folderIconSize, folderIconSize),
                            position=(10, 0.5 * entryHeight - folderIconSize * 0.5),
                            opacity=1.0 if isValidFilePath else 0.5,
                            drawController=c, texture=self._fileTex,
                            color=self._fileColor)
                        if entry.endswith('.brp'):
                            fileCheckBox(parent=c, name=entryPath, position=(self._width-130, -5), 
                                valueChangeCall=self.fileSelectCallback)
                    t = bs.textWidget(
                        parent=c, drawController=c, text=entry, hAlign='left',
                        vAlign='center',
                        position=(10 + folderIconSize * 1.05, entryHeight * 0.5),
                        size=(0, 0),
                        maxWidth=self._scrollWidth * 0.93 - 50, color=(1, 1, 1, 1)
                        if(isValidFilePath or isDir) else(0.5, 0.5, 0.5, 1))
                    v -= entryHeight

    def select_replays(path=None, callback=None):
        if path is not None and os.path.exists(bs.utf8(path)):
            bsUI.uiGlobals['mainMenuWindow'] = ReplaySelector(
                path=path, callback=callback).getRootWidget()

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
        