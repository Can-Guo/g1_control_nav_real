import rospy
import csv
import sys
import select
from geometry_msgs.msg import PoseStamped

class NavGoalPublisher:
    def __init__(self):
        rospy.init_node('nav_goal_publisher', anonymous=True)
        self.goal_pub = rospy.Publisher('/move_base_simple/goal', PoseStamped, queue_size=10)
        
        # Location dictionary
        self.locations = {
            'home': [0.0, 0.0],
            'door': [1.0, 2.0],
            'kitchen': [5.0, 6.0],
            'bedroom': [10.0, 10.0]
        }
        
        # Mode control variables
        self.mode = "keyboard"  # Default mode
        self.auto_goals = []
        self.auto_index = 0
        self.last_goal_time = None

    def publish_goal_from_coords(self, coords):
        """Publish navigation goal from coordinates"""
        goal = PoseStamped()
        goal.header.stamp = rospy.Time.now()
        goal.header.frame_id = "map"
        goal.pose.position.x = coords[0]
        goal.pose.position.y = coords[1]
        goal.pose.position.z = 0.0
        goal.pose.orientation.w = 1.0
        self.goal_pub.publish(goal)
        rospy.loginfo("Published goal at: (%f, %f)", coords[0], coords[1])

    def publish_goal(self, location_name):
        """Publish goal for named location"""
        if location_name in self.locations:
            self.publish_goal_from_coords(self.locations[location_name])
        else:
            rospy.logwarn("Unknown location: %s", location_name)

    def load_auto_goals(self, filename):
        """Load navigation goals from CSV file"""
        self.auto_goals = []
        try:
            with open(filename, 'r') as f:
                reader = csv.reader(f)
                for row in reader:
                    if len(row) >= 2:
                        try:
                            x = float(row[0])
                            y = float(row[1])
                            self.auto_goals.append([x, y])
                        except ValueError:
                            rospy.logwarn("Skipping invalid row: %s", row)
            rospy.loginfo("Loaded %d goals from %s", len(self.auto_goals), filename)
            return True
        except Exception as e:
            rospy.logerr("Failed to load CSV: %s", e)
            return False

    def change_mode(self, new_mode):
        """Switch operation mode"""
        valid_modes = ["keyboard", "audio", "auto_nav"]
        if new_mode in valid_modes:
            self.mode = new_mode
            rospy.loginfo("Switched to %s mode", new_mode)
            
            # Reset auto-nav state when entering this mode
            if new_mode == "auto_nav":
                self.auto_goals = []
                self.auto_index = 0
                self.last_goal_time = None
            return True
        rospy.logwarn("Invalid mode: %s", new_mode)
        return False

    def check_keyboard(self):
        """Check for keyboard input (non-blocking)"""
        if select.select([sys.stdin], [], [], 0)[0]:
            return sys.stdin.readline().strip()
        return None

    def run(self):
        rate = rospy.Rate(10)  # 10Hz
        rospy.loginfo("Starting in keyboard mode. Commands: 'mode <name>', 'quit'")
        
        while not rospy.is_shutdown():
            # Check for keyboard input
            user_input = self.check_keyboard()
            
            if user_input:
                if user_input.startswith("mode "):
                    new_mode = user_input.split()[1]
                    self.change_mode(new_mode)
                elif user_input == "quit":
                    break
                elif self.mode == "keyboard":
                    self.publish_goal(user_input)

            # Handle auto_nav mode processing
            if self.mode == "auto_nav":
                # Load goals if not done
                if not self.auto_goals:
                    rospy.loginfo("Enter CSV filename for auto_nav:")
                    filename = sys.stdin.readline().strip()
                    if not self.load_auto_goals(filename):
                        self.change_mode("keyboard")
                        continue
                
                # Publish next goal if ready
                if self.auto_index < len(self.auto_goals):
                    current_time = rospy.Time.now()
                    if self.last_goal_time is None or (current_time - self.last_goal_time).to_sec() >= 10.0:
                        self.publish_goal_from_coords(self.auto_goals[self.auto_index])
                        self.last_goal_time = current_time
                        self.auto_index += 1
                else:
                    rospy.loginfo("Auto navigation completed")
                    self.change_mode("keyboard")

            rate.sleep()


if __name__ == '__main__':
    try:
        node = NavGoalPublisher()
        node.run()
    except rospy.ROSInterruptException:
        pass


