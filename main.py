import numpy as np
import pygame
import time

pygame.init()
pygame.font.init()
text_font = pygame.font.SysFont('Comic Sans MS', 30)
win = pygame.display.set_mode((800, 800))

def mandelbrot(c, n):
    z = 0
    for i in range(n):
        z = z ** 2 + c
        if np.abs(z) >= 2:
            return i
    return n

topleft = -2 + 1.5j
increment = 0.005

#topleft = -0.5080700000000001+0.65207j
#increment = 6.999999999999993e-05

plane = np.array([[topleft + (k - i * 1j)* increment for i in range(800)] for k in range(800)])
mandelbrot_plane = np.zeros((800, 800))

def generate():
    t1 = time.time()
    for i in range(800):
        for j in range(800):
            mandelbrot_plane[i, j] = mandelbrot(plane[i, j], 500)

    win.fill((0, 0, 0))
    maximum = np.max(mandelbrot_plane)
    for i in range(800):
        for j in range(800):
            pygame.draw.circle(win, color=mandelbrot_plane[i, j] * (255 / maximum) * np.array([1,1,1]), center=(i, j), radius=1)

    zoom_text = text_font.render(f"{round(0.005 / increment)}x", False, (255, 255, 255))
    pygame.draw.rect(win, color=(0,0,0), rect=pygame.Rect(0, 750, 40 + zoom_text.get_width(), 50))
    win.blit(zoom_text, (20, 750))

    pygame.image.save(win, "mandelbrot.png")
    print(time.time() - t1)

generate()
running = True
mouse_down = False
mouse_coord = (0, 0)
while running:
    set_image = pygame.image.load("mandelbrot.png")
    win.fill((0, 0, 0))
    win.blit(set_image, (0,0))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if mouse_down:
                end_coord = pygame.mouse.get_pos()
                bottomright = plane[end_coord[0], end_coord[1]]
                print(topleft, bottomright)
                diff = max(np.abs(topleft.real - bottomright.real), np.abs(topleft.imag - bottomright.imag))
                print(diff)
                increment = diff / 800
                mouse_down = False

                plane = np.array([[topleft + (k - i * 1j) * increment for i in range(800)] for k in range(800)])
                print(plane[-1,-1], topleft, increment)

                generate()
            else:
                mouse_down = True
                mouse_coord = pygame.mouse.get_pos()
                topleft = plane[mouse_coord[0], mouse_coord[1]]
    if mouse_down:
        current_mouse_coord = pygame.mouse.get_pos()
        pygame.draw.line(win, color=(255,255,255), start_pos=mouse_coord, end_pos=(mouse_coord[0], current_mouse_coord[1]))
        pygame.draw.line(win, color=(255, 255, 255), start_pos=mouse_coord,
                         end_pos=(current_mouse_coord[0], mouse_coord[1]))
        pygame.draw.line(win, color=(255, 255, 255), start_pos=(mouse_coord[0], current_mouse_coord[1]),
                         end_pos=current_mouse_coord)
        pygame.draw.line(win, color=(255, 255, 255), start_pos=(current_mouse_coord[0], mouse_coord[1]),
                         end_pos=current_mouse_coord)
    pygame.display.flip()