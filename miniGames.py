import bs, random
import bsHockey
from bsMap import _maps as all_maps
all_maps = all_maps.keys()

def bsGetAPIVersion():
    return 4

def bsGetGames():
    return [Testing, TNTShowerGame, TNTInvasionGame]

class Testing(bs.TeamGameActivity):
    @classmethod
    def getName(cls):
        return 'Testing'

    @classmethod
    def getScoreInfo(cls):
        return {'scoreName': 'Points', 'scoreType': 'points', 'noneIsWinner': True}

    @classmethod
    def getDescription(cls, sessionType):
        return 'Just for tests.'

    @classmethod
    def supportsSessionType(cls, sessionType):
        return True if not issubclass(sessionType, bs.CoopSession) else False

    @classmethod
    def getSupportedMaps(cls, sessionType):
        return all_maps

    @classmethod
    def getSettings(cls, sessiontype):
        return []

    def __init__(self, settings):
        bs.TeamGameActivity.__init__(self, settings)

    def onTransitionIn(self):
        bs.TeamGameActivity.onTransitionIn(self, music='Survival')

    def onTeamJoin(self, team):
        pass

    def onPlayerJoin(self, player):
        bs.TeamGameActivity.onPlayerJoin(self, player)

    def onPlayerLeave(self, player):
        bs.TeamGameActivity.onPlayerLeave(self, player)

    def onBegin(self):
        bs.TeamGameActivity.onBegin(self)

    def handleMessage(self, m):
        if isinstance(m, bs.PlayerSpazDeathMessage):
            bs.TeamGameActivity.handleMessage(self, m)
            player = m.spaz.getPlayer()
            self.spawnPlayerIfExists(player)

    def endGame(self):
        if self.hasEnded(): return
        self.end(results=bs.TeamGameResults())

class TNTShowerGame(bs.TeamGameActivity):
    @classmethod
    def getName(cls):
        return 'TNT Shower'

    @classmethod
    def getScoreInfo(cls):
        return {'scoreName': 'Points', 'scoreType': 'points', 'noneIsWinner': True}

    @classmethod
    def getDescription(cls, sessionType):
        return 'Are you ready?'

    @classmethod
    def supportsSessionType(cls, sessionType):
        return True if not issubclass(sessionType, bs.CoopSession) else False

    @classmethod
    def getSupportedMaps(cls, sessionType):
        return all_maps

    @classmethod
    def getSettings(cls, sessiontype):
        return []

    def get_level_bounds_range(self):
        pts = self.getMap().defs.points
        points = ()
        for i in pts: points+=pts[i]
        self.points = []
        x, y, z = [0,1], [0,1], [0,1]
        data = []
        for i in range(len(points)):
            data.append(points[i]) # 0 1 2   3 4 5
            if i-2 >= 0 and (i-2) % 3 == 0:
                self.points.append(data)
                data = []
        for pts in self.points:
            for i in range(len(pts)):
                pt = pts[i]
                if i == 0:
                    if pt > x[1]: x[1] = pt
                    if pt < x[0]: x[0] = pt
                elif i == 1:
                    if pt > y[1]: y[1] = pt
                    if pt < y[0]: y[0] = pt
                else: 
                    if pt > z[1]: z[1] = pt
                    if pt < z[0]: z[0] = pt
        return x, y, z

    def __init__(self, settings):
        bs.TeamGameActivity.__init__(self, settings)

    def onTransitionIn(self):
        bs.TeamGameActivity.onTransitionIn(self, music='Survival')

    def spawn_tnts(self):
        x, y, z = [[int(c) for c in i] for i in self.get_level_bounds_range()]
        self.spawn_tnt(x=x, y=y, z=z)

    def spawn_tnt(self, x, y, z, recall=True):
        position = (random.randint(x[0], x[1]), random.randint(min(y[0]+8, y[1]+2), min(10, y[1]+3)), random.randint(z[0], z[1]))
        try: bs.Bomb(position=position, bombType='tnt').autoRetain()
        except: pass
        if recall: bs.gameTimer(int(random.randint(1, 10)*50), bs.Call(self.spawn_tnt, x, y, z, recall))

    def onTeamJoin(self, team):
        pass

    def onPlayerJoin(self, player):
        bs.TeamGameActivity.onPlayerJoin(self, player)

    def onPlayerLeave(self, player):
        bs.TeamGameActivity.onPlayerLeave(self, player)

    def onBegin(self):
        bs.TeamGameActivity.onBegin(self)
        self.spawn_tnts()

    def handleMessage(self, m):
        if isinstance(m, bs.PlayerSpazDeathMessage):
            bs.TeamGameActivity.handleMessage(self, m)
            player = m.spaz.getPlayer()
            self.spawnPlayerIfExists(player)

    def endGame(self):
        if self.hasEnded(): return
        self.end(results=bs.TeamGameResults())

class TNTInvasionGame(TNTShowerGame):
    @classmethod
    def getName(cls):
        return 'TNT Invasion'

    def spawn_tnt(self, x, y, z, recall=True):
        position = (random.randint(x[0], x[1]), random.randint(y[0], y[0]+2), random.randint(z[0], z[1]))
        a = bs.Bomb(position=position, bombType='tnt').autoRetain()
        a.explode()
        if recall: bs.gameTimer(50, bs.Call(self.spawn_tnt, x, y, z, recall))
