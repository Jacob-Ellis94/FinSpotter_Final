from kivy.app import App
from kivy.lang import Builder
from kivy.uix.widget import Widget
from kivy.clock import Clock


class CircularArrow(Widget):
    def __init__(self, **kw):
        super().__init__(**kw)
        Clock.schedule_interval(self.draw, 1 / 60)
        self.saend = 180
        self.sastart = 0

    def get_diff(self):
        return self.aend - self.astart

    def draw(self, dt):
        self.aend += self.saend * dt
        self.astart += self.sastart * dt

        diff = self.get_diff()
        if diff < 250:
            r = min(dt * 150, self.sastart)
            self.sastart -= r
            self.saend += r

        elif diff > 270:
            r = min(dt * 100, self.saend)
            self.saend -= r
            self.sastart += r


KV = """
#:import rect cmath.rect
#:import radians math.radians

<CircularArrow>:
    line_width: 5
    radius: 100
    x: root.radius + root.line_width * 3
    y: root.radius + root.line_width * 3
    astart: 90
    aend: 270
    arrow_x1: rect(root.radius + 5, radians(-root.aend + 90)).real + root.x
    arrow_y1: rect(root.radius + 5, radians(-root.aend + 90)).imag + root.y
    arrow_x2: rect(root.radius - 5, radians(-root.aend + 90)).real + root.x
    arrow_y2: rect(root.radius - 5, radians(-root.aend + 90)).imag + root.y
    arrow_x3: rect(root.radius, radians(-root.aend - 5 + 90)).real + root.x
    arrow_y3: rect(root.radius, radians(-root.aend - 5 + 90)).imag + root.y
    arrow_head: [root.arrow_x1, root.arrow_y1, root.arrow_x2, root.arrow_y2, root.arrow_x3, root.arrow_y3]
    canvas.after:
        Color:
            rgba: 1,0,0,1
        Line:
            width: root.line_width
            circle: (root.x, root.y, root.radius, root.astart, root.aend)
        Line:
            width: 5
            joint: "miter"
            close: True
            points: root.arrow_head or []

CircularArrow:
"""
"""
FloatLayout:
    CircularArrow:
        radius: 260
        line_width: 5
    CircularArrow:
        radius: 230
        line_width: 5
    CircularArrow:
        radius: 200
        line_width: 5
"""


class MyApp(App):
    def build(self):
        return Builder.load_string(KV)


MyApp().run()
