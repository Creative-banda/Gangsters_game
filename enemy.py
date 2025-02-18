import pygame, random
from settings import PLAYER_SIZE, CELL_SIZE, ENEMIES
from player import Bullet, bullet_group


class Enemy(pygame.sprite.Sprite):
    
    def __init__(self, x, y, enemy_type, ZOOM_VALUE=1):
        super().__init__()
        
        self.animations = {}
        self.zoom_value = ZOOM_VALUE
        self.size = 1 
        
        self.speed = 0.7
        
        self.max_health = 100

        if enemy_type == "normal":
            self.health = 100
            self.shoot_frame = 5
            self.bullet_damage = 40
            self.vision_length = 300 * self.zoom_value
            self.animation_dict =ENEMIES['NORMAL_ENEMY']
            self.type = "normal"
        elif enemy_type == "strong":
            self.health = 500
            self.max_health = 500
            self.shoot_frame = 3
            self.bullet_damage = 60
            self.vision_length = 400 * self.zoom_value
            self.type = "strong"
            
            self.animation_dict = ENEMIES['HEAVY_ENEMY']
        elif enemy_type == "boss":
            self.health = 10000
            self.punch_damage = 50
            self.animation_dict = ENEMIES['BOSS_ENEMY']
            self.vision_length = 500 * self.zoom_value
            self.base_speed = 3
            self.size = 2
            self.type = "boss"
            self.speed = 3
            self.max_health = 10000
            self.last_punch_time = pygame.time.get_ticks()
            
            
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
        self.isAttacking = False
        self.isHurt = False  
        self.idle_counter = 0
        self.move_counter = 0
        self.idling = False
        self.last_bullet_time = pygame.time.get_ticks()
        
        self.last_player_x = x
        self.attack_index = 0 
        
        # Create a rect in front of the enemy as enemy vision
        self.vision_rect = pygame.Rect(self.x, self.y, self.vision_length, 50)
        self.vision_rect.center = self.rect.center
        
        # Create a health bar in the top of the enemy as health bar
        
        self.health_bar_length = 50
        self.health_ratio = self.max_health / self.health_bar_length
        # creating a rect for health bar
        self.health_bar = pygame.Rect(self.rect.centerx , self.rect.y, self.health_bar_length, 5)
        
    def take_damage(self, damage):
        if not self.isHurt:  # Only trigger hurt if not already hurt
            self.isHurt = True
            self.update_animation("Hurt")
            # Reset other states
            self.isAttacking = False
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
            self.isAttacking = True
            bullet = Bullet(self.rect.centerx + (15*self.direction) + (PLAYER_SIZE[1]// 2 * self.direction),
                             self.rect.centery-10, self.direction, self.bullet_damage, self.zoom_value)
            bullet_group.add(bullet)
            self.last_bullet_time = pygame.time.get_ticks()
            pygame.mixer.Sound("assets/sfx/pistol.mp3").play()
   

    def load_animations(self):
        """Load animations from the defined data."""
        
        BASE_FRAME_SIZE = 128  # Reference frame size (Normal Enemy)
        BASE_CUT_TOP = 20
        BASE_CUT_RIGHT = 25

        for action, data in self.animation_dict.items():
            frames = []
            sprite_sheet = pygame.image.load(data["image_path"]).convert_alpha()

            # Get the full image size dynamically
            sheet_width, sheet_height = sprite_sheet.get_size()
            
            # Calculate frame dimensions dynamically
            frame_count = data["frame_count"]
            frame_width = sheet_width // frame_count
            frame_height = sheet_height  # Use full height dynamically

            # Calculate ratio based on base size (128x128)
            width_ratio = frame_width / BASE_FRAME_SIZE
            height_ratio = frame_height / BASE_FRAME_SIZE

            # Apply ratio to cut values
            cut_top = int(BASE_CUT_TOP * height_ratio)
            cut_right = int(BASE_CUT_RIGHT * width_ratio)

            # Loop through each frame and extract it
            for frame_index in range(frame_count):
                x = (frame_index * frame_width)
                y = cut_top
                cropped_width = frame_width - (cut_right)
                cropped_height = frame_height - cut_top

                frame = sprite_sheet.subsurface((x, y, cropped_width, cropped_height))

                # Scale based on zoom value
                frame = pygame.transform.scale(
                    frame, 
                    (int(cropped_width * self.zoom_value * self.size), int(cropped_height * self.zoom_value * self.size))
                )
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
            elif self.current_action  == "Shot" and self.frame_index >= len(self.animations[self.current_action]):
                self.update_animation("idle")
            
            elif self.current_action in ["Attack1", "Attack2", "Attack3"] and self.frame_index >= len(self.animations[self.current_action]):
                self.update_animation("idle")
                self.isAttacking = False  # Ensure boss can attack again

            
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
        
    def move(self, player, ground_group, bg_scroll_x, bg_scroll_y):

        # Adjust rendering position first
        self.rect.x = self.x - bg_scroll_x
        self.rect.y = self.y - bg_scroll_y
        self.vision_rect.y = self.y - bg_scroll_y

        dx = 0
        dy = 0

        if self.health > 0:  # Apply movement logic only if alive
            self.vel_y += 0.5  # Apply gravity
            dy += self.vel_y

            # Move left or right based on direction
            if self.direction == 1:
                dx = self.speed
            else:
                dx = -self.speed
        else:
            # If dead, apply gravity but no horizontal movement
            self.vel_y += 0.5 * self.zoom_value  # Keep applying gravity
            dy += self.vel_y
            dx = 0  # Stop moving left or right

        # Check vertical collisions
        temp_rect = self.rect.copy()
        temp_rect.y += dy

        for ground in ground_group:
            if temp_rect.colliderect(ground.rect):
                if dy > 0:  # Falling down
                    self.vel_y = 0
                    if self.health > 0:  # Only snap to ground if alive
                        dy = ground.rect.top - self.rect.bottom
                    else:
                        dy = 0  # Let the enemy fall naturally
                    self.InAir = False
                elif dy < 0:  # Moving up
                    self.vel_y = 0
                    dy = 0
                break  # Stop checking once collision is handled

        # Only check horizontal collisions if alive
        if self.health > 0:
            temp_rect = self.rect.copy()
            temp_rect.x += dx

            for ground in ground_group:
                if temp_rect.colliderect(ground.rect):
                    if temp_rect.right > ground.rect.left:
                        dx = 0
                        
        if self.health > 0 and not self.isReloading and not self.isHurt:
            if self.type == "boss":
                self.bossAi(player)
            else:
                self.ai(player)


        # Update enemy's actual position (without applying bg_scroll_y)
        self.y += dy  # Always allow falling
        self.rect.y = self.y - bg_scroll_y  # Adjust rendering only

        if self.health > 0 and not self.isReloading and not self.idling and not self.isHurt:
            self.x += dx  # Allow movement only if alive

        # Update rect position
        self.rect.x = self.x - bg_scroll_x  # Adjust rendering only
        self.vision_rect.center = self.rect.center

        


    def update_animation(self, new_action):
        if new_action != self.current_action:
            self.current_action = new_action
            self.frame_index = 0
            self.last_update_time = pygame.time.get_ticks()


    def draw(self, screen):
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
        else:
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


    def bossAi(self, player):
        """Boss AI behavior with improved movement and attack logic"""
        if self.health <= 0:
            return

        # Check if stuck (Hasn't moved in 20 frames)
        if hasattr(self, "stuck_counter") and self.rect.x == self.prev_x and not self.idling:
            self.stuck_counter += 1
        else:
            self.stuck_counter = 0

        # If stuck for too long, jump AND move slightly
        if self.stuck_counter > 40:
            self.jump()
            self.rect.x += 40 * self.direction  # Move slightly more to avoid repeated stuck issues
            self.stuck_counter = 0  # Reset counter after jumping

        # Store previous position to check if stuck next frame
        self.prev_x = self.rect.x

        # **Only move if NOT attacking or idling**
        if not self.idling and player.health > 0:
            self.last_player_x = player.rect.x  # Store last seen position
            target_x = player.rect.x if random.randint(1, 3) > 1 else self.last_player_x

            # **If close enough, attack instead of moving**
            distance_to_player = abs(self.rect.x - player.rect.x)
            if distance_to_player < 10:
                self.punch_attack(player)  # Attack when close
                self.speed = 0
            else:
                self.speed = self.base_speed
                # Move toward target when far away
                if self.rect.x < target_x:
                    self.rect.x += self.speed
                    self.direction = 1
                elif self.rect.x > target_x:
                    self.rect.x -= self.speed
                    self.direction = -1
                if not self.isAttacking:
                    self.update_animation("Run")

        # Randomly idle to add variety
        if self.idling == False and random.randint(1, 400) == 1:
            self.update_animation("idle")
            self.idling = True
            self.idle_counter = 80

        # Handle idling state
        if self.idling:
            self.idle_counter -= 1
            if self.idle_counter <= 0:
                self.idling = False
                self.update_animation("Run")

    def punch_attack(self, player):
        """Performs a punch attack"""
        
        attack_moves = ["Attack1", "Attack2", "Attack3"]
        if not self.isAttacking:
            self.update_animation(random.choice(attack_moves))
        
        self.isAttacking = True
        if player.rect.colliderect(self.rect) and self.frame_index >= 3 :
            player.health -= 1
            if player.health <= 0:
                player.alive = False
            else:
                player.update_animation("Hurt")


    def jump(self):
        """Boss jumps when stuck"""
        if self.vel_y == 0:
            self.vel_y -= 10
            self.update_animation("jump")
            self.rect.x -= 30 * self.direction  # Move slightly to avoid getting stuck


