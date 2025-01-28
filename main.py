import pygame
import sys

# Initialize Pygame
pygame.init()

PLAYER_SIZE = (100, 110)  # Target size for each frame

screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Hello Pygame")
clock = pygame.time.Clock()


class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()

        self.frame_index = 0
        self.current_action = "idle"
        self.animations = {}
        self.animation_cooldown = 100
        self.direction = 1  # 1: Right, -1: Left
        self.last_update_time = pygame.time.get_ticks()
        self.InAir = False
        self.vel_y = -11
        self.speed = 3
        self.running_speed = 7
        self.isReloading = False

        # Define animations with frame counts, offsets, and sprite sheet paths
        self.animation_data = {
            "idle": {
                "frame_count": 6,  # Number of frames
                "image_path": "assets/player/Idle.png",  # Sprite sheet path
            },
            "Run": {
                "frame_count": 10,  # Number of frames
                "image_path": "assets/player/Run.png",  # Sprite sheet path
            },
            "Shot": {
                "frame_count": 4,  # Number of frames
                "image_path": "assets/player/Shot.png",  # Sprite sheet path
            },
            "Walk": {
                "frame_count": 10,  # Number of frames
                "image_path": "assets/player/Walk.png",  # Sprite sheet path
            },
            "Jump": {
                "frame_count": 10,  # Number of frames
                "image_path": "assets/player/Jump.png",  # Sprite sheet path
            },
            
            "Reload": {
                "frame_count": 17,  # Number of frames
                "image_path": "assets/player/Recharge.png",  # Sprite sheet path
            },
        }

        # Load animations
        self.load_animations()

        # Set initial frame and position
        self.image = self.animations[self.current_action][self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.midbottom = (400, 300)  # Changed from center to midbottom

    def load_animations(self):
        """Load animations from the defined data."""
        for action, data in self.animation_data.items():
            frames = []
            sprite_sheet = pygame.image.load(data["image_path"]).convert_alpha()

            # Extract frames based on offsets and dimensions
            for frame_index in range(data["frame_count"]):
                x = frame_index * 128
                y = 0
                frame = sprite_sheet.subsurface(
                    (x, y, 100,128)
                )
                frame = pygame.transform.scale(frame, PLAYER_SIZE)
                frames.append(frame)

            self.animations[action] = frames
            
    def move(self):
        dx = 0
        dy = 0
        keys = pygame.key.get_pressed()

        # Reset action to determine new animation
        new_action = None

        # Handle Jumping (highest priority)
        if keys[pygame.K_w] and not self.InAir:
            self.InAir = True
            self.vel_y = -11
            new_action = "Jump"
        # Only check other actions if not jumping and grounded
        elif not self.InAir and not self.isReloading:
            if keys[pygame.K_SPACE]:
                new_action = "Shot"
            elif keys[pygame.K_LSHIFT] and (keys[pygame.K_a] or keys[pygame.K_d]):
                new_action = "Run"
                dx = self.running_speed * self.direction
                if keys[pygame.K_a]:
                    dx = -self.running_speed
                    self.direction = -1
                else:
                    dx = self.running_speed
                    self.direction = 1
                
            elif keys[pygame.K_a] or keys[pygame.K_d]:
                new_action = "Walk"
                # Horizontal movement
                if keys[pygame.K_a]:
                    dx = -self.speed
                    self.direction = -1
                else:
                    dx = self.speed
                    self.direction = 1

                
            else:
                if not self.isReloading:
                    new_action = "idle"

        # Update animation if needed
        if new_action and new_action != self.current_action:
            self.update_animation(new_action)

        # Apply gravity
        if self.InAir:
            self.vel_y += 0.6
            dx += 5 * self.direction
            if self.vel_y > 10:
                self.vel_y = 10
            dy += self.vel_y

        # Calculate new vertical position
        new_y = self.rect.y + dy

        # Ground collision check (using sprite bottom)
        if new_y + self.rect.height > 300:  # Check if bottom exceeds ground
            self.rect.y = 300 - self.rect.height  # Place feet on ground
            self.InAir = False
            dy = 0
            # Revert to idle unless another action is active
            if not (keys[pygame.K_SPACE] or keys[pygame.K_a] or keys[pygame.K_d]):
                self.update_animation("idle")
        else:
            self.rect.y = new_y

        # Horizontal boundaries
        self.rect.x += dx
        if self.rect.right > 800:
            self.rect.right = 800
        if self.rect.left < 0:
            self.rect.left = 0

    def update(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_update_time > self.animation_cooldown:
            self.last_update_time = current_time
            self.frame_index += 1

            # Reset Jump animation when it ends
            if self.current_action == "Jump" and self.frame_index >= len(self.animations[self.current_action]):
                self.InAir = True
                self.update_animation("idle")
            elif self.current_action == "Reload" and self.frame_index >= len(self.animations[self.current_action]):
                self.isReloading = False
                self.update_animation("idle")
                self.animation_cooldown = 100

            # Loop animation
            if self.frame_index >= len(self.animations[self.current_action]):
                self.frame_index = 0

        self.image = self.animations[self.current_action][self.frame_index]
        self.image = pygame.transform.flip(self.image, self.direction == -1, False)

    def reload(self):
        self.animation_cooldown = 50
        self.isReloading = True
        self.update_animation("Reload")

    def update_animation(self, new_action):
        if new_action != self.current_action:
            self.current_action = new_action
            self.frame_index = 0
            self.last_update_time = pygame.time.get_ticks()

    def draw(self):
        self.image = pygame.transform.scale(self.image, PLAYER_SIZE)
        screen.blit(self.image, self.rect)


player = Player()


def main():
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                if event.key == pygame.K_r:
                    player.reload()

        # Clear the screen with the background color
        screen.fill((255, 155, 155))

        # Update and draw the player
        player.move()
        player.update()
        player.draw()

        # Update the display
        pygame.display.flip()
        clock.tick(60)


if __name__ == "__main__":
    main()
