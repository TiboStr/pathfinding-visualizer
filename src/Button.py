import pygame


class Button:
    # https://github.com/russs123/pygame_tutorials/tree/main/Button
    def __init__(self, window, x, y, img, img_size, function):
        self.window = window
        self.x = x
        self.y = y
        self.img = pygame.transform.scale(img, (img_size, img_size))
        self.rect = self.img.get_rect()
        self.rect.topleft = (x, y)
        self.function = function
        self.clicked = False

        self.window.blit(self.img, (self.rect.x, self.rect.y))

    def act(self):
        action = False

        pos = pygame.mouse.get_pos()

        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] and not self.clicked:
                self.clicked = True
                action = True

        if not pygame.mouse.get_pressed()[0]:
            self.clicked = False

        if action:
            self.function()
