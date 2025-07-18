#include <chrono>
#include <iostream>
#include <thread>
#include <unitree/robot/g1/loco/g1_loco_api.hpp>
#include <unitree/robot/g1/loco/g1_loco_client.hpp>
// ROS2 includes
#include "rclcpp/rclcpp.hpp"
#include "geometry_msgs/msg/twist.hpp"


lass G1RealNavNode : public rclcpp::Node {
public:
    G1RealNavNode(const std::string& network_interface)
        : Node("g1_real_nav_node"), vx_(0.0f), vy_(0.0f), omega_(0.0f)
    {
        // 初始化Unitree底盘SDK
        unitree::robot::ChannelFactory::Instance()->Init(0, network_interface);
        client_ = std::make_shared<unitree::robot::g1::LocoClient>();
        client_->Init();
        client_->SetTimeout(10.f);

        // bool flag;
        // client_->SwitchMoveMode(flag);
        client_->StopMove();

        client_->ShakeHand(0);
        RCLCPP_INFO(this->get_logger(), "Shake hand starts!");
        std::this_thread::sleep_for(std::chrono::seconds(3));
        client_->ShakeHand(1);
        RCLCPP_INFO(this->get_logger(), "Shake hand ends!");

        // 订阅/cmd_vel
        cmd_vel_sub_ = this->create_subscription<geometry_msgs::msg::Twist>(
            "/cmd_vel", 10,
            std::bind(&G1RealNavNode::cmdVelCallback, this, std::placeholders::_1)
        );

        RCLCPP_INFO(this->get_logger(), "G1RealNavNode initialized, waiting for /cmd_vel...");
    }

private:
    void cmdVelCallback(const geometry_msgs::msg::Twist::SharedPtr msg)
    {
        vx_ = static_cast<float>(msg->linear.x);
        vy_ = static_cast<float>(msg->linear.y);
        omega_ = static_cast<float>(msg->angular.z);

        // 控制底盘
        // client_->Move(vx_, vy_, omega_);
        RCLCPP_INFO(this->get_logger(), "Set velocity: vx=%.2f, vy=%.2f, omega=%.2f", vx_, vy_, omega_);
    }

    std::shared_ptr<unitree::robot::g1::LocoClient> client_;
    rclcpp::Subscription<geometry_msgs::msg::Twist>::SharedPtr cmd_vel_sub_;
    float vx_, vy_, omega_;
};



int main(int argc, char const *argv[]) {

    rclcpp::init(argc, argv);
    std::string network_interface = "eth0"; // 根据实际情况设置网卡名
    auto node = std::make_shared<G1RealNavNode>(network_interface);
    rclcpp::spin(node);
    rclcpp::shutdown();
    return 0;

    // std::map<std::string, std::string> args = {{"network_interface", "lo"}};

    // unitree::robot::ChannelFactory::Instance()->Init(0, args["network_interface"]);
    // unitree::robot::g1::LocoClient client;

    // client.Init();
    // client.SetTimeout(10.f);

    // float vx = 0.0f, vy = 0.0f, omega = 0.0f, duration = 0.0f;


    // bool flag;
    // client.SwitchMoveMode(flag);
    
    // client.StopMove();


    // client.ShakeHand(0);
    // std::cout << "Shake hand starts! Waiting for 10 s for ending" << std::endl;
    // std::this_thread::sleep_for(std::chrono::seconds(3));

    // client.ShakeHand(1);
    // std::cout << "Shake hand ends!" << std::endl;



    // client.SetVelocity(vx, vy, omega, duration);
    // std::cout << "set velocity to " << vx << ", " << vy << ", " << omega << std::endl;


    // // client.Move(vx, vy, omega);

    // std::this_thread::sleep_for(std::chrono::seconds(5));
    // client.WaveHand();
    // std::this_thread::sleep_for(std::chrono::seconds(1));
    // std::cout << "Wave hand ends!" << std::endl;




    // std::cout << "Done!" << std::endl;

    // return 0;



}