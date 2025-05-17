import math
import numpy as np
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.slider import Slider
from kivy.uix.checkbox import CheckBox
from kivy.uix.textinput import TextInput
from kivy.garden.matplotlib.backend_kivyagg import FigureCanvasKivyAgg
from kivy.uix.gridlayout import GridLayout
from kivy.clock import Clock
from kivy.uix.scrollview import ScrollView
from kivy.properties import NumericProperty, BooleanProperty, StringProperty
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle, Polygon
from kivy.config import Config

# Set up configuration
Config.set('graphics', 'width', '800')
Config.set('graphics', 'height', '600')

class ProjectileSimulator(BoxLayout):
    initial_velocity = NumericProperty(20.0)
    angle = NumericProperty(45.0)
    height = NumericProperty(1.5)
    gravity = NumericProperty(9.8)
    rock_size = NumericProperty(0.2)
    target_enabled = BooleanProperty(False)
    target_distance = NumericProperty(30.0)
    target_height = NumericProperty(2.0)
    target_width = NumericProperty(1.0)
    status_text = StringProperty("Ready to throw! Adjust parameters and click 'Throw Rock!'")
    
    def __init__(self, **kwargs):
        super(ProjectileSimulator, self).__init__(**kwargs)
        self.orientation = 'horizontal'
        self.padding = 10
        self.spacing = 10
        
        # Left panel for controls
        left_panel = ScrollView(size_hint=(0.4, 1))
        control_layout = BoxLayout(orientation='vertical', size_hint=(1, None), spacing=10)
        control_layout.bind(minimum_height=control_layout.setter('height'))
        
        # Title
        title = Label(text="Rock Throwing Simulator", font_size=24, size_hint=(1, None), height=40)
        control_layout.add_widget(title)
        
        # Parameters section
        param_section = self.create_section("Throwing Parameters")
        
        # Velocity slider
        param_section.add_widget(self.create_slider_row("Throwing Speed (m/s):", 1, 50, 0.5, self.initial_velocity, self.set_velocity))
        
        # Angle slider
        param_section.add_widget(self.create_slider_row("Throwing Angle (°):", 0, 90, 1, self.angle, self.set_angle))
        
        # Height slider
        param_section.add_widget(self.create_slider_row("Throwing Height (m):", 0, 5, 0.1, self.height, self.set_height))
        
        # Rock size slider
        param_section.add_widget(self.create_slider_row("Rock Size (m):", 0.1, 1, 0.1, self.rock_size, self.set_rock_size))
        
        # Advanced button
        adv_button = Button(text="Advanced Settings", size_hint=(1, None), height=40)
        adv_button.bind(on_press=self.toggle_advanced)
        param_section.add_widget(adv_button)
        
        # Advanced settings (initially hidden)
        self.adv_section = BoxLayout(orientation='vertical', size_hint=(1, None), height=0, opacity=0)
        self.adv_section.add_widget(self.create_slider_row("Gravity (m/s²):", 1, 20, 0.1, self.gravity, self.set_gravity))
        param_section.add_widget(self.adv_section)
        
        control_layout.add_widget(param_section)
        
        # Target section
        target_section = self.create_section("Target")
        
        # Target checkbox
        target_row = BoxLayout(orientation='horizontal', size_hint=(1, None), height=40)
        target_check = CheckBox(active=self.target_enabled, size_hint=(None, 1), width=30)
        target_check.bind(active=self.set_target_enabled)
        target_row.add_widget(target_check)
        target_row.add_widget(Label(text="Enable Target", halign='left', valign='middle', text_size=(None, 40)))
        target_section.add_widget(target_row)
        
        # Target distance slider
        target_section.add_widget(self.create_slider_row("Target Distance (m):", 5, 100, 1, self.target_distance, self.set_target_distance))
        
        # Target height slider
        target_section.add_widget(self.create_slider_row("Target Height (m):", 0.5, 10, 0.5, self.target_height, self.set_target_height))
        
        # Target width slider
        target_section.add_widget(self.create_slider_row("Target Width (m):", 0.5, 5, 0.5, self.target_width, self.set_target_width))
        
        control_layout.add_widget(target_section)
        
        # Results section
        results_section = self.create_section("Flight Results")
        
        self.max_height_label = Label(text="Maximum Height: --", size_hint=(1, None), height=30, halign='left')
        self.max_height_label.bind(size=self.max_height_label.setter('text_size'))
        
        self.distance_label = Label(text="Range: --", size_hint=(1, None), height=30, halign='left')
        self.distance_label.bind(size=self.distance_label.setter('text_size'))
        
        self.flight_time_label = Label(text="Flight Time: --", size_hint=(1, None), height=30, halign='left')
        self.flight_time_label.bind(size=self.flight_time_label.setter('text_size'))
        
        self.target_hit_label = Label(text="Target Hit: --", size_hint=(1, None), height=30, halign='left')
        self.target_hit_label.bind(size=self.target_hit_label.setter('text_size'))
        
        results_section.add_widget(self.max_height_label)
        results_section.add_widget(self.distance_label)
        results_section.add_widget(self.flight_time_label)
        results_section.add_widget(self.target_hit_label)
        
        control_layout.add_widget(results_section)
        
        # Buttons
        buttons_layout = BoxLayout(orientation='vertical', size_hint=(1, None), height=100, spacing=10)
        
        self.throw_button = Button(text="Throw Rock!", size_hint=(1, None), height=50)
        self.throw_button.bind(on_press=self.calculate)
        
        self.animate_button = Button(text="Animate Throw", size_hint=(1, None), height=50, disabled=True)
        self.animate_button.bind(on_press=self.toggle_animation)
        
        buttons_layout.add_widget(self.throw_button)
        buttons_layout.add_widget(self.animate_button)
        
        control_layout.add_widget(buttons_layout)
        
        # Status bar
        self.status_bar = Label(text=self.status_text, size_hint=(1, None), height=30, halign='left')
        self.status_bar.bind(size=self.status_bar.setter('text_size'))
        control_layout.add_widget(self.status_bar)
        
        left_panel.add_widget(control_layout)
        self.add_widget(left_panel)
        
        # Right panel for plot
        self.plot_layout = BoxLayout(orientation='vertical', size_hint=(0.6, 1))
        self.setup_plot()
        self.add_widget(self.plot_layout)
        
        # Animation variables
        self.animation_event = None
        self.frame_num = 0
        self.rock = None
    
    def create_section(self, title):
        section = BoxLayout(orientation='vertical', size_hint=(1, None), spacing=5)
        section.bind(minimum_height=section.setter('height'))
        
        title_label = Label(text=title, font_size=18, size_hint=(1, None), height=40)
        section.add_widget(title_label)
        
        return section
    
    def create_slider_row(self, label_text, min_val, max_val, step, initial_val, callback):
        row = BoxLayout(orientation='horizontal', size_hint=(1, None), height=40)
        
        label = Label(text=label_text, size_hint=(0.4, 1), halign='left', valign='middle')
        label.bind(size=label.setter('text_size'))
        
        slider = Slider(min=min_val, max=max_val, step=step, value=initial_val, size_hint=(0.4, 1))
        
        value_input = TextInput(text=str(initial_val), multiline=False, size_hint=(0.2, 1))
        
        # Connect slider and text input
        slider.bind(value=callback)
        value_input.bind(text=self.on_text_value)
        self.bind(**{str(initial_val).replace('.', '_'): self.update_text_value})
        
        row.add_widget(label)
        row.add_widget(slider)
        row.add_widget(value_input)
        
        # Store text input reference for updates
        setattr(self, f"{label_text.split('(')[0].strip().lower().replace(' ', '_')}_input", value_input)
        
        return row
    
    def on_text_value(self, instance, value):
        try:
            property_name = None
            if instance == getattr(self, "throwing_speed_input", None):
                property_name = "initial_velocity"
            elif instance == getattr(self, "throwing_angle_input", None):
                property_name = "angle"
            elif instance == getattr(self, "throwing_height_input", None):
                property_name = "height"
            elif instance == getattr(self, "rock_size_input", None):
                property_name = "rock_size"
            elif instance == getattr(self, "gravity_input", None):
                property_name = "gravity"
            elif instance == getattr(self, "target_distance_input", None):
                property_name = "target_distance"
            elif instance == getattr(self, "target_height_input", None):
                property_name = "target_height"
            elif instance == getattr(self, "target_width_input", None):
                property_name = "target_width"
                
            if property_name:
                setattr(self, property_name, float(value))
        except:
            pass
    
    def update_text_value(self, instance, value):
        property_name = None
        if property_name == "initial_velocity":
            getattr(self, "throwing_speed_input").text = str(value)
        elif property_name == "angle":
            getattr(self, "throwing_angle_input").text = str(value)
        elif property_name == "height":
            getattr(self, "throwing_height_input").text = str(value)
        elif property_name == "rock_size":
            getattr(self, "rock_size_input").text = str(value)
        elif property_name == "gravity":
            getattr(self, "gravity_input").text = str(value)
        elif property_name == "target_distance":
            getattr(self, "target_distance_input").text = str(value)
        elif property_name == "target_height":
            getattr(self, "target_height_input").text = str(value)
        elif property_name == "target_width":
            getattr(self, "target_width_input").text = str(value)
    
    def set_velocity(self, instance, value):
        self.initial_velocity = value
        if hasattr(self, "throwing_speed_input"):
            self.throwing_speed_input.text = f"{value:.1f}"
    
    def set_angle(self, instance, value):
        self.angle = value
        if hasattr(self, "throwing_angle_input"):
            self.throwing_angle_input.text = f"{value:.1f}"
    
    def set_height(self, instance, value):
        self.height = value
        if hasattr(self, "throwing_height_input"):
            self.throwing_height_input.text = f"{value:.1f}"
    
    def set_rock_size(self, instance, value):
        self.rock_size = value
        if hasattr(self, "rock_size_input"):
            self.rock_size_input.text = f"{value:.1f}"
    
    def set_gravity(self, instance, value):
        self.gravity = value
        if hasattr(self, "gravity_input"):
            self.gravity_input.text = f"{value:.1f}"
    
    def set_target_enabled(self, instance, value):
        self.target_enabled = value
    
    def set_target_distance(self, instance, value):
        self.target_distance = value
        if hasattr(self, "target_distance_input"):
            self.target_distance_input.text = f"{value:.1f}"
    
    def set_target_height(self, instance, value):
        self.target_height = value
        if hasattr(self, "target_height_input"):
            self.target_height_input.text = f"{value:.1f}"
    
    def set_target_width(self, instance, value):
        self.target_width = value
        if hasattr(self, "target_width_input"):
            self.target_width_input.text = f"{value:.1f}"
    
    def toggle_advanced(self, instance):
        if self.adv_section.opacity == 0:
            self.adv_section.height = 50
            self.adv_section.opacity = 1
        else:
            self.adv_section.height = 0
            self.adv_section.opacity = 0
    
    def setup_plot(self):
        self.figure = plt.Figure(figsize=(6, 4), dpi=100)
        self.ax = self.figure.add_subplot(111)
        self.canvas = FigureCanvasKivyAgg(self.figure)
        self.plot_layout.clear_widgets()
        self.plot_layout.add_widget(self.canvas)
        self.initialize_scene()
    
    def initialize_scene(self):
        self.ax.clear()
        
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
        
        # Draw trees
        self.draw_tree(10, 0, height=5)
        self.draw_tree(25, 0, height=6)
        self.draw_tree(40, 0, height=4.5)
        
        # Draw person
        self.draw_person(0, 0)
        
        self.ax.set_xlabel('Distance (m)')
        self.ax.set_ylabel('Height (m)')
        self.ax.set_title('Rock Trajectory')
        self.ax.grid(True, alpha=0.3)
        
        self.canvas.draw()
    
    def draw_person(self, x, y):
        head = Circle((x, y+1.7), 0.3, color='#f39c12')
        self.ax.add_patch(head)
        
        self.ax.plot([x, x], [y+1.4, y+0.7], color='#f39c12', linewidth=3)
        self.ax.plot([x, x+0.5], [y+1.2, y+1.3], color='#f39c12', linewidth=2)
        self.ax.plot([x, x-0.3], [y+0.7, y], color='#f39c12', linewidth=2)
        self.ax.plot([x, x+0.3], [y+0.7, y], color='#f39c12', linewidth=2)
    
    def draw_tree(self, x, y, height=5):
        trunk = Rectangle((x-0.5, y), 1, height*0.4, color='#795548')
        self.ax.add_patch(trunk)
        
        tree_width = height * 0.6
        tree_top = y + height
        
        foliage = Polygon([
            [x-tree_width/2, y+height*0.3],
            [x+tree_width/2, y+height*0.3],
            [x, tree_top]
        ], closed=True, color='#2ecc71')
        self.ax.add_patch(foliage)
    
    def draw_target(self, x, y, width, height):
        target = Rectangle((x, y), width, height, color='#e74c3c', alpha=0.8)
        self.ax.add_patch(target)
        
        bullseye_x = x + width/2
        bullseye_y = y + height/2
        bullseye_size = min(width, height) * 0.3
        
        outer_ring = Circle((bullseye_x, bullseye_y), bullseye_size, color='white')
        self.ax.add_patch(outer_ring)
        
        inner_ring = Circle((bullseye_x, bullseye_y), bullseye_size*0.6, color='#e74c3c')
        self.ax.add_patch(inner_ring)
        
        center = Circle((bullseye_x, bullseye_y), bullseye_size*0.2, color='white')
        self.ax.add_patch(center)
    
    def calculate(self, instance):
        try:
            v0 = self.initial_velocity
            angle_deg = self.angle
            h0 = self.height
            g = self.gravity
            rock_size = self.rock_size
            
            if v0 <= 0 or g <= 0:
                self.status_text = "Error: Velocity and gravity must be positive values!"
                self.status_bar.text = self.status_text
                return
            
            angle_rad = math.radians(angle_deg)
            
            self.trajectory_data = self.calculate_trajectory(v0, angle_rad, h0, g)
            
            if self.trajectory_data:
                self.animate_button.disabled = False
                self.plot_trajectory(self.trajectory_data, rock_size)
                self.status_text = "Rock thrown! Click 'Animate Throw' to see animation."
                self.status_bar.text = self.status_text
            
        except Exception as e:
            self.status_text = f"Error: {str(e)}"
            self.status_bar.text = self.status_text
    
    def calculate_trajectory(self, v0, angle_rad, h0, g):
        v0x = v0 * math.cos(angle_rad)
        v0y = v0 * math.sin(angle_rad)
        
        # Calculate time when projectile hits the ground
        discriminant = v0y**2 + 2*g*h0
        
        if discriminant >= 0:
            t_flight = (v0y + math.sqrt(discriminant)) / g
        else:
            return None
            
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
            
            target_hit = False
            hit_time = None
            
            if self.target_enabled:
                target_x = self.target_distance
                target_y = 0
                target_height = self.target_height
                target_width = self.target_width
                
                for i in range(len(t)-1):
                    if (target_x <= x[i] <= target_x + target_width and
                        target_y <= y[i] <= target_y + target_height):
                        target_hit = True
                        hit_time = t[i]
                        break
            
            # Update result labels
            self.max_height_label.text = f"Maximum Height: {max_height:.2f} m"
            self.distance_label.text = f"Range: {distance:.2f} m"
            self.flight_time_label.text = f"Flight Time: {t_flight:.2f} s"
            
            if self.target_enabled:
                if target_hit:
                    self.target_hit_label.text = f"Target Hit: Yes! At {hit_time:.2f} s"
                else:
                    self.target_hit_label.text = "Target Hit: No"
            else:
                self.target_hit_label.text = "Target Hit: No target set"
            
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
            self.status_text = "Error: Invalid trajectory - Check your parameters"
            self.status_bar.text = self.status_text
            return None
    
    def plot_trajectory(self, data, rock_size):
        if data is None:
            return
        
        self.initialize_scene()
        
        self.ax.plot(data["x"], data["y"], 'blue', linestyle='--', alpha=0.7, linewidth=1.5)
        
        x_max = max(50, data["distance"] * 1.1)
        y_max = max(20, data["max_height"] * 1.2)
        self.ax.set_xlim(-5, x_max)
        self.ax.set_ylim(-1, y_max)
        
        if self.target_enabled:
            target_x = self.target_distance
            target_height = self.target_height
            target_width = self.target_width
            self.draw_target(target_x, 0, target_width, target_height)
        
        rock_x = data["distance"]
        rock_y = 0
        final_rock = Circle((rock_x, rock_y), rock_size, color='#95a5a6')
        self.ax.add_patch(final_rock)
        
        if data["max_height_time"] > 0:
            peak_x = data["v0x"] * data["max_height_time"]
            peak_rock = Circle((peak_x, data["max_height"]), rock_size, color='#95a5a6', alpha=0.5)
            self.ax.add_patch(peak_rock)
            
            self.ax.annotate(f'Max Height: {data["max_height"]:.2f} m', 
                             xy=(peak_x, data["max_height"]), 
                             xytext=(peak_x+2, data["max_height"]+1),
                             arrowprops=dict(facecolor='black', shrink=0.05, width=1.5, headwidth=8))
        
        self.ax.annotate(f'Range: {data["distance"]:.2f} m', 
                         xy=(data["distance"], 0.2), 
                         xytext=(data["distance"]-5, 2),
                         arrowprops=dict(facecolor='black', shrink=0.05, width=1.5, headwidth=8))
        
        self.canvas.draw()
    
    def toggle_animation(self, instance):
        if self.animation_event is None:
            self.animate_throw()
            self.animate_button.text = "Stop Animation"
        else:
            if self.animation_event:
                self.animation_event.cancel()
                self.animation_event = None
            self.animate_button.text = "Animate Throw"
    
    def animate_throw(self):
        if not hasattr(self, 'trajectory_data') or self.trajectory_data is None:
            self.status_text = "Calculate the trajectory first!"
            self.status_bar.text = self.status_text
            return
        
        # Reset animation
        self.frame_num = 0
        if self.rock is None:
            rock_size = self.rock_size
            self.rock = Circle((0, self.height), rock_size, color='#95a5a6')
            self.ax.add_patch(self.rock)
        
        # Animation update function
        def update_animation(dt):
            if self.frame_num < len(self.trajectory_data["times"]):
                x = self.trajectory_data["x"][self.frame_num]
                y = self.trajectory_data["y"][self.frame_num]
                self.rock.center = (x, y)
                
                time = self.trajectory_data["times"][self.frame_num]
                self.status_text = f"Time: {time:.2f}s | Position: ({x:.2f}m, {y:.2f}m)"
                self.status_bar.text = self.status_text
                
                if (self.target_enabled and self.trajectory_data["target_hit"] and 
                    self.trajectory_data["hit_time"] <= time and 
                    self.trajectory_data["hit_time"] >= self.trajectory_data["times"][max(0, self.frame_num-1)]):
                    self.status_text = "TARGET HIT! 🎯"
                    self.status_bar.text = self.status_text
                
                self.frame_num += 1
                self.canvas.draw()
            else:
                # Reset animation to start
                self.frame_num = 0
        
        # Schedule the animation
        interval = self.trajectory_data["flight_time"] / len(self.trajectory_data["times"])
        self.animation_event = Clock.schedule_interval(update_animation, interval)

class ProjectileMotionApp(App):
    def build(self):
        self.title = 'Rock Throwing Simulator'
        return ProjectileSimulator()

if __name__ == '__main__':
