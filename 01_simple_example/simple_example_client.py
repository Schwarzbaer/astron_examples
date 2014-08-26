#!/usr/bin/env python

# FIXME: Insure that in the repo heartbeat is started/stopped.

# This string has to match the one in astrond.yml, role clientagent.
version_string = "SimpleExample v0.2"

import sys
from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from panda3d.core import URLSpec
from direct.distributed.AstronClientRepository import AstronClientRepository
from direct.distributed import MsgTypes
from pandac.PandaModules import STUint16, STUint32

class SimpleClient(ShowBase):
    def __init__(self):
        # Basics
        ShowBase.__init__(self)
        base.disableMouse()
        self.accept("escape", self.disconnect)
        base.camera.set_pos(0, 0, 60)
        base.camera.look_at(0, 0, 0)
        # Game-relevant attributes
        self.has_avatar = False
        self.avatar_owner_view = False
        # Avatar controls
        # FIXME: These values will be off the kilter if keys are pressed when the client starts.
        self.movement_heading = 0
        self.movement_speed = 0
        self.accept("avatar", self.get_avatar)
        self.accept("distributed_avatar", self.get_distributed_avatar)
        self.accept("arrow_up", self.indicate_movement, [0, 1])
        self.accept("arrow_up-up", self.indicate_movement, [0, -1])
        self.accept("arrow_down", self.indicate_movement, [0, -1])
        self.accept("arrow_down-up", self.indicate_movement, [0, 1])
        self.accept("arrow_left", self.indicate_movement, [1, 0])
        self.accept("arrow_left-up", self.indicate_movement, [-1, 0])
        self.accept("arrow_right", self.indicate_movement, [-1, 0])
        self.accept("arrow_right-up", self.indicate_movement, [1, 0])
        # Create repository
        # FIXME: For some freaky reason, using the default method
        # (CM_HTTP) won't result in further callbacks being called
        # back. Does connection() fail?
        self.repo = AstronClientRepository(dcFileNames = ["simple_example.dc"],
                                           connectMethod = AstronClientRepository.CM_NET)
        # Callback events. These names are "magic" (defined in AstronClientRepository)
        self.accept("CLIENT_HELLO_RESP", self.client_is_handshaked)
        self.accept("CLIENT_EJECT", self.ejected)
        self.accept("CLIENT_OBJECT_LEAVING", self.avatar_leaves)
        self.accept("CLIENT_OBJECT_LEAVING_OWNER", self.avatar_leaves_owner)
        self.accept("LOST_CONNECTION", self.lost_connection)
        # Connecting
        url = URLSpec()
        url.setServer("127.0.0.1")
        url.setPort(6667)
        # FIXME: No idea why this doesn't work instead...
        # url = URLSpec("127.0.0.1", 6667)
        self.notify.debug("Connecting...")
        self.repo.connect([url],
                          successCallback = self.connection_success,
                          failureCallback = self.connection_failure)

    #
    # Connection management (callbacks and helpers)
    #

    # Connection established. Send CLIENT_HELLO to progress from NEW to UNKNOWN.
    # Normally, there could be code here for things to do before entering making
    # the connection and actually interacting with the server.
    def connection_success(self, *args):
        self.repo.sendHello(version_string)

    def connection_failure(self):
        self.notify.error("Failed to connect")
        sys.exit()

    def lost_connection(self):
        self.notify.error("Lost connection")
        sys.exit()

    # Voluntarily end the connection.
    def disconnect(self):
        self.repo.disconnect()
        sys.exit()
    
    # Client was ejected
    def ejected(self, error_code, reason):
        self.notify.error("Ejected! %d: %s" % (error_code, reason))
        sys.exit()

    # Client has received CLIENT_HELLO_RESP and now is in state UNKNOWN.
    def client_is_handshaked(self, *args):
        login_manager = self.repo.generateGlobalObject(1234, 'LoginManager')
        # Attach map to scene graph
        self.map = self.loader.loadModel("map")
        self.map.reparent_to(self.render)
        # Log in and receive; leads to enter_owner (ownership of avatar)
        login_manager.login("guest", "guest")

    def avatar_leaves(self, do_id):
        print("Avatar leaving: "+str(do_id))

    def avatar_leaves_owner(self, do_id):
        print("AvatarOV leaving: "+str(do_id))
        
    #
    # Interface
    #
    
    # Adjust current intention and send it.
    def indicate_movement(self, heading, speed):
        if self.has_avatar:
            # FIXME: Not really graceful to just ignore this.
            # What if a button was already pressed when we got the OV?
                        
            self.movement_heading += heading
            self.movement_speed += speed
            self.avatar_owner_view.indicateIntent(self.movement_heading, self.movement_speed)
        else:
            print("Avatar not complete yet!")

    # A DistributedAvatarOV was created, here is it.
    def get_avatar(self, owner_view):
        print("Received avatar OV in client")
        self.avatar_owner_view = owner_view
        self.taskMgr.add(self.complete_avatar, 'complete avatar')

    def complete_avatar(self, task):
        try:
            avatar = self.repo.doId2do[self.avatar_owner_view.doId]
            base.camera.reparent_to(avatar)
            base.camera.set_pos(0, -20, 10)
            base.camera.look_at(0, 0, 0)
            self.has_avatar = True
        except KeyError:
            print("Couldn't complete avatar "+str(self.avatar_owner_view.doId)+", available DOs: "+", ".join([str(doId) for doId in self.repo.doId2do.keys()]))
            return Task.cont

    # A DistributedAvatar was created, here is it.
    def get_distributed_avatar(self, avatar):
        print("Received avatar "+str(avatar.doId))
        avatar.reparent_to(self.map)

# Create and run this client
if __name__ == "__main__":
    simple_client = SimpleClient()
    simple_client.run()

