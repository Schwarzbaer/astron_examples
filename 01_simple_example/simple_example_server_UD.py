#!/usr/bin/env python

from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from direct.distributed.AstronInternalRepository import AstronInternalRepository
from direct.directnotify.DirectNotifyGlobal import directNotify
from panda3d.core import loadPrcFileData
from time import sleep

# Globally known object and channel IDs
from simple_example_globals_server import LoginManagerId, UDChannel, SSChannel

# No camera or window is needed, but notifications are.
loadPrcFileData("", "\n".join(["window-type none",
                               "notify-level-udserver debug"]))
notify = directNotify.newCategory("udserver")

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
        self.startUberDOG()

    # Idle task, so that the server doesn't eat 100% CPU
    def idle(self, task):
        # If this frame took less time than a frame should take,
        # sleep for the difference.
        elapsed = globalClock.getDt()
        if elapsed < self.server_frametime:
            sleep(self.server_frametime - elapsed)
        else:
            notify.warning("Framedrop! Elapsed time in frame: "+str(elapsed))
        return Task.cont

    def startUberDOG(self):
        notify.info("Starting UberDOG")
        # UberDOG repository
        air = AstronInternalRepository(UDChannel,                           # Repository channel
                                       serverId = SSChannel,                # Stateserver channel
                                       dcFileNames = ["simple_example.dc"],
                                       dcSuffix = "UD",
                                       connectMethod = AstronInternalRepository.CM_NET)
        air.connect("127.0.0.1", 7199)
        air.districtId = air.GameGlobalsId = UDChannel
        
        # Create the LoginManager
        self.login_manager = air.generateGlobalObject(LoginManagerId, 'LoginManager')

simple_server = SimpleServer()
simple_server.run()
