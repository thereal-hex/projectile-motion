import tkinter as tk
import math
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.patches import Rectangle, Circle, Polygon
import matplotlib.image as mpimg
from matplotlib.animation import FuncAnimation

class EnhancedProjectileSimulator:
    def __init__(self, root):
        self.root = root
        self.root.title("Enhanced Projectile Motion Simulator")
        self.root.geometry("1000x700")
        self.root.configure(bg="#2c3e50")
        
        # Input variables
        self.initial_velocity = tk.DoubleVar(value=20.0)
        self.angle = tk.DoubleVar(value=45.0)
        self.height = tk.DoubleVar(value=1.5)  # Default human throwing height
        self.gravity = tk.DoubleVar(value=9.8)
        self.rock_size = tk.DoubleVar(value=0.2)  # Size of the rock in meters
        
        # Animation variables
        self.anim = None
        self.rock = None
        
        # Create main frame
        main_frame = tk.Frame(root, bg="#2c3e50")
        main_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        
        # Create title
        title_label = tk.Label(main_frame, text="Rock Throwing Simulator", 
                              font=("Arial", 18, "bold"), bg="#2c3e50", fg="#ecf0f1")
        title_label.pack(pady=(0, 10))
        
        # Create left panel with scrollbar for inputs and results
        left_panel_frame = tk.Frame(main_frame, bg="#2c3e50")
        left_panel_frame.pack(side=tk.LEFT, padx=(0, 10), fill=tk.BOTH)
        
        # Add scrollbar to left panel
        left_scrollbar = tk.Scrollbar(left_panel_frame)
        left_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Create canvas for scrollable content
        left_canvas = tk.Canvas(left_panel_frame, bg="#2c3e50", highlightthickness=0, 
                              yscrollcommand=left_scrollbar.set)
        left_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Configure scrollbar
        left_scrollbar.config(command=left_canvas.yview)
        
        # Create frame inside canvas for content
        left_panel = tk.Frame(left_canvas, bg="#2c3e50")
        left_canvas.create_window((0, 0), window=left_panel, anchor="nw", tags="left_panel")
        
        # Formula frame
        formula_frame = tk.LabelFrame(left_panel, text="Physics Formulas", bg="#34495e", fg="#ecf0f1", 
                                    font=("Arial", 12, "bold"), padx=10, pady=10)
        formula_frame.pack(padx=10, pady=10, fill=tk.X)
        
        # Add formulas with labels (increased font size from 9 to 12)
        formula_text = """
Position: x(t) = v₀ cos(θ) · t
          y(t) = h₀ + v₀ sin(θ) · t - ½gt²

Velocity: vₓ(t) = v₀ cos(θ)
          vᵧ(t) = v₀ sin(θ) - gt

Max Height: h_max = h₀ + (v₀ sin(θ))²/(2g)

Range: R = v₀ cos(θ) · [v₀ sin(θ) + √((v₀ sin(θ))² + 2gh₀)]/g

Flight Time: t_flight = [v₀ sin(θ) + √((v₀ sin(θ))² + 2gh₀)]/g

where:
v₀ = initial velocity
θ = launch angle
h₀ = initial height
g = gravity
t = time
        """
        
        formula_label = tk.Label(formula_frame, text=formula_text, justify=tk.LEFT,
                               bg="#34495e", fg="#ecf0f1", font=("Courier", 12))  # Changed from 9 to 12
        formula_label.pack(fill=tk.X, pady=5)
        
        # Input frame
        input_frame = tk.LabelFrame(left_panel, text="Throwing Parameters", bg="#34495e", fg="#ecf0f1", 
                                    font=("Arial", 12, "bold"), padx=10, pady=10)
        input_frame.pack(padx=10, pady=10, fill=tk.X)
        
        # Helper function for creating input rows
        def create_input_row(parent, label_text, variable, unit="", min_val=0, max_val=100, increment=1):
            frame = tk.Frame(parent, bg="#34495e")
            frame.pack(fill=tk.X, pady=5)
            
            # Label
            label = tk.Label(frame, text=label_text, bg="#34495e", fg="#ecf0f1", width=20, anchor="w")
            label.pack(side=tk.LEFT)
            
            # Scale
            scale = tk.Scale(frame, from_=min_val, to=max_val, orient=tk.HORIZONTAL, 
                            variable=variable, resolution=increment, bg="#34495e", fg="#ecf0f1",
                            highlightbackground="#34495e", troughcolor="#2c3e50", activebackground="#3498db")
            scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
            
            # Entry
            entry = tk.Entry(frame, textvariable=variable, width=6, bg="#ecf0f1")
            entry.pack(side=tk.LEFT)
            
            # Unit
            if unit:
                unit_label = tk.Label(frame, text=unit, bg="#34495e", fg="#ecf0f1")
                unit_label.pack(side=tk.LEFT, padx=(2, 0))
                
            return frame
        
        # Create input controls
        create_input_row(input_frame, "Throwing Speed (v₀):", self.initial_velocity, "m/s", 1, 50, 0.5)
        create_input_row(input_frame, "Throwing Angle (θ):", self.angle, "°", 0, 90, 1)
        create_input_row(input_frame, "Throwing Height (h₀):", self.height, "m", 0, 5, 0.1)
        create_input_row(input_frame, "Rock Size:", self.rock_size, "m", 0.1, 1, 0.1)
        
        # Advanced settings expandable section
        advanced_button = tk.Button(input_frame, text="Advanced Settings", 
                                   command=self.toggle_advanced_settings,
                                   bg="#7f8c8d", fg="#ecf0f1", font=("Arial", 10))
        advanced_button.pack(pady=(10, 0), fill=tk.X)
        
        # Hidden advanced frame
        self.advanced_frame = tk.Frame(input_frame, bg="#34495e")
        self.advanced_frame.pack_forget()
        
        create_input_row(self.advanced_frame, "Gravity (g):", self.gravity, "m/s²", 1, 20, 0.1)
        
        # Target frame
        target_frame = tk.LabelFrame(left_panel, text="Target", bg="#34495e", fg="#ecf0f1", 
                                    font=("Arial", 12, "bold"), padx=10, pady=10)
        target_frame.pack(padx=10, pady=10, fill=tk.X)
        
        # Target distance
        self.target_enabled = tk.BooleanVar(value=False)
        self.target_distance = tk.DoubleVar(value=30.0)
        self.target_height = tk.DoubleVar(value=2.0)
        self.target_width = tk.DoubleVar(value=1.0)
        
        # Target checkbox
        target_check = tk.Checkbutton(target_frame, text="Enable Target", variable=self.target_enabled,
                                     bg="#34495e", fg="#ecf0f1", selectcolor="#2c3e50", activebackground="#34495e")
        target_check.pack(fill=tk.X, pady=5)
        
        create_input_row(target_frame, "Target Distance:", self.target_distance, "m", 5, 100, 1)
        create_input_row(target_frame, "Target Height:", self.target_height, "m", 0.5, 10, 0.5)
        create_input_row(target_frame, "Target Width:", self.target_width, "m", 0.5, 5, 0.5)
        
        # Results frame
        results_frame = tk.LabelFrame(left_panel, text="Flight Results", bg="#34495e", fg="#ecf0f1", 
                                     font=("Arial", 12, "bold"), padx=10, pady=10)
        results_frame.pack(padx=10, pady=10, fill=tk.X)
        
        self.result_labels = {
            "max_height": tk.StringVar(value="Maximum Height: --"),
            "distance": tk.StringVar(value="Range: --"),
            "flight_time": tk.StringVar(value="Flight Time: --"),
            "target_hit": tk.StringVar(value="Target Hit: --")
        }
        
        for key, var in self.result_labels.items():
            result_frame = tk.Frame(results_frame, bg="#34495e")
            result_frame.pack(fill=tk.X, pady=3)
            tk.Label(result_frame, textvariable=var, bg="#34495e", fg="#ecf0f1").pack(side=tk.LEFT)
        
        # Button frame
        button_frame = tk.Frame(left_panel, bg="#2c3e50")
        button_frame.pack(padx=10, pady=10, fill=tk.X)
        
        # Calculate button
        calculate_button = tk.Button(button_frame, text="Throw Rock!", command=self.calculate,
                                   bg="#e74c3c", fg="white", font=("Arial", 12, "bold"),
                                   padx=10, pady=10, relief=tk.RAISED)
        calculate_button.pack(fill=tk.X, pady=5)
        
        # Animation button
        self.animate_button = tk.Button(button_frame, text="Animate Throw", command=self.toggle_animation,
                                      bg="#3498db", fg="white", font=("Arial", 12, "bold"),
                                      padx=10, pady=10, relief=tk.RAISED, state=tk.DISABLED)
        self.animate_button.pack(fill=tk.X, pady=5)
        
        # Plot frame (right panel)
        plot_frame = tk.Frame(main_frame, bg="#2c3e50")
        plot_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Create plot
        self.figure = plt.Figure(figsize=(8, 6), dpi=100, facecolor="#2c3e50")
        self.ax = self.figure.add_subplot(111, facecolor="#1e272e")
        self.canvas = FigureCanvasTkAgg(self.figure, plot_frame)
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        
        # Configure plot
        self.ax.set_xlabel('Distance (m)', color="#ecf0f1")
        self.ax.set_ylabel('Height (m)', color="#ecf0f1")
        self.ax.set_title('Rock Trajectory', color="#ecf0f1", fontsize=14)
        self.ax.tick_params(colors="#ecf0f1")
        self.ax.grid(True, alpha=0.3)
        self.figure.tight_layout()
        
        # Initialize scene
        self.initialize_scene()
        
        # Status bar
        status_frame = tk.Frame(main_frame, bg="#34495e", height=25)
        status_frame.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.status_var = tk.StringVar(value="Ready to throw! Adjust parameters and click 'Throw Rock!'")
        status_label = tk.Label(status_frame, textvariable=self.status_var, bg="#34495e", fg="#ecf0f1", anchor="w", padx=10)
        status_label.pack(side=tk.LEFT, fill=tk.X)
        
        # Update scrollregion after all widgets are added
        left_panel.update_idletasks()
        left_canvas.config(scrollregion=left_canvas.bbox("all"))
        
        # Bind mouse wheel to scroll
        left_canvas.bind_all("<MouseWheel>", lambda event: left_canvas.yview_scroll(int(-1*(event.delta/120)), "units"))
        # For Linux systems
        left_canvas.bind_all("<Button-4>", lambda event: left_canvas.yview_scroll(-1, "units"))
        left_canvas.bind_all("<Button-5>", lambda event: left_canvas.yview_scroll(1, "units"))
    
    def toggle_advanced_settings(self):
        if self.advanced_frame.winfo_ismapped():
            self.advanced_frame.pack_forget()
        else:
            self.advanced_frame.pack(fill=tk.X, pady=5)
    
    def toggle_animation(self):
        if self.anim is None or not self.anim.event_source:
            self.animate_throw()
            self.animate_button.config(text="Stop Animation")
        else:
            if self.anim:
                self.anim.event_source.stop()
                self.anim = None
            self.animate_button.config(text="Animate Throw")
    
    def initialize_scene(self):
        # Clear the plot
        self.ax.clear()
        
        # Set plot limits with margins for the ground and sky
        self.ax.set_xlim(-5, 50)
        self.ax.set_ylim(-1, 20)
        
        # Draw ground
        ground = Rectangle((-5, -1), 60, 1, color='#7f8c8d')
        self.ax.add_patch(ground)
        
        # Draw grass
        for i in range(0, 55, 2):
            grass_height = 0.2 + 0.1 * np.random.random()
            grass = Rectangle((i-5, 0), 0.1, grass_height, color='#27ae60')
            self.ax.add_patch(grass)
        
        # Draw trees (at random positions)
        self.draw_tree(10, 0, height=5)
        self.draw_tree(25, 0, height=6)
        self.draw_tree(40, 0, height=4.5)
        
        # Draw person
        self.draw_person(0, 0)
        
        # Configure plot
        self.ax.set_xlabel('Distance (m)', color="#ecf0f1")
        self.ax.set_ylabel('Height (m)', color="#ecf0f1")
        self.ax.set_title('Rock Trajectory', color="#ecf0f1", fontsize=14)
        self.ax.tick_params(colors="#ecf0f1")
        for spine in self.ax.spines.values():
            spine.set_color('#7f8c8d')
        self.ax.grid(True, alpha=0.3)
        
        # Update canvas
        self.canvas.draw()
    
    def draw_person(self, x, y):
        # Draw stick figure
        # Head
        head = Circle((x, y+1.7), 0.3, color='#f39c12')
        self.ax.add_patch(head)
        
        # Body
        self.ax.plot([x, x], [y+1.4, y+0.7], color='#f39c12', linewidth=3)
        
        # Arms
        self.ax.plot([x, x+0.5], [y+1.2, y+1.3], color='#f39c12', linewidth=2)  # Right arm raised
        
        # Legs
        self.ax.plot([x, x-0.3], [y+0.7, y], color='#f39c12', linewidth=2)  # Left leg
        self.ax.plot([x, x+0.3], [y+0.7, y], color='#f39c12', linewidth=2)  # Right leg
    
    def draw_tree(self, x, y, height=5):
        # Draw trunk
        trunk = Rectangle((x-0.5, y), 1, height*0.4, color='#795548')
        self.ax.add_patch(trunk)
        
        # Draw foliage (triangle)
        tree_width = height * 0.6
        tree_top = y + height
        
        foliage = Polygon([
            [x-tree_width/2, y+height*0.3],  # Left bottom
            [x+tree_width/2, y+height*0.3],  # Right bottom
            [x, tree_top]                     # Top
        ], closed=True, color='#2ecc71')
        self.ax.add_patch(foliage)
    
    def draw_target(self, x, y, width, height):
        # Draw target
        target = Rectangle((x, y), width, height, color='#e74c3c', alpha=0.8)
        self.ax.add_patch(target)
        
        # Draw bullseye
        bullseye_x = x + width/2
        bullseye_y = y + height/2
        bullseye_size = min(width, height) * 0.3
        
        # Outer ring
        outer_ring = Circle((bullseye_x, bullseye_y), bullseye_size, color='white')
        self.ax.add_patch(outer_ring)
        
        # Inner ring
        inner_ring = Circle((bullseye_x, bullseye_y), bullseye_size*0.6, color='#e74c3c')
        self.ax.add_patch(inner_ring)
        
        # Center
        center = Circle((bullseye_x, bullseye_y), bullseye_size*0.2, color='white')
        self.ax.add_patch(center)
    
    def calculate(self):
        try:
            # Get values from inputs
            v0 = self.initial_velocity.get()
            angle_deg = self.angle.get()
            h0 = self.height.get()
            g = self.gravity.get()
            rock_size = self.rock_size.get()
            
            # Validate inputs
            if v0 <= 0 or g <= 0:
                self.status_var.set("Error: Velocity and gravity must be positive values!")
                return
            
            # Convert angle to radians
            angle_rad = math.radians(angle_deg)
            
            # Calculate trajectory and plot
            self.trajectory_data = self.calculate_trajectory(v0, angle_rad, h0, g)
            
            # Enable animation button
            self.animate_button.config(state=tk.NORMAL)
            
            # Plot trajectory
            self.plot_trajectory(self.trajectory_data, rock_size)
            
            # Set status
            self.status_var.set("Rock thrown! Click 'Animate Throw' to see animation.")
            
        except Exception as e:
            self.status_var.set(f"Error: {str(e)}")
    
    def calculate_trajectory(self, v0, angle_rad, h0, g):
        # Calculate velocity components
        v0x = v0 * math.cos(angle_rad)
        v0y = v0 * math.sin(angle_rad)
        
        # Calculate time when projectile hits the ground
        # Using quadratic formula: h0 + v0y*t - 0.5*g*t^2 = 0
        # at^2 + bt + c = 0, where a = -0.5*g, b = v0y, c = h0
        discriminant = v0y**2 + 2*g*h0
        
        if discriminant >= 0:
            t_flight = (v0y + math.sqrt(discriminant)) / g
        else:
            # If it won't reach the ground (this shouldn't happen in normal cases)
            t_flight = 0
            
        # Calculate range
        distance = v0x * t_flight
        
        # Calculate maximum height time
        t_max_height = v0y / g if v0y > 0 else 0
        
        # Calculate maximum height
        max_height = h0 + v0y**2 / (2*g) if v0y > 0 else h0
        
        # Create time points for trajectory
        if t_flight > 0:
            num_points = 200
            t = np.linspace(0, t_flight, num_points)
            
            # Calculate x and y coordinates
            x = v0x * t
            y = h0 + v0y * t - 0.5 * g * t**2
            
            # Check if target is hit
            target_hit = False
            hit_time = None
            
            if self.target_enabled.get():
                target_x = self.target_distance.get()
                target_y = 0
                target_height = self.target_height.get()
                target_width = self.target_width.get()
                
                # Check if any point of trajectory is within target
                for i in range(len(t)-1):
                    if (target_x <= x[i] <= target_x + target_width and
                        target_y <= y[i] <= target_y + target_height):
                        target_hit = True
                        hit_time = t[i]
                        break
            
            # Update result labels
            self.result_labels["max_height"].set(f"Maximum Height: {max_height:.2f} m")
            self.result_labels["distance"].set(f"Range: {distance:.2f} m")
            self.result_labels["flight_time"].set(f"Flight Time: {t_flight:.2f} s")
            
            if self.target_enabled.get():
                if target_hit:
                    self.result_labels["target_hit"].set(f"Target Hit: Yes! At {hit_time:.2f} s")
                else:
                    self.result_labels["target_hit"].set("Target Hit: No")
            else:
                self.result_labels["target_hit"].set("Target Hit: No target set")
            
            # Return trajectory data
            return {
                "times": t,
                "x": x,
                "y": y,
                "v0x": v0x,
                "v0y": v0y,
                "max_height": max_height,
                "distance": distance,
                "flight_time": t_flight,
                "max_height_time": t_max_height,
                "target_hit": target_hit,
                "hit_time": hit_time
            }
        else:
            self.status_var.set("Error: Invalid trajectory - Check your parameters")
            return None
    
    def plot_trajectory(self, data, rock_size):
        if data is None:
            return
        
        # Reinitialize the scene
        self.initialize_scene()
        
        # Plot trajectory path
        self.ax.plot(data["x"], data["y"], 'white', linestyle='--', alpha=0.7, linewidth=1.5)
        
        # Get plot limits
        x_max = max(50, data["distance"] * 1.1)
        y_max = max(20, data["max_height"] * 1.2)
        self.ax.set_xlim(-5, x_max)
        self.ax.set_ylim(-1, y_max)
        
        # Draw the target if enabled
        if self.target_enabled.get():
            target_x = self.target_distance.get()
            target_height = self.target_height.get()
            target_width = self.target_width.get()
            self.draw_target(target_x, 0, target_width, target_height)
        
        # Draw rock at final position
        rock_x = data["distance"]
        rock_y = 0
        final_rock = Circle((rock_x, rock_y), rock_size, color='#95a5a6')
        self.ax.add_patch(final_rock)
        
        # Draw rock at peak position
        if data["max_height_time"] > 0:
            peak_x = data["v0x"] * data["max_height_time"]
            peak_rock = Circle((peak_x, data["max_height"]), rock_size, color='#95a5a6', alpha=0.5)
            self.ax.add_patch(peak_rock)
        
        # Draw annotations
        # Maximum height
        if data["max_height_time"] > 0:
            peak_x = data["v0x"] * data["max_height_time"]
            self.ax.annotate(f'Max Height: {data["max_height"]:.2f} m', 
                             xy=(peak_x, data["max_height"]), 
                             xytext=(peak_x+2, data["max_height"]+1),
                             arrowprops=dict(facecolor='white', shrink=0.05, width=1.5, headwidth=8),
                             color='white')
        
        # Range
        self.ax.annotate(f'Range: {data["distance"]:.2f} m', 
                         xy=(data["distance"], 0.2), 
                         xytext=(data["distance"]-5, 2),
                         arrowprops=dict(facecolor='white', shrink=0.05, width=1.5, headwidth=8),
                         color='white')
        
        # Initial velocity vector
        arrow_length = data["v0x"] * 0.5
        arrow_height = data["v0y"] * 0.5
        self.ax.arrow(0, data["y"][0], arrow_length, arrow_height, 
                     head_width=0.5, head_length=1, fc='#e74c3c', ec='#e74c3c', linewidth=2)
        
        self.ax.text(arrow_length/2, data["y"][0] + arrow_height/2 + 0.5, 
                    f'{self.initial_velocity.get():.1f} m/s', color='#e74c3c')
        
        # Update canvas
        self.canvas.draw()
    
    def animate_throw(self):
        if not hasattr(self, 'trajectory_data') or self.trajectory_data is None:
            self.status_var.set("Calculate the trajectory first!")
            return
        
        # Stop any existing animation
        if self.anim and self.anim.event_source:
            self.anim.event_source.stop()
            self.anim = None
            
        # Re-draw the scene to prevent flickering
        self.plot_trajectory(self.trajectory_data, self.rock_size.get())
            
        # Create rock object if it doesn't exist
        rock_size = self.rock_size.get()
        self.rock = Circle((0, self.height.get()), rock_size, color='#95a5a6')
        self.ax.add_patch(self.rock)
        
        # Create a list to keep track of artists that need updating
        self.animated_artists = [self.rock]
        
        # Animation function
        def update(frame_num):
            # Get the position at this frame
            if frame_num < len(self.trajectory_data["times"]):
                x = self.trajectory_data["x"][frame_num]
                y = self.trajectory_data["y"][frame_num]
                self.rock.center = (x, y)
                
                # Update status bar with current time and position
                time = self.trajectory_data["times"][frame_num]
                self.status_var.set(f"Time: {time:.2f}s | Position: ({x:.2f}m, {y:.2f}m)")
                
                # Handle target hit
                if (self.target_enabled.get() and self.trajectory_data["target_hit"] and 
                    self.trajectory_data["hit_time"] <= time and 
                    self.trajectory_data["hit_time"] >= self.trajectory_data["times"][max(0, frame_num-1)]):
                    self.status_var.set("TARGET HIT! 🎯")
            
            return self.animated_artists
        
        # Create animation with blitting to prevent flickering
        frames = len(self.trajectory_data["times"])
        interval = max(10, self.trajectory_data["flight_time"]*1000/frames)  # Ensure minimum interval
        
        self.anim = FuncAnimation(
            self.figure, update, frames=frames, 
            interval=interval,  # Total duration in ms
            blit=True, repeat=True
        )
        
        # Draw once to ensure everything is visible
        self.canvas.draw()

if __name__ == "__main__":
    root = tk.Tk()
    app = EnhancedProjectileSimulator(root)
    root.mainloop()
