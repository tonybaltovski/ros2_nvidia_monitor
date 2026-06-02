ARG ROS_DISTRO=jazzy
FROM ros:${ROS_DISTRO}

SHELL ["/bin/bash", "-c"]

WORKDIR /ros_ws/src/nvidia_monitor
COPY . .

WORKDIR /ros_ws
RUN pip install --no-cache-dir --break-system-packages pynvml && \
    source /opt/ros/${ROS_DISTRO}/setup.bash && \
    rosdep install --from-paths src --ignore-src -r -y --skip-keys="python3-pynvml" && \
    colcon build --packages-select nvidia_monitor

COPY docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
CMD ["ros2", "launch", "nvidia_monitor", "nvidia_monitor.launch.py"]
