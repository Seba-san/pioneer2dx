#!/usr/bin/env python
import rospy

from geometry_msgs.msg import Twist
#from std_msgs.msg import String
import threading
import sys, select, termios, tty # Esto es para leer el teclado
import os
from gazebo_msgs.srv import SetModelState, DeleteModel
from gazebo_msgs.msg import ModelState
from controller_manager_msgs.srv import LoadController, SwitchController

class ControlAction():
    """
    Esta clase genera un nodo para controlar:
    diff_drive_controller/DiffDriveController
    """
    def __init__(self,name):
        self.name=name
        self.getNameTopic()
        self.setPoint=Twist()
        self.keyBoardOperation()
        msg='Recordar que es necesario cargar el controlador antes' \
            ' en el launch file, ver ejemplo launch/controller.launch'
        print(msg)
	#self.x = threading.Thread(target=self.controlAction)
        #self.controlAction()

    def getNameTopic(self):
        # Por ahora lo pongo asi. A futuro buscar una forma de automatizarlo
        self._name='/rrbot/mobile_base_controller/cmd_vel'

    def run(self):
        #name=getNameTopic()
        self.pub = rospy.Publisher(self._name, Twist, queue_size=10)
        rospy.init_node(self.name, anonymous=True)
        self.time=0.1
        self.rate = rospy.Rate(1/self.time) # 10hz
        #setPoint=Twist()
        print('Iniciando nodo')
        while not rospy.is_shutdown() and self.on:
	    
            #hello_str = "hello world %s" % rospy.get_time()
            #rospy.loginfo(hello_str)
	    self.getCommand()

            self.pub.publish(self.setPoint)
            self.rate.sleep()

        rospy.signal_shutdown('Nodo finalizado por el usuario')

    def _setPoint(self,acc=[0,0]):
        self.setPoint.linear.x+=acc[0]
        self.setPoint.angular.z+=acc[1]
        if abs(self.setPoint.linear.x)<0.01:
            self.setPoint.linear.x=0
        
        if abs(self.setPoint.angular.z)<0.01:
            self.setPoint.angular.z=0

        

    def killNode(self):
        # No se como se hace eso
        #rospy.signal_shutdown(reason)
        print('Cerrando nodo')
        self.on=False

    def getCommand(self):
        key=self.getKey()
        if key in self.moveBindings.keys():
            funcExe,_=self.moveBindings.get(key)
            if self.moveBindings[key][1]!=0:
                self.out=funcExe(self.moveBindings[key][1])
            else:
                self.out=funcExe()

            if self.out==-1:
               self.on=False
    
    def getKey(self):

        # Fuente principal: https://github.com/turtlebot/turtlebot/blob/melodic/turtlebot_teleop/scripts/turtlebot_teleop_key
        settings = termios.tcgetattr(sys.stdin)
        tty.setraw(sys.stdin.fileno())
        rlist, _, _ = select.select([sys.stdin], [], [], self.time)
        if rlist:
            key = sys.stdin.read(1)
        else:
            key = ''

        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)
        return key

    def keyBoardOperation(self):
	self.moveBindings = {
	    'a':[self._setPoint,[0,-0.5]],
	    's':[self._setPoint,[-0.5,0]],
	    'd':[self._setPoint,[0,0.5]],
	    'w':[self._setPoint,[0.5,0]],
	    'q':[self.killNode,0],
	    'x':[self.setIniciar,0],
	    'r':[self.respawnModel,0]
	       }
	self.on=True
    
    def setIniciar(self):
        rospy.wait_for_service('/gazebo/set_model_state')
        #modelState=ModelState()
        setEstadoFun=rospy.ServiceProxy('/gazebo/set_model_state',SetModelState)
        modelState=ModelState()
        modelState.model_name='pioneer2dx'
        resp=setEstadoFun(modelState)

    def respawnModel(self):
        print('Inicializando Respawn model')
        service='/gazebo/delete_model'
        rospy.wait_for_service(service)
        deleteModel=rospy.ServiceProxy(service,DeleteModel)
        deleteModel(model_name='pioneer2dx')
        os.system("roslaunch pioneer2dx respawn.launch")
        print('configurando controlador')
        service='/rrbot/controller_manager/load_controller'
        rospy.wait_for_service(service)
        loadController=rospy.ServiceProxy(service,LoadController)
        msg=LoadController._request_class()
        msg.name='mobile_base_controller'
        loadController(msg)
        service='/rrbot/controller_manager/switch_controller'
        rospy.wait_for_service(service)
        switchController=rospy.ServiceProxy(service,SwitchController)
        msg=SwitchController._request_class()
        msg.start_controllers=['mobile_base_controller']
        switchController(msg)
        print('Respawn Finalizado')


if __name__ == '__main__':
    try:
        pioneer=ControlAction(name='human_control')
        pioneer.run()
    except rospy.ROSInterruptException:
        pass
