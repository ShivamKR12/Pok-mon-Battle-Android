from settings import * 

class UI:
    def __init__(self, monster, player_monsters, simple_surfs, get_input):
        self.display_surface = pygame.display.get_surface()
        self.font = pygame.font.Font(None, 30)
        self.left = WINDOW_WIDTH / 2 - 100 
        self.top = WINDOW_HEIGHT / 2 + 50
        self.monster = monster
        self.simple_surfs = simple_surfs
        self.get_input = get_input

        # UI Config
        self.general_options = ['attack', 'heal', 'switch', 'escape']
        self.state = 'general'
        self.rows, self.cols = 2, 2
        self.visible_monsters = 4
        self.player_monsters = player_monsters
        self.available_monsters = [monster for monster in self.player_monsters if monster != self.monster and monster.health > 0]
        self.switch_index = 0

        # Touch-specific layout rectangles (Instantiated dynamically or tracked in render loops)
        self.quad_rect = pygame.FRect(self.left + 40, self.top + 60, 400, 200)
        self.switch_rect = pygame.FRect(self.left + 40, self.top - 140, 400, 400)

    def handle_touch(self, touch_pos):
        """Processes a single scaled tap/click point."""
        tx, ty = touch_pos

        if self.state == 'general':
            # Check if touch is inside the main quad menu box
            if self.quad_rect.collidepoint(tx, ty):
                # Calculate which column and row was pressed based on click positioning
                col = int((tx - self.quad_rect.left) / (self.quad_rect.width / self.cols))
                row = int((ty - self.quad_rect.top) / (self.quad_rect.height / self.rows))
                
                # Keep calculations clamped safely inside boundaries
                col = max(0, min(col, self.cols - 1))
                row = max(0, min(row, self.rows - 1))
                
                chosen_option = self.general_options[col + row * self.cols]
                
                if chosen_option == 'heal':
                    self.get_input('heal')
                elif chosen_option == 'escape':
                    self.get_input('escape')
                else:
                    self.state = chosen_option

        elif self.state == 'attack':
            if self.quad_rect.collidepoint(tx, ty):
                col = int((tx - self.quad_rect.left) / (self.quad_rect.width / self.cols))
                row = int((ty - self.quad_rect.top) / (self.quad_rect.height / self.rows))
                col = max(0, min(col, self.cols - 1))
                row = max(0, min(row, self.rows - 1))
                
                attack = self.monster.abilities[col + row * self.cols]
                self.get_input(self.state, attack)
                self.state = 'general'
            else:
                # Tap outside the choice box to cancel out and return
                self.state = 'general'

        elif self.state == 'switch':
            if self.switch_rect.collidepoint(tx, ty):
                # Calculate row target height allocations
                row_height = self.switch_rect.height / self.visible_monsters
                v_offset = 0 if self.switch_index < self.visible_monsters else -(self.switch_index - self.visible_monsters + 1) * row_height
                
                # Find out which visible index row was clicked
                for i in range(len(self.available_monsters)):
                    item_y_center = self.switch_rect.top + (row_height / 2) + (row_height * i) + v_offset
                    item_rect = pygame.FRect(self.switch_rect.left, item_y_center - (row_height / 2), self.switch_rect.width, row_height)
                    
                    if item_rect.collidepoint(tx, ty):
                        self.get_input(self.state, self.available_monsters[i])
                        self.state = 'general'
                        break
            else:
                # Tap outside layout elements to cancel
                self.state = 'general'

    def quad_select(self, options):
        # Background Layout Boundaries
        pygame.draw.rect(self.display_surface, COLORS['white'], self.quad_rect, 0, 6)
        pygame.draw.rect(self.display_surface, COLORS['gray'], self.quad_rect, 6, 6)

        # Draw Menu Texts 
        for col in range(self.cols):
            for row in range(self.rows):
                x = self.quad_rect.left + self.quad_rect.width / (self.cols * 2) + (self.quad_rect.width / self.cols) * col
                y = self.quad_rect.top + self.quad_rect.height / (self.rows * 2) + (self.quad_rect.height / self.rows) * row
                i = col + 2 * row

                text_surf = self.font.render(options[i], True, COLORS['black'])
                text_rect = text_surf.get_frect(center=(x, y))
                self.display_surface.blit(text_surf, text_rect)

    def switch(self):
        # Background Box Layout
        pygame.draw.rect(self.display_surface, COLORS['white'], self.switch_rect, 0, 4)
        pygame.draw.rect(self.display_surface, COLORS['gray'], self.switch_rect, 4, 4)

        # Menu listing item processing loop
        v_offset = 0 if self.switch_index < self.visible_monsters else -(self.switch_index - self.visible_monsters + 1) * self.switch_rect.height / self.visible_monsters
        for i in range(len(self.available_monsters)):
            x = self.switch_rect.centerx
            y = self.switch_rect.top + self.switch_rect.height / (self.visible_monsters * 2) + self.switch_rect.height / self.visible_monsters * i + v_offset
            name = self.available_monsters[i].name

            simple_surf = self.simple_surfs[name]
            simple_rect = simple_surf.get_frect(center=(x - 100, y))

            text_surf = self.font.render(name, True, COLORS['black'])
            text_rect = text_surf.get_frect(midleft=(x, y))
            
            if self.switch_rect.collidepoint(text_rect.center):
                self.display_surface.blit(text_surf, text_rect)
                self.display_surface.blit(simple_surf, simple_rect)

    def stats(self):
        rect = pygame.FRect(self.left, self.top, 250, 80)
        pygame.draw.rect(self.display_surface, COLORS['white'], rect, 0, 4)
        pygame.draw.rect(self.display_surface, COLORS['gray'], rect, 4, 4)

        name_surf = self.font.render(self.monster.name, True, COLORS['black'])
        name_rect = name_surf.get_frect(topleft=rect.topleft + pygame.Vector2(rect.width * 0.05, 12))
        self.display_surface.blit(name_surf, name_rect)

        health_rect = pygame.FRect(name_rect.left, name_rect.bottom + 10, rect.width * 0.9, 20)
        pygame.draw.rect(self.display_surface, COLORS['gray'], health_rect)
        self.draw_bar(health_rect, self.monster.health, self.monster.max_health)
    
    def draw_bar(self, rect, value, max_value):
        ratio = rect.width / max_value
        progress_rect = pygame.FRect(rect.topleft, (value * ratio, rect.height))
        pygame.draw.rect(self.display_surface, COLORS['red'], progress_rect)

    def update(self):
        # Keep tracking updating active monster datasets dynamically
        self.available_monsters = [monster for monster in self.player_monsters if monster != self.monster and monster.health > 0]

    def draw(self):
        match self.state:
            case 'general': self.quad_select(self.general_options)
            case 'attack': self.quad_select(self.monster.abilities)
            case 'switch': self.switch()
        
        if self.state != 'switch':
            self.stats()

class OpponentUI:
    def __init__(self, monster):
        self.display_surface = pygame.display.get_surface()
        self.monster = monster
        self.font = pygame.font.Font(None, 30)

    def draw(self):
        rect = pygame.FRect((0,0), (250,80)).move_to(bottomright=(self.monster.rect.left - 20, self.monster.rect.centery))
        # Fallback if it goes off-screen
        if rect.left < 10:
            rect = pygame.FRect((0,0), (250,80)).move_to(midbottom=(self.monster.rect.centerx, self.monster.rect.top - 20))
            
        pygame.draw.rect(self.display_surface, COLORS['white'], rect, 0, 4)
        pygame.draw.rect(self.display_surface, COLORS['gray'], rect, 4, 4)

        name_surf = self.font.render(self.monster.name, True, COLORS['black'])
        name_rect = name_surf.get_frect(topleft=rect.topleft + pygame.Vector2(rect.width * 0.05, 12))
        self.display_surface.blit(name_surf, name_rect)

        health_rect = pygame.FRect(name_rect.left, name_rect.bottom + 10, rect.width * 0.9, 20)
        ratio = health_rect.width / self.monster.max_health
        progress_rect = pygame.FRect(health_rect.topleft, (self.monster.health * ratio, health_rect.height))
        pygame.draw.rect(self.display_surface, COLORS['gray'], health_rect)
        pygame.draw.rect(self.display_surface, COLORS['red'], progress_rect)
