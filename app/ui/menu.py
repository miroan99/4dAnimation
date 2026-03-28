class Menu:
    def __init__(self):
        self.visible = False

    def toggle(self):
        self.visible = not self.visible

    def draw(self):
        if not self.visible:
            return
