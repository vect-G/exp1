# README 中文版（中英对照）

本文件是 [`README.md`](/home/wl/exp1_ws/src/visualize/scripts/README.md) 的中文整理版，采用中文主导、英文辅助的沉浸式翻译写法。  
This file is a Chinese-friendly bilingual rewrite of the original `README.md`.

说明：下面的命令、路径、包名和文件名均保持与原文一致。  
Note: Commands, paths, package names, and file names are kept the same as in the original document.

## 1. 配置 ROS2 环境 / Source ROS2 Environment

每次新开终端时，先执行下面的命令。  
Execute the command below whenever you start a new terminal.

```bash
source /opt/ros/humble/setup.bash
```

或者，把它写进 `~/.bashrc`，以后终端启动时会自动加载。  
Or add it to `~/.bashrc` so it is sourced automatically.

1. 用你习惯的方式打开 `~/.bashrc`。  
   Open `~/.bashrc` in any way you like.
2. 在文件末尾加入下面这一行：  
   Add the following line to the end of the file:

   ```bash
   source /opt/ros/humble/setup.bash
   ```

3. 让配置立即生效：  
   Source `~/.bashrc`.

   ```bash
   source ~/.bashrc
   ```

## 2. 创建工作区和功能包 / Create a Workspace and a Package

参考资料 / References:  
<https://docs.ros.org/en/humble/Tutorials/Beginner-Client-Libraries/Creating-A-Workspace/Creating-A-Workspace.html>  
<https://docs.ros.org/en/humble/Tutorials/Beginner-Client-Libraries/Creating-Your-First-ROS2-Package.html>

1. 创建工作区。  
   Create a workspace.

   ```bash
   mkdir -p ~/exp1_ws/src
   cd ~/exp1_ws/src
   ```

2. 创建名为 `visualize` 的功能包。  
   Create a package named `visualize`.

   ```bash
   ros2 pkg create --build-type ament_cmake visualize
   ```

## 3. 下载 launch 文件和机器人描述 / Download Launch File and Robot Description

1. 下载相关文件。  
   Download the related files.

   说明：原始 README 在这里没有给出具体下载链接，你可以根据课程材料、仓库说明或老师提供的资源补齐。  
   Note: The original README does not provide a concrete download link here.

2. 你的工作区目录结构应类似如下：  
   The workspace should look like this:

   ```text
   exp1_ws/
       src/
           visualize/
               include/
               launch/
                   rviz_vis.launch.py
               robot_description/
                   ur3/
                       meshes/
                       ur3.xacro
               scripts/
                   rviz_visualize.py
               CMakeLists.txt
               package.xml
   ```

3. 编辑 `CMakeLists.txt`，加入以下内容。  
   Edit `CMakeLists.txt` and add the following lines.

   ```cmake
   find_package(ament_cmake_python REQUIRED)
   find_package(rclcpp REQUIRED)
   find_package(rclpy REQUIRED)

   install(DIRECTORY launch robot_description
     DESTINATION share/${PROJECT_NAME})

   install(PROGRAMS
     scripts/rviz_visualize.py
     DESTINATION lib/${PROJECT_NAME}
   )
   ```

4. 安装依赖。  
   Install dependencies.

   ```bash
   sudo apt install python3-colcon-common-extensions
   sudo apt install ros-humble-xacro
   sudo apt install ros-humble-joint-state-publisher
   ```

5. 编译工作区并重新加载环境。  
   Build the workspace and source it.

   ```bash
   cd ~/exp1_ws
   colcon build
   source install/setup.bash
   ```

## 4. 任务 1：可视化 UR3 的 URDF 模型 / Task 1: Visualize UR3 URDF Model

1. 启动 `rviz2`。  
   Launch `rviz2`.

   ```bash
   ros2 launch visualize rviz_vis.launch.py
   ```

2. 在 `rviz2` 中添加并设置以下内容。  
   Add the following displays/settings in `rviz2`.

   - `Global Options` -> `Fixed Frame`: `/visualize/base_link`
   - `Add` -> `By display type` -> `TF`
   - `Add` -> `By display type` -> `RobotModel`
   - `RobotModel` -> `Description Topic`: `/visualize/robot_description`
   - `TF Prefix`: `visualize`

3. 可视化 TF 树。  
   Visualize the TF tree.

   ```bash
   sudo apt-get install ros-humble-rqt-tf-tree
   ros2 run rqt_tf_tree rqt_tf_tree --force-discover
   ```

现在你应该能在 `rviz2` 中看到虚拟机械臂以及对应的坐标系。  
Now you should be able to see a virtual robot and its corresponding frames in `rviz2`.

## 5. 任务 2：发布 `JointState` 消息并驱动机械臂 / Task 2: Publish JointState Message and Move the Robot

1. 编辑 `scripts/rviz_visualize.py` 中的 `init` 和 `publish_robot_joint_states` 函数。  
   Edit the `init` and `publish_robot_joint_states` functions in `scripts/rviz_visualize.py`.

   提示：你需要编写一个发布器，发送关节状态消息 `sensor_msgs.msg.JointState`。这里要先弄清楚 URDF 模型中的关节名称，然后再发送对应的关节位置。对于 `ur3`，它有 6 个关节，你可以参考 `ur3.xacro` 来查找这些关节名。  
   Hint: Write a publisher that sends `sensor_msgs.msg.JointState`. You need the joint names from the URDF model so you can publish the corresponding joint positions. For `ur3`, there are 6 joints, and you can refer to `ur3.xacro` to find their names.

2. 重新编译工作区。  
   Build the workspace again.

   ```bash
   cd ~/exp1_ws
   colcon build
   source install/setup.bash
   ```

3. 运行 `rviz_visualize.py`。  
   Run `rviz_visualize.py`.

   ```bash
   ros2 run visualize rviz_visualize.py
   ```

## 6. 任务 3：查询 TF2 变换并发布 Marker / Task 3: Lookup TF2 Transform and Publish a Marker

1. 编辑 `scripts/rviz_visualize.py` 中的 `init` 和 `publish_marker` 函数。  
   Edit the `init` and `publish_marker` functions in `scripts/rviz_visualize.py`.

   提示：你需要在 `init` 中创建 TF buffer 和 listener，使用 `lookupTransform` 获取从 `wrist_3_link` 到 `base_link` 的坐标变换；然后定义 marker 的位置、尺寸和颜色，类型为 `visualization_msgs.msg.Marker`，最后把消息发布出去。  
   Hint: Create a TF buffer and listener in `init`, use `lookupTransform` to get the transform from `wrist_3_link` to `base_link`, define the marker's position/scale/color using `visualization_msgs.msg.Marker`, and publish the message.

2. 重新编译工作区。  
   Build the workspace again.

   ```bash
   cd ~/exp1_ws
   colcon build
   ```

3. 在 `rviz` 中添加 Marker 对应的话题，然后运行 `rviz_visualize.py`。  
   Add the Marker topic in `rviz`, then run `rviz_visualize.py`.

   ```bash
   ros2 run visualize rviz_visualize.py
   ```
