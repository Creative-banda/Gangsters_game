import pygame, random
from settings import PLAYER_SIZE, NORMAL_ENEMY, CELL_SIZE, HEAVY_ENEMY
from player import Bullet, bullet_group


class Enemy(pygame.sprite.Sprite):
    
    def __init__(self, x, y, enemy_type):
        super().__init__()
        
        self.animations = {}

        if enemy_type == "normal":
            self.health = 100
            self.shoot_frame = 5
            self.bullet_damage = 40
            self.vision_length = 300
            self.animation_dict = NORMAL_ENEMY
        elif enemy_type == "strong":
            self.health = 200
            self.shoot_frame = 3
            self.bullet_damage = 60
            self.vision_length = 400
            
            self.animation_dict = HEAVY_ENEMY
        self.current_action = "idle"
        self.load_animations()

        self.frame_index = 0
        self.last_update_time = pygame.time.get_ticks()
        self.image = self.animations[self.current_action][self.frame_index]
        self.rect = self.image.get_rect()
        self.x = x
        self.y = y
        self.rect.center = (self.x, self.y)
        self.direction = -1
        self.vel_y = 0
        self.isReloading = False
        self.isShoting = False
        self.isHurt = False  
        self.idle_counter = 0
        self.move_counter = 0
        self.idling = False
        self.last_bullet_time = pygame.time.get_ticks()
        self.speed = 0.7
    
        
        # Create a rect in front of the enemy as enemy vision
        self.vision_rect = pygame.Rect(self.x, self.y, self.vision_length, 50)
        self.vision_rect.center = self.rect.center
        
        # Create a health bar in the top of the enemy as health bar
        
        self.max_health = 100
        self.health_bar_length = 50
        self.health_ratio = self.max_health / self.health_bar_length
        # creating a rect for health bar
        self.health_bar = pygame.Rect(self.rect.centerx , self.rect.y, self.health_bar_length, 5)
        


    def take_damage(self, damage):
        if not self.isHurt:  # Only trigger hurt if not already hurt
            self.isHurt = True
            self.update_animation("Hurt")
            # Reset other states
            self.isShoting = False
            self.isReloading = False
            self.idling = False
            
        self.health -= damage
   
            
        # update the health bar
        self.health_bar.width = self.health / self.health_ratio
        if self.health <= 0:
            self.isHurt = False
            self.update_animation("Dead")
            sound = random.randint(0,3)
            pygame.mixer.Sound(f"assets/sfx/enemy_die/{sound}.mp3").play()
                

    def shoot(self):
        if self.isHurt:  # Don't shoot if hurt
            return
        if pygame.time.get_ticks() - self.last_bullet_time < 500 or self.isReloading:
            return
        if self.frame_index == self.shoot_frame:
            self.isShooting = True
            bullet = Bullet(self.rect.centerx + (15*self.direction) + (PLAYER_SIZE[1]// 2 * self.direction),
                             self.rect.centery-10, self.direction, self.bullet_damage)
            bullet_group.add(bullet)
            self.last_bullet_time = pygame.time.get_ticks()
            pygame.mixer.Sound("assets/sfx/pistol.mp3").play()
   

    def load_animations(self):
        """Load animations from the defined data."""
        data = None

        for action, data in self.animation_dict.items():
            frames = []
            sprite_sheet = pygame.image.load(data["image_path"]).convert_alpha()

            cut_top = 50
            cut_left = 33
            cut_right = 25
            frame_height = 128 - cut_top
            frame_width = 128 - (cut_left + cut_right)

            for frame_index in range(data["frame_count"]):
                x = (frame_index * 128) + cut_left
                y = cut_top
                frame = sprite_sheet.subsurface(
                    (x, y, frame_width, frame_height)
                )
                # frame = pygame.transform.scale(frame, PLAYER_SIZE)
                frames.append(frame)

            self.animations[action] = frames


    def update(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_update_time > self.animation_dict[self.current_action]["animation_cooldown"]:
            self.last_update_time = current_time
            self.frame_index += 1

            # Handle hurt animation completion
            if self.current_action == "Hurt" and self.frame_index >= len(self.animations[self.current_action]):
                self.isHurt = False
                self.update_animation("idle")
            # Handle other animations
            elif self.current_action == "Shot" and self.frame_index >= len(self.animations[self.current_action]):
                self.update_animation("idle")
            
            elif self.current_action == "Dead" and self.frame_index >= len(self.animations[self.current_action]):
                self.frame_index = len(self.animations[self.current_action]) - 1
            
            # Loop animation
            if self.frame_index >= len(self.animations[self.current_action]):
                self.frame_index = 0

        try:
            self.image = self.animations[self.current_action][self.frame_index]
        except:
            self.frame_index = 0
            self.image = self.animations[self.current_action][self.frame_index] 
        self.image = pygame.transform.flip(self.image, self.direction == -1, False)
        
        
    def move(self, player, ground_group):
        if self.isHurt:  # Don't move if hurt
            return
                    
        dy = 0
        dx = 0
        self.vel_y += 0.5 
        dy += self.vel_y
        
        if self.health > 0:
            if self.direction == 1:
                dx = self.speed
            else:
                dx = -self.speed


        # Create a temp rect with upcoming values
        temp_rect = self.rect.copy()
        temp_rect.y += dy
        # Check vertical collisions
        for ground in ground_group:
            if temp_rect.colliderect(ground.rect):
                if dy > 0:  # Falling down
                    self.vel_y = 0
                    dy = ground.rect.top - self.rect.bottom
                    self.InAir = False
                elif dy < 0:  # Moving up
                    self.vel_y = 0
                    dy = 0
                break


        new_x = self.rect.x + dx
        temp_rect = self.rect.copy()
        temp_rect.x = new_x
        
        # Check horizontal collisions
        for ground in ground_group:
            if temp_rect.colliderect(ground.rect):
                if temp_rect.right > ground.rect.left:
                    dx = 0

        if self.ai == "boss":
            self.bossAi()
        else:
            self.ai(player)  

        # Update enemy's position
        self.y += dy
        self.rect.y = self.y  
        if not self.isShoting and not self.isReloading and not self.idling:
            self.x += dx
        
        # Update vision rect
        self.vision_rect.center = self.rect.center
      

    def update_animation(self, new_action):
        if new_action != self.current_action:
            self.current_action = new_action
            self.frame_index = 0
            self.last_update_time = pygame.time.get_ticks()


    def draw(self, screen, bg_scroll_x, bg_scroll_y):
        self.rect.x = self.x - bg_scroll_x
        self.rect.y = self.y - bg_scroll_y
        self.vision_rect.y = self.y - bg_scroll_y
        screen.blit(self.image, self.rect)
        
        # pygame.draw.rect(screen, (0,255,0), self.rect, 1)
        # pygame.draw.rect(screen, (255, 0, 0), self.vision_rect, 1)

        # Update health bar position
        self.health_bar.centerx = self.rect.centerx
        self.health_bar.y = self.rect.y 

        
        # Draw health bar
        pygame.draw.rect(screen, (255, 0, 0), self.health_bar)


    def ai(self, player):
        if self.health <= 0:
            return
        if self.idling == False and random.randint(1, 200) == 1:
            self.update_animation("idle")
            self.idling = True
            self.idle_counter = 100
            self.dx = 0
            
        if self.vision_rect.colliderect(player.rect) and player.alive:
            self.direction = 1 if player.rect.x > self.rect.x else -1
            self.update_animation("Shot")
            self.shoot()
            self.isShoting = True
        else:
            self.isShoting = False
            if self.idling == False:
                self.update_animation("Walk")
                self.move_counter += 1

                if self.move_counter > CELL_SIZE:
                    self.direction *= -1
                    self.move_counter *= -1
            else:
                self.idle_counter -= 1
                if self.idle_counter <= 0:
                    self.idling = False


    def bossAi(self):
        pass
