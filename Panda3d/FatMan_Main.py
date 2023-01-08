from math import radians, sin
from direct.showbase.ShowBase import *
from panda3d.core import loadPrcFileData, Vec3
from direct.showbase.InputStateGlobal import *
from direct.actor.Actor import Actor
from direct.interval.IntervalGlobal import Sequence
#from direct.gui.DirectLabel import *
from direct.gui.DirectGui import *
from panda3d.core import *
from panda3d.physics import *
from panda3d.bullet import *
from panda3d.bullet import BulletSphereShape, BulletPlaneShape, BulletBoxShape, BulletCylinderShape, BulletCapsuleShape, BulletWorld, BulletDebugNode, BulletGhostNode, BulletCharacterControllerNode, BulletRigidBodyNode
from direct.task.TaskManagerGlobal import taskMgr
import sys
import os

# My Config Variables
winTitle = "FatMan"
fov = 50
frameMeter = True
winWidth = 1080
winLength = 1920
fullscreen = False
syncVideo = True
clock_rate = 60

gameConfiguration = f"""
win-size {winLength} {winWidth}
window-title {winTitle}
show-frame-rate-meter {frameMeter}
default-fov {fov}
fullscreen {fullscreen}
sync-video {syncVideo}
clock-mode limited
clock-frame-rate {clock_rate}
"""

loadPrcFileData("", gameConfiguration)

class fatMan(ShowBase):

    running = False
    
    def __init__(self):
        ShowBase.__init__(self)    
 
        self.settings_setup()    

        #Sets up in game physics engine
        self.world = BulletWorld()
        self.world.setGravity(Vec3(0, 0, -29.43))

        #Debugging Node Setup
        debug_Node = BulletDebugNode("Debug")
        debug_Node.showWireframe(True)
        debug_Node.showConstraints(True)
        debug_NP = self.render.attachNewNode(debug_Node)
        debug_NP.show()
        self.world.setDebugNode(debug_NP.node())

        #Disables Default Mouse Controls
        self.disableMouse()

        #Generates the player
        self.generate_player()

        #Generates All Game World
        self.generate_worlds()

        #Generates Items
        self.generate_items()

        #Loads level items
        self.load_items(self.level)

        #Loads the level terrain
        self.loadLevel(self.level)

        #Initialize HUD
        self.HUD()

        #Sets up Camera
        self.camera.reparentTo(self.player_NP)
        self.camera.setPos(-15, 0, 20)
        self.camera.lookAt(0, 0, 0)
        self.camera.setHpr(270, -30, 0)

        #Keyboard Controls
        inputState.watchWithModifiers('forward', 'w')
        inputState.watchWithModifiers('reverse', 's')
        inputState.watchWithModifiers('left', 'a')
        inputState.watchWithModifiers('right', 'd')
        inputState.watchWithModifiers('jump', 'space')
        inputState.watchWithModifiers('accept', "e")
        inputState.watchWithModifiers('no_accept', 'e-up')
        inputState.watchWithModifiers('console','c')

        self.accept('escape', self.exit)     

        #Starts Updating Game frame by frame
        self.updateTask = taskMgr.add(self.update, "update")



    def update(self, task):
        # Get the amount of time since the last update
        dt = globalClock.getDt()

        #Calculates Physics
        self.world.doPhysics(dt)

        #Checks for collisions with Items only
        self.Check_Item_Collisions()

        #Updates the player HUD
        self.HUD_update()

        #Checks for Collisions with NPCs
        self.Check_NPC_Collisions()     

        #Checks for if player initiates a level change
        self.Check_Level_Change_Collisions()

        ###Checks for user input
        self.user_input()
        
        return task.cont 



    def generate_player(self):
        
        ###Sets up the player

        #Loads Player model
        self.player_Model = self.loader.loadModel("Assets/Models/Fatman.gltf")
        self.player_Model.setScale(1, 1, 1)
        self.player_Model.setPos(0, 0, -4.5)  

        #Creates a player controller      
        self.player_Node = BulletCharacterControllerNode(BulletBoxShape(Vec3(3, 3, 4.5)), 1.0, 'Character')

        #Creates a node point
        self.player_NP = self.render.attachNewNode(self.player_Node)

        #Copies the player model to the node point
        self.player_Model.copyTo(self.player_NP)
        self.player_NP.setPos(-7, 0, 7)
        self.world.attachCharacter(self.player_Node)
        self.playerHP = 50

        #Changes functions name for ease of use
        self.Movement = self.player_Node.setLinearMovement


    
    def loadLevel(self,level):
        

        if level == "1":
            self.House_exterior_NP.show()
            self.Ground_NP.show()
            self.world.attach(self.House_Node)
            self.world.attach(self.House_Portal_Node)
        if level != "1":
            if self.Ground_NP.isHidden() == False:
                self.Ground_NP.hide()
                self.world.remove(self.Ground_Node)
            if self.House_exterior_NP.isHidden() == False:
                self.House_exterior_NP.hide() 
                self.world.remove(self.House_Node)
            if self.House_Portal_NP.isHidden() == False:
                self.world.remove(self.House_Portal_Node)

        if level == "haus":
            self.House_NP.show()
            self.Bed_NP.show()
            self.world.attach(self.House_Exit_Portal_Node)
            self.world.attach(self.Bed_Node)
            self.player_NP.setPos(-5, 5, 0)
            self.player_NP.setHpr(-45, 0, 0)
            for x in range(4):
                self.world.attach(self.walls_node[x])
        if level != "haus":
            if self.House_NP.isHidden() == False:
                self.House_NP.hide()
            if self.Bed_NP.isHidden() == False:
                self.world.remove(self.Bed_Node)
                self.Bed_NP.hide()
            if self.House_Exit_Portal_NP.isHidden() == False:
                self.world.remove(self.House_Exit_Portal_Node)
            for x in range(4):
                self.world.remove(self.walls_node[x])


    def generate_worlds(self):


    ######################################################################
    ###Level1 Loading


            #Loads Terrain Map
            self.level1_ground = self.loader.loadModel("Assets/Models/Level1.gltf")
            self.level1_ground.setScale(1, 1, 1)
            self.level1_ground.setPos(0, 0, 0)

            #Generates Bullet Physics for map
            self.Ground_Shape = BulletPlaneShape(Vec3(0, 0, 1), 1)
            self.Ground_Node = BulletRigidBodyNode("Ground")
            self.Ground_Node.addShape(self.Ground_Shape)
            self.Ground_NP = self.render.attachNewNode(self.Ground_Node)
            self.Ground_NP.setPos(0, 0, 0)
            self.world.attachRigidBody(self.Ground_Node)
            self.level1_ground.copyTo(self.Ground_NP)

            #Loads in the player's house
            self.House_Model = self.loader.loadModel("Assets/Models/DummyHous.gltf")
            self.House_Model.setScale(1, 1, 1)
            self.House_Model.setPos(0, 0, -10)
            self.House_Model.setHpr(180, 0, 0)
            self.House_Shape = BulletBoxShape(Vec3(10, 10, 10))
            self.House_Node = BulletRigidBodyNode("Hous")
            self.House_Node.addShape(self.House_Shape)
            self.House_exterior_NP = self.render.attachNewNode(self.House_Node)
            self.House_exterior_NP.setPos(50, 0, 10)
            self.world.attachRigidBody(self.House_Node)
            self.House_Model.copyTo(self.House_exterior_NP)

            #Creates collision object for transport inside player's house
            self.House_Portal_Shape =  BulletBoxShape(Vec3(3, 3, 5))
            self.House_Portal_Node = BulletGhostNode("House Door")
            self.House_Portal_Node.addShape(self.House_Portal_Shape)
            self.House_Portal_NP = self.render.attachNewNode(self.House_Portal_Node)
            self.House_Portal_NP.setPos(37, 0, 5)


    ############################################################################
    ###Generates inside of player's house
            
            
            self.House_level = self.loader.loadModel("Assets/Models/House_Interior.gltf")
            self.House_level.setScale(1, 1, 1)
            self.House_level.setPos(0, 0, 0)
            
            self.House_Floor = BulletPlaneShape(Vec3(0, 0, 1), 1)
            self.House_Floor_Node = BulletRigidBodyNode("House_Floor")
            self.House_Floor_Node.addShape(self.House_Floor)
            self.House_NP = self.render.attachNewNode(self.House_Floor_Node)
            self.House_NP.setPos(0, 0, 0)
            self.House_NP.setHpr(-90, 0, 0)
            self.world.attach(self.House_Floor_Node)
            self.House_level.copyTo(self.House_NP)

            self.Bed_Shape = BulletBoxShape(Vec3(5, 2.5, 2))
            self.Bed_Node = BulletRigidBodyNode("Bed")
            self.Bed_Node.addShape(self.Bed_Shape)
            self.Bed_NP = self.render.attachNewNode(self.Bed_Node)
            self.Bed_NP.setPos(15,-17.5,1)
            self.world.attach(self.Bed_Node)

            #Creates collision object for transport inside player's house
            self.House_Exit_Portal_Shape =  BulletBoxShape(Vec3(3, 3, 5))
            self.House_Exit_Portal_Node = BulletGhostNode("House Door")
            self.House_Exit_Portal_Node.addShape(self.House_Exit_Portal_Shape)
            self.House_Exit_Portal_NP = self.render.attachNewNode(self.House_Exit_Portal_Node)
            self.House_Exit_Portal_NP.setPos(-17, 17, 5)

            self.walls_shape = []
            self.walls_node = []
            self.walls_NP = []

            for x in range(4):
                self.walls_shape.append(BulletBoxShape(Vec3(20,5,10)))
                self.walls_node.append(BulletRigidBodyNode("Wall{}".format(x)))
                self.walls_node[x].addShape(self.walls_shape[x])
                self.walls_NP.append(self.render.attachNewNode(self.walls_node[x]))
            
            self.walls_NP[0].setPos(Vec3(0, -25, 10))
            self.walls_NP[1].setPos(Vec3(0, 25, 10))

            self.walls_NP[2].setPos(Vec3(-25, 0, 10))
            self.walls_NP[2].setHpr(Vec3(90, 0, 0))
            self.walls_NP[3].setPos(Vec3(25, 0, 10))
            self.walls_NP[3].setHpr(Vec3(90, 0, 0))


    def load_items(self,level):
        
        if level == "haus":
            if self.health_pill_NP.isHidden() == True:
                self.health_pill_NP.show()
                self.world.attach(self.health_pill_node)
        if level != "haus":
            if self.health_pill_NP.isHidden() == False:
                self.health_pill_NP.hide()
                self.world.remove(self.health_pill_node)

    

    def generate_items(self):
        #loads healthpill powerups
        self.health_pill = self.loader.loadModel("Assets/Models/HealthPill.gltf")
        self.health_pill.setScale(1, 1, 1)            
        self.health_pill.setPos(0, 0, -2)
        self.health_pill_shape = BulletSphereShape(2)
        self.health_pill_node  = BulletGhostNode("HealthPill")
        self.health_pill_node.addShape(self.health_pill_shape)
        self.health_pill_NP = self.render.attachNewNode(self.health_pill_node)                
        self.health_pill_NP.setPos(18, -10, 3)
        self.health_pill.copyTo(self.health_pill_NP)



    def HUD(self):

        #Creates health bar
        self.HP_Label = DirectLabel(text='Health: {}  '.format(self.playerHP), frameSize = (-3, 3, -1, 1), frameColor = (0, 0, 0, 0), pos = (150, 0, -50), 
            text_fg = (255, 0, 0, 1), scale=50,  parent=self.pixel2d
        )

        self.commandtext = DirectEntry(text = " ", scale=.05, pos = (-1.5, 0, 0), frameSize = (0, 20, -1, 1), numLines = 2, focus = 0, width = 20
        )

        self.commandbutton = DirectButton(text=("Enter Command", "Command Entered!"), pos = (1, 0, 0), frameSize = (-3, 3, -1, 1),
                 scale=.05, command=self.console
        )

        self.commandtext.hide()
        self.commandtext.show()



    def HUD_update(self):

        #Updates player health
        self.HP_Label.setText('Health: {}'.format(self.playerHP))



    def settings_setup(self):

        #Sets up game settings variables
        self.jumpSpeed = 1
        self.playerSpeed = 20
        self.negPlayerSpeed = (-1 * self.playerSpeed)
        self.rotateSpeed = 1
        self.level = "1"



    def Check_Item_Collisions(self):
        if self.level == "haus":
            if (self.player_NP.node() in self.health_pill_NP.node().getOverlappingNodes()):
                self.health_pill_NP.hide()
                self.playerHP = self.playerHP + 50
                self.world.remove(self.health_pill_node)



    def Check_NPC_Collisions(self):
        #Todo
        return



    def Check_Level_Change_Collisions(self):
        if self.level == "1":
            if (self.player_NP.node() in self.House_Portal_NP.node().getOverlappingNodes()):
                self.level = "haus"
                self.loadLevel(self.level)
                self.load_items(self.level)
        if self.level == "haus":
            if (self.player_NP.node() in self.House_Exit_Portal_NP.node().getOverlappingNodes()):
                self.level = "1"
                self.loadLevel(self.level)
                self.load_items(self.level)
                self.player_NP.setPos(Vec3(30,0,0))
                self.player_NP.setHpr(Vec3(180,0,0))
            
        return

    def user_input(self):
        #Initializes movement variables/resets movement variables 
        speed = Vec3(0, 0, 0)
        AngleChange = 0

        if inputState.isSet('forward'): 
            speed.setX( self.playerSpeed)

        if inputState.isSet('reverse'): 
            speed.setX( self.negPlayerSpeed)

        if inputState.isSet('left'):    
            speed.setY( self.playerSpeed)
            AngleChange = 360

        if inputState.isSet('right'):   
            speed.setY(self.negPlayerSpeed)
            AngleChange = -360

        if inputState.isSet('jump') and self.player_Node.isOnGround() == True:
            self.player_Node.setMaxJumpHeight(10.0)
            self.player_Node.setJumpSpeed(10.0)
            self.player_Node.setGravity(30.0)
            self.player_Node.doJump()

        if inputState.isSet('console'):

            if self.commandbutton.isHidden() == True:
                self.commandbutton.show()

            if self.commandbutton.isHidden() == False:
                self.commandbutton.hide()

            if self.commandtext.isHidden() == True:
                self.commandtext.show()

            if self.commandtext.isHidden() == False:
                self.commandtext.hide()
        

        #Moves player character
        self.Movement(speed, True)

        #Rotates player character
        self.player_Node.setAngularMovement(AngleChange)

    def buttonclicked(self):
        self.buttonstatus = True
    
    def console(self):
        try:
            exec(self.commandtext.get(True))
        except:
            print("Error in trying to run: " + self.commandtext.get(True))
        self.commandtext.set("")
        self.commandtext.setFocus()


    def exit(self):
        sys.exit()  

    def enumerate_items(self):
        return



game = fatMan()
game.run()