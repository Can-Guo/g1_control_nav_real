import time
import rclpy
import sys
import os
from rclpy.node import Node
from geometry_msgs.msg import Twist
from unitree_sdk2py.core.channel import ChannelFactoryInitialize
from unitree_sdk2py.g1.loco.g1_loco_client import LocoClient


class G1CmdVelControl(Node):
    def __init__(self, interface):
        super().__init__('g1_cmdvel_control')
        self.network_interface = interface
        
        # Set critical environment variables
        os.environ['RMW_IMPLEMENTATION'] = 'rmw_cyclonedds_cpp'
        os.environ['CYCLONEDDS_URI'] = f'file://{os.path.expanduser("~")}/g1_control_nav_real/cyclonedds_config.xml'
        
        self.get_logger().info(f"Using DDS config: {os.environ['CYCLONEDDS_URI']}")
        self.get_logger().info(f"Network interface: {interface}")
        
        try:
            self.get_logger().info("Initializing DDS channel...")
            ChannelFactoryInitialize(0, self.network_interface)
            self.get_logger().info("DDS initialized successfully")
        except Exception as e:
            self.get_logger().error(f"DDS init failed: {str(e)}")
            raise RuntimeError("DDS initialization failed")
        
        try:
            self.sport_client = LocoClient()
            self.sport_client.SetTimeout(15.0)
            if not self.sport_client.Init():
                raise RuntimeError("LocoClient Init() returned False")
            self.get_logger().info("LocoClient initialized")

            self.sport_client.Damp()
            self.get_logger().info("Robot in Damp mode, waiting for 1 second")
            time.sleep(2)

            self.sport_client.HighStand()
            self.get_logger().info("Robot in HighStand mode, waiting for 1 second")
            time.sleep(1)
            self.get_logger().info("Robot ready for control!")

            # self.sport_client.Shakehand()
            # time.sleep(3)
            # self.sport_client.Shakehand()
            # time.sleep(1)   
            # self.get_logger().info("Robot shakehand completed")

            self.get_logger().info("Robot ready for cmd_vel control!\r\n")
            time.sleep(1)

        except Exception as e:
            self.get_logger().error(f"Robot control error: {str(e)}")
            raise
        

        # Create a subscription to the cmd_vel topic
        self.subscription = self.create_subscription(
            Twist,
            '/cmd_vel',
            self.cmdvel_callback,
            10
        )

        self.get_logger().info("Initialization is complete, waiting for cmd_vel messages...\r\n")


    def cmdvel_callback(self, msg):
        try:
            vx = msg.linear.x
            vy = msg.linear.y
            wz = msg.angular.z
            
            self.get_logger().info(f"Received cmd_vel: vx={vx:.2f}, vy={vy:.2f}, wz={wz:.2f}")
            # self.sport_client.Move(vx, vy, wz)

        except Exception as e:
            self.get_logger().error(f"Command error: {str(e)}")


def main(args=None):
    rclpy.init(args=args)
    
    if len(sys.argv) < 2:
        print("Usage: python3 g1_control_real_PC2_v2.py <network_interface>")
        print("Example: python3 g1_control_real_PC2_v2.py eth0")
        return
    
    interface = sys.argv[1]
    node = None
    
    try:
        node = G1CmdVelControl(interface)
        rclpy.spin(node)

    except Exception as e:
        print(f"Fatal error: {str(e)}")
        if node:
            node.get_logger().fatal(str(e))

    finally:
        if node:
            node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()

