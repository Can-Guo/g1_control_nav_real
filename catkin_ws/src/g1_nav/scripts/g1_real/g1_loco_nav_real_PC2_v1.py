import time
import sys
from unitree_sdk2py.core.channel import ChannelSubscriber, ChannelFactoryInitialize
from unitree_sdk2py.idl.default import unitree_go_msg_dds__SportModeState_
from unitree_sdk2py.idl.unitree_go.msg.dds_ import SportModeState_
from unitree_sdk2py.g1.loco.g1_loco_client import LocoClient

from geometry_msgs.msg import Twist
import rclpy
rclpy.init()

from rclpy.node import Node

# ChannelFactoryInitialize(0, "eth0")
# print("Initializing LocoClient with network interface: eth0!\r\n")


class LocoNavRealPC2(Node):
    def __init__(self, network_interface='eth0'):
        super().__init__('g1_loco_nav_real_pc2')

        self.network_interface = network_interface

        try:
            ChannelFactoryInitialize(0, network_interface)
            self.get_logger().info(f"Initializing LocoClient with network interface: {self.network_interface}")
        
        except Exception as e:
            self.get_logger().error(f"Failed to initialize ChannelFactory: {e}")
            # sys.exit(1) 
            raise RuntimeError(f"Failed to initialize ChannelFactory: {e}")
        
        self.nav_client = LocoClient()
        self.nav_client.SetTimeout(15.0)

        if self.nav_client.Init():
            self.get_logger().info("LocoClient initialized successfully!")
        else:
            self.get_logger().error("Failed to initialize LocoClient!")
            raise RuntimeError("Failed to initialize LocoClient!")
        
        self.nav_client.ShakeHand()
        time.sleep(3.0)
        self.nav_client.ShakeHand()
        time.sleep(1.0)
        self.get_logger().info("Robot shakehand completed!\r\n")

        time.sleep(1.0)
        self.get_logger().info("WARNING: Please ensure there are no obstacles around the robot while running this example!\r\n")
        self.get_logger().info("Press Ctrl+C to exit the program.\r\n")
        
        time.sleep(1.0)
        
        # Create a subscriber for cmd_vel topic
        self.cmd_vel_subscriber = self.create_subscription(
            Twist,
            '/cmd_vel',
            self.cmd_vel_callback,
            10
        )

    def cmd_vel_callback(self, msg):
        try:
            vx = msg.linear.x
            vy = msg.linear.y
            vz = msg.angular.z

            self.get_logger().info(f"Received cmd_vel: linear.x={vx}, linear.y={vy}, angular.z={vz}.\r\n")   
            # self.nav_client.Move(vx, vy, vz)

        except Exception as e:
            self.get_logger().error(f"Error processing cmd_vel message: {e}")
            return


if __name__ == '__main__':

    nav_node = LocoNavRealPC2("eth0")

    try:
        rclpy.spin(nav_node)
    except Exception as e:
        nav_node.get_logger().error(f"Exception occurred: {e}")
    finally:
        nav_node.get_logger().info("Shutting down LocoNavRealPC2 node.")
        # Clean up resources
        nav_node.destroy_node()
        nav_node.get_logger().info("Node shutdown complete!")
        # Shutdown rclpy
        rclpy.shutdown()
        # Exit the script
        exit(0)

