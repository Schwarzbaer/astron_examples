# For UberDOGs
from direct.distributed.DistributedObjectGlobal import DistributedObjectGlobal
from direct.distributed.DistributedObjectGlobalAI import DistributedObjectGlobalAI
from direct.distributed.DistributedObjectGlobalUD import DistributedObjectGlobalUD
# For regular DOs
from direct.distributed.DistributedObject import DistributedObject
from direct.distributed.DistributedObjectAI import DistributedObjectAI
from direct.distributed.DistributedObjectUD import DistributedObjectUD
from direct.distributed.DistributedObjectOV import DistributedObjectOV
# For DOs that are also Panda3D scene graph nodes
from direct.distributed.DistributedNode import DistributedNode
from direct.distributed.DistributedNodeAI import DistributedNodeAI
# Assembling messages
from direct.distributed.PyDatagram import PyDatagram
from direct.distributed import MsgTypes
from direct.distributed.AstronInternalRepository import AstronInternalRepository
# AI tasks
from direct.task import Task

import random
from datetime import datetime

# Constant DO and channel IDs
from simple_example_globals import LoginManagerId

# Game settings
avatar_speed = 100.0
avatar_rotation_speed = 20.0 * 360.0

# LoginManager
# * Authenticates Client
# * Makes DistributedMaproot set up and create an avatar

class LoginManager(DistributedObjectGlobal):
    def generateInit(self):
        print(datetime.now().strftime("%H:%M:%S")+" LoginManager.generateInit() for "+str(self.doId))
        
    def login(self, username, password):
        # FIXME: Use TLS so that these are encrypted!
        print(datetime.now().strftime("%H:%M:%S")+" LoginManager.login("+username+", "+password+") in "+str(self.doId))
        self.sendUpdate("login", [username, password])

class LoginManagerAI(DistributedObjectGlobalAI):
    def generate(self):
        print(datetime.now().strftime("%H:%M:%S")+" LoginManagerAI.generate() for "+str(self.doId))

    def set_maproot(self, maproot_doId):
        self.sendUpdate("set_maproot", [maproot_doId])
        print(datetime.now().strftime("%H:%M:%S")+" LoginManagerAI.set_maproot("+str(maproot_doId)+") in "+str(self.doId))

class LoginManagerUD(DistributedObjectGlobalUD):
    def generate(self):
        print(datetime.now().strftime("%H:%M:%S")+" LoginManagerUD.generate() for "+str(self.doId))

    def set_maproot(self, maproot_doId):
        """Tells the LoginManagerUD what maproot to notify on login."""
        
        print(datetime.now().strftime("%H:%M:%S")+" LoginManagerUD.set_maproot("+str(maproot_doId)+") in "+str(self.doId))
        self.maproot = DistributedMaprootUD(self.air)
        self.maproot.generateWithRequiredAndId(maproot_doId, 0, 1)

    def login(self, username, password):
        clientId = self.air.get_msg_sender()
        print(datetime.now().strftime("%H:%M:%S")+" LoginManagerUD.login("+username+", "+password+")  in "+str(self.doId)+" for client "+str(clientId))
        if (username == "guest") and (password == "guest"):
            # Authenticate a client
            # FIXME: "2" is the magic number for CLIENT_STATE_ESTABLISHED,
            # for which currently no mapping exists.
            self.air.setClientState(clientId, 2)

            # The client is now authenticated; create an Avatar
            #self.maproot.sendUpdate("createAvatar", # Field to call
            #                        [clientId])     # Arguments
            self.maproot.create_avatar(clientId)
            
            # log login
            self.notify.info("Login successful (user: %s)" % (username,))

        else:
            # Disconnect for bad auth
            # FIXME: "122" is the magic number for login problems.
            # See https://github.com/Astron/Astron/blob/master/doc/protocol/10-client.md
            self.air.eject(clientId, 122, "Bad credentials")
            
            # log login attempt
            self.notify.info("Ejecting client for bad credentials (user: %s)" % (username,))

#
# DistributedMaproot
# * has all avatars in its zone 0
# * generates new avatars
#

class DistributedMaproot(DistributedObject):
    def generateInit(self):
        print(datetime.now().strftime("%H:%M:%S")+" DistributedMaproot.generateInit() for "+str(self.doId))
    
class DistributedMaprootOV(DistributedObjectOV):
    def generate(self):
        print(datetime.now().strftime("%H:%M:%S")+" DistributedMaprootOV.generate() for "+str(self.doId))

class DistributedMaprootAI(DistributedObjectAI):
    def generate(self):
        print(datetime.now().strftime("%H:%M:%S")+" DistributedMaprootAI.generate() for "+str(self.doId))
    
    def set_maproot(self):
        print(datetime.now().strftime("%H:%M:%S")+" DistributedMaprootAI.set_maproot() in "+str(self.doId))
        login_manager = self.air.generateGlobalObject(LoginManagerId, 'LoginManager')
        login_manager.set_maproot(self.doId)
    
    def createAvatar(self, clientId):
        print(datetime.now().strftime("%H:%M:%S")+" DistributedMaprootAI.createAvatar("+str(clientId)+") in "+str(self.doId))
        # Create the avatar
        avatar = DistributedAvatarAI(self.air)
        avatar.generateWithRequiredAndId(self.air.allocateChannel(), self.getDoId(), 0) # random doId, parentId, zoneId
        # Set the client to be interested in our zone 0. He can't do
        # that himself (or rather: shouldn't be allowed to) as he has
        # no visibility of this object.
        # We're always using the interest_id 
        self.air.clientAddInterest(clientId, 0, self.getDoId(), 0) # client, interest, parent, zone
        # Set its owner to the client, upon which in the Clients repo
        # magically OV (OwnerView) is generated.
        self.air.setOwner(avatar.getDoId(), clientId)
        # Declare this to be a session object.
        self.air.clientAddSessionObject(clientId, self.getDoId())

# The UberDOG needs this. FIXME: Or maybe just the DC reader because of /UD in .dc?
class DistributedMaprootUD(DistributedObjectUD):
    def generate(self):
        print(datetime.now().strftime("%H:%M:%S")+" DistributedMaprootUD.generate() for "+str(self.doId))
        
    def create_avatar(self, clientId):
        print(datetime.now().strftime("%H:%M:%S")+" DistributedMaprootUD.create_avatar("+str(clientId)+") in "+str(self.doId))
        self.sendUpdate("createAvatar", # Field to call
                            [clientId])     # Arguments

#
# DistributedAvatar
#

class DistributedAvatar(DistributedNode):
    def generateInit(self):
        print(datetime.now().strftime("%H:%M:%S")+" Generated DistributedAvatar "+str(self.doId))
        model = base.loader.loadModel("models/smiley")
        model.reparent_to(self)
        model.setH(180.0)
        # Signal app that this is its avatar
        base.messenger.send("distributed_avatar", [self])
        
    def setXYZH(self, *args):
        DistributedNode.setXYZH(self, *args)
        
    def delete(self):
        print("Avatar got removed.")

class DistributedAvatarOV(DistributedObjectOV):
    def generateInit(self):
        # Make yourself known to the client
        print(datetime.now().strftime("%H:%M:%S")+" DistributedAvatarOV.generate() for "+str(self.doId))
        base.messenger.send("avatar", [self])
        
    def indicateIntent(self, heading, speed):
        self.sendUpdate("indicateIntent", [heading, speed])

class DistributedAvatarAI(DistributedNodeAI):
    def generate(self, repository=None):
        print(datetime.now().strftime("%H:%M:%S")+" DistributedAvatarAI.generate() for "+str(self.doId))
        self.heading = 0.0
        self.speed = 0.0
        self.update_task = base.taskMgr.add(self.update_position, "Avatar position update")

    def delete(self):
        print(datetime.now().strftime("%H:%M:%S")+" DistributedAvatarAI.delete() for "+str(self.doId))
        base.taskMgr.remove(self.update_task)

    def indicateIntent(self, heading, speed):
        if (heading < -1.0) or (heading > 1.0) or (speed < -1.0) or (speed > 1.0):
            # Client is cheating!
            # FIXME: Eject client
            return
        self.heading = heading
        self.speed = speed
    
    def update_position(self, task):
        if (self.heading != 0.0) or (self.speed != 0.0):
            dt = task.getDt()
            self.setH((self.getH() + self.heading * avatar_rotation_speed * dt) % 360.0)
            self.setY(self, self.speed * avatar_speed * dt)
            if self.getX() < -10.0:
                self.setX(-10.0)
            if self.getX() > 10.0:
                self.setX(10.0)
            if self.getY() < -10.0:
                self.setY(-10.0)
            if self.getY() > 10.0:
                self.setY(10.0)
            self.b_setXYZH(self.getX(), self.getY(), self.getZ(), self.getH())
        return Task.cont
