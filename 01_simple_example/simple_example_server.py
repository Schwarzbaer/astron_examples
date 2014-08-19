#!/usr/bin/env python

# This controls whether events from the server framerate limiter are
# logged. FIXME: Make those debug messages after finding a way to
# lower the loglevel to debug.
print_performance_data = False

from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from direct.distributed.PyDatagram import PyDatagram
from direct.distributed import MsgTypes
from direct.distributed.AstronInternalRepository import AstronInternalRepository
from panda3d.core import loadPrcFileData
from datetime import datetime, timedelta
from time import sleep

# Globally known object and channel IDs
from simple_example_globals_server import LoginManagerId, AIChannel, SSChannel

# No camera or window is needed.
loadPrcFileData("", "window-type none")

# This class manages the UberDOGs, which in this case is just one, the login
# manager.
class SimpleServer(ShowBase):
    def __init__(self, server_framerate = 60):
        ShowBase.__init__(self)
        # First, set up the idle task that forces a sleep
        # that reduces the servers speed to a given framerate.
        self.server_frametime = timedelta(seconds = 1./server_framerate)
        self.current_second = datetime.now().second
        self.last_frame_end = datetime.now()
        self.server_measured_framerate = 0
        self.server_measured_idletime = timedelta(seconds = 0)
        self.taskMgr.add(self.idle, 'idle task', sort = 47)
        # Start UberDOG
        self.startUberDOG()
        # Start AI shard
        self.startAIShard()

    def startUberDOG(self):
        # UberDOG repository
        # FIXME: Why do AIR and LoginManager have the same doId? WAT!
        air = AstronInternalRepository(LoginManagerId, # Uberdog channel typically == Uberdog ID
                                       serverId = SSChannel, # Stateserver Channel
                                       dcFileNames = ["simple_example.dc"],
                                       dcSuffix = "UD",
                                       connectMethod = AstronInternalRepository.CM_NET)
        air.connect("127.0.0.1", 7199)
        # Create the LoginManager
        login_manager = air.generateGlobalObject(LoginManagerId, 'LoginManager')

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

        # The map root
        maproot = DistributedMaprootAI(air)
        air.generateWithRequired(maproot, 0, 0) # No parent / zone
        
        # Setting AI channel
        dg = PyDatagram()
        dg.addServerHeader(maproot.doId, # Recipient channel/object-id
                           AIChannel,    # Sending channel --- this is our channel 300001
                           MsgTypes.STATESERVER_OBJECT_SET_AI)
        dg.add_uint64(AIChannel) # The AI to set, we want it to be us
        air.send(dg)

    # Idle task, so that the server doesn't eat 100% CPU
    def idle(self, task):
        # If this frame took less time than a frame should take,
        # sleep for the difference.
        now = datetime.now()
        elapsed = now - self.last_frame_end
        if elapsed < self.server_frametime:
            self.server_measured_idletime += self.server_frametime - elapsed
            sleep((self.server_frametime - elapsed).total_seconds())
        self.last_frame_end = datetime.now()
        # Determine and log framerate
        self.server_measured_framerate += 1
        second = datetime.now().second
        if second != self.current_second:
            self.current_second = second
            if print_performance_data:
                print("Framerate: %d, idle time: %f" %
                      (self.server_measured_framerate,
                       self.server_measured_idletime.total_seconds()))
            self.server_measured_framerate = 0
            self.server_measured_idletime = timedelta(seconds = 0)
        # Done!
        return Task.cont

simple_server = SimpleServer()
simple_server.run()
