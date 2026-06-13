# Copyright 2026 Tony Baltovski
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Publish NVIDIA GPU telemetry via diagnostic_updater."""

import contextlib

from diagnostic_msgs.msg import DiagnosticStatus
from diagnostic_updater import Updater
import rclpy
from rclpy.node import Node

try:
    import pynvml
except ImportError as exc:  # pragma: no cover
    raise ImportError(
        'pynvml is required. Install with `sudo apt install python3-pynvml`.'
    ) from exc


def _nvml_str(value):
    return value.decode('utf-8') if isinstance(value, bytes) else value


class NvidiaMonitor(Node):

    def __init__(self):
        super().__init__('nvidia_monitor')

        self.declare_parameter('update_period', 1.0)
        self.declare_parameter('temperature_warn', 80.0)
        self.declare_parameter('temperature_error', 95.0)
        self.declare_parameter('memory_warn', 0.85)
        self.declare_parameter('memory_error', 0.95)
        self.declare_parameter('power_warn', 0.0)
        self.declare_parameter('power_error', 0.0)
        self.declare_parameter('power_ratio_warn', 0.90)
        self.declare_parameter('power_ratio_error', 1.00)

        self._temp_warn = float(self.get_parameter('temperature_warn').value)
        self._temp_error = float(self.get_parameter('temperature_error').value)
        self._mem_warn = float(self.get_parameter('memory_warn').value)
        self._mem_error = float(self.get_parameter('memory_error').value)
        self._power_warn = float(self.get_parameter('power_warn').value)
        self._power_error = float(self.get_parameter('power_error').value)
        self._power_ratio_warn = float(self.get_parameter('power_ratio_warn').value)
        self._power_ratio_error = float(self.get_parameter('power_ratio_error').value)

        pynvml.nvmlInit()
        self._driver_version = _nvml_str(pynvml.nvmlSystemGetDriverVersion())
        self._device_count = pynvml.nvmlDeviceGetCount()
        self.get_logger().info(
            f'Found {self._device_count} NVIDIA GPU(s); driver {self._driver_version}'
        )

        self._handles = [pynvml.nvmlDeviceGetHandleByIndex(i) for i in range(self._device_count)]

        self._updater = Updater(self)
        self._updater.setHardwareID(f'nvidia_driver_{self._driver_version}')
        for idx, handle in enumerate(self._handles):
            name = _nvml_str(pynvml.nvmlDeviceGetName(handle))
            self._updater.add(
                f'GPU {idx}: {name}',
                lambda stat, h=handle, n=name: self._produce(stat, h, n),
            )

        period = float(self.get_parameter('update_period').value)
        self._updater.period = period
        self._timer = self.create_timer(period, self._updater.update)

    def destroy_node(self):
        with contextlib.suppress(pynvml.NVMLError):
            pynvml.nvmlShutdown()
        return super().destroy_node()

    def _produce(self, stat, handle, name):
        stat.summary(DiagnosticStatus.OK, 'OK')

        stat.add('Name', name)
        stat.add('Driver Version', self._driver_version)

        with contextlib.suppress(pynvml.NVMLError):
            stat.add('Serial', _nvml_str(pynvml.nvmlDeviceGetSerial(handle)))
        with contextlib.suppress(pynvml.NVMLError):
            stat.add('UUID', _nvml_str(pynvml.nvmlDeviceGetUUID(handle)))

        worst_level = DiagnosticStatus.OK
        messages = []

        try:
            temp = pynvml.nvmlDeviceGetTemperature(handle, pynvml.NVML_TEMPERATURE_GPU)
            stat.add('Temperature (C)', f'{temp}')
            if temp >= self._temp_error:
                worst_level = max(worst_level, DiagnosticStatus.ERROR)
                messages.append(f'Temperature critical: {temp} C')
            elif temp >= self._temp_warn:
                worst_level = max(worst_level, DiagnosticStatus.WARN)
                messages.append(f'Temperature high: {temp} C')
        except pynvml.NVMLError as exc:
            stat.add('Temperature (C)', f'N/A ({exc})')

        try:
            util = pynvml.nvmlDeviceGetUtilizationRates(handle)
            stat.add('GPU Utilization (%)', f'{util.gpu}')
            stat.add('Memory Utilization (%)', f'{util.memory}')
        except pynvml.NVMLError as exc:
            stat.add('Utilization', f'N/A ({exc})')

        try:
            mem = pynvml.nvmlDeviceGetMemoryInfo(handle)
            used_mb = mem.used / (1024 * 1024)
            total_mb = mem.total / (1024 * 1024)
            free_mb = mem.free / (1024 * 1024)
            ratio = mem.used / mem.total if mem.total else 0.0
            stat.add('Memory Used (MiB)', f'{used_mb:.1f}')
            stat.add('Memory Free (MiB)', f'{free_mb:.1f}')
            stat.add('Memory Total (MiB)', f'{total_mb:.1f}')
            stat.add('Memory Used (%)', f'{ratio * 100:.1f}')
            if ratio >= self._mem_error:
                worst_level = max(worst_level, DiagnosticStatus.ERROR)
                messages.append(f'Memory critical: {ratio * 100:.1f}%')
            elif ratio >= self._mem_warn:
                worst_level = max(worst_level, DiagnosticStatus.WARN)
                messages.append(f'Memory high: {ratio * 100:.1f}%')
        except pynvml.NVMLError as exc:
            stat.add('Memory', f'N/A ({exc})')

        power_w = None
        try:
            power_w = pynvml.nvmlDeviceGetPowerUsage(handle) / 1000.0
            stat.add('Power (W)', f'{power_w:.2f}')
        except pynvml.NVMLError as exc:
            stat.add('Power (W)', f'N/A ({exc})')

        limit_w = None
        try:
            limit_w = pynvml.nvmlDeviceGetPowerManagementLimit(handle) / 1000.0
            stat.add('Power Limit (W)', f'{limit_w:.2f}')
        except pynvml.NVMLError as exc:
            stat.add('Power Limit (W)', f'N/A ({exc})')

        if power_w is not None:
            if self._power_error > 0.0 and power_w >= self._power_error:
                worst_level = max(worst_level, DiagnosticStatus.ERROR)
                messages.append(f'Power critical: {power_w:.1f} W')
            elif self._power_warn > 0.0 and power_w >= self._power_warn:
                worst_level = max(worst_level, DiagnosticStatus.WARN)
                messages.append(f'Power high: {power_w:.1f} W')

            if limit_w is not None and limit_w > 0.0:
                ratio = power_w / limit_w
                stat.add('Power Used (%)', f'{ratio * 100:.1f}')
                if ratio >= self._power_ratio_error:
                    worst_level = max(worst_level, DiagnosticStatus.ERROR)
                    messages.append(f'Power critical: {ratio * 100:.1f}% of limit')
                elif ratio >= self._power_ratio_warn:
                    worst_level = max(worst_level, DiagnosticStatus.WARN)
                    messages.append(f'Power high: {ratio * 100:.1f}% of limit')

        try:
            fan = pynvml.nvmlDeviceGetFanSpeed(handle)
            stat.add('Fan Speed (%)', f'{fan}')
        except pynvml.NVMLError:
            stat.add('Fan Speed (%)', 'N/A')

        try:
            sm_clock = pynvml.nvmlDeviceGetClockInfo(handle, pynvml.NVML_CLOCK_SM)
            mem_clock = pynvml.nvmlDeviceGetClockInfo(handle, pynvml.NVML_CLOCK_MEM)
            graphics_clock = pynvml.nvmlDeviceGetClockInfo(handle, pynvml.NVML_CLOCK_GRAPHICS)
            stat.add('SM Clock (MHz)', f'{sm_clock}')
            stat.add('Memory Clock (MHz)', f'{mem_clock}')
            stat.add('Graphics Clock (MHz)', f'{graphics_clock}')
        except pynvml.NVMLError as exc:
            stat.add('Clocks', f'N/A ({exc})')

        with contextlib.suppress(pynvml.NVMLError):
            procs = pynvml.nvmlDeviceGetComputeRunningProcesses(handle)
            stat.add('Compute Processes', f'{len(procs)}')
        with contextlib.suppress(pynvml.NVMLError):
            procs = pynvml.nvmlDeviceGetGraphicsRunningProcesses(handle)
            stat.add('Graphics Processes', f'{len(procs)}')

        if messages:
            stat.summary(worst_level, '; '.join(messages))

        return stat


def main(args=None):
    rclpy.init(args=args)
    node = NvidiaMonitor()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
