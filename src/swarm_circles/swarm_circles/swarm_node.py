#!/usr/bin/env python3
import math

import rclpy
from rclpy.node import Node
from rclpy.parameter import Parameter
from rcl_interfaces.msg import ParameterDescriptor, SetParametersResult
from geometry_msgs.msg import Twist
from sensor_msgs.msg import Joy
from std_msgs.msg import String
from std_srvs.srv import Empty
from turtlesim.msg import Pose
from turtlesim.srv import SetPen, Spawn

NAMES = ['turtle1', 'turtle2', 'turtle3', 'turtle4']
COLORS = {'turtle1': (255, 60, 60), 'turtle2': (60, 220, 60), 'turtle3': (70, 120, 255), 'turtle4': (255, 200, 0)}
SPAWN = {'turtle2': (4.0, 5.5), 'turtle3': (7.0, 5.5), 'turtle4': (5.5, 7.5)}   # turtle1 already exists at center

RADIUS_LIMITS = (0.3, 5.0)
SPEED_LIMITS = (0.0, 3.0)
DEFAULTS = {'radius': 2.5, 'angular_speed': 0.8, 'direction': 1}


def wrap(a):
    return math.atan2(math.sin(a), math.cos(a))


def clamp(x, lo, hi):
    return max(lo, min(hi, x))


class SwarmNode(Node):
    def __init__(self):
        super().__init__('swarm_node')
        dyn = ParameterDescriptor(dynamic_typing=True)

        # Parametros

        self.declare_parameter('radius', DEFAULTS['radius'], dyn)
        self.declare_parameter('angular_speed', DEFAULTS['angular_speed'], dyn)
        self.declare_parameter('direction', DEFAULTS['direction'], dyn)

        self.declare_parameter('center_x', 5.544445)
        self.declare_parameter('center_y', 5.544445)
        self.declare_parameter('kp', 2.0)            # position gain
        self.declare_parameter('kw', 6.0)            # heading gain
        self.declare_parameter('max_linear', 6.0)
        self.declare_parameter('rate', 50.0)

        self.add_on_set_parameters_callback(self._validate)

        self.poses = {}
        self.pubs = {}
        for n in NAMES:
            self.pubs[n] = self.create_publisher(Twist, f'/{n}/cmd_vel', 10)
            self.create_subscription(
                Pose, f'/{n}/pose', lambda m, n=n: self.poses.__setitem__(n, m), 10)

        self.phase = 0.0
        self.axes = (0.0, 0.0)
        self.prev_buttons = []

        self.create_subscription(Joy, '/joy', self._on_joy, 10)
        self.create_subscription(String, '/swarm/command', self._on_command, 10)
        self.clear_cli = self.create_client(Empty, '/clear')

        self._setup_turtles()

        dt = 1.0 / self.get_parameter('rate').value
        self.dt = dt
        self.create_timer(dt, self._loop)
        self.get_logger().info('Swarm ready. Use params, /joy, or the keyboard_node.')

    # ---------- setup ----------
    def _setup_turtles(self):
        spawn = self.create_client(Spawn, '/spawn')
        while not spawn.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('Waiting for turtlesim /spawn ...')

        self._set_pen('turtle1')
        for name, (x, y) in SPAWN.items():
            req = Spawn.Request(x=x, y=y, theta=0.0, name=name)
            fut = spawn.call_async(req)
            fut.add_done_callback(lambda f, name=name: self._set_pen(name))

    def _set_pen(self, name):
        cli = self.create_client(SetPen, f'/{name}/set_pen')
        if not cli.wait_for_service(timeout_sec=2.0):
            return
        r, g, b = COLORS[name]
        cli.call_async(SetPen.Request(r=r, g=g, b=b, width=2, off=0))

    # ---------- parameters ----------
    def _validate(self, params):
        for p in params:
            try:
                if p.name == 'radius' and not RADIUS_LIMITS[0] <= float(p.value) <= RADIUS_LIMITS[1]:
                    return SetParametersResult(
                        successful=False, reason=f'radius must be in {RADIUS_LIMITS}')
                if p.name == 'angular_speed' and not SPEED_LIMITS[0] <= float(p.value) <= SPEED_LIMITS[1]:
                    return SetParametersResult(
                        successful=False, reason=f'angular_speed must be in {SPEED_LIMITS}')
                if p.name == 'direction' and int(p.value) not in (1, -1):
                    return SetParametersResult(
                        successful=False, reason='direction must be 1 (CCW) or -1 (CW)')
            except (TypeError, ValueError):
                return SetParametersResult(successful=False, reason='bad value type')
        return SetParametersResult(successful=True)

    def _get(self, name):
        return self.get_parameter(name).value

    def _bump(self, name, delta, limits):
        new = clamp(float(self._get(name)) + delta, *limits)
        self.set_parameters([Parameter(name, Parameter.Type.DOUBLE, new)])

    def _flip(self):
        new = -int(self._get('direction'))
        self.set_parameters([Parameter('direction', Parameter.Type.INTEGER, new)])
        self.get_logger().info('Direction: ' + ('CCW' if new == 1 else 'CW'))

    def _reset(self):
        self.set_parameters([
            Parameter('radius', Parameter.Type.DOUBLE, DEFAULTS['radius']),
            Parameter('angular_speed', Parameter.Type.DOUBLE, DEFAULTS['angular_speed']),
            Parameter('direction', Parameter.Type.INTEGER, DEFAULTS['direction']),
        ])

    def _clear(self):
        if self.clear_cli.service_is_ready():
            self.clear_cli.call_async(Empty.Request())

    # ---------- inputs ----------
    def _on_command(self, msg):
        cmd = msg.data.strip().lower()
        if cmd == 'radius+':
            self._bump('radius', 0.25, RADIUS_LIMITS)
        elif cmd == 'radius-':
            self._bump('radius', -0.25, RADIUS_LIMITS)
        elif cmd == 'speed+':
            self._bump('angular_speed', 0.1, SPEED_LIMITS)
        elif cmd == 'speed-':
            self._bump('angular_speed', -0.1, SPEED_LIMITS)
        elif cmd == 'flip':
            self._flip()
        elif cmd == 'clear':
            self._clear()
        elif cmd == 'reset':
            self._reset()

    # ---------- control ----------
    def _loop(self):
        # continuous gamepad adjustment (stick up = increase)
        if self.axes[0]:
            self._bump('radius', self.axes[0] * 2.0 * self.dt, RADIUS_LIMITS)
        if self.axes[1]:
            self._bump('angular_speed', self.axes[1] * 1.5 * self.dt, SPEED_LIMITS)

        R = float(self._get('radius'))
        w = float(self._get('angular_speed'))
        d = int(self._get('direction'))
        cx, cy = self._get('center_x'), self._get('center_y')
        kp, kw, vmax = self._get('kp'), self._get('kw'), self._get('max_linear')

        self.phase += d * w * self.dt

        for i, name in enumerate(NAMES):
            pose = self.poses.get(name)
            if pose is None:
                continue
            a = self.phase + i * 2.0 * math.pi / len(NAMES)

            # virtual target position and velocity
            tx, ty = cx + R * math.cos(a), cy + R * math.sin(a)
            tvx, tvy = -d * w * R * math.sin(a), d * w * R * math.cos(a)

            # desired velocity = feedforward + position correction
            dvx = tvx + kp * (tx - pose.x)
            dvy = tvy + kp * (ty - pose.y)
            speed = math.hypot(dvx, dvy)

            cmd = Twist()
            if speed > 1e-3:
                err = wrap(math.atan2(dvy, dvx) - pose.theta)
                cmd.linear.x = min(vmax, speed * max(0.0, math.cos(err)))
                cmd.angular.z = kw * err
            self.pubs[name].publish(cmd)


def main():
    rclpy.init()
    node = SwarmNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()
