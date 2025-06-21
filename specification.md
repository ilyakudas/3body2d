# Technical Specification: 2D Three-Body Problem Simulation

1. Purpose  
   • Visualise the classical three-body problem (Newtonian gravity) in a single plane.  
   • Allow interactive control (pause, reset, parameter tweaks, camera zoom / pan).  
   • Provide basic data logging (positions, energies) for later analysis.

2. High-level Architecture  
   ├── main.py              – program entry; initialises Pygame, loads config, runs main loop  
   ├── physics.py           – numerical integration & vector math  
   ├── bodies.py            – `Body` class (mass, pos, vel, radius, colour, trail)  
   ├── renderer.py          – draws bodies, trails, HUD, UI overlays  
   ├── ui.py                – button & slider widgets (optional)  
   ├── config.json / yaml   – initial masses, positions, velocities, colours, G, Δt, etc.  
   ├── utils.py             – helpers: vector ops, colour conversions, file I/O  
   └── docs / README.md     – usage, theory, extensibility notes  

3. Core Data Structures  
   Body (dataclass)  
   • mass: float (kg)  
   • pos: Vector2 (m)  
   • vel: Vector2 (m s⁻¹)  
   • acc: Vector2 (m s⁻²) — computed each step  
   • radius: int (px) – for drawing  
   • colour: tuple[int,int,int]  
   • trail: deque[Vector2] – capped to N points for performance  

4. Physics Engine  
   Algorithm: Explicit 4th-order Runge–Kutta (RK4) or Velocity-Verlet (simpler, stable).  
   For each step Δt:  
   a. Compute pairwise force:  
      F₁₂ = G m₁ m₂ / |r₁₂|²   direction = r̂₁₂  
   b. Sum forces → accelerations.  
   c. Integrate to update velocities & positions.  
   d. Optionally compute kinetic, potential, total energy for read-out.  

   Constants:  
   • G = 6.674 × 10⁻¹¹ N m² kg⁻² (scaled to keep coordinates in a convenient range).  
   • scale_factor = meters → pixels mapping for rendering (adjustable).  

5. Rendering Layer (Pygame)  
   • Double-buffered 60 fps (or vsync) loop.  
   • Convert world coordinates to screen coordinates via scale & translation (camera).  
   • Draw each `Body` as filled circle; optionally gradient or image sprite.  
   • Trails drawn as polylines or faint circles (alpha blending).  
   • HUD: FPS, sim-time, Δt, total energy drift %.  
   • Interactive controls:  
     – Space: pause / resume  
     – R: reset initial conditions  
     – +/-: speed multiplier (Δt *= 2 or 0.5)  
     – Mouse wheel: zoom; drag: pan  
     – Esc / Q: quit  

6. Main Loop (pseudo)  
   init()  
   while running:  
       dt_real = clock.tick(60) / 1000  # real seconds between frames  
       handle_events()                   # keyboard/mouse/UI  
       if not paused:  
           for _ in range(integrations_per_frame):  
               physics.step(Δt_sim)  
       renderer.draw(world_state)  

7. Configuration & Persistence  
   • `config.json` lists bodies with vectors and masses.  
   • `--config path` CLI flag overrides default.  
   • Save current state to `save_YYYYMMDD_HHMM.json` on keypress (S).  
   • Load save on keypress (L) or via menu.

8. Performance Considerations  
   • Only three bodies → O(1) physics cost, negligible.  
   • Trail length cap and alpha-blending batching to keep ≤ 2–3 k draw calls.  
   • Use `pygame.Vector2` for native SIMD optimisation.

9. Dependencies  
   • Python ≥ 3.10  
   • pygame ≥ 2.5  
   • numpy (optional: faster RK4 vector ops)  

10. Testing & Validation  
   • Unit tests: force calculation symmetry & conservation (pytest).  
   • Energy drift should remain < 0.1 % over 10 k steps with chosen integrator/Δt.  
   • Compare special cases: two-body (one negligible mass) → closed ellipse.

11. Extensibility Hooks  
   • Switch integrator (Euler → RK4 → Symplectic).  
   • N-body generalisation (simply extend list of `Body` objects).  
   • Soft-body radius / collision detection for merging bodies.  
   • Export CSV of positions/velocities for external plotting.  
   • GPU rendering with OpenGL via `pygame.GL` or pyglet.