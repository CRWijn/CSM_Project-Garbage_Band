class GameObject:
    def __init__(self, surf, position):
        self.surf = surf
        self.pos = position

    def __eq__(self, other):
        return bool(self.surf == other.surf and self.pos == other.pos)
