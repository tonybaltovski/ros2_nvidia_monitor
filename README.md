# ros2_nvidia_monitor

ROS 2 node that polls NVIDIA GPUs via NVML and republishes telemetry on
`/diagnostics` using `diagnostic_updater`.

## Per-GPU metrics

- Temperature (C)
- GPU / memory utilization (%)
- Memory used / free / total (MiB) and percent used
- Power draw and power limit (W)
- Fan speed (%)
- SM / memory / graphics clocks (MHz)
- Compute and graphics process counts
- Name, UUID, serial, driver version

## Parameters

| Name | Default | Description |
| --- | --- | --- |
| `update_period` | `1.0` | Diagnostic publish period (s). |
| `temperature_warn` | `80.0` | WARN threshold (C). |
| `temperature_error` | `95.0` | ERROR threshold (C). |
| `memory_warn` | `0.85` | WARN threshold (fraction of total VRAM). |
| `memory_error` | `0.95` | ERROR threshold (fraction of total VRAM). |
| `power_warn` | `0.0` | WARN threshold on raw power draw (W). `0` disables. |
| `power_error` | `0.0` | ERROR threshold on raw power draw (W). `0` disables. |
| `power_ratio_warn` | `0.90` | WARN threshold (fraction of power limit). |
| `power_ratio_error` | `1.00` | ERROR threshold (fraction of power limit). |

## Dependencies

> **Note:** The proprietary NVIDIA driver must be installed and loaded on the
> host (verify with `nvidia-smi`). This package talks to the GPU via NVML; the
> open-source `nouveau` driver is not supported.

## Build & run

```bash
rosdep install --from-paths src --ignore-src -r -y
colcon build --packages-select nvidia_monitor
source install/setup.bash
ros2 launch nvidia_monitor nvidia_monitor.launch.py
```

### Launch arguments

| Argument | Default | Description |
| --- | --- | --- |
| `namespace` | `''` | ROS namespace for the node. |
| `namespace_diagnostics` | `false` | When `true`, remap `/diagnostics` into the namespace. |

```bash
ros2 launch nvidia_monitor nvidia_monitor.launch.py namespace:=gpu0 namespace_diagnostics:=true
```

## Docker

Pre-built images are available from GitHub Container Registry:

```bash
docker pull ghcr.io/tonybaltovski/ros2_nvidia_monitor:jazzy
docker pull ghcr.io/tonybaltovski/ros2_nvidia_monitor:rolling
```

### docker compose

```bash
# Default (jazzy)
docker compose up -d

# Override ROS distro
ROS_DISTRO=rolling PYNVML_INSTALL=pip docker compose up -d --build
```

All parameters are configurable via environment variables (see `docker-compose.yml`):

```bash
UPDATE_PERIOD=2.0 TEMPERATURE_WARN=75.0 docker compose up -d
```

> **Note:** Requires the [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html)
> on the host.

## View

```bash
# sudo apt install ros-${ROS_DISTRO}-rqt-runtime-monitor, if not installed (requires a desktop environment).
ros2 run rqt_runtime_monitor rqt_runtime_monitor
```
