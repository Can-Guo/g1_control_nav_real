// g1_imu_server.cpp
#include <yaml-cpp/yaml.h>
#include <websocketpp/config/asio_no_tls.hpp>
#include <websocketpp/server.hpp>
#include <unitree/robot/channel/channel_subscriber.hpp>
#include <unitree/idl/hg/LowState_.hpp>
#include <mutex>
#include <thread>
#include <atomic>

using namespace unitree::robot;
using namespace unitree::common;
namespace asio = boost::asio;

// WebSocket server setup
typedef websocketpp::server<websocketpp::config::asio> server;
server ws_server;
std::mutex connection_mutex;
std::set<websocketpp::connection_hdl, std::owner_less<websocketpp::connection_hdl>> connections;
std::atomic<bool> server_running{true};

// IMU data storage
struct ImuData {
    std::array<float, 3> rpy;
    std::array<float, 3> omega;
};
std::mutex imu_mutex;
ImuData current_imu;

// DDS LowState Handler
void LowStateHandler(const void* message) {
    auto low_state = *(const unitree_hg::msg::dds_::LowState_*)message;
    
    // Extract IMU data
    ImuData new_data;
    new_data.rpy = low_state.imu_state().rpy();
    new_data.omega = low_state.imu_state().gyroscope();
    
    // Update current IMU state
    {
        std::lock_guard<std::mutex> lock(imu_mutex);
        current_imu = new_data;
    }
}

// WebSocket server handlers
void on_open(websocketpp::connection_hdl hdl) {
    std::lock_guard<std::mutex> lock(connection_mutex);
    connections.insert(hdl);
}

void on_close(websocketpp::connection_hdl hdl) {
    std::lock_guard<std::mutex> lock(connection_mutex);
    connections.erase(hdl);
}

// Send IMU data to all connected clients
void broadcast_imu_data() {
    std::lock_guard<std::mutex> lock(imu_mutex);
    std::ostringstream ss;
    ss << current_imu.rpy[0] << "," 
       << current_imu.rpy[1] << ","
       << current_imu.rpy[2] << ","
       << current_imu.omega[0] << ","
       << current_imu.omega[1] << ","
       << current_imu.omega[2];
    
    std::string payload = ss.str();
    
    std::lock_guard<std::mutex> conn_lock(connection_mutex);
    for (auto& hdl : connections) {
        ws_server.send(hdl, payload, websocketpp::frame::opcode::text);
    }
}

int main(int argc, char* argv[]) {
    if (argc < 2) {
        std::cerr << "Usage: " << argv[0] << " <network_interface>" << std::endl;
        return 1;
    }

    // Initialize DDS
    ChannelFactory::Instance()->Init(0, argv[1]);
    auto lowstate_sub = std::make_shared<ChannelSubscriber<unitree_hg::msg::dds_::LowState_>>("rt/lowstate");
    lowstate_sub->InitChannel(LowStateHandler, 1);

    // Configure WebSocket server
    ws_server.set_open_handler(&on_open);
    ws_server.set_close_handler(&on_close);
    ws_server.init_asio();
    ws_server.listen(9002);
    ws_server.start_accept();

    // Start WebSocket thread
    std::thread ws_thread([&]() {
        ws_server.run();
    });

    // Main loop: Broadcast IMU data at 100Hz
    while (server_running) {
        broadcast_imu_data();
        std::this_thread::sleep_for(std::chrono::milliseconds(10));
    }

    // Cleanup
    ws_server.stop();
    ws_thread.join();
    return 0;
}



