from settings import * 
from random import sample

class Creature:
    def get_data(self, name):
        self.element = MONSTER_DATA[name]['element']
        self._health = self.max_health = MONSTER_DATA[name]['health']
        self.abilities = sample(list(ABILITIES_DATA.keys()),4)
        self.name = name
    
    @property
    def health(self):
        return self._health
    
    @health.setter
    def health(self, value):
        self._health = min(self.max_health, max(0, value))

class Monster(pygame.sprite.Sprite, Creature):
    def __init__(self, name, surf):
        super().__init__()
        
        max_w = WINDOW_WIDTH * 0.4
        max_h = WINDOW_HEIGHT * 0.4
        w, h = surf.get_size()
        if w > max_w or h > max_h:
            scale = min(max_w / w, max_h / h)
            surf = pygame.transform.smoothscale(surf, (int(w * scale), int(h * scale)))
            
        self.image = surf 
        self.rect = self.image.get_frect(midbottom = (WINDOW_WIDTH * 0.25, WINDOW_HEIGHT * 0.85))
        self.get_data(name)
    
    def __repr__(self):
        return f'{self.name}: {self.health}/{self.max_health}'

class Opponent(pygame.sprite.Sprite, Creature):
    def __init__(self, name, surf, groups):
        super().__init__(groups)
        
        max_w = WINDOW_WIDTH * 0.4
        max_h = WINDOW_HEIGHT * 0.4
        w, h = surf.get_size()
        if w > max_w or h > max_h:
            scale = min(max_w / w, max_h / h)
            surf = pygame.transform.smoothscale(surf, (int(w * scale), int(h * scale)))
            
        self.image = surf
        self.rect = self.image.get_frect(midbottom = (WINDOW_WIDTH * 0.75, WINDOW_HEIGHT * 0.45))
        self.get_data(name)
