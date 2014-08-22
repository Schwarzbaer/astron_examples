#!/usr/bin/env python

from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from direct.distributed.PyDatagram import PyDatagram
from direct.distributed import MsgTypes
from direct.distributed.AstronInternalRepository import AstronInternalRepository
from panda3d.core import loadPrcFileData
from time import sleep

# Globally known object and channel IDs
from simple_example_globals_server import LoginManagerId, AIChannel, UDChannel, SSChannel

# No camera or window is needed.
loadPrcFileData("", "window-type none")

# This class manages the UberDOGs, which in this case is just one, the login
# manager.
class SimpleServer(ShowBase):
    def __init__(self, server_framerate = 60):
        ShowBase.__init__(self)
        # First, set up the idle task that forces a sleep
        # that reduces the servers speed to a given framerate.
        self.server_frametime = 1./server_framerate
        self.taskMgr.add(self.idle, 'idle task', sort = 47)
        # Start UberDOG
        #self.startUberDOG()
        # Start AI shard
        self.startAIShard()

    def startUberDOG(self):
        # UberDOG repository
        # FIXME: Why do AIR and LoginManager have the same doId? WAT!
        air = AstronInternalRepository(UDChannel, # Uberdog channel typically == Uberdog ID
                                       serverId = SSChannel, # Stateserver Channel
                                       dcFileNames = ["simple_example.dc"],
                                       dcSuffix = "UD",
                                       connectMethod = AstronInternalRepository.CM_NET)
        air.connect("127.0.0.1", 7199)
        
        air.districtId = air.GameGlobalsId = 10000
        
        # Create the LoginManager
        self.login_manager = air.generateGlobalObject(LoginManagerId, 'LoginManager')

    def startAIShard(self):
        # DO mappings can only be imported once ShowBase has been instantiated.
        # WTF! FIXME: This has to be fought! No idea how, though...
        from simple_example import DistributedMaprootAI

        # AI repository
        air = AstronInternalRepository(AIChannel, # AI/Shard Channel
                                       serverId = SSChannel, # Stateserver Channel
                                       dcFileNames = ["simple_example.dc"],
                                       connectMethod = AstronInternalRepository.CM_NET)
        air.connect("127.0.0.1", 7199)

        air.districtId = air.GameGlobalsId = 10000

        # The map root
        maproot = DistributedMaprootAI(air)
        maproot.generateWithRequiredAndId(air.districtId, 0, 1) # No parent / zone
        # Setting AI channel.
        air.setAI(maproot.doId, AIChannel)
        maproot.set_maproot()
        #self.login_manager.set_maproot(air.districtId)
        

    # Idle task, so that the server doesn't eat 100% CPU
    def idle(self, task):
        # If this frame took less time than a frame should take,
        # sleep for the difference.
        elapsed = globalClock.getDt()
        if elapsed < self.server_frametime:
            sleep(self.server_frametime - elapsed)
        return Task.cont

simple_server = SimpleServer()
simple_server.run()
