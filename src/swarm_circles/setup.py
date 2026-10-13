import os
from glob import glob
from setuptools import setup

package_name = 'swarm_circles'

setup(
    name=package_name,
    version='0.1.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.py')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='you',
    maintainer_email='you@example.com',
    description='TurtleSwarm',
    license='MIT',
    entry_points={
        'console_scripts': [
            'swarm_node = swarm_circles.swarm_node:main',
            'keyboard_node = swarm_circles.keyboard_node:main',
        ],
    },
)
