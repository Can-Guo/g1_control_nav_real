#include <websocketpp/config/asio_no_tls_client.hpp>
#include <websocketpp/client.hpp>
#include <iostream>
#include <cstdio>

typedef websocketpp::client<websocketpp::config::asio_client> client;

class IMUClient {
public:
    IMUClient() : m_open(false) {
        m_client.set_access_channels(websocketpp::log::alevel::none);
        m_client.set_error_channels(websocketpp::log::elevel::none);
        
        m_client.init_asio();
        m_client.set_open_handler([this](auto hdl) {
            m_open = true;
            std::cout << "Connected to IMU server" << std::endl;
        });
        
        m_client.set_close_handler([this](auto hdl) {
            m_open = false;
            std::cout << "Disconnected from server" << std::endl;
        });
        
        m_client.set_message_handler([this](auto hdl, auto msg) {
            process_message(msg->get_payload());
        });
    }
    
    void connect(const std::string& uri) {
        websocketpp::lib::error_code ec;
        client::connection_ptr con = m_client.get_connection(uri, ec);
        
        if (ec) {
            std::cerr << "Connection error: " << ec.message() << std::endl;
            return;
        }
        
        m_client.connect(con);
        
        try {
            m_client.run();
        } catch (const std::exception& e) {
            std::cerr << "Client runtime error: " << e.what() << std::endl;
        }
    }
    
    void process_message(const std::string& payload) {
        float rpy[3], omega[3];
        if (sscanf(payload.c_str(), "%f,%f,%f,%f,%f,%f", 
                   &rpy[0], &rpy[1], &rpy[2],
                   &omega[0], &omega[1], &omega[2]) == 6) {
            
            printf("\rIMU: RPY=[%6.3f, %6.3f, %6.3f] Omega=[%6.3f, %6.3f, %6.3f]",
                   rpy[0], rpy[1], rpy[2],
                   omega[0], omega[1], omega[2]);
            fflush(stdout);
        }
    }

private:
    client m_client;
    bool m_open;
};

int main(int argc, char* argv[]) {
    if (argc != 2) {
        std::cerr << "Usage: " << argv[0] << " <server_ip>" << std::endl;
        return 1;
    }
    
    std::string uri = "ws://" + std::string(argv[1]) + ":9009";
    
    IMUClient client;
    client.connect(uri);
    return 0;
}

