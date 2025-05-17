import tkinter as tk
import math
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class ProjectileMotionSimulator:
    def __init__(self, root):
        self.root = root
        self.root.title("Projectile Motion Simulator")
        self.root.geometry("800x600")
        self.root.configure(bg="#f0f0f0")
        
        # Input variables
        self.initial_velocity = tk.DoubleVar(value=20.0)
        self.angle = tk.DoubleVar(value=45.0)
        self.height = tk.DoubleVar(value=0.0)
        self.gravity = tk.DoubleVar(value=9.8)
        
        # Create main frame
        main_frame = tk.Frame(root, bg="#f0f0f0")
        main_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        
        # Input frame
        input_frame = tk.LabelFrame(main_frame, text="Input Parameters", bg="#f0f0f0", font=("Arial", 12, "bold"))
        input_frame.pack(padx=10, pady=10, fill=tk.X)
        
        # Initial velocity
        velocity_frame = tk.Frame(input_frame, bg="#f0f0f0")
        velocity_frame.pack(fill=tk.X, padx=5, pady=5)
        tk.Label(velocity_frame, text="Initial Velocity (m/s):", bg="#f0f0f0", width=20, anchor="w").pack(side=tk.LEFT)
        tk.Entry(velocity_frame, textvariable=self.initial_velocity, width=10).pack(side=tk.LEFT, padx=5)
        
        # Launch angle
        angle_frame = tk.Frame(input_frame, bg="#f0f0f0")
        angle_frame.pack(fill=tk.X, padx=5, pady=5)
        tk.Label(angle_frame, text="Launch Angle (degrees):", bg="#f0f0f0", width=20, anchor="w").pack(side=tk.LEFT)
        tk.Entry(angle_frame, textvariable=self.angle, width=10).pack(side=tk.LEFT, padx=5)
        
        # Initial height
        height_frame = tk.Frame(input_frame, bg="#f0f0f0")
        height_frame.pack(fill=tk.X, padx=5, pady=5)
        tk.Label(height_frame, text="Initial Height (m):", bg="#f0f0f0", width=20, anchor="w").pack(side=tk.LEFT)
        tk.Entry(height_frame, textvariable=self.height, width=10).pack(side=tk.LEFT, padx=5)
        
        # Gravity
        gravity_frame = tk.Frame(input_frame, bg="#f0f0f0")
        gravity_frame.pack(fill=tk.X, padx=5, pady=5)
        tk.Label(gravity_frame, text="Gravity (m/s²):", bg="#f0f0f0", width=20, anchor="w").pack(side=tk.LEFT)
        tk.Entry(gravity_frame, textvariable=self.gravity, width=10).pack(side=tk.LEFT, padx=5)
        
        # Calculate button
        button_frame = tk.Frame(input_frame, bg="#f0f0f0")
        button_frame.pack(fill=tk.X, padx=5, pady=10)
        tk.Button(button_frame, text="Calculate and Display", command=self.calculate, 
                  bg="#4CAF50", fg="white", font=("Arial", 10, "bold"), 
                  padx=10, pady=5).pack(pady=5)
        
        # Results frame
        self.results_frame = tk.LabelFrame(main_frame, text="Calculation Results", bg="#f0f0f0", font=("Arial", 12, "bold"))
        self.results_frame.pack(padx=10, pady=10, fill=tk.X)
        
        self.result_labels = {
            "max_height": tk.StringVar(value="Maximum Height: --"),
            "distance": tk.StringVar(value="Range: --"),
            "flight_time": tk.StringVar(value="Flight Time: --")
        }
        
        for key, var in self.result_labels.items():
            result_frame = tk.Frame(self.results_frame, bg="#f0f0f0")
            result_frame.pack(fill=tk.X, padx=5, pady=5)
            tk.Label(result_frame, textvariable=var, bg="#f0f0f0").pack(side=tk.LEFT)
        
        # Plot frame
        plot_frame = tk.LabelFrame(main_frame, text="Trajectory", bg="#f0f0f0", font=("Arial", 12, "bold"))
        plot_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        
        # Create plot
        self.figure = plt.Figure(figsize=(6, 4), dpi=100)
        self.ax = self.figure.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.figure, plot_frame)
        self.canvas.get_tk_widget().pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Configure plot
        self.ax.set_xlabel('Horizontal Distance (m)')
        self.ax.set_ylabel('Height (m)')
        self.ax.set_title('Projectile Motion Trajectory')
        self.ax.grid(True)
        
        # Initialize an empty plot
        self.plot_trajectory(20, math.radians(45), 0, 9.8)
        
    def calculate(self):
        try:
            # Get values from inputs
            v0 = self.initial_velocity.get()
            angle_deg = self.angle.get()
            h0 = self.height.get()
            g = self.gravity.get()
            
            # Validate inputs
            if v0 <= 0 or g <= 0:
                tk.messagebox.showerror("Input Error", "Velocity and gravity must be positive values!")
                return
            
            # Convert angle to radians
            angle_rad = math.radians(angle_deg)
            
            # Plot trajectory
            self.plot_trajectory(v0, angle_rad, h0, g)
            
        except Exception as e:
            tk.messagebox.showerror("Error", f"An error occurred: {str(e)}")
    
    def plot_trajectory(self, v0, angle_rad, h0, g):
        # Clear previous plot
        self.ax.clear()
        
        # Calculate velocity components
        v0x = v0 * math.cos(angle_rad)
        v0y = v0 * math.sin(angle_rad)
        
        # Calculate flight time
        # For the case where the projectile returns to the same height
        # Using the quadratic formula: h0 + v0y*t - 0.5*g*t^2 = 0
        if v0y**2 + 2*g*h0 >= 0:  # Check if projectile will reach the ground
            t_flight = (v0y + math.sqrt(v0y**2 + 2*g*h0)) / g
        else:
            # If it won't reach the ground (e.g., thrown downward with insufficient velocity)
            t_flight = 0
            
        # Calculate range
        distance = v0x * t_flight
        
        # Calculate maximum height time
        t_max_height = v0y / g if v0y > 0 else 0
        
        # Calculate maximum height
        max_height = h0 + v0y**2 / (2*g) if v0y > 0 else h0
        
        # Update result labels
        self.result_labels["max_height"].set(f"Maximum Height: {max_height:.2f} m")
        self.result_labels["distance"].set(f"Range: {distance:.2f} m")
        self.result_labels["flight_time"].set(f"Flight Time: {t_flight:.2f} s")
        
        # Create time points for plotting
        if t_flight > 0:
            # Create more points for a smoother curve
            num_points = 200
            t = np.linspace(0, t_flight, num_points)
            
            # Calculate x and y coordinates
            x = v0x * t
            y = h0 + v0y * t - 0.5 * g * t**2
            
            # Plot trajectory
            self.ax.plot(x, y, 'b-', linewidth=2)
            
            # Plot start and end points
            self.ax.scatter([0], [h0], color='green', s=50, label='Start')
            self.ax.scatter([distance], [0], color='red', s=50, label='Landing')
            
            # Plot maximum height point
            if t_max_height > 0 and t_max_height < t_flight:
                max_height_x = v0x * t_max_height
                self.ax.scatter([max_height_x], [max_height], color='orange', s=50, label='Max Height')
            
            # Set plot limits with proper margins
            x_margin = max(distance * 0.1, 1)
            y_margin = max(max_height * 0.1, 1)
            
            self.ax.set_xlim(-x_margin, distance + x_margin)
            self.ax.set_ylim(-y_margin, max_height + y_margin)
        else:
            self.ax.text(0.5, 0.5, 'Invalid trajectory - Check your parameters', 
                         horizontalalignment='center', verticalalignment='center',
                         transform=self.ax.transAxes)
        
        # Set plot labels and grid
        self.ax.set_xlabel('Horizontal Distance (m)')
        self.ax.set_ylabel('Height (m)')
        self.ax.set_title('Projectile Motion Trajectory')
        self.ax.grid(True)
        self.ax.legend()
        
        # Update canvas
        self.canvas.draw()

if __name__ == "__main__":
    root = tk.Tk()
    app = ProjectileMotionSimulator(root)
    root.mainloop()
