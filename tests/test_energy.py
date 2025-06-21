"""
Test script to validate energy conservation over a long simulation run.
"""
from physics import PhysicsEngine
from bodies import Body
from pygame.math import Vector2

def main():
    # Create bodies with the same parameters as in config.json
    bodies = [
        Body(
            mass=1.0e16,
            pos=Vector2(0, 0),
            vel=Vector2(0, 0),
            radius=10,
            color=(255, 255, 0)
        ),
        Body(
            mass=2.0e14,
            pos=Vector2(100, 0),
            vel=Vector2(0, 40),
            radius=5,
            color=(0, 255, 0)
        ),
        Body(
            mass=1.0e14,
            pos=Vector2(-100, 0),
            vel=Vector2(0, -80),
            radius=5,
            color=(0, 0, 255)
        )
    ]
    
    # Create physics engine
    engine = PhysicsEngine()
    
    # Get initial energy
    initial_ke, initial_pe, initial_total = engine.calculate_system_energy(bodies)
    print(f"Initial Energy: {initial_total:.6e}")
    
    # Run simulation for 10,000 steps
    dt = 0.001
    steps = 10000
    
    for i in range(steps):
        engine.step_verlet(bodies, dt)
        
        # Print energy every 1000 steps
        if i % 1000 == 0:
            ke, pe, total = engine.calculate_system_energy(bodies)
            drift = abs((total - initial_total) / initial_total) * 100
            print(f"Step {i}: Energy {total:.6e}, Drift {drift:.6f}%")
    
    # Get final energy
    final_ke, final_pe, final_total = engine.calculate_system_energy(bodies)
    drift = abs((final_total - initial_total) / initial_total) * 100
    print(f"Final Energy: {final_total:.6e}, Total Drift: {drift:.6f}%")
    
    # Check if energy drift is within acceptable limits
    if drift < 0.1:
        print("PASS: Energy conservation is good (drift < 0.1%)")
    else:
        print(f"FAIL: Energy drift too high: {drift:.6f}%")

if __name__ == "__main__":
    main()
