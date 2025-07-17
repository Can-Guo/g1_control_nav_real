cmake_minimum_required(VERSION 3.0.2)
project(g1_nav)

# 添加编译选项
set(CMAKE_CXX_STANDARD 14)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

# 设置构建类型
if(NOT CMAKE_BUILD_TYPE)
  set(CMAKE_BUILD_TYPE Release)
endif()

# 查找依赖包
find_package(catkin REQUIRED COMPONENTS
  roscpp
  nav_msgs
  geometry_msgs
  tf2
  tf2_ros
  robot_localization
)

# 添加包含路径
include_directories(
  include
  ${catkin_INCLUDE_DIRS}
  ${CMAKE_SOURCE_DIR}/../../unitree_sdk2/thirdparty/include
  ${CMAKE_SOURCE_DIR}/../../unitree_sdk2/thirdparty/include/ddscxx
  ${CMAKE_SOURCE_DIR}/../../unitree_sdk2/thirdparty/include/ddsc
  ${CMAKE_SOURCE_DIR}/../../unitree_sdk2/include
)

# 添加库路径
link_directories(
  ${CMAKE_SOURCE_DIR}/../../unitree_sdk2/lib/x86_64
  ${CMAKE_SOURCE_DIR}/../../unitree_sdk2/thirdparty/lib/x86_64
)

# 声明catkin包
catkin_package(
  INCLUDE_DIRS include
  LIBRARIES ${PROJECT_NAME}
  CATKIN_DEPENDS roscpp nav_msgs geometry_msgs tf2 tf2_ros robot_localization
)

install(DIRECTORY config launch rviz
  DESTINATION ${CATKIN_PACKAGE_SHARE_DESTINATION}
)

# 输出配置信息
message(STATUS "")
message(STATUS "Configuring ${PROJECT_NAME}")
message(STATUS "CMake version: ${CMAKE_VERSION}")
message(STATUS "Build type: ${CMAKE_BUILD_TYPE}")
message(STATUS "C++ Standard: ${CMAKE_CXX_STANDARD}")
message(STATUS "Unitree SDK: ${CMAKE_SOURCE_DIR}/../../unitree_sdk2")
message(STATUS "")
