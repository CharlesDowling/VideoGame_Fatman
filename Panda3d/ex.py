from direct.showbase.ShowBase import ShowBase
from direct.showbase.InputStateGlobal import *
from direct.gui.DirectLabel import DirectLabel
from direct.gui.DirectButton import DirectButton
from panda3d.core import *
from panda3d.bullet import *
import sys

loadPrcFile('config/Config.prc')

class Game(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        self.menu()

    def menu(self):
        self.label = DirectLabel(text='Fight 4 Life', pos=(400, 0, -250), scale=50,  parent=self.pixel2d)
        self.singleplayer = DirectButton(text='Singleplayer', pos=(400, 0, -350), scale=50, parent=self.pixel2d, command=self.game)
        self.multiplayer = DirectButton(text='Multiplayer', pos=(400, 0, -450), scale=50, parent=self.pixel2d)
        self.multiplayer['state'] = 0

    def game(self):
        self.label.hide()
        self.singleplayer.hide()
        self.multiplayer.hide()

        self.props = WindowProperties()
        self.props.cursor_hidden = True
        self.win.requestProperties(self.props)
        self.win.setClearColor((0, 1, 1, 1))
        
        self.disableMouse()

        self.mouse_sens = 0.05
        
        inputState.watchWithModifiers('forward', 'w')
        inputState.watchWithModifiers('reverse', 's')
        inputState.watchWithModifiers('left', 'a')
        inputState.watchWithModifiers('right', 'd')

        self.accept('escape', self.exit)

        self.world = BulletWorld()
        self.world.setGravity(0, 0, -9.81)

        self.groundNode = BulletRigidBodyNode('Ground')
        self.groundShape = BulletPlaneShape(Vec3(0, 0, 1), 1)
        self.groundNode.addShape(self.groundShape)
        self.world.attachRigidBody(self.groundNode)
        self.groundNP = self.render.attachNewNode(self.groundNode)
        self.groundNP.setPos(0, 0, -2)
        self.groundModel = self.loader.loadModel('Assets/Models/Level1.gltf')
        self.groundModel.setScale(100, 100, 100)
        self.groundModel.reparentTo(self.groundNP)

        
        self.capsuleShape = BulletBoxShape(Vec3(5, 5, 5))
        self.characterNode = BulletCharacterControllerNode(self.capsuleShape, 1.0, 'Character')
        self.world.attachCharacter(self.characterNode)
        self.characterNP = self.render.attachNewNode(self.characterNode)
        self.camera.reparentTo(self.render)        
        self.characterNP.setPos(-20,0,10)
        self.camera.setPos(self.characterNP,-10,0,5)
        self.characterNP.setZ(100)

        self.zombieNode = BulletRigidBodyNode('Zombie')
        self.zombieShape = BulletBoxShape(Vec3(25, 25, 25))
        self.zombieNode.setMass(100.0)
        self.zombieNode.addShape(self.zombieShape)
        self.world.attachRigidBody(self.zombieNode)
        self.zombieNP = self.render.attachNewNode(self.zombieNode)
        self.zombieModel = self.loader.loadModel("Assets/Models/Fatman.gltf")
        self.zombieModel.setScale(25, 25, 25)
        self.zombieModel.setColor(0, 0, 255)
        self.zombieModel.reparentTo(self.characterNP)
        self.zombieNP.reparentTo(self.characterNP)

        debugNode = BulletDebugNode("Debug")
        debugNode.showWireframe(True)
        debugNode.showConstraints(True)
        debugNP = self.render.attachNewNode(debugNode)
        debugNP.show()

        self.taskMgr.add(self.update, "Updates the scene")
        
    def setKey(self, key, value):
        self.keyMap[key] = value
    
    def update(self, task):
        dt = globalClock.getDt()

        speed = Vec3(0, 0, 0)

        if inputState.isSet('forward'): speed.setY( 500.0)
        if inputState.isSet('reverse'): speed.setY(-500.0)
        if inputState.isSet('left'):    speed.setX(-500.0)
        if inputState.isSet('right'):   speed.setX( 500.0)
        self.characterNode.setLinearMovement(speed, True)

        self.world.doPhysics(dt)

        md = self.win.getPointer(0)
        x = md.getX()
        y = md.getY()
        if self.win.movePointer(0, self.win.getXSize() // 2, self.win.getYSize() // 2):
            self.camera.setH(self.camera.getH() - (x - self.win.getXSize()/2)*self.mouse_sens) 
            self.camera.setP(self.camera.getP() - (y - self.win.getYSize()/2)*self.mouse_sens)
        
        return task.cont

    def exit(self):
        self.props.cursor_hidden = False
        self.win.requestProperties(self.props)
        sys.exit()
        
game = Game()
game.run()