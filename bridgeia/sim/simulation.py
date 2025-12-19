from __future__ import annotations

import pymunk

from bridgeia.core.bridge import BridgeDesign
from bridgeia.core.level import Level


class PhysicsSimulation:
    def __init__(self, level: Level, bridge: BridgeDesign) -> None:
        self.space = pymunk.Space()
        self.space.gravity = (0, 900)  # Gravity downwards
        self.bodies: dict[str, pymunk.Body] = {}

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
            self.space.add(segment)

        # 2. Create Anchors (Static or Dynamic)
        # Note: Level anchors are "mount points". If they are fixed, they are static.
        # If not fixed (unlikely for level anchors usually?), they might be dynamic?
        # Typically level anchors are fixed points to the ground.
        for anchor in level.anchors:
            # We treat level anchors as infinite mass static points for now
            # But we might need a Body to attach joints to.
            # Static bodies are good.
            body = pymunk.Body(body_type=pymunk.Body.STATIC)
            body.position = (anchor.x, anchor.y)
            # Add a small shape just for collision if needed, but mainly for joints
            shape = pymunk.Circle(body, 5)
            shape.filter = pymunk.ShapeFilter(group=1) # Don't collide with self
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
            shape.filter = pymunk.ShapeFilter(group=1) # Don't collide with other bridge parts (usually)
            # Actually, in PolyBridge, bridge parts can collide with each ohter? 
            # Usually they are linked. Let's ignore self-collisions for now to prevent exploding.
            
            self.space.add(body, shape)
            self.bodies[j_id] = body

        # 4. Create Edges (Constraints)
        for edge in bridge.edges:
            body_a = self.bodies.get(edge.a)
            body_b = self.bodies.get(edge.b)
            
            if body_a and body_b:
                # PinJoint keeps distance fixed, allows rotation
                # We expect the constraints to hold the bridge together
                # We could use DampedSpring for "soft" bridges or PinJoint for rigid wood
                # Wood is rigid -> PinJoint
                pin = pymunk.PinJoint(body_a, body_b)
                # pin.collide_bodies = False
                self.space.add(pin)

    def step(self, dt: float) -> None:
        self.space.step(dt)

    def get_joint_position(self, joint_id: str) -> tuple[float, float] | None:
        body = self.bodies.get(joint_id)
        if body:
            return body.position.x, body.position.y # type: ignore
        return None
