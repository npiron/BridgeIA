from __future__ import annotations

import pymunk

from bridgeia.core.bridge import BridgeDesign
from bridgeia.core.level import Level


class PhysicsSimulation:
    def __init__(self, level: Level, bridge: BridgeDesign) -> None:
        self.space = pymunk.Space()
        self.space.gravity = (0, 900)  # Gravity downwards
        self.bodies: dict[str, pymunk.Body] = {}
        self.edge_constraints: dict[int, pymunk.PinJoint] = {}

        self._build_world(level, bridge)

    def _build_world(self, level: Level, bridge: BridgeDesign) -> None:
        # 1. Create Static Terrain (Banks)
        for bank in level.banks:
            segment = pymunk.Segment(
                self.space.static_body,
                (bank.x1, bank.y1),
                (bank.x2, bank.y2),
                4.0,  # Thickness
            )
            segment.friction = 1.0
            segment.elasticity = 0.0
            # Put banks in Group 1 so they don't collide with Bridge Joints (also Group 1)
            # This prevents "explosion" if a joint is placed exactly on the ground line.
            segment.filter = pymunk.ShapeFilter(group=1)
            self.space.add(segment)

        # 2. Create Anchors (Static or Dynamic)
        for anchor in level.anchors:
            body = pymunk.Body(body_type=pymunk.Body.STATIC)
            body.position = (anchor.x, anchor.y)
            shape = pymunk.Circle(body, 5)
            shape.filter = pymunk.ShapeFilter(group=1) # Don't collide with self/bridge
            self.space.add(body, shape)
            self.bodies[anchor.anchor_id] = body

        # 3. Create Bridge Joints (Dynamic)
        joint_mass = 1.0
        joint_radius = 3.0
        joint_moment = pymunk.moment_for_circle(joint_mass, 0, joint_radius)

        for j_id, (x, y) in bridge.joints.items():
            body = pymunk.Body(joint_mass, joint_moment)
            body.position = (x, y)
            shape = pymunk.Circle(body, joint_radius)
            shape.elasticity = 0.0
            shape.friction = 0.5
            shape.filter = pymunk.ShapeFilter(group=1)
            self.space.add(body, shape)
            self.bodies[j_id] = body
            
        self.space.damping = 0.9

        # 4. Create Edges (Constraints)
        for edge in bridge.edges:
            body_a = self.bodies.get(edge.a)
            body_b = self.bodies.get(edge.b)
            
            if body_a and body_b:
                # Revert to PinJoint for stability.
                # DampedSpring was too chaotic.
                pin = pymunk.PinJoint(body_a, body_b)
                # pin.collide_bodies = False
                self.space.add(pin)
                self.edge_constraints[edge.edge_id] = pin

    def step(self, dt: float) -> None:
        # Increase sub-steps for stability?
        steps = 5
        dt_step = dt / steps
        for _ in range(steps):
            self.space.step(dt_step)

    def get_joint_position(self, joint_id: str) -> tuple[float, float] | None:
        body = self.bodies.get(joint_id)
        if body:
            return body.position.x, body.position.y # type: ignore
        return None

    def get_edge_stresses(self) -> dict[int, float]:
        """
        Returns a dictionary mapping edge_id to its current stress.
        With PinJoint, we only get impulse magnitude (non-directional).
        So we will return positive values (Red) for now.
        To get Tension/Compression with PinJoint is hard without external calculation.
        Let's just show Magnitude -> Red intensity.
        """
        MAX_IMPULSE = 2000.0
        stresses = {}
        for edge_id, constraint in self.edge_constraints.items():
            if isinstance(constraint, pymunk.PinJoint):
                impulse = constraint.impulse
                # Normalized 0.0 to 1.0
                stress = min(1.0, impulse / MAX_IMPULSE)
                stresses[edge_id] = stress
        return stresses
