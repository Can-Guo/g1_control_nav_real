import os
import time
import sys
from unitree_sdk2py.core.channel import ChannelFactoryInitialize
from unitree_sdk2py.g1.loco.g1_loco_client import LocoClient
from geometry_msgs.msg import Twist
import rclpy
from rclpy.node import Node

# Set environment variables BEFORE initializing ROS 2
os.environ['RMW_IMPLEMENTATION'] = 'rmw_cyclonedds_cpp'
os.environ['CYCLONEDDS_URI'] = 'file:///home/unitree/cyclonedds_ws/cyclonedds.xml'

class LocoNavRealPC2(Node):
    def __init__(self, network_interface='eth0'):
        super().__init__('g1_loco_nav_real_pc2')
        
        # Store interface and initialize SDK
        self.network_interface = network_interface
        self.init_unitree_sdk()
        
        # ROS 2 subscription
        self.cmd_vel_subscriber = self.create_subscription(
            Twist, '/cmd_vel', self.cmd_vel_callback, 10
        )

    def init_unitree_sdk(self):
        """Initialize Unitree SDK components"""
        try:
            self.get_logger().info("Initializing Unitree SDK...")
            
            # Initialize DDS channel
            ChannelFactoryInitialize(0, self.network_interface)
            self.get_logger().info(f"ChannelFactory initialized on {self.network_interface}")
            
            # Initialize LocoClient
            self.nav_client = LocoClient()
            self.nav_client.SetTimeout(15.0)
            
            if not self.nav_client.Init():
                raise RuntimeError("LocoClient Init() failed")
            
            self.get_logger().info("LocoClient initialized")
            
            # Perform handshake
            self.nav_client.ShakeHand()
            time.sleep(1.0)
            self.nav_client.ShakeHand()
            self.get_logger().info("Robot handshake completed")
            
        except Exception as e:
            self.get_logger().fatal(f"Unitree SDK init failed: {str(e)}")
            raise RuntimeError("Unitree SDK initialization failed")

    def cmd_vel_callback(self, msg):
        try:
            vx = msg.linear.x
            vy = msg.linear.y
            vz = msg.angular.z

            self.get_logger().info(f"Received cmd_vel: vx={vx:.2f}, vy={vy:.2f}, vz={vz:.2f}")
            # self.nav_client.Move(vx, vy, vz)  # Uncomment when ready
            
        except Exception as e:
            self.get_logger().error(f"Command error: {str(e)}")

def main():
    # Initialize ROS 2 after environment setup
    rclpy.init()
    
    try:
        nav_node = LocoNavRealPC2("eth0")
        rclpy.spin(nav_node)
    except RuntimeError as e:
        print(f"Fatal error: {str(e)}")
    finally:
        if 'nav_node' in locals():
            nav_node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()

    