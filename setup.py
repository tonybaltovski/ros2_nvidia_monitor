from setuptools import setup

package_name = 'nvidia_monitor'

setup(
    name=package_name,
    version='0.1.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/launch', ['launch/nvidia_monitor.launch.py']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Tony Baltovski',
    maintainer_email='tony@example.com',
    description='ROS 2 node that publishes NVIDIA GPU telemetry as diagnostic messages.',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'nvidia_monitor = nvidia_monitor.nvidia_monitor_node:main',
        ],
    },
)
