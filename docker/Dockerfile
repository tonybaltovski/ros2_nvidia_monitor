ARG ROS_DISTRO=jazzy
ARG PYNVML_INSTALL=deb

FROM ros:${ROS_DISTRO} AS base

SHELL ["/bin/bash", "-c"]

WORKDIR /ros_ws/src/nvidia_monitor
COPY . .
WORKDIR /ros_ws

FROM base AS deps-deb
RUN apt-get update && apt-get install -y python3-pynvml && rm -rf /var/lib/apt/lists/*

FROM base AS deps-pip
RUN pip install --no-cache-dir --break-system-packages pynvml

FROM deps-${PYNVML_INSTALL} AS build
ARG ROS_DISTRO
RUN source /opt/ros/${ROS_DISTRO}/setup.bash && \
    rosdep install --from-paths src --ignore-src -r -y --skip-keys="python3-pynvml" && \
    colcon build --packages-select nvidia_monitor

COPY docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
CMD ["ros2", "launch", "nvidia_monitor", "nvidia_monitor.launch.py"]
