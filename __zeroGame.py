# -*- coding: utf-8 -*-
import bs
import random
import bsUtils
import bsInternal
import time
import bsSpaz
from bsSpaz import SpazBot, _BombDiedMessage, Spaz
try: from bsSpaz import Poison
except ImportError:
    class Poison(object):
        def __init__(self, owner=None):
            self.owner = owner
            if self.owner is not None and self.owner.exists():
                self.light = bs.newNode('light', owner=self.owner,
                    attrs={'radius': 0.095,
                        'volumeIntensityScale': 0.7,
                        'color': (0, 1.4, 0.2)})
                self.owner.connectAttr('position', self.light, 'position')
                self.timer = bs.Timer(50, bs.Call(self.run), True)
                bs.gameTimer(10000, bs.Call(self.delete))
            else:
                self.delete()

        def run(self):
            if self.owner.exists():
                self.owner.handleMessage(bs.HitMessage(pos=self.owner.position,
                    velocity=(0, 0, 0),
                    magnitude=13,
                    hitType='explosion',
                    hitSubType='poisonEffect',
                    radius=1,
                    sourcePlayer=bs.Player(None),
                    kickBack=0))
            else: self.delete()

        def delete(self):
            if hasattr(self, "light"):
                if hasattr(self.light, "radius"): bsUtils.animate(self.light, "radius", {0: self.light.radius, 500: 0})
                bs.gameTimer(500, self.light.delete)
            self.timer = None
            self.owner = None
try: from bsSpaz import EffectHurt
except ImportError:
    class EffectHurt(object):
        def __init__(self, owner=None):
            self.owner = owner
            self._hurt = {}
            if hasattr(bs, "get_setting"):
                if not bs.get_setting(name="timer_the_disappearance_of_the_effect", default_value=False): return
            if self.owner is not None and self.owner.exists():
                self._hurt['text'] = bs.newNode('text', owner=self.owner,
                    attrs={'text': '', 'inWorld': True,
                        'shadow': 0.15,
                        'flatness': 1,
                        'color': (1, 1, 1),
                        'scale': 0,
                        'hAlign': 'center'})
                self._hurt['text'].addDeathAction(bs.Call(self.delete))
            else: self.delete()

        def add(self, text="test", time=5000, color=(1, 1, 1)):
            if self.owner is None or not self.owner.exists():
                self.delete()
                return
            if hasattr(self, "_hurt"):
                if "text_pos" not in self._hurt:
                    self._hurt['text_pos'] = bs.newNode('math', owner=self.owner,
                        attrs={'input1': (0.8, 1, 0), 'operation': 'add'})
                if "timer_pos" not in self._hurt:
                    self._hurt['timer_pos'] = bs.newNode('math', owner=self.owner,
                        attrs={'input1': (0.8, 0.2, 0), 'operation': 'add'})
                for i in ['text_pos', 'timer_pos']: self.owner.connectAttr('position', self._hurt[i], 'input2')
                if "timer" in self._hurt and self._hurt["timer"] is not None and self._hurt["timer"].exists(): self._hurt["timer"].delete()
                self._hurt["timer"] = bs.newNode('shield', owner=self.owner,
                    attrs={'radius': 0, 'color': (0, 0, 0), 'hurt': 0, 'alwaysShowHealthBar': True})
                if "text" in self._hurt:
                    self._hurt["text"].text = text
                    self._hurt["text"].color = color
                    for i in ['timer', 'text']: self._hurt[i + '_pos'].connectAttr('output', self._hurt[i], 'position')
                    bs.animate(self._hurt['text'], 'scale', {0: 0, 300: 0.0085})
                    bs.animate(self._hurt['timer'], 'hurt', {0: 0, time: 1})
                else:
                    self.delete()
                    return
                def a():
                    if hasattr(self, "_hurt"):
                        if "text" in self._hurt and self._hurt["text"] is not None and self._hurt["text"].exists(): self._hurt["text"].text = ""
                        if "timer" in self._hurt and self._hurt["timer"] is not None and self._hurt["timer"].exists(): self._hurt["timer"].delete()
                bs.gameTimer(time, bs.Call(a))

        def delete(self):
            if hasattr(self, "_hurt") and self._hurt is not None:
                for i in self._hurt:
                    if hasattr(self._hurt[i], 'exists') and self._hurt[i].exists(): self._hurt[i].delete()
                self._hurt = None
                del self._hurt

class AlertMessage(object):
    def __init__(self, owner=None):
        self.owner = owner
        if self.owner is not None and self.owner.exists():
            if hasattr(self.owner.getDelegate(), "_text") and self.owner.getDelegate()._text.exists(): self.owner.getDelegate()._text.delete()
            m = bs.newNode('math', owner=self.owner, attrs={'input1': (0, 2.325, 0), 'operation': 'add'})
            self.owner.connectAttr('position', m, 'input2')
            self._text = bs.newNode('text', owner=self.owner, attrs={'text': 'Alert!',
                'inWorld': True,
                'position': (0, 0, 0),
                'color': (3, 0, 0),
                'scale': 0,
                'hAlign':'center'})
            m.connectAttr('output', self._text, 'position')
            self.owner.getDelegate()._text = self._text
            bs.animate(self._text, 'scale', {0:0, 250: 0.0095, 2000: 0.0095, 2500: 0})
            bs.animate(self._text, 'opacity', {0: 0.6, 250: 1, 500: 0.6}, loop=True)
            bs.gameTimer(2500, self._text.delete)

class ExplodeMessage(object):
    pass

class ExplodeHitMessage(object):
    def __init__(self):
        pass

class PoisonBombHitMessage(object):
    def __init__(self):
        pass

playerspazinit_old, handleMessage_old, bot_handleMessage_old = bsSpaz.PlayerSpaz.__init__, bsSpaz.PlayerSpaz.handleMessage, bsSpaz.SpazBot.handleMessage

def playerspazinit(self, color=(1, 1, 1), highlight=(0.5, 0.5, 0.5), character="Spaz", player=None, powerupsExpire=True):
    if player is None: player = bs.Player(None)
    Spaz.__init__(self, color=color, highlight=highlight,
                  character=character, sourcePlayer=player,
                  startInvincible=True, powerupsExpire=powerupsExpire)
    self.lastPlayerAttackedBy = None
    self.lastAttackedTime = 0
    self.lastAttackedType = None
    self.heldCount = 0
    self.lastPlayerHeldBy = None
    self._player = player
    if player.exists():
        playerNode = bs.getActivity()._getPlayerNode(player)
        self.node.connectAttr('torsoPosition', playerNode, 'position')
        self.effects = EffectHurt(owner=self.node)

class ZeroBossHitMessage(object):
    def __init__(self, type, subType, player, damage):
        self.type = type
        self.subType = subType
        self.player = player
        self.damage = damage

class ZeroBossDeathMessage(object):
    def __init__(self, badGuy, killerPlayer, how):
        self.badGuy = badGuy
        self.killerPlayer = killerPlayer
        self.how = how

def handleMessageModifed(self, msg):
    self._handleMessageSanityCheck()
    if hasattr(self, 'is_boss') and self.is_boss:
        if isinstance(msg, bs.HitMessage) and (msg.hitSubType in ['bossBlast', 'impact', 'killLaKill', 'poisonEffect', 'poison', 'landMine'] or msg.sourcePlayer is None): return True
        elif isinstance(msg, bs.HitMessage):
            activity = self._activity()
            if msg.flatDamage: dmg = msg.flatDamage * 1.0
            else: dmg = 0.22 * self.node.damage
            if activity is not None:
                if msg.sourcePlayer is not None and msg.sourcePlayer.exists():
                    if dmg > 0.0: activity.handleMessage(ZeroBossHitMessage(msg.hitType, msg.hitSubType, msg.sourcePlayer, dmg*1.0))
        if isinstance(msg, bs.DieMessage):
            activity = self._activity()
            if activity is not None: activity.handleMessage(ZeroBossDeathMessage(self, None, msg.how))
    if isinstance(msg, PoisonBombHitMessage):
        if not self.node.exists(): return
        Poison(owner=self.node)
        if hasattr(self, "effects"): self.effects.add(text="Poisoned", color=(0, 2, 0), time=10000)
    elif isinstance(msg, bs.HitMessage) and hasattr(msg, "hitSubType") and msg.hitSubType == "poisonEffect":
        damageScale = 0.22
        damage = msg.magnitude * 1.0 * damageScale
        if self.hitPoints > 0:
            self.node.handleMessage("flash")
            if damage > 0.0 and self.node.holdNode.exists(): self.node.holdNode = bs.Node(None)
            self.hitPoints -= damage
            self.node.hurt = 1.0 - float(self.hitPoints) / self.hitPointsMax
            if self._cursed and damage > 0: bs.gameTimer(50, bs.WeakCall(self.curseExplode, msg.sourcePlayer))
            if self.frozen and (damage > 200 or self.hitPoints <= 0): self.shatter()
            elif self.hitPoints <= 0: self.node.handleMessage(bs.DieMessage(how='impact'))
            if self.hitPoints <= 0:
                damageAvg = self.node.damageSmoothed * damageScale
                if damageAvg > 1000: self.shatter()
            activity = self._activity()
            if activity is not None: activity.handleMessage(bs.PlayerSpazHurtMessage(self))
    else:
        if isinstance(self, bsSpaz.PlayerSpaz): handleMessage_old(self, msg)
        elif isinstance(self, bsSpaz.SpazBot): bot_handleMessage_old(self, msg)

class PoisonBombBlast(bs.Blast):
    def __init__(self, position=(0,1,0), velocity=(0,0,0), sourcePlayer=None, hitType='explosion', hitSubType='normal'):
        bs.Actor.__init__(self)
        factory = bs.Bomb.getFactory()
        self.sourcePlayer = sourcePlayer
        self.hitType = hitType;
        self.hitSubType = hitSubType;
        self.blastMaterial = bs.Material()
        self.blastMaterial.addActions(
            conditions=(('theyHaveMaterial',
                         bs.getSharedObject('objectMaterial'))),
            actions=(('modifyPartCollision','collide',True),
                     ('modifyPartCollision','physical',False),
                     ('message','ourNode','atConnect',ExplodeHitMessage())))
        self.radius = 2
        self.node = bs.newNode('region', delegate=self, attrs={
            'position':(position[0], position[1]-0.1, position[2]),
            'scale':(2,2,2),
            'type':'sphere',
            'materials':(self.blastMaterial, bs.getSharedObject('attackMaterial'))})
        bs.gameTimer(10, self.node.delete)
        explosion = bs.newNode("explosion", attrs={
            'position':position,
            'velocity':(velocity[0],max(-1.0,velocity[1]),velocity[2]),
            'radius':self.radius,
            'big':False})
        explosion.color = (1,0.8,0)
        bs.gameTimer(1000, explosion.delete)
        bs.emitBGDynamics(
            position=position, velocity=velocity,
            count=int(4.0+random.random()*4), emitType='tendrils',
            tendrilType='smoke')
        bs.emitBGDynamics(position=position, emitType='distortion', spread=2.0)
        def _doEmit():
            bs.emitBGDynamics(position=position, velocity=velocity, count=30, 
                spread=2.0, scale=0.4, chunkType='rock', emitType='stickers');
        bs.gameTimer(50, _doEmit)

        def _doEmit():
            bs.emitBGDynamics(position=position, velocity=velocity,
                              count=int(4.0+random.random()*8),
                              chunkType='rock');
            bs.emitBGDynamics(position=position, velocity=velocity,
                              count=int(4.0+random.random()*8),
                              scale=0.5,chunkType='rock');
            bs.emitBGDynamics(position=position, velocity=velocity,
                              count=30,
                              scale=0.7,
                              chunkType='spark', emitType='stickers');
            bs.emitBGDynamics(position=position, velocity=velocity,
                              count=int(18.0+random.random()*20),
                              scale=0.8,
                              spread=1.5, chunkType='spark');
                
            if random.random() < 0.1:
                def _emitExtraSparks():
                    bs.emitBGDynamics(position=position, velocity=velocity,
                                      count=int(10.0+random.random()*20),
                                      scale=0.8, spread=1.5,
                                      chunkType='spark');
                bs.gameTimer(20,_emitExtraSparks)
                        
        bs.gameTimer(50,_doEmit)

        light = bs.newNode('light', attrs={
            'position': position,
            'volumeIntensityScale': 10.0,
            'color': (1, 0.3, 0.1)})

        s = random.uniform(0.6,0.9)
        scorchRadius = lightRadius = self.radius
        iScale = 1.6
        bsUtils.animate(light,"intensity", {
            0:0, 10:0.5, 20:1.0, 2000:0.5, 2750:0})
        bsUtils.animate(light,"radius", {
            0:0, 10:0.5, 20:1.0, 2000:0.5, 2750:0})
        bs.gameTimer(2750,light.delete)
        scorch = bs.newNode('scorch', attrs={
            'position':position,
            'size':scorchRadius*0.5,
            'big':False})
        scorch.color = (light.color[0]-0.05, light.color[1]-0.05, light.color[2]-0.07)
        bsUtils.animate(scorch,"presence",{3000:1, 8000:1, 13000:0})
        bs.gameTimer(13000,scorch.delete)
            
        p = light.position
        bs.playSound(factory.getRandomExplodeSound(),position=p)
        bs.playSound(factory.debrisFallSound,position=p)
        bs.shakeCamera(1.0)

    def handleMessage(self, msg):
        self._handleMessageSanityCheck()

        if isinstance(msg, bs.DieMessage):
            self.node.delete()

        elif isinstance(msg, ExplodeHitMessage):
            node = bs.getCollisionInfo("opposingNode")
            if node is not None and node.exists():
                t = self.node.position
                node.handleMessage(bs.HitMessage(
                    pos=t,
                    velocity=(0,0,0),
                    magnitude=800.0,
                    hitType=self.hitType,
                    hitSubType=self.hitSubType,
                    radius=self.radius,
                    sourcePlayer=self.sourcePlayer, 
                    kickBack = 0))
                node.handleMessage(PoisonBombHitMessage())
        else:
            bs.Actor.handleMessage(self, msg)


class PoisonBomb(bs.Bomb):
    def __init__(self, position=(0,5,0), velocity=(0,1,0), sourcePlayer=None, owner=None):
        bs.Actor.__init__(self)
        self._exploded = False
        self._explodeCallbacks = []
        self.poisonTex = bs.getTexture('bombColor')
        self.poisonModel = bs.getModel('bomb')
        self.sourcePlayer = sourcePlayer
        self.bombType = 'poison'
        factory = self.getFactory()
        materials = (factory.bombMaterial, bs.getSharedObject('objectMaterial')) + (factory.normalSoundMaterial,)
        fuseTime = 4500
        if owner is None: owner=bs.Node(None)
        self.node = bs.newNode('bomb', delegate=self, attrs={
            'position':position,
            'velocity':velocity,
            'body':'sphere',
            'model': self.poisonModel,
            'shadowSize':0.3,
            'colorTexture': self.poisonTex,
            'reflection':'soft',
            'reflectionScale':(1,1.5,1),
            'materials':materials})
        sound = bs.newNode('sound', owner=self.node, attrs={
            'sound':factory.fuseSound,
            'volume':0.25})
        self.node.connectAttr('position', sound, 'position')
        bsUtils.animate(self.node, 'fuseLength', {0:1.0, fuseTime:0.0})
        bs.gameTimer(fuseTime, bs.WeakCall(self.handleMessage, ExplodeMessage()))
        if hasattr(bs, "get_setting") and bs.get_setting(name="timer_before_the_bomb_explode", default_value=False):
            m = bs.newNode('math', attrs={'input1': (0, 0.45, 0), 'operation': 'add'})
            self.node.connectAttr('position', m, 'input2')
            self._timer = bs.newNode('text', owner=self.node, attrs={
                'text': '( )',
                'position': (0, 0, 0),
                'color': (0, 3, 0),
                'scale': 0,
                'inWorld': True,
                'hAlign': 'center'})
            m.connectAttr('output', self._timer, 'position')
            bsUtils.animate(self._timer, 'scale', {0: 0.0, 240: 0.009})
            bsUtils.animateArray(self._timer, 'color', 3, {0: (0, 3, 0), fuseTime: (3, 0, 0)}, False)
        bsUtils.animate(self.node,"modelScale",{0:0, 200:1.3, 260:1})
    def _handleHit(self, msg):
        isPunch = (msg.srcNode.exists() and msg.srcNode.getNodeType() == 'spaz')
        if not self._exploded and not isPunch:
            if msg.sourcePlayer not in [None]:
                self.sourcePlayer = msg.sourcePlayer
                self.hitType = msg.hitType
                self.hitSubType = msg.hitSubType

            bs.gameTimer(100+int(random.random()*100),
                         bs.WeakCall(self.handleMessage, ExplodeMessage()))
        self.node.handleMessage(
            "impulse", msg.pos[0], msg.pos[1], msg.pos[2],
            msg.velocity[0], msg.velocity[1], msg.velocity[2],
            msg.magnitude, msg.velocityMagnitude, msg.radius, 0,
            msg.velocity[0], msg.velocity[1], msg.velocity[2])

        if msg.srcNode.exists():
            pass

    def _handleDie(self,m):
        self.node.delete()
        if hasattr(self, "_timer") and self._timer is not None and self._timer.exists():
            self._timer.delete()
            self._timer = None

    def handleMessage(self, msg):
        if isinstance(msg, ExplodeMessage): self.explode()
        elif isinstance(msg, bs.PickedUpMessage):
            if self.sourcePlayer is not None: self.sourcePlayer = msg.node.sourcePlayer
        elif isinstance(msg, bs.HitMessage): self._handleHit(msg)
        elif isinstance(msg, bs.DieMessage): self._handleDie(msg)
        elif isinstance(msg, bs.OutOfBoundsMessage): self._handleOOB(msg)
        else: bs.Actor.handleMessage(self, msg)

    def explode(self):
        if self._exploded: return
        self._exploded = True
        activity = self.getActivity()
        if activity is not None and self.node.exists():
            blast = PoisonBombBlast(position=self.node.position, velocity=self.node.velocity,
                sourcePlayer=self.sourcePlayer,
                hitType='explosion',
                hitSubType='poison').autoRetain()
            for c in self._explodeCallbacks: c(self,blast)
        bs.gameTimer(1, bs.WeakCall(self.handleMessage, bs.DieMessage()))

class ZeroBoss(SpazBot):
    color=(0.5, 0.5, 2.5)
    highlight=(-0.5, -0.5, -2.5)
    character = 'Snake Shadow'
    defaultBombType = 'poison'
    punchiness = 0.4
    throwiness = 0.35
    run = True
    bouncy = True
    defaultShields = True
    chargeDistMin = 0
    chargeDistMax = 0.5
    chargeSpeedMin = 1
    chargeSpeedMax = 1
    throwDistMin = 4
    throwDistMax = 9999
    pointsMult = 12000
    hp = 40200
    ph = 3.8
    defaultBombCount = 5
    def __init__(self):
        SpazBot.__init__(self)
        self.hitPoints = self.hitPointsMax = self.hp
        self._punchPowerScale = self.ph
        self.effects = EffectHurt(owner=self.node)
        self.is_boss = True
    def __superHandleMessage(self, msg):
        super(SpazBot, self).handleMessage(msg)
    def dropBomb(self):
        if self.frozen or self.bombCount < 1: return
        p = self.node.positionForward
        v = self.node.velocity
        droppingBomb = True
        bomb = PoisonBomb(position=(p[0], p[1] - 0.0, p[2]),
                       velocity=(v[0], v[1], v[2]),
                       sourcePlayer=self.sourcePlayer,
                       owner=self.node).autoRetain()
        if droppingBomb:
            self.bombCount -= 1
            bomb.node.addDeathAction(bs.WeakCall(self.handleMessage, _BombDiedMessage()))
        self._pickUp(bomb.node)
        for c in self._droppedBombCallbacks: c(self, bomb)
        return bomb

class ZeroBossBotSpecial(SpazBot):
    color=(0, 0, 0)
    highlight=(-0.5, -0.5, -2.5)
    character = 'Snake Shadow'
    defaultBombType = 'impact'
    punchiness = 0.4
    throwiness = 0.35
    run = True
    bouncy = True
    defaultShields = True
    chargeDistMin = 0
    chargeDistMax = 0.5
    chargeSpeedMin = 1
    chargeSpeedMax = 1
    throwDistMin = 4
    throwDistMax = 9999
    pointsMult = 60
    hp = 3250
    ph = 1.2
    defaultBombCount = 1
    def __init__(self):
        SpazBot.__init__(self)
        self.hitPoints = self.hitPointsMax = self.hp
        self._punchPowerScale = self.ph
        self.effects = EffectHurt(owner=self.node)

class ZeroBossBot(SpazBot):
    color=(1,1,1)
    highlight=(3, 3, 3)
    character = 'Snake Shadow'
    defaultBombType = 'normal'
    punchiness = 2.2
    throwiness = 0
    run = True
    bouncy = True
    defaultShields = True
    chargeDistMin = 0
    chargeDistMax = 0.5
    chargeSpeedMin = 1
    chargeSpeedMax = 1
    throwDistMin = 9998
    throwDistMax = 9999
    pointsMult = 30
    hp = 920
    ph = 2.2
    defaultBombCount = 1
    def __init__(self):
        SpazBot.__init__(self)
        self.hitPoints = self.hitPointsMax = self.hp
        self._punchPowerScale = self.ph
        self.effects = EffectHurt(owner=self.node)

def bsGetAPIVersion():
    return 4

def bsGetGames():
    return [ZeroGameUpdated]

def bsGetLevels():
    return [bs.Level('Zero Chance', displayName='${GAME}', gameType=ZeroGameUpdated, settings={'HardCore?':False}, previewTexName='black')]

class ZeroGameUpdated(bs.TeamGameActivity):

    @classmethod
    def getName(cls):
        return 'Zero Chance\'s'

    @classmethod
    def getScoreInfo(cls):
        return {'scoreName': 'Score', 'scoreType': 'points'}

    @classmethod
    def getDescription(cls, sessionType):
        return 'Stay alive.'

    @classmethod
    def getSupportedMaps(cls, sessionType):
        return ['Football Stadium']

    @classmethod
    def supportsSessionType(cls, sessionType):
        return True if issubclass(sessionType, bs.FreeForAllSession) or issubclass(sessionType, bs.CoopSession) else False

    @classmethod
    def getSettings(cls, sessionType):
        return [("Lives Per Player", {
                'default': 5, 'minValue': 1,
                'maxValue': 5, 'increment': 1
            })]

    def __init__(self, settings):
        bs.TeamGameActivity.__init__(self, settings)
        self._scoreBoard = bs.ScoreBoard()
        self._bots = bs.BotSet()
        self.settings = settings

    def onTransitionIn(self):
        bsSpaz.PlayerSpaz.__init__ = playerspazinit
        bsSpaz.PlayerSpaz.handleMessage, bsSpaz.SpazBot.handleMessage = handleMessageModifed, handleMessageModifed
        bs.TeamGameActivity.onTransitionIn(self, music='Scary')

    def onBegin(self):
        bs.TeamGameActivity.onBegin(self)
        self.damage = {'boss': 0, 'bots': 0, 'now': 0, 'next': 9000}
        self.respawn = 0
        self.boss = None
        self.st = 1
        self._bots.spawnBot(ZeroBoss, pos=(0, 0.5, 0), spawnTime=5000, onSpawnCall=self.set_boss_node)
        self._updateTimer = bs.Timer(1000, bs.Call(self._update), repeat = True)
        self._attackTimer = {bs.getRealTime()+19000: bs.Timer(19000, bs.Call(self._rnd_attack, "19000_0"))}
        self._update()
        self.tpSound = bs.getSound('block')
        self.result = {}

    def set_boss_node(self, spaz=None):
        self.boss = spaz

    def _update_timer(self, force=False):
        time = 20000
        if self.st == 2: time=16000
        if self.st == 3: time=12000
        if self.st == 4: time=9000
        if self.st == 5: time=6000
        if self.st == 6: time=4200
        if self.st == 7: time=3000
        if self.st == 8: time=2200
        if self.st == 9: time=3250
        if self.st == 10: time=1800
        key = bs.getRealTime()+time
        if self._attackTimer is not None:
            if len(self._attackTimer) > 1:
                try:
                    for i in self._attackTimer:
                        if i < bs.getRealTime(): self._attackTimer.pop(i)
                except RuntimeError: pass
            if force: self._attackTimer[key] = bs.Timer(time, bs.Call(self._rnd_attack, key))

    def _rnd_attack(self, key=27654):
        if self.st > 0:
            stinfo = {1: (0, 3), 2: (4, 6), 3: (7, 10), 4: (11, 16), 5: (17, 18), 6: (19, 20), 7: (21, 23)}
            if key in self._attackTimer: self._attackTimer.pop(key)
            while True:
                rng = stinfo.get(self.st, (24, 28))
                rnd = random.randint(rng[0], rng[1])
                if getattr(self, 'last_attack', 0) != rnd:
                    self.last_attack = rnd
                    break
            def attack():
                self.attack_number = getattr(self, 'attack_number', 0)+1
                self._update_timer(force=True)
                if self.st == 1:
                    if rnd == 0: self.light_attack(type='multi')
                    elif rnd == 1: self.light_attack(type='vertical')
                    elif rnd == 2: self.light_attack(type='horizontal')
                    elif rnd == 3: self.circles_on_floor()
                elif self.st == 2:
                    if rnd == 4: self.bomb_worker()
                    elif rnd == 5: self.light_attack(type='multi')
                    elif rnd == 6: self.spawnBots()
                elif self.st == 3:
                    if rnd == 7: self.circles_on_floor()
                    elif rnd == 8: self.impact_bombs_attack()
                    elif rnd == 9: self.spawnBots()
                    elif rnd == 10: self.light_attack(type='multi')
                elif self.st == 4:
                    if rnd == 11: self.circles_on_floor()
                    elif rnd == 12: self.bomb_worker(count=random.randint(2,4))
                    elif rnd == 13: self.teleport(alert=True, count=(random.randint(1,3)*7))
                    elif rnd == 14: self.light_attack(type='horizontal')
                    elif rnd == 15: self.impact_bombs_attack(count=random.randint(1,2), interval=(random.randint(1,6)*1000))
                    elif rnd == 16: self.spawnBots()
                elif self.st == 5:
                    if rnd == 17: self.spawnBots()
                    elif rnd == 18: self.bomb_worker(count=10)
                elif self.st == 6:
                    if rnd == 19: self.light_attack(type="multi")
                    elif rnd == 20: self.impact_bombs_attack(count=random.randint(1,3), interval=1000)
                elif self.st == 7:
                    if rnd == 21: self.bomb_worker(count=(random.randint(1,3)*random.randint(1,2)))
                    elif rnd == 22: self.special_attack(count=1)
                    elif rnd == 23: self.circles_on_floor(delay=1000, count=random.randint(15, 22), pos=random.choice(['left', 'right', 'center']))
                elif self.st == 8:
                    if rnd == 24: self.light_attack(type="multi")
                    elif rnd == 25: self.bomb_worker(count=random.randint(3, 4))
                    elif rnd == 26: self.circles_on_floor(delay=600, count=random.randint(10, 12))
                    elif rnd == 27: self.spawnBots()
                    elif rnd == 28: self.special_attack(interval=5000, count=2)
                elif self.st == 9:
                    if rnd == 29: self.circles_on_floor(delay=600, count=10, pos='center')
                    elif rnd == 30:
                        if random.randint(0, 3) == 1: self.special_attack(interval=100, count=5)
                        else: self.special_attack()
                    elif rnd == 31: self.light_attack(type='multi')
                elif self.st == 10:
                    if rnd == 32: self.bomb_worker(count=1, bomb_drops=2, interval=500)
                    elif rnd == 33: self.special_attack()
                    elif rnd == 34: self.light_attack(type=random.choice(['horizontal', 'vertical']))
            self.heal()
            bs.gameTimer(1000, bs.Call(attack))
        else: self._attackTimer = None

    def _update(self):
        self.maxRespawn = len(self.players) * self.settings['Lives Per Player']
        self.damage.update({'now': self.damage.get('boss', 0)+self.damage.get('bots', 0)})
        self._update_timer(force=False)
        if self.damage['now'] > self.damage.get('next', 10000):
            if self.st > 0:
                damage = self.damage.get('now', 0)
                dmgst = {2: 10000, 3: 16050, 4: 22500, 5: 28500, 6: 33000, 7: 40500, 8: 52000, 9: 56500, 10: 59500}
                dmgst_sorted = dmgst.keys()
                dmgst_sorted.sort()
                dmgst_sorted.reverse()
                self.st = 1
                for i in dmgst_sorted:
                    if damage > dmgst.get(i):
                        self.st = i
                        self.damage.update({'next': dmgst.get(self.st+1, 999999999999999)})
                        break

    def spawnPlayer(self, player):
        spaz = self.spawnPlayerSpaz(player)
        spaz.connectControlsToPlayer()

    def celebratePlayers(self):
        for i in self.players:
            if i.exists() and i.isAlive(): i.actor.node.handleMessage("celebrate", 10000.0)

    def heal(self):
        def spawn():
            spawnCounts = 0
            players = [i for i in self.players if i.exists() and i.isAlive() and i.actor.hitPoints < 500]
            if self.st > 2: spawnCounts = min(2, len(players))
            if spawnCounts > 0:
                if len(players) > 0:
                    if self.getMap().defs is not None: 
                        positions = [self.getMap().defs.points.get('powerupSpawn'+str(i), (0, 5, 0)) for i in range(4)]
                        for i in range(spawnCounts): bs.Powerup(powerupType='health', position = random.choice(positions)).autoRetain()
        spawn()
        

    def checkInAlertPlayers(self, type='custom'):
        def check_position(bounds = ((-15, 15), (-2, 2)), position=None):
            if position is not None:
                if int(position[0]) in range(bounds[0][0], bounds[0][1]) and int(position[2]) in range(bounds[1][0], bounds[1][1]): return True
            return False
        boss_pos = self.boss.node.position if self.boss is not None and self.boss.exists() and self.boss.isAlive() else None
        for i in self.players:
            if i.exists() and i.isAlive():
                pos = i.actor.node.position
                if type == 'all': AlertMessage(owner=i.actor.node)
                else:
                    if (type == 'horizontal' and check_position(bounds=((-15,15), (-2,2)), position=pos)) or (type == 'vertical' and 
                        check_position(bounds=((-2,2), (-15,15)), position=pos)) or (type == 'center' and 
                        check_position(bounds=((-3,3), (-2,2)), position=pos)) or (type == 'custom' and boss_pos is not None and 
                        check_position(bounds=((-3,3), (-3,3)), position=boss_pos)): AlertMessage(owner=i.actor.node)

    def spawnBots(self):
        if (len(self._bots.getLivingBots()) < 2 and self.st < 7) or (len(self._bots.getLivingBots()) == 0 and self.st > 6):
            if self.st > 1:
                for i in range(2): self._bots.spawnBot(ZeroBossBot, pos=(random.randint(-1,1),1,random.randint(-1,1)), spawnTime=1000)
            if self.st > 2:
                for i in range(2): self._bots.spawnBot(ZeroBossBotSpecial, pos=(random.randint(-1,1),1,random.randint(-1,1)), spawnTime=1)
        else: self.light_attack('multi')

    def special_attack(self, count=1, interval=1000):
        self.checkInAlertPlayers(type="all")
        def start():
            def a(player):
                if player.exists() and player.isAlive():
                    pos = (player.actor.node.position[0], player.actor.node.position[1] + 0.5, player.actor.node.position[2])
                    player.actor.node.handleMessage("impulse", pos[0], pos[1], pos[2], 0, -2, 0, 2000, 0, 1, 0, 0, -2, 0)
            for i in self.players:
                if i.exists() and i.isAlive():
                    for c in range(random.randint(1, 3)): bs.gameTimer(interval+c*interval, bs.Call(a, i))
        for i in range(count): bs.gameTimer(interval+i*interval, bs.Call(start))

    def light_attack(self, type='vertical'):
        type = [type] if type != 'multi' else ['horizontal','vertical']
        def start():
            for i in type: ZeroBossBlast(type=i).autoRetain()
        for i in type: self.checkInAlertPlayers(type=i)
        bs.gameTimer(1500+(random.randint(0, 4)*100), bs.Call(start))

    def circles_on_floor(self, interval=30, count=None, delay=500, pos=None):
        if pos in ['left', 'right', None]: self.checkInAlertPlayers(type='all')
        elif pos == 'center': self.checkInAlertPlayers(type='center')
        if count is None: count = random.randint(40, 50)
        def spawn():
            ZeroBossBlast(type='sphere', interval=interval, count=count, delay=delay, position=pos).autoRetain()
        bs.gameTimer(500, bs.Call(spawn))

    def bomb_worker(self, count=1, bomb_drops=1, interval=1000, delay=5000):
        def start():
            ZeroBossCircle(count=bomb_drops, position=random.choice([(-8, 1.5, 0), (8, 1.5, 0), (0, 1.5, 0)]), delay=delay, interval=interval, radius=0.416)
        self.checkInAlertPlayers(type='center')
        for i in range(count): bs.gameTimer(interval+((delay-interval)*i)+(random.randint(0,10)*100), bs.Call(start))

    def teleport(self, count=1, interval=100, alert=False, sound=True):
        if self.boss is not None and self.boss.exists() and self.boss.isAlive():
            if alert: self.checkInAlertPlayers(type='custom')
            if sound and count < 2: 
                try: bs.playSound(self.tpSound, 0.5, position=self.boss.node.position)
                except: pass
            mapBounds = self.getMap().spawnPoints
            def start():
                pos = (random.uniform(mapBounds[0][0], mapBounds[1][0]), random.uniform(mapBounds[0][1], mapBounds[1][1]), random.uniform(mapBounds[0][2], mapBounds[1][2]))
                bs.emitBGDynamics(position=pos, velocity=(0.1,-1,0.1),
                    count=random.randint(30, 50), scale=0.35,
                    spread=0.2, chunkType='spark')
                self.boss.node.handleMessage("stand", pos[0], pos[1], pos[2], random.randrange(0,360))
            for i in range(count): bs.gameTimer(100+(i*interval), bs.Call(start))
        else: return 

    def impact_bombs_attack(self, count=1, interval=1000):
        self.checkInAlertPlayers(type='center')
        def start():
            for i in range(8):
                for c in [(i, i), (-i, -i), (-i, i), (i, -i)]: bs.Bomb(position=(c[0],7,c[1]), velocity=(0,0,0), bombType='impact', blastRadius=1, sourcePlayer=None).autoRetain()
        for i in range(count): bs.gameTimer(2000+(i*interval), bs.Call(start))

    def handleMessage(self, m):
        if isinstance(m, bs.PlayerSpazDeathMessage):
            bs.TeamGameActivity.handleMessage(self, m)
            self._aPlayerHasBeenKilled = True
            player = m.spaz.getPlayer()
            if not player.exists(): return
            self.scoreSet.playerLostSpaz(player)
            respawnTime = 1000 + len(self.initialPlayerInfo)*2500
            if player.gameData.get("lives") is None: player.gameData['lives'] = self.settings['Lives Per Player']
            player.gameData['lives'] -= 1
            if player.gameData['lives'] > 0:
                player.gameData['respawnTimer'] = bs.Timer(respawnTime, bs.Call(self.spawnPlayerIfExists, player))
                player.gameData['respawnIcon'] = bs.RespawnIcon(player, respawnTime)
            self.respawn, self.maxRespawn = 0, 0
            for i in self.players:
                if i.exists():
                    self.maxRespawn += self.settings['Lives Per Player']
                    self.respawn += (self.settings['Lives Per Player']-i.gameData['lives']) if hasattr(i, 'gameData') and 'lives' in i.gameData else 0
            if self.respawn >= self.maxRespawn: self.endGame()
        elif isinstance(m, ZeroBossDeathMessage):
            self.celebratePlayers()
            self.damage['bots'] += 16000
            bs.gameTimer(5000, bs.Call(self.endGame))
        elif isinstance(m, bs.SpazBotDeathMessage):
            bonus = 1000
            if self.st > 3: bonus += 200
            if self.st > 6: bonus += 1200
            self.damage['bots'] += bonus
        elif isinstance(m, ZeroBossHitMessage):
            mult = 1.0 * (self.st * 0.12) if self.st > 4 else 1.0
            self.damage['boss'] += m.damage*mult
            if m.player is not None and m.player.exists(): 
                if hasattr(m.player, 'getTeam'): team=m.player.getTeam()
                else: team = None
                if team is not None: team.gameData.update({'score': team.gameData.get('score', 0)+m.damage})
            if self.boss is not None and self.boss.exists() and self.boss.isAlive():
                hp = 0
                if self.boss.hitPoints < 3000:
                    hp += m.damage * 0.65
                    if self.st > 5: self.teleport(count=random.randint(20, 30), interval=random.randint(40,50))
                    else: self.teleport()
                elif (m.type == "punch" and m.damage >= 450) or (m.type == "explosion" and m.damage >= 1000): self.teleport()
                if self.st > 7:
                    hp += m.damage * 0.3
                    if self.boss.hitPoints < 3000 and m.damage > 400: hp += m.damage * 0.2 # 0.15 reg
                elif m.type in ["punch", "explosion"] and m.damage > 1200: self.boss.node.handleMessage('knockout', int(m.damage/12))
                if hp > 0: self.boss.hitPoints = min(self.boss.hitPoints + hp, self.boss.hitPointsMax)
        else:
            bs.TeamGameActivity.handleMessage(self, m)

    def endGame(self):
        self.st = 0
        results = bs.TeamGameResults()
        for team in self.teams: results.setTeamScore(team, int(max(0, team.gameData.get('score', 0)+self.damage['bots']*0.72+self.damage['boss']-(self.respawn*1000))))
        self._attackTimer = None
        self._updateTimer = None
        self.end(results)
        # set handle message methods and player spaz init to default
        bsSpaz.PlayerSpaz.__init__ = playerspazinit_old
        bsSpaz.PlayerSpaz.handleMessage = handleMessage_old
        bsSpaz.SpazBot.handleMessage = bot_handleMessage_old

class ZeroBossCircle(object):
    def __init__(self, position=(0, 1.5, 0), count=2, radius=1, interval=1000, delay=5000):
        self.pos = position
        def spawn():
            def a(velocities):
                for i in velocities: bs.Bomb(position=self.pos, velocity=i, bombType='normal', blastRadius=2.0, sourcePlayer=None).autoRetain()
            bs.gameTimer(interval, bs.Call(a, [(0, 0, -6), (0, 0, 6)]))
            bs.gameTimer(interval*2, bs.Call(a, [(-6, 0, 6), (6, 0, -6)]))
            bs.gameTimer(interval*3, bs.Call(a, [(-6, 0, 0), (6, 0, 0)]))
            bs.gameTimer(interval*4, bs.Call(a, [(6, 0, 6), (-6, 0, -6)]))
        for i in range(count): bs.gameTimer(delay*i, bs.Call(spawn))
        self.light = bs.newNode('light', attrs={'position': self.pos,'color': (1, 0.35, 0), 'radius': radius})
        bsUtils.animate(self.light, 'intensity', {0: 0, 1000: 0.9, count*delay-interval: 0.9, count*delay: 0})
        bsUtils.animate(self.light, 'radius', {0: radius, 700: radius, 1000: radius*1.2, 2000: radius}, loop=True)
        bs.gameTimer(count*delay, self.light.delete)

class ZeroBossLight(object):
    def __init__(self, position=(0,0,0), color=(1,0.75,0), radius=0.3, animateRadius=True, animateIntensity=True, delay=1, time=2000, radiusMultiple=1.5, radiusAnimateCounts=2, intensityScale=1.05):
        self.pos = position
        def spawn():
            self.light = bs.newNode('light', attrs={'position': self.pos,
                'heightAttenuated': True,
                'volumeIntensityScale': 20,
                'color': color,
                'radius': radius})
            if animateIntensity: bsUtils.animate(self.light, 'intensity', {0: 0, 1000: intensityScale, time*0.75: intensityScale, time: 0})
            if animateRadius:
                animTime = 1/radiusAnimateCounts * time
                bsUtils.animate(self.light, 'radius', {0: radius, animTime*0.4: radius * radiusMultiple, animTime: radius}, True)
            bs.gameTimer(time, self.light.delete)
        bs.gameTimer(delay, bs.Call(spawn))

class ZeroBossBlast(bs.Actor):
    def __init__(self, position=None, time=5000, type='horizontal', delay=500, interval=30, count=30):
        bs.Actor.__init__(self)
        factory = self.getFactory()
        self.pos = position
        self.scale = (1, 1, 1)
        if type in ['vertical', 'horizontal']:
            self.scale = (0.1, 10, 20) if type == 'vertical' else (20, 10, 0.1)
            count = 20 if type == 'vertical' else 30
            if type == 'horizontal': set_pos = (-15, 1, 0) if self.pos in ['left', 'right', 'center', None] else self.pos
            else: set_pos = (0, 1, -12) if self.pos in ['left', 'right', 'center', None] else self.pos
            def b():
                self.node = bs.newNode('region', delegate=self,
                    attrs={'position': (0, set_pos[1] - 0.1, 0),
                        'scale': self.scale, 'type': 'box',
                        'materials': (factory.newBlastMaterial, bs.getSharedObject('attackMaterial'))})
                bs.gameTimer(time, self.node.delete)
            def spawn():
                def a(cnt=0):
                    ZeroBossLight(position=(set_pos[0], set_pos[1], set_pos[2]+cnt) if type == 'vertical' else (set_pos[0]+cnt, set_pos[1], set_pos[2]),
                        color=(1, 0.5, 0), radius=0.1, delay=cnt*interval, time=delay+int(time * 1.0), animateRadius=False)
                for i in range(count): bs.gameTimer(1+(i*interval), bs.Call(a, i))
                bs.gameTimer(delay, bs.Call(b))
            bs.gameTimer(interval, bs.Call(spawn))
        if type == 'sphere':
            self.scale = (0.6, 10, 0.6)
            self.nodes = []
            def spawn():
                if self.pos not in ['left', 'center', 'right']:
                    randPos = (random.randrange(-12, 12), 1, random.randrange(-5, 5)) if self.pos is None else self.pos
                elif self.pos == 'center':
                    randPos = (random.randrange(-2, 2), 0, random.randrange(-2, 2))
                elif self.pos == 'left':
                    randPos = (random.randrange(-5, -2), 0, random.randrange(-5, 5))
                elif self.pos == 'right':
                    randPos = (random.randrange(-2, 5), 0, random.randrange(-5, 5))
                ZeroBossLight(position=(randPos[0], randPos[1] - 0.1, randPos[2]),
                    color=(1, 0.5, 0), radius=0.1, time=(delay+int(time * 1.0)), animateRadius=True, intensityScale=0.9)
                def a():
                    self.nodes.append(bs.newNode('region', delegate=self, attrs={'position':(randPos[0], randPos[1]-0.1, randPos[2]),'scale':self.scale,'type':'sphere','materials':(factory.newBlastMaterial, bs.getSharedObject('attackMaterial'))}))
                    bs.gameTimer(int(time*1.0), self.nodes[-1].delete)
                bs.gameTimer(delay, bs.Call(a))
            for i in range(count): bs.gameTimer(delay+i*interval, bs.Call(spawn))


    def getFactory(cls):
        activity = bs.getActivity()
        try: return activity._sharedZeroBossBlastFact
        except Exception:
            f = activity._sharedZeroBossBlastFact = ZeroBossBlastFactory()
            return f

    def handleMessage(self, msg):
        self._handleMessageSanityCheck()
        if isinstance(msg, bs.DieMessage):
            if hasattr(self, "node") and self.node.exists(): self.node.delete()
            if hasattr(self, "nodes"):
                for i in self.nodes:
                    if i.exists: i.delete()
        if isinstance(msg, NewExplodeHitMessage):
            node = bs.getCollisionInfo("opposingNode")
            if node is not None and node.exists():
                t = node.position
                if node.getNodeType() == 'spaz':
                    node.handleMessage(bs.HitMessage(
                        pos=t,
                        velocity=(0,0,0),
                        magnitude=550.0,
                        hitType='explosion',
                        hitSubType='bossBlast',
                        radius=100.0,
                        sourcePlayer=bs.Player(None), 
                        kickBack=0))
                    node.handleMessage('impulse', t[0], t[1]-3.0, t[2], 0, 0, 0, 2000, 0, 200.0, 1, 0, 100, 0)
        else:
            bs.Actor.handleMessage(self, msg)

class ZeroBossBlastFactory(object):
    def __init__(self):
        self.blastSound = bs.getSound('activateBeep')
        self.newBlastMaterial = bs.Material()
        self.newBlastMaterial.addActions(
            conditions=(('theyHaveMaterial',
                         bs.getSharedObject('objectMaterial'))),
            actions=(('modifyPartCollision','collide',True),
                     ('modifyPartCollision','physical',False),
                     ('message','ourNode','atConnect',NewExplodeHitMessage())))

class NewExplodeHitMessage(object):
    def __init__(self):
        pass