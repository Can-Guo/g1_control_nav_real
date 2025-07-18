import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
import unitree_sdk2py as sdk2  # 需 pip 安装或源码编译


class G1CmdVelControl(Node):
    def __init__(self):
        super().__init__('g1_cmdvel_control')
        self.subscription = self.create_subscription(
            Twist,
            '/cmd_vel',
            self.cmdvel_callback,
            10)
        # 初始化SDK2底盘控制
        self.robot = sdk2.Robot()
        self.robot.connect()
        self.get_logger().info("Unitree SDK2 connected.")


    def cmdvel_callback(self, msg):
        # ROS2 Twist消息转SDK2底盘速度
        vx = msg.linear.x
        vy = msg.linear.y
        wz = msg.angular.z

        # 发送速度指令
        # self.robot.send_chassis_cmd(vx, vy, wz)
        self.get_logger().info(f"Send G1 cmd velocity:\tvx={vx:.2f},\tvy={vy:.2f},\twz={wz:.2f}")


def main(args=None):
    rclpy.init(args=args)
    node = G1CmdVelControl()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()