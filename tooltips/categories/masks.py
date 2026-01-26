"""Tooltips for masks-related nodes."""

from ..tooltip_manager import TooltipManager

def register_tooltips():
    """Register tooltips for masks nodes"""

    # Base classes first
    # MaskBase tooltips (inherits from: RyanOnTheInside, ABC)
    TooltipManager.register_tooltips("MaskBase", {
        "masks": "Input mask or sequence of masks to be processed (MASK type)",
        "strength": "Overall strength of the mask effect (0.0 to 1.0)",
        "invert": "When enabled, inverts the mask output (black becomes white and vice versa)",
        "subtract_original": "Amount of the original mask to subtract from the result (0.0 to 1.0)",
        "grow_with_blur": "Amount of Gaussian blur to apply for mask growth (0.0 to 10.0)"
    }, inherits_from=['RyanOnTheInside', 'ABC'],)

    # FlexMaskBase tooltips (inherits from: FlexBase, MaskBase)
    TooltipManager.register_tooltips("FlexMaskBase", {
        "feature": "Feature used to modulate the effect (FEATURE type)",
        "feature_pipe": "Feature pipe containing frame information (FEATURE_PIPE type)",
        "feature_threshold": "Threshold for feature activation (0.0 to 1.0)",
        "mask_strength": "Overall strength of the mask effect (0.0 to 1.0)",
        "strength": "Overall strength of the feature modulation (0.0 to 1.0)",
        "feature_param": """Choose which parameter to modulate with the input feature
        
Each node type has different parameters that can be modulated:
- 'None': No parameter modulation (default behavior)
- Other options depend on the specific node type"""
    }, inherits_from=['FlexBase', 'MaskBase'])

    # TemporalMaskBase tooltips (inherits from: MaskBase, ABC)
    TooltipManager.register_tooltips("TemporalMaskBase", {
        "start_frame": "Frame number where the effect begins (0 to 1000)",
        "end_frame": "Frame number where the effect ends (0 to 1000, 0 means until end)",
        "effect_duration": "Number of frames over which the effect is applied (0 to 1000, 0 means full range)",
        "temporal_easing": "Controls how the effect strength changes over time ('ease_in_out', 'linear', 'bounce', 'elastic', 'none')",
        "palindrome": "When enabled, the effect plays forward then reverses within the specified duration"
    }, inherits_from=['MaskBase', 'ABC'], description="[DEPRECATED] these effects can be acheived with more control using the FlexMask nodes")



    # OpticalFlowMaskBase tooltips (inherits from: MaskBase, ABC)
    TooltipManager.register_tooltips("OpticalFlowMaskBase", {
        "images": "Sequence of images to calculate optical flow from (IMAGE type)",
        "flow_method": "Algorithm used to calculate optical flow ('Farneback', 'LucasKanade', 'PyramidalLK')",
        "flow_threshold": "Minimum flow magnitude to consider (0.0 to 1.0)",
        "magnitude_threshold": "Relative threshold for flow magnitude as fraction of maximum (0.0 to 1.0)"
    }, inherits_from=['MaskBase', 'ABC'], description="Generate masks based on motion detection between frames, perfect for creating motion-reactive effects.")

    # ParticleSystemMaskBase tooltips (inherits from: MaskBase, ABC)
    TooltipManager.register_tooltips("ParticleSystemMaskBase", {
        "emitters": "List of particle emitter configurations (PARTICLE_EMITTER type)",
        "particle_count": "Maximum number of particles in the system (1 to 10000)",
        "particle_lifetime": "How long each particle lives in seconds (0.1 to 10.0)",
        "wind_strength": "Strength of the wind force (-100.0 to 100.0)",
        "wind_direction": "Direction of the wind in degrees (0.0 to 360.0)",
        "gravity": "Strength and direction of gravity (-1000.0 to 1000.0)",
        "warmup_period": "Number of frames to simulate before starting (0 to 1000)",
        "start_frame": "Frame to start particle emission (0 to 1000)",
        "end_frame": "Frame to end particle emission (0 to 1000, 0 means until end)",
        "respect_mask_boundary": "Whether particles should collide with mask boundaries",
        "vortices": "Optional list of vortex configurations (VORTEX type)",
        "wells": "Optional list of gravity well configurations (GRAVITY_WELL type)",
        "static_bodies": "Optional list of static collision bodies (STATIC_BODY type)",
        "well_strength_multiplier": "Global multiplier for gravity well strengths (0.0 to 10.0)"
    }, inherits_from=['MaskBase', 'ABC'], description="Create dynamic mask effects using particle systems with physics simulation, including forces like gravity, wind, and vortices. Tips: increase particle_count for density, lower gravity for floaty motion, and use warmup_period for instant fills.")

    # FlexMaskNormalBase tooltips (inherits from: FlexMaskBase)
    TooltipManager.register_tooltips("FlexMaskNormalBase", {
        "normal_map": "Normal map to be used for lighting calculations (IMAGE type)"
    }, inherits_from='FlexMaskBase')

    # MaskMorph tooltips (inherits from: TemporalMaskBase)
    TooltipManager.register_tooltips("MaskMorph", {
        "morph_type": "Type of morphological operation ('erode', 'dilate', 'open', 'close')",
        "max_kernel_size": "Maximum size of the morphological kernel (3 to 21, odd numbers only)",
        "max_iterations": "Maximum number of times to apply the operation (1 to 50)"
    }, inherits_from='TemporalMaskBase', description="Morphological operations on masks.")

    # MaskTransform tooltips (inherits from: TemporalMaskBase)
    TooltipManager.register_tooltips("MaskTransform", {
        "transform_type": "Type of transformation to apply ('translate', 'rotate', 'scale')",
        "x_value": "Horizontal component of the transformation (-1000 to 1000)",
        "y_value": "Vertical component of the transformation (-1000 to 1000)"
    }, inherits_from='TemporalMaskBase', description="Transform masks over time.")

    # MaskMath tooltips (inherits from: TemporalMaskBase)
    TooltipManager.register_tooltips("MaskMath", {
        "mask_b": "Second mask to combine with the input mask (MASK type)",
        "combination_method": "Mathematical operation to apply ('add', 'subtract', 'multiply', 'minimum', 'maximum')"
    }, inherits_from='TemporalMaskBase')

    # MaskRings tooltips (inherits from: TemporalMaskBase)
    TooltipManager.register_tooltips("MaskRings", {
        "num_rings": "Number of rings to generate (1 to 50)",
        "max_ring_width": "Maximum width of each ring as a fraction of the total distance (0.01 to 0.5)"
    }, inherits_from='TemporalMaskBase')

    # MaskWarp tooltips (inherits from: TemporalMaskBase)
    TooltipManager.register_tooltips("MaskWarp", {
        "warp_type": "Type of warping effect to apply ('perlin', 'radial', 'swirl')",
        "frequency": "Controls the scale of the warping effect (0.01 to 1.0)",
        "amplitude": "Controls the strength of the warping effect (0.1 to 500.0)",
        "octaves": "For noise-based warps, adds detail at different scales (1 to 8)"
    }, inherits_from='TemporalMaskBase')

    # ParticleEmissionMask tooltips (inherits from: ParticleSystemMaskBase)
    TooltipManager.register_tooltips("ParticleEmissionMask", {
        "emission_strength": "Strength of particle emission effect (0.0 to 1.0)",
        "draw_modifiers": "Visibility of vortices and gravity wells (0.0 to 1.0)"
    }, inherits_from='ParticleSystemMaskBase', description="Render the particle system into a mask/image. Tips: lower emission_strength for subtle trails and hide modifiers for clean output.")

    # TaichiParticleMask tooltips (inherits from: MaskBase)
    TooltipManager.register_tooltips("TaichiParticleMask", {
        "emitters": "List of Taichi emitter configurations (TAICHI_EMITTER type)",
        "particle_count": "Maximum number of particles allowed in the simulation",
        "particle_lifetime": "Lifetime of particles in seconds (0.1 to 10.0)",
        "wind_strength": "Horizontal wind strength in pixels/sec² (-500.0 to 500.0)",
        "wind_direction": "Wind direction in degrees (0.0 to 360.0)",
        "gravity": "Vertical gravity in pixels/sec² (-2000.0 to 2000.0)",
        "frame_rate": "Simulation frame rate for time step (1.0 to 120.0)",
        "start_frame": "Frame to start emission (0 to 10000)",
        "end_frame": "Frame to end emission (0 to 10000, 0 means until end)"
    }, inherits_from='MaskBase', description="Taichi-accelerated particle emission mask with audio-reactive emission support. Tips: raise particle_count for density, adjust frame_rate for speed, and use emitter-level particle_lifetime to override the global lifetime.")

    # TaichiParticleEmitter tooltips
    TooltipManager.register_tooltips("TaichiParticleEmitter", {
        "emitter_x": "X-coordinate of the emitter (0.0 to 1.0)",
        "emitter_y": "Y-coordinate of the emitter (0.0 to 1.0)",
        "particle_direction": "Direction of particle emission in degrees (0.0 to 360.0)",
        "direction_offset": "Additional direction offset in degrees (-360.0 to 360.0)",
        "particle_spread": "Spread angle of particle emission in degrees (0.0 to 360.0)",
        "particle_size": "Size of emitted particles (1.0 to 100.0)",
        "particle_speed": "Speed of emitted particles in pixels/sec (0.0 to 1000.0)",
        "emission_rate": "Base emission rate in particles/sec (0.0 to 200.0)",
        "color": "Color of emitted particles (RGB string)",
        "emission_radius": "Radius of the area from which particles are emitted (0.0 to 200.0)",
        "particle_shape": "Particle shape ('circle', 'square', 'spark')",
        "spark_length": "Length of spark streaks when using 'spark' shape (0.0 to 200.0)",
        "particle_lifetime": "Override particle lifetime for this emitter (0 means use global)",
        "endless_mode": "When enabled, reuse particle slots for endless emission",
        "start_frame": "Frame to start the emission (0 to 10000)",
        "end_frame": "Frame to end the emission (0 to 10000)",
        "previous_emitter": "Optional previous emitter to chain with (TAICHI_EMITTER type)",
        "emitter_modulation": "Optional audio modulation for emission (TAICHI_EMITTER_MOD type)"
    }, description="Define a Taichi particle emitter with optional audio-driven modulation. Tips: lower particle_spread for tight beams, set emission_radius to 0 for sharp points, and use endless_mode if you hit particle_count limits.")

    # TaichiParticleEmitterFromMaskEdges tooltips
    TooltipManager.register_tooltips("TaichiParticleEmitterFromMaskEdges", {
        "masks": "Input masks used to locate edge points (MASK type)",
        "spot_count": "Number of edge emitters to sample (1 to 200)",
        "edge_low_threshold": "Canny low threshold for edge detection (0 to 255)",
        "edge_high_threshold": "Canny high threshold for edge detection (0 to 255)",
        "sampling_mode": "Sample edges per frame or reuse the first frame ('per_frame', 'first_frame')",
        "direction_mode": "Emit outward or inward from the mask boundary",
        "random_seed": "Seed for deterministic edge sampling",
        "particle_direction": "Fallback direction when edge normals are unavailable",
        "direction_offset": "Additional direction offset in degrees (-360.0 to 360.0)",
        "particle_spread": "Spread angle of particle emission in degrees (0.0 to 360.0)",
        "particle_size": "Size of emitted particles (1.0 to 100.0)",
        "particle_speed": "Speed of emitted particles in pixels/sec (0.0 to 1000.0)",
        "emission_rate": "Base emission rate in particles/sec (0.0 to 200.0)",
        "color": "Color of emitted particles (RGB string)",
        "emission_radius": "Radius of the area from which particles are emitted (0.0 to 200.0)",
        "particle_shape": "Particle shape ('circle', 'square', 'spark')",
        "spark_length": "Length of spark streaks when using 'spark' shape (0.0 to 200.0)",
        "particle_lifetime": "Override particle lifetime for this emitter (0 means use global)",
        "endless_mode": "When enabled, reuse particle slots for endless emission",
        "start_frame": "Frame to start the emission (0 to 10000)",
        "end_frame": "Frame to end the emission (0 to 10000)",
        "previous_emitter": "Optional previous emitter to chain with (TAICHI_EMITTER type)",
        "emitter_modulation": "Optional audio modulation for emission (TAICHI_EMITTER_MOD type)"
    }, description="Emit Taichi particles from mask edges with outward or inward normals. Tips: use first_frame for stable masks, lower spot_count for clean silhouettes, and set emission_radius to 0 to avoid ring patterns.")

    # TaichiParticleBurstSpots tooltips
    TooltipManager.register_tooltips("TaichiParticleBurstSpots", {
        "feature": "Feature input used to trigger bursts (FEATURE type)",
        "spot_count": "Number of burst spots to create (1 to 200)",
        "position_mode": "How spot positions are chosen ('random', 'lock_x', 'lock_y', 'lock_xy')",
        "lock_x": "Locked X coordinate when using lock_x or lock_xy (0.0 to 1.0)",
        "lock_y": "Locked Y coordinate when using lock_y or lock_xy (0.0 to 1.0)",
        "random_seed": "Seed for deterministic random spot placement",
        "particle_direction": "Direction of particle emission in degrees (0.0 to 360.0)",
        "direction_offset": "Additional direction offset in degrees (-360.0 to 360.0)",
        "particle_spread": "Spread angle of particle emission in degrees (0.0 to 360.0)",
        "particle_size": "Size of emitted particles (1.0 to 100.0)",
        "particle_speed": "Speed of emitted particles in pixels/sec (0.0 to 1000.0)",
        "emission_rate": "Base emission rate in particles/sec (0.0 to 200.0)",
        "color": "Color of emitted particles (RGB string)",
        "emission_radius": "Radius of the area from which particles are emitted (0.0 to 200.0)",
        "particle_shape": "Particle shape ('circle', 'square', 'spark')",
        "spark_length": "Length of spark streaks when using 'spark' shape (0.0 to 200.0)",
        "particle_lifetime": "Override particle lifetime for this emitter (0 means use global)",
        "endless_mode": "When enabled, reuse particle slots for endless emission",
        "start_frame": "Frame to start the emission (0 to 10000)",
        "end_frame": "Frame to end the emission (0 to 10000)",
        "scale": "Emission rate scale applied to the feature value (0.0 to 10.0)",
        "threshold": "Feature activation threshold (0.0 to 1.0)",
        "mode": "Emission modulation mode ('relative' or 'absolute')",
        "onset_threshold": "Feature delta threshold to trigger a burst (0.0 to 1.0)",
        "burst_strength": "Burst multiplier applied to feature delta (0.0 to 5000.0)",
        "burst_min": "Minimum burst count when triggered (0 to 20000, 0 disables)",
        "burst_max": "Maximum burst count when triggered (0 to 20000, 0 disables)",
        "previous_emitter": "Optional previous emitter to chain with (TAICHI_EMITTER type)"
    }, description="Create multiple burst-only Taichi emitters with audio-driven bursts. Tips: set emission_rate to 0 for pure bursts, raise onset_threshold to reduce triggers, and use lock_x or lock_y for aligned bursts.")

    # TaichiParticleAudioReactiveEmission tooltips
    TooltipManager.register_tooltips("TaichiParticleAudioReactiveEmission", {
        "feature": "Audio or feature input used to drive emission rate (FEATURE type)",
        "scale": "Multiplier for the feature value (0.0 to 10.0)",
        "threshold": "Feature activation threshold (0.0 to 1.0)",
        "mode": "Emission modulation mode ('relative' scales base rate, 'absolute' adds to base rate)",
        "onset_threshold": "Feature delta threshold to trigger a burst (0.0 to 1.0)",
        "burst_strength": "Burst multiplier applied to feature delta (0.0 to 5000.0)",
        "burst_min": "Minimum burst count when triggered (0 to 20000, 0 disables)",
        "burst_max": "Maximum burst count when triggered (0 to 20000, 0 disables)"
    }, description="Create an audio-reactive modulation payload for Taichi emitters. Tips: use relative mode for gentle scaling, absolute mode for hard spikes, and adjust onset_threshold to control burst frequency.")

    # TaichiPathFromPoints tooltips
    TooltipManager.register_tooltips("TaichiPathFromPoints", {
        "points": "JSON list of points [{'x':0.2,'y':0.3}, ...] in normalized coordinates",
        "interpolation": "Interpolation method for path sampling",
        "closed": "Whether the path loops back to the first point",
        "width": "Preview width in pixels",
        "height": "Preview height in pixels",
        "thickness": "Path preview thickness in pixels",
        "preview_color": "Path preview color (RGB string)"
    }, description="Create a Taichi path from explicit points with a preview mask. Tips: keep points in 0..1 space and enable closed for loops.")

    # TaichiPathFromShape tooltips
    TooltipManager.register_tooltips("TaichiPathFromShape", {
        "shape_type": "Shape used to generate the path",
        "center_x": "Center X for circle/arc/spiral/sine (0.0 to 1.0)",
        "center_y": "Center Y for circle/arc/spiral/sine (0.0 to 1.0)",
        "size_x": "Normalized width of the shape bounding box",
        "size_y": "Normalized height of the shape bounding box",
        "sides": "Number of sides for polygon/square shapes",
        "rotation": "Polygon rotation in degrees",
        "corner_radius": "Corner radius (0-1 as fraction of radius, >1 as absolute units)",
        "start_angle": "Start angle for arc in degrees",
        "end_angle": "End angle for arc in degrees",
        "segments": "Number of segments used to sample the shape",
        "polyline_points": "JSON list of points for polyline shape",
        "closed": "Whether to close the generated path",
        "preview_mask": "Emit a mask preview for the path",
        "preview_image": "Emit a colored image preview for the path",
        "preview_width": "Preview width in pixels",
        "preview_height": "Preview height in pixels",
        "preview_thickness": "Path preview thickness in pixels",
        "preview_color": "Path preview color (RGB string)"
    }, description="Generate a Taichi path from simple shapes with preview. Tips: increase segments for smoother curves and use preview to confirm placement.")

    # TaichiPathPreview tooltips
    TooltipManager.register_tooltips("TaichiPathPreview", {
        "path": "Path definition (TAICHI_PATH type)",
        "width": "Preview width in pixels",
        "height": "Preview height in pixels",
        "thickness": "Path preview thickness in pixels",
        "preview_color": "Path preview color (RGB string)",
        "show_emitter": "Overlay a marker at a progress position along the path",
        "emitter_progress": "Normalized path progress (0.0 to 1.0)",
        "emitter_size": "Marker size in pixels",
        "emitter_color": "Marker color (RGB string)"
    }, description="Preview a Taichi path as a mask and image. Tips: enable show_emitter to confirm alignment and direction.")

    TooltipManager.register_tooltips("TaichiPathFromSpeedDirection", {
        "speed_feature": "Feature driving speed (FEATURE type)",
        "direction_feature": "Feature driving direction angle (FEATURE type)",
        "frame_rate": "Frame rate used to integrate the path",
        "start_x": "Starting X position (0.0 to 1.0)",
        "start_y": "Starting Y position (0.0 to 1.0)",
        "min_speed": "Minimum speed (normalized units per second)",
        "max_speed": "Maximum speed (normalized units per second)",
        "min_direction": "Minimum direction angle in degrees",
        "max_direction": "Maximum direction angle in degrees",
        "direction_mode": "Absolute uses mapped angle; relative adds to current heading",
        "direction_smoothing": "How quickly direction follows the feature (0..1)",
        "speed_smoothing": "How quickly speed follows the feature (0..1)"
    }, description="Build a path by integrating speed and direction features with edge bounces. Tips: increase smoothing to reduce jitter and clamp min/max speeds for stability.")

    # TaichiPathEmitterModulation tooltips
    TooltipManager.register_tooltips("TaichiPathEmitterModulation", {
        "speed_feature": "Feature used to modulate path speed (FEATURE type)",
        "speed_scale": "Scale for speed modulation",
        "speed_offset": "Offset for speed modulation",
        "speed_threshold": "Threshold for speed modulation",
        "speed_mode": "Mode for speed modulation",
        "size_feature": "Feature used to modulate particle size (FEATURE type)",
        "size_scale": "Scale for size modulation",
        "size_offset": "Offset for size modulation",
        "size_threshold": "Threshold for size modulation",
        "size_mode": "Mode for size modulation",
        "angle_feature": "Feature used to modulate emission angle (FEATURE type)",
        "angle_scale": "Scale for angle modulation",
        "angle_offset": "Offset for angle modulation",
        "angle_threshold": "Threshold for angle modulation",
        "angle_mode": "Mode for angle modulation",
        "spread_feature": "Feature used to modulate emission spread (FEATURE type)",
        "spread_scale": "Scale for spread modulation",
        "spread_offset": "Offset for spread modulation",
        "spread_threshold": "Threshold for spread modulation",
        "spread_mode": "Mode for spread modulation",
        "burst_feature": "Feature used to trigger bursts (FEATURE type)",
        "onset_threshold": "Delta threshold to trigger a burst",
        "burst_strength": "Burst multiplier for feature deltas",
        "burst_min": "Minimum burst count",
        "burst_max": "Maximum burst count"
    }, description="Modulate path speed, size, angle, and spread using features. Tips: use small scales first, then add offsets to bias direction or size.")

    # TaichiParticleEmitterOnPath tooltips
    TooltipManager.register_tooltips("TaichiParticleEmitterOnPath", {
        "path": "Path definition (TAICHI_PATH type)",
        "emitter_x": "Base emitter X for relative paths (0.0 to 1.0)",
        "emitter_y": "Base emitter Y for relative paths (0.0 to 1.0)",
        "path_speed": "Path traversal speed in cycles/sec",
        "loop_mode": "Path traversal mode ('loop', 'clamp', 'pingpong')",
        "align_to_path": "Align emission direction to the path tangent",
        "use_emitter_origin": "Treat path points as offsets from emitter_x/y",
        "particle_direction": "Base particle direction in degrees",
        "direction_offset": "Direction offset (use 180 for sparks behind travel)",
        "particle_spread": "Base particle spread in degrees",
        "particle_size": "Base particle size in pixels",
        "particle_speed": "Base particle speed in pixels/sec",
        "emission_rate": "Base emission rate in particles/sec",
        "color": "Particle color (RGB string)",
        "emission_radius": "Emitter radius in pixels",
        "particle_shape": "Particle shape ('circle', 'square', 'spark')",
        "spark_length": "Length of spark streaks for spark shape",
        "particle_lifetime": "Override particle lifetime for this emitter (0 means use global)",
        "endless_mode": "When enabled, reuse particle slots for endless emission",
        "start_frame": "Frame to start emission",
        "end_frame": "Frame to end emission",
        "emitter_modulation": "Optional emission modulation (TAICHI_EMITTER_MOD)",
        "path_modulation": "Optional path modulation (TAICHI_PATH_MOD)"
    }, description="Emit Taichi particles while traversing a path. Tips: enable align_to_path for motion-aligned bursts and reduce path_speed for smoother loops.")

    # TaichiResetCache tooltips
    TooltipManager.register_tooltips("TaichiResetCache", {
    }, description="Reset cached Taichi particle buffers to free GPU/CPU memory. Tip: use after changing resolution or particle_count.")

    # ParticleSystemModulatorBase tooltips (inherits from: RyanOnTheInside)
    TooltipManager.register_tooltips("ParticleSystemModulatorBase", {
        # TODO: Add parameter tooltips
    }, inherits_from='RyanOnTheInside', description="Modify particle system behavior with controls for forces, emissions, and particle properties.")

    # EmitterModulationBase tooltips (inherits from: ParticleSystemModulatorBase)
    TooltipManager.register_tooltips("EmitterModulationBase", {
        "start_frame": "Frame number where the effect begins (0 to 1000)",
        "end_frame": "Frame number where the effect ends (0 to 1000, 0 means until end)",
        "effect_duration": "Number of frames over which the effect is applied (0 to 1000, 0 means full range)",
        "temporal_easing": "Controls how the effect strength changes over time ('ease_in_out', 'linear', 'bounce', 'elastic', 'none')",
        "palindrome": "When enabled, the effect plays forward then reverses within the specified duration",
        "random": "When enabled, selects random values between start and target",
        "previous_modulation": "Optional previous modulation to chain with (EMITTER_MODULATION type)",
        "feature": "Optional feature to drive the modulation (FEATURE type)"
    }, inherits_from='ParticleSystemModulatorBase', description="Control particle emitter properties over time with support for easing, randomization, and feature-driven animation.")

    # EmitterEmissionRateModulation tooltips (inherits from: EmitterModulationBase)
    TooltipManager.register_tooltips("EmitterEmissionRateModulation", {
        "target_emission_rate": "Target emission rate at the end of the modulation (0.1 to 100.0 particles/frame)"
    }, inherits_from='EmitterModulationBase', description="Animate emission rate over time. Tips: use easing + palindrome for pulsating emitters.")

    # Vortex tooltips (inherits from: ParticleSystemModulatorBase)
    TooltipManager.register_tooltips("Vortex", {
        "x": "X-coordinate of the vortex center (0.0 to 1.0)",
        "y": "Y-coordinate of the vortex center (0.0 to 1.0)",
        "strength": "Strength of the vortex effect (0.0 to 1000.0)",
        "radius": "Radius of effect for the vortex (10.0 to 500.0)",
        "inward_factor": "Factor controlling how quickly particles are pulled towards the center (0.0 to 1.0)",
        "movement_speed": "Speed of movement of the vortex object (0.0 to 10.0)",
        "color": "Color of the vortex visualization (RGB tuple)",
        "draw": "Thickness of the vortex visualization (0.0 to 1.0)"
    }, inherits_from='ParticleSystemModulatorBase', description="Swirling force field. Tips: raise radius for smoother flow and lower strength to avoid tight spirals.")

    # GravityWell tooltips (inherits from: ParticleSystemModulatorBase)
    TooltipManager.register_tooltips("GravityWell", {
        "x": "X-coordinate of the gravity well (0.0 to 1.0)",
        "y": "Y-coordinate of the gravity well (0.0 to 1.0)",
        "strength": "Strength of the gravity well",
        "radius": "Radius of effect for the gravity well",
        "type": "Type of gravity well ('attract' or 'repel')",
        "color": "Color of the gravity well visualization (RGB tuple)",
        "draw": "Thickness of the gravity well visualization (0.0 to 1.0)"
    }, inherits_from='ParticleSystemModulatorBase', description="Attracts or repels particles. Tips: keep radius larger than emission_radius for smoother curves.")

    # ParticleEmitter tooltips (inherits from: ParticleSystemModulatorBase)
    TooltipManager.register_tooltips("ParticleEmitter", {
        "emitter_x": "X-coordinate of the emitter (0.0 to 1.0)",
        "emitter_y": "Y-coordinate of the emitter (0.0 to 1.0)",
        "particle_direction": "Direction of particle emission in degrees (0.0 to 360.0)",
        "particle_spread": "Spread angle of particle emission in degrees (0.0 to 360.0)",
        "particle_size": "Size of emitted particles (1.0 to 400.0)",
        "particle_speed": "Speed of emitted particles (1.0 to 1000.0)",
        "emission_rate": "Rate of particle emission (0.1 to 100.0)",
        "color": "Color of emitted particles (RGB string)",
        "initial_plume": "Initial burst of particles (0.0 to 1.0)",
        "start_frame": "Frame to start the emission (0 to 10000)",
        "end_frame": "Frame to end the emission (0 to 10000)",
        "emission_radius": "Radius of the area from which particles are emitted (0.0 to 100.0)",
        "previous_emitter": "Optional previous emitter to chain with (PARTICLE_EMITTER type)",
        "emitter_movement": "Optional movement configuration (EMITTER_MOVEMENT type)",
        "spring_joint_setting": "Optional spring joint configuration (SPRING_JOINT_SETTING type)",
        "particle_modulation": "Optional particle modulation configuration (PARTICLE_MODULATION type)",
        "emitter_modulation": "Optional emitter modulation configuration (EMITTER_MODULATION type)"
    }, inherits_from='ParticleSystemModulatorBase', description="Define a particle emitter for the CPU particle system. Tips: set emission_radius to 0 for pinpoint sources and reduce spread for beams.")

    # SpringJointSetting tooltips (inherits from: ParticleSystemModulatorBase)
    TooltipManager.register_tooltips("SpringJointSetting", {
        "stiffness": "Stiffness of the spring (0.0 to 1000.0)",
        "damping": "Damping factor of the spring (0.0 to 100.0)",
        "rest_length": "Rest length of the spring (0.0 to 100.0)",
        "max_distance": "Maximum distance the spring can stretch (0.0 to 500.0)"
    }, inherits_from='ParticleSystemModulatorBase', description="Connects particles with springs. Tips: increase damping to prevent jitter and keep rest_length close to particle spacing.")

    # EmitterMovement tooltips (inherits from: ParticleSystemModulatorBase)
    TooltipManager.register_tooltips("EmitterMovement", {
        "emitter_x_frequency": "How quickly the emitter moves horizontally (0.0 to 10.0)",
        "emitter_x_amplitude": "Maximum horizontal distance the emitter moves (0.0 to 0.5)",
        "emitter_y_frequency": "How quickly the emitter moves vertically (0.0 to 10.0)",
        "emitter_y_amplitude": "Maximum vertical distance the emitter moves (0.0 to 0.5)",
        "direction_frequency": "How quickly the emission angle changes (0.0 to 10.0)",
        "direction_amplitude": "Maximum angle change in degrees (0.0 to 360.0)",
        "feature_param": "Parameter to be modulated by the feature ('emitter_x_frequency', 'emitter_y_frequency', 'direction_frequency')",
        "feature": "Optional feature to modulate the movement (FEATURE type)"
    }, inherits_from='ParticleSystemModulatorBase', description="Animate emitter position and direction. Tips: start with low amplitudes to avoid leaving frame bounds.")

    # StaticBody tooltips (inherits from: ParticleSystemModulatorBase)
    TooltipManager.register_tooltips("StaticBody", {
        "shape_type": "Type of shape (\"segment\" or \"polygon\")",
        "x1": "First X coordinate",
        "y1": "First Y coordinate",
        "x2": "Second X coordinate",
        "y2": "Second Y coordinate",
        "elasticity": "Bounciness of the static body (0.0 to 1.0)",
        "friction": "Friction of the static body (0.0 to 1.0)",
        "draw": "Whether to visualize the static body and how thick",
        "color": "Color of the static body (RGB tuple)"
    }, inherits_from='ParticleSystemModulatorBase', description="Static collision geometry. Tips: use low friction for sliding and higher elasticity for bouncy results.")

    # ParticleModulationBase tooltips (inherits from: ParticleSystemModulatorBase)
    TooltipManager.register_tooltips("ParticleModulationBase", {
        "start_frame": "Frame to start the modulation effect (0 to 1000)",
        "end_frame": "Frame to end the modulation effect (0 to 1000)",
        "effect_duration": "Duration of the modulation effect in frames (0 to 1000)",
        "temporal_easing": "Easing function for the modulation effect ('ease_in_out', 'linear', 'bounce', 'elastic', 'none')",
        "palindrome": "Whether to reverse the modulation effect after completion",
        "random": "When enabled, selects random values between start and target",
        "previous_modulation": "Optional previous modulation to chain with (PARTICLE_MODULATION type)",
        "feature": "Optional feature to drive the modulation (FEATURE type)"
    }, inherits_from='ParticleSystemModulatorBase')

    # ParticleSizeModulation tooltips (inherits from: ParticleModulationBase)
    TooltipManager.register_tooltips("ParticleSizeModulation", {
        "target_size": "Target size for particles at the end of the modulation (0.0 to 400.0)"
    }, inherits_from='ParticleModulationBase', description="Animate particle size over time. Tips: use ease_in_out to avoid popping.")

    # ParticleSpeedModulation tooltips (inherits from: ParticleModulationBase)
    TooltipManager.register_tooltips("ParticleSpeedModulation", {
        "target_speed": "Target speed for particles at the end of the modulation (0.0 to 1000.0)"
    }, inherits_from='ParticleModulationBase', description="Animate particle speed over time. Tips: use palindrome for oscillating speed.")

    # ParticleColorModulation tooltips (inherits from: ParticleModulationBase)
    TooltipManager.register_tooltips("ParticleColorModulation", {
        "target_color": "Target color for particles at the end of the modulation (RGB tuple)"
    }, inherits_from='ParticleModulationBase', description="Animate particle color over time. Tips: use long durations for smooth gradients.")

    # OpticalFlowMaskModulation tooltips (inherits from: OpticalFlowMaskBase)
    TooltipManager.register_tooltips("OpticalFlowMaskModulation", {
        "modulation_strength": "Intensity of the modulation effect (0.0 to 5.0)",
        "blur_radius": "Amount of smoothing applied to the flow magnitude (0 to 20 pixels)",
        "trail_length": "Number of frames to maintain in the trail effect (1 to 20)",
        "decay_factor": "Rate at which trail intensity decreases (0.1 to 1.0)",
        "decay_style": "Method of trail decay ('fade' or 'thickness')",
        "max_thickness": "Maximum thickness of trails when using thickness decay (1 to 50 pixels)"
    }, inherits_from='OpticalFlowMaskBase')

    # OpticalFlowDirectionMask tooltips (inherits from: OpticalFlowMaskBase)
    TooltipManager.register_tooltips("OpticalFlowDirectionMask", {
        "direction": "Direction of motion to detect ('horizontal', 'vertical', 'radial_in', 'radial_out', 'clockwise', 'counterclockwise')",
        "angle_threshold": "Maximum angle deviation from target direction (0.0 to 180.0 degrees)",
        "blur_radius": "Amount of smoothing applied to the mask (0 to 20 pixels)",
        "invert": "When enabled, reverses the mask output"
    }, inherits_from='OpticalFlowMaskBase')

    # OpticalFlowParticleSystem tooltips (inherits from: OpticalFlowMaskBase)
    TooltipManager.register_tooltips("OpticalFlowParticleSystem", {
        "num_particles": "Total number of particles in the system (100 to 10000)",
        "particle_size": "Size of each particle in pixels (1 to 50)",
        "particle_color": "Color of particles in hex format (e.g., '#FFFFFF')",
        "particle_opacity": "Transparency of particles (0.0 to 1.0)",
        "flow_multiplier": "Multiplier for optical flow influence (0.1 to 5.0)",
        "particle_lifetime": "Number of frames each particle exists (1 to 100)",
        "initial_velocity": "Starting speed of newly emitted particles (0.1 to 5.0)"
    }, inherits_from='OpticalFlowMaskBase')

    # MovingShape tooltips
    TooltipManager.register_tooltips("MovingShape", {
        "frame_width": "Width of each frame in pixels (1 to 3840)",
        "frame_height": "Height of each frame in pixels (1 to 2160)",
        "num_frames": "Number of frames in the animation sequence (1 to 120)",
        "rgb": "Color of the shape in RGB format (e.g., '(255,255,255)')",
        "shape": "Type of shape to generate ('square', 'circle', 'triangle')",
        "shape_width_percent": "Width of the shape as percentage of frame width (0 to 100)",
        "shape_height_percent": "Height of the shape as percentage of frame height (0 to 100)",
        "shape_start_position_x": "Starting X position relative to frame (-100 to 100)",
        "shape_start_position_y": "Starting Y position relative to frame (-100 to 100)",
        "shape_end_position_x": "Ending X position relative to frame (-100 to 100)",
        "shape_end_position_y": "Ending Y position relative to frame (-100 to 100)",
        "movement_type": "Type of movement animation ('linear', 'ease_in_out', 'bounce', 'elastic')",
        "grow": "Growth factor during animation (0 to 100)",
        "palindrome": "Whether to play the animation forward then reverse",
        "delay": "Number of static frames at the start (0 to 60)"
    })

    # TextMaskNode tooltips
    TooltipManager.register_tooltips("TextMaskNode", {
        "width": "Width of the output image in pixels (1 to 8192)",
        "height": "Height of the output image in pixels (1 to 8192)",
        "text": "Text content to render",
        "font": "Font family to use for rendering (from system fonts)",
        "font_size": "Size of the font in pixels (1 to 1000)",
        "font_color": "Color of the text in RGB format (e.g., '(255,255,255)')",
        "background_color": "Color of the background in RGB format (e.g., '(0,0,0)')",
        "x_position": "Horizontal position of text relative to frame width (0.0 to 1.0)",
        "y_position": "Vertical position of text relative to frame height (0.0 to 1.0)",
        "rotation": "Rotation angle of the text in degrees (0 to 360)",
        "max_width_ratio": "Maximum text width as ratio of frame width (0.1 to 1.0)",
        "batch_size": "Number of identical text masks to generate (1 to 10000)"
    })

    # _mfc tooltips
    TooltipManager.register_tooltips("_mfc", {
        "image": "Input image to create mask from (IMAGE type)",
        "red": "Red component of target color (0 to 255)",
        "green": "Green component of target color (0 to 255)",
        "blue": "Blue component of target color (0 to 255)",
        "threshold": "Color matching tolerance (0 to 127)"
    })

    # MaskCompositePlus tooltips
    TooltipManager.register_tooltips("MaskCompositePlus", {
        "mask1": "First input mask (MASK type)",
        "mask2": "Second input mask (MASK type)",
        "operation": "Operation to combine masks ('add', 'subtract', 'multiply', 'divide', 'min', 'max', 'pixel_wise_min', 'pixel_wise_max')"
    })

    # AdvancedLuminanceMask tooltips
    TooltipManager.register_tooltips("AdvancedLuminanceMask", {
        "image": "Input image to create mask from (IMAGE type)",
        "luminance_threshold": "Base threshold for detecting non-background elements (0.0 to 1.0). Lower values catch more subtle details.",
        "glow_radius": "Size of the glow effect in pixels (0 to 50). Higher values create larger, softer glows.",
        "edge_preservation": "How much to preserve sharp edges while allowing glow (0.0 to 1.0). Higher values maintain more edge detail.",
        "background_samples": "Number of corner samples to determine background color (1 to 100). More samples give better background detection.",
        "denoise_strength": "Strength of noise reduction (0.0 to 1.0). Higher values smooth out noise while preserving edges."
    }, description="Creates a sophisticated luminance-based mask that preserves translucency, glows, and gradients while intelligently handling non-pure-black backgrounds.")

    # TranslucentComposite tooltips
    TooltipManager.register_tooltips("TranslucentComposite", {
        "background": "The base image to composite onto (IMAGE type)",
        "foreground": "The image to composite over the background (IMAGE type)",
        "mask": "Mask determining where to apply the composite (MASK type)",
        "blend_mode": """Blending method for the composite:
- normal: Standard alpha compositing
- screen: Brightens the result, good for glows and reflections
- multiply: Darkens the result, good for shadows and dark glass
- overlay: Increases contrast while preserving highlights and shadows""",
        "opacity": "Overall opacity of the composite effect (0.0 to 1.0)",
        "preserve_transparency": "When enabled, uses the foreground's luminance to modify transparency, creating realistic translucent effects",
        "luminance_boost": "Adjusts the brightness of the foreground before compositing (-1.0 to 1.0). Useful for enhancing or subduing glow effects",
        "background_influence": "How much the background colors influence the final result (0.0 to 1.0). Higher values create more realistic integration"
    }, description="Composites a foreground image onto a background with advanced blending modes and transparency preservation, perfect for realistic translucent effects like glasses or holograms.")

    # FlexMaskMorph tooltips (inherits from: FlexMaskBase)
    TooltipManager.register_tooltips("FlexMaskMorph", {
        "morph_type": "Type of morphological operation ('erode', 'dilate', 'open', 'close')",
        "max_kernel_size": "Maximum size of the morphological kernel (3 to 21, odd numbers only)",
        "max_iterations": "Maximum number of times to apply the operation (1 to 50)",
        "feature_param": """Choose which parameter to modulate:
        
- kernel_size: Dynamically adjust the size of the morphological operation
- iterations: Dynamically adjust how many times the operation is applied
- None: No parameter modulation"""
    }, inherits_from='FlexMaskBase')

    # FlexMaskWarp tooltips (inherits from: FlexMaskBase)
    TooltipManager.register_tooltips("FlexMaskWarp", {
        "warp_type": "Type of warping effect ('perlin', 'radial', 'swirl')",
        "frequency": "Controls the scale of the warping effect (0.01 to 1.0)",
        "max_amplitude": "Maximum amplitude of the warping effect (0.1 to 500.0)",
        "octaves": "For noise-based warps, adds detail at different scales (1 to 8)",
        "feature_param": """Choose which parameter to modulate:
        
- amplitude: Dynamically adjust the strength of warping
- frequency: Dynamically adjust the scale of warping
- octaves: Dynamically adjust the detail level of noise
- None: No parameter modulation"""
    }, inherits_from='FlexMaskBase')

    # FlexMaskTransform tooltips (inherits from: FlexMaskBase)
    TooltipManager.register_tooltips("FlexMaskTransform", {
        "transform_type": "Type of transformation ('translate', 'rotate', 'scale')",
        "max_x_value": "Maximum horizontal component of the transformation (-1000.0 to 1000.0)",
        "max_y_value": "Maximum vertical component of the transformation (-1000.0 to 1000.0)",
        "feature_param": """Choose which parameter to modulate:
        
- x_value: Dynamically adjust horizontal transformation
- y_value: Dynamically adjust vertical transformation
- None: No parameter modulation"""
    }, inherits_from='FlexMaskBase')

    # FlexMaskMath tooltips (inherits from: FlexMaskBase)
    TooltipManager.register_tooltips("FlexMaskMath", {
        "mask_b": "Second mask to combine with the input mask (MASK type)",
        "combination_method": "Mathematical operation to apply ('add', 'subtract', 'multiply', 'minimum', 'maximum')",
        "max_blend": "Maximum blend factor between masks (0.0 to 1.0)",
        "feature_param": """Choose which parameter to modulate:
        
- max_blend: Dynamically adjust the blend between masks
- None: No parameter modulation"""
    }, inherits_from='FlexMaskBase')

    # FlexMaskOpacity tooltips (inherits from: FlexMaskBase)
    TooltipManager.register_tooltips("FlexMaskOpacity", {
        "max_opacity": "Maximum opacity to apply to the mask (0.0 to 1.0)",
        "feature_param": """Choose which parameter to modulate:
        
- opacity: Dynamically adjust the mask opacity
- None: No parameter modulation"""
    }, inherits_from='FlexMaskBase')

    # FlexMaskVoronoiScheduled tooltips (inherits from: FlexMaskBase)
    TooltipManager.register_tooltips("FlexMaskVoronoiScheduled", {
        "distance_metric": "Method used to calculate distances in the Voronoi diagram",
        "scale": "Base scale of the Voronoi cells (0.1 to 10.0)",
        "detail": "Number of Voronoi cells (10 to 1000)",
        "randomness": "Degree of randomness in cell placement (0.0 to 5.0)",
        "seed": "Random seed for reproducible results",
        "x_offset": "Horizontal offset of the Voronoi pattern (-1000.0 to 1000.0)",
        "y_offset": "Vertical offset of the Voronoi pattern (-1000.0 to 1000.0)",
        "formula": "Mathematical formula for feature value mapping ('Linear', 'Quadratic', 'Cubic', 'Sinusoidal', 'Exponential')",
        "a": "First parameter for fine-tuning the chosen formula (0.1 to 10.0)",
        "b": "Second parameter for fine-tuning the chosen formula (0.1 to 10.0)",
        "feature_param": """Choose which parameter to modulate:
        
- scale: Dynamically adjust cell size
- detail: Dynamically adjust number of cells
- randomness: Dynamically adjust cell randomness
- seed: Dynamically change pattern
- x_offset: Dynamically adjust horizontal position
- y_offset: Dynamically adjust vertical position
- None: No parameter modulation""",
        "formula": "Mathematical formula for feature value mapping ('Linear', 'Quadratic', 'Cubic', 'Sinusoidal', 'Exponential')",
        "a": "First parameter for fine-tuning the chosen formula (0.1 to 10.0)",
        "b": "Second parameter for fine-tuning the chosen formula (0.1 to 10.0)"
    }, inherits_from='FlexMaskBase')

    # FlexMaskBinary tooltips (inherits from: FlexMaskBase)
    TooltipManager.register_tooltips("FlexMaskBinary", {
        "threshold": "Base threshold value for binarization (0.0 to 1.0)",
        "feature_param": """Choose which parameter to modulate:
        
- threshold: Dynamically adjust the binarization threshold
- None: No parameter modulation"""
    }, inherits_from='FlexMaskBase')

    # FlexMaskWavePropagation tooltips (inherits from: FlexMaskBase)
    TooltipManager.register_tooltips("FlexMaskWavePropagation", {
        "wave_speed": "Speed of wave propagation (0.1 to 100.0)",
        "wave_amplitude": "Amplitude of the wave effect (0.1 to 2.0)",
        "wave_decay": "Rate of wave decay (0.9 to 10.0)",
        "wave_frequency": "Frequency of wave oscillation (0.01 to 10.0)",
        "max_wave_field": "Maximum size of the wave field (10.0 to 10000.0)",
        "feature_param": """Choose which parameter to modulate:
        
- wave_speed: Dynamically adjust propagation speed
- wave_amplitude: Dynamically adjust wave height
- wave_decay: Dynamically adjust decay rate
- wave_frequency: Dynamically adjust oscillation speed
- max_wave_field: Dynamically adjust field size
- None: No parameter modulation"""
    }, inherits_from='FlexMaskBase')

    # FlexMaskEmanatingRings tooltips (inherits from: FlexMaskBase)
    TooltipManager.register_tooltips("FlexMaskEmanatingRings", {
        "ring_speed": "Speed of ring propagation (0.01 to 0.2)",
        "ring_width": "Width of each ring (0.01 to 0.5)",
        "ring_falloff": "Rate at which rings fade out (0.0 to 1.0)",
        "binary_mode": "Whether to output binary rings instead of smooth gradients",
        "feature_param": """Choose which parameter to modulate:
        
- ring_speed: Dynamically adjust propagation speed
- ring_width: Dynamically adjust ring thickness
- ring_falloff: Dynamically adjust ring fade rate
- None: No parameter modulation"""
    }, inherits_from='FlexMaskBase')

    # FlexMaskRandomShapes tooltips (inherits from: FlexMaskBase)
    TooltipManager.register_tooltips("FlexMaskRandomShapes", {
        "max_num_shapes": "Maximum number of shapes to generate (1 to 100)",
        "max_shape_size": "Maximum size of each shape (0.01 to 1.0)",
        "appearance_duration": "Duration of shape appearance (1 to 100 frames)",
        "disappearance_duration": "Duration of shape disappearance (1 to 100 frames)",
        "appearance_method": "Method of shape appearance ('grow', 'pop', 'fade')",
        "easing_function": "Easing function for shape animation ('linear', 'ease_in_out', 'bounce', 'elastic')",
        "shape_type": "Type of shape to generate",
        "feature_param": """Choose which parameter to modulate:
        
- max_num_shapes: Dynamically adjust shape count
- max_shape_size: Dynamically adjust shape size
- appearance_duration: Dynamically adjust fade-in time
- disappearance_duration: Dynamically adjust fade-out time
- None: No parameter modulation"""
    }, inherits_from='FlexMaskBase')

    # FlexMaskDepthChamber tooltips (inherits from: FlexMaskBase)
    TooltipManager.register_tooltips("FlexMaskDepthChamber", {
        "depth_map": "Input depth map (IMAGE type)",
        "z_front": "Front depth threshold (0.0 to 1.0)",
        "z_back": "Back depth threshold (0.0 to 1.0)",
        "feature_mode": "Mode of feature modulation ('squeeze', 'expand', 'move_forward', 'move_back')",
        "feature_param": """Choose which parameter to modulate:
        
- z_front: Dynamically adjust front threshold
- z_back: Dynamically adjust back threshold
- None: No parameter modulation"""
    }, inherits_from='FlexMaskBase')

    # FlexMaskDepthChamberRelative tooltips (inherits from: FlexMaskBase)
    TooltipManager.register_tooltips("FlexMaskDepthChamberRelative", {
        "depth_map": "Input depth map (IMAGE type)",
        "z1": "First depth threshold (0.0 to 1.0)",
        "z2": "Second depth threshold (0.0 to 1.0)",
        "feature_mode": "Mode of feature modulation ('squeeze', 'expand')",
        "feature_param": """Choose which parameter to modulate:
        
- z1: Dynamically adjust first threshold
- z2: Dynamically adjust second threshold
- None: No parameter modulation"""
    }, inherits_from='FlexMaskBase')

    # FlexMaskInterpolate tooltips (inherits from: FlexMaskBase)
    TooltipManager.register_tooltips("FlexMaskInterpolate", {
        "mask_b": "Second mask to interpolate with (MASK type)",
        "interpolation_method": "Method of interpolation ('linear', 'ease_in', 'ease_out', 'ease_in_out', 'cubic', 'sigmoid', 'radial', 'distance_transform', 'random_noise')",
        "max_blend": "Maximum blend factor between masks (0.0 to 1.0)",
        "invert_mask_b": "Whether to invert the second mask before interpolation",
        "blend_mode": "Method for blending masks ('normal', 'add', 'multiply', 'overlay', 'soft_light')",
        "feature_param": """Choose which parameter to modulate:
        
- max_blend: Dynamically adjust blend amount
- None: No parameter modulation"""
    }, inherits_from='FlexMaskBase')

    # FlexMaskNormalLighting tooltips (inherits from: FlexMaskNormalBase)
    TooltipManager.register_tooltips("FlexMaskNormalLighting", {
        "light_direction_x": "X component of light direction (-1.0 to 1.0)",
        "light_direction_y": "Y component of light direction (-1.0 to 1.0)",
        "light_direction_z": "Z component of light direction (-1.0 to 1.0)",
        "shadow_threshold": "Threshold for shadow creation (0.0 to 1.0)",
        "feature_param": "Parameter to modulate based on the feature ('none', 'direction', 'threshold', 'both')",
        "feature_mode": "Mode of feature modulation ('rotate', 'intensity')"
    }, inherits_from='FlexMaskNormalBase')