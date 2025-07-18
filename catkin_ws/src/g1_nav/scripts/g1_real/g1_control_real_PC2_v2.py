import time
import rclpy
import sys
from rclpy.node import Node
from geometry_msgs.msg import Twist
from unitree_sdk2py.core.channel import ChannelFactoryInitialize
from unitree_sdk2py.g1.loco.g1_loco_client import LocoClient

class G1CmdVelControl(Node):
    def __init__(self, interface):
        super().__init__('g1_cmdvel_control')
        
        # Store interface name
        self.network_interface = interface
        
        try:
            # Initialize DDS channel
            self.get_logger().info(f"Initializing DDS on interface: {self.network_interface}")
            ChannelFactoryInitialize(0, self.network_interface)
            self.get_logger().info("DDS channel initialized successfully")
        except Exception as e:
            self.get_logger().error(f"Failed to initialize DDS: {str(e)}")
            self.get_logger().error("Check network interface and CycloneDDS installation")
            raise RuntimeError("DDS initialization failed")
        
        try:
            # Initialize LocoClient
            self.sport_client = LocoClient()
            self.sport_client.SetTimeout(10.0)
            if not self.sport_client.Init():
                raise RuntimeError("LocoClient Init() returned False")
            self.get_logger().info("LocoClient initialized")
        except Exception as e:
            self.get_logger().error(f"Failed to initialize LocoClient: {str(e)}")
            raise RuntimeError("LocoClient initialization failed")
        
        try:
            # Put robot in standing position
            self.sport_client.HighStand()
            time.sleep(1)
            self.get_logger().info("Robot in HighStand mode")
        except Exception as e:
            self.get_logger().error(f"Failed to set HighStand: {str(e)}")
        
        # Create cmd_vel subscription
        self.subscription = self.create_subscription(
            Twist,
            '/cmd_vel',
            self.cmdvel_callback,
            10
        )

    def cmdvel_callback(self, msg):
        try:
            vx = msg.linear.x
            vy = msg.linear.y
            wz = msg.angular.z
            
            self.get_logger().info(f"Received cmd_vel: vx={vx:.2f}, vy={vy:.2f}, wz={wz:.2f}")
            
            # Uncomment to send actual commands
            # self.sport_client.Move(vx, vy, wz)
        except Exception as e:
            self.get_logger().error(f"Error in cmdvel_callback: {str(e)}")

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
        if node:
            node.get_logger().error(f"Fatal error: {str(e)}")
        else:
            print(f"Fatal error before node creation: {str(e)}")
    finally:
        if node:
            node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()

    