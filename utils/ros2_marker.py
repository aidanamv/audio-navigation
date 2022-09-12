import rclpy
from rclpy.node import Node
from std_msgs.msg import *
from utils.marker import *

class AtracsysPublisher(Node):
    def __init__(self):
        super().__init__('atracsys')
        self.publisher4 = self.create_publisher(Float64MultiArray, '/data_tracking/marker4', 10)
        self.publisher410 = self.create_publisher(Float64MultiArray, '/data_tracking/marker410', 10)
        self.publisher300 = self.create_publisher(Float64MultiArray, '/data_tracking/marker300', 10)
        timer_period = 0.5  # seconds
        self.recording = False
        self.timer = self.create_timer(timer_period, self.ROS_publisher(markers=[]))

    def ROS_publisher(self, markers :list):
        pose4 = Float64MultiArray()
        pose410 = Float64MultiArray()
        pose300 = Float64MultiArray()
        pose4_array=[]
        pose410_array=[]
        pose300_array=[]



        for m in markers:
            id=m._identifier
            if not isinstance(m, Marker):
                m = Marker(m)
            if id==4:
                for el_row,row in enumerate(m._rotation):
                    for el_col,rot in enumerate(row):
                        pose4.data.append(rot.astype(float))
                pose4.data.append(m._position[0].astype(float))
                pose4.data.append(m._position[1].astype(float))
                pose4.data.append(m._position[2].astype(float))
            if id==410:
                for el_row,row in enumerate(m._rotation):
                    for el_col,rot in enumerate(row):
                        pose410.data.append(rot.astype(float))
                pose410.data.append(m._position[0].astype(float))
                pose410.data.append(m._position[1].astype(float))
                pose410.data.append(m._position[2].astype(float))
            if id==300:
                for el_row,row in enumerate(m._rotation):
                    for el_col,rot in enumerate(row):
                        pose300.data.append(rot.astype(float))
                pose300.data.append(m._position[0].astype(float))
                pose300.data.append(m._position[1].astype(float))
                pose300.data.append(m._position[2].astype(float))

        self.publisher4.publish(pose4)
        self.publisher410.publish(pose410)
        self.publisher300.publish(pose300)

        self.get_logger().info('Publishing: "%s"' % pose4.data)
        self.get_logger().info('Publishing: "%s"' % pose410.data)
        self.get_logger().info('Publishing: "%s"' % pose300.data)




def main(args=None):
    rclpy.init(args=args)

    minimal_publisher = AtracsysPublisher()

    rclpy.spin(minimal_publisher)

    # Destroy the node explicitly
    # (optional - otherwise it will be done automatically
    # when the garbage collector destroys the node object)
   #  minimal_publisher.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
