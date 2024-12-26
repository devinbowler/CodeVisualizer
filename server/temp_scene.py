from manim import *

class CreateCircle(Scene):
    def construct(self):
        circle = Circle()  # Create a circle
        circle.set_fill(PINK, opacity=0.5)  # Set the color and transparency
        self.play(Create(circle))  # Animate the creation of the circle
