import bs, bsInternal, time

# written by drov.drov

PLAYER_SPAZ = bs.PlayerSpaz

class PlayerSpaz(PLAYER_SPAZ):
    def __init__(self, color=(1, 1, 1), highlight=(0.5, 0.5, 0.5), 
        character="Spaz", player=None, powerupsExpire=True):
        PLAYER_SPAZ.__init__(self, color=color, highlight=highlight,
            character=character, player=player, powerupsExpire=False)
        self._fly_mode = False
        self._fly_speed = self._fly_speed_normal = 2.0
    def delete_hold_node(self):
        for attr in ['_c','hold_node']:
            node = getattr(self, attr, None)
            if node is not None and node.exists(): node.delete()
        self._fly_timer = None
    def spawn_hold_node(self):
        if self.node is None or not self.node.exists(): return
        self.delete_hold_node()
        t = self.node.position
        t = (t[0], t[1]+1, t[2])
        self.hold_node = bs.newNode('prop', owner=self.node,
            delegate=self, attrs={
                'position': t,
                'body': 'box',
                'bodyScale': 0.000001,
                'model': None,
                'modelScale': 0.000001,
                'colorTexture': None,
                'maxSpeed': 0,
                'sticky': True,
                'stickToOwner': True,
                'owner': self.node,
                'materials': []})
        self._c = c = bs.newNode('combine', owner=self.hold_node, attrs={'size': 3})
        self._c_move = [0, 0, 0]
        c.input0, c.input1, c.input2 = t
        self._c.connectAttr('output', self.hold_node, 'position')
        self._fly_timer = bs.Timer(100, bs.WeakCall(self.move_hold_node, 'all'), repeat=True)
    def move_hold_node(self, v='height'):
        if getattr(self, '_c', None) is not None and self._c.exists(): 
            l = [0, 1, 2] if v == 'all' else [1] if v == 'height' else [0, 2]
            for c in l:
                val = getattr(self._c, 'input'+str(c))
                bs.animate(self._c, 'input'+str(c), {0: val, 500: val+self._c_move[c]})
    def hold_node_alive(self):
        for attr in ['_c','hold_node']:
            node = getattr(self, attr, None)
            if node is None or not node.exists(): return False
        return True
    def set_fly_mode(self, val):
        self._fly_mode = val
        if self._fly_mode:
            PLAYER_SPAZ.onMoveUpDown(self, 0)
            PLAYER_SPAZ.onMoveLeftRight(self, 0)
            self.spawn_hold_node() 
            node = getattr(self, 'hold_node', None)
            if node is None or not node.exists(): node = bs.Node(None)
            self.node.holdBody = 0
            self.node.holdNode = node
                #self.node.holdBody = 1
        else:
            self.node.holdBody = 0
            self.node.holdNode = bs.Node(None)
            self.delete_hold_node()
            PLAYER_SPAZ.onMoveUpDown(self, 0)
            PLAYER_SPAZ.onMoveLeftRight(self, 0)
    def onPunchPress(self):
        if self.node is None or not self.node.exists(): return
        if not self._fly_mode: PLAYER_SPAZ.onPunchPress(self)
        elif self.hold_node_alive():
            t = self.node.position
            self._c.input0, self._c.input1, self._c.input2 = (t[0], t[1]+1, t[2])
    def onPunchRelease(self):
        if not self._fly_mode: PLAYER_SPAZ.onPunchRelease(self)
        else:
            player = self.getPlayer()
            if player is not None and player.exists() and not player.isAlive():
                activity = self.getActivity()
                if activity is not None and hasattr(activity, 'spawnPlayer'):
                    player.gameData['respawnTimer'] = player.gameData['respawnIcon'] = None
                    with bs.Context(activity): activity.spawnPlayer(player=player)
    def onBombPress(self):
        if not self._fly_mode: PLAYER_SPAZ.onBombPress(self)
        else: self._fly_speed *= 2.5
    def onBombRelease(self):  
        if not self._fly_mode: PLAYER_SPAZ.onBombRelease(self)
        else: self._fly_speed = self._fly_speed_normal
    def onJumpRelease(self):
        if not self._fly_mode: PLAYER_SPAZ.onJumpRelease(self)
        else: self._c_move[1] = 0
    def onPickUpRelease(self):
        if not self._fly_mode: PLAYER_SPAZ.onPickUpRelease(self)
        else: self._c_move[1] = 0
    def onJumpPress(self):
        if self.node is None or not self.node.exists(): return
        now = time.time()
        if float(now - getattr(self, 'last_jump_press_time', 0)) <= 0.28: 
            self.set_fly_mode(not self._fly_mode)
        else:
            self.last_jump_press_time = now
            if not self._fly_mode: PLAYER_SPAZ.onJumpPress(self)
            else: 
                self._c_move[1] = 0.5*self._fly_speed
                self.move_hold_node()
    def onPickUpPress(self):
        if not self._fly_mode: PLAYER_SPAZ.onPickUpPress(self)
        elif self.node is not None and self.node.exists(): 
            self._c_move[1] = -0.5*self._fly_speed
            self.move_hold_node()
    def onMoveUpDown(self, value):
        if self.node is None or not self.node.exists(): return
        if not self._fly_mode: PLAYER_SPAZ.onMoveUpDown(self, value)
        else: self._c_move[2] = -value*self._fly_speed
    def onMoveLeftRight(self, value):
        if self.node is None or not self.node.exists(): return
        if not self._fly_mode: PLAYER_SPAZ.onMoveLeftRight(self, value)
        else: self._c_move[0] = value*self._fly_speed
    def handleMessage(self, msg):
        if isinstance(msg, bs.DieMessage) or isinstance(msg, bs.OutOfBoundsMessage):
            n = getattr(self, 'hold_node', None)
            if n is not None and n.exists(): n.delete()
        elif isinstance(msg, bs.HitMessage) and self._fly_mode: return
        PLAYER_SPAZ.handleMessage(self, msg=msg)
bs.PlayerSpaz = PlayerSpaz