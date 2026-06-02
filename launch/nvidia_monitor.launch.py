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

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration, PythonExpression
from launch_ros.actions import Node


def generate_launch_description():
    namespace = LaunchConfiguration('namespace')
    namespace_diagnostics = LaunchConfiguration('namespace_diagnostics')
    update_period = LaunchConfiguration('update_period')
    temperature_warn = LaunchConfiguration('temperature_warn')
    temperature_error = LaunchConfiguration('temperature_error')
    memory_warn = LaunchConfiguration('memory_warn')
    memory_error = LaunchConfiguration('memory_error')
    power_warn = LaunchConfiguration('power_warn')
    power_error = LaunchConfiguration('power_error')
    power_ratio_warn = LaunchConfiguration('power_ratio_warn')
    power_ratio_error = LaunchConfiguration('power_ratio_error')

    return LaunchDescription(
        [
            DeclareLaunchArgument('namespace', default_value=''),
            DeclareLaunchArgument(
                'namespace_diagnostics',
                default_value='false',
                description='If true, apply the namespace to the /diagnostics topic.',
            ),
            DeclareLaunchArgument('update_period', default_value='1.0'),
            DeclareLaunchArgument('temperature_warn', default_value='80.0'),
            DeclareLaunchArgument('temperature_error', default_value='95.0'),
            DeclareLaunchArgument('memory_warn', default_value='0.85'),
            DeclareLaunchArgument('memory_error', default_value='0.95'),
            DeclareLaunchArgument('power_warn', default_value='0.0'),
            DeclareLaunchArgument('power_error', default_value='0.0'),
            DeclareLaunchArgument('power_ratio_warn', default_value='0.90'),
            DeclareLaunchArgument('power_ratio_error', default_value='1.00'),
            Node(
                package='nvidia_monitor',
                executable='nvidia_monitor',
                name='nvidia_monitor',
                namespace=namespace,
                output='screen',
                remappings=[
                    (
                        '/diagnostics',
                        PythonExpression(
                            [
                                "'diagnostics' if '",
                                namespace_diagnostics,
                                "'.lower() in ('true', '1') else '/diagnostics'",
                            ]
                        ),
                    )
                ],
                parameters=[
                    {
                        'update_period': update_period,
                        'temperature_warn': temperature_warn,
                        'temperature_error': temperature_error,
                        'memory_warn': memory_warn,
                        'memory_error': memory_error,
                        'power_warn': power_warn,
                        'power_error': power_error,
                        'power_ratio_warn': power_ratio_warn,
                        'power_ratio_error': power_ratio_error,
                    }
                ],
            ),
        ]
    )
