from app.render.cube import Cube
from app.render.axes import Axes
from app.render.grid import Grid


class Scene:
    def __init__(self):
        self.objects = []
        self.axes = Axes()
        self.grid = Grid()

        cube = Cube()
        self.objects.append(cube)

    def update(self, delta: float):
        for obj in self.objects:
            obj.update(delta)

    def draw(self, renderer):
        self.grid.draw(renderer)
        self.axes.draw(renderer)
        for obj in self.objects:
            obj.draw(renderer)
