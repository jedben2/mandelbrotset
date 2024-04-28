import numpy as np
import pygame
import time
import ray

ray.init()
pygame.init()
pygame.font.init()
text_font = pygame.font.SysFont('Comic Sans MS', 30)
win = pygame.display.set_mode((800, 800))

topleft = -2 + 1.5j
increment = 0.005
N = 200
# topleft = -0.311962621923828+0.6462113426464844j
# increment = 2.994653320320673e-09

plane = np.array([[topleft + (k - i * 1j)* increment for i in range(800)] for k in range(800)])

def colouring(x):
    return x * 255 / N

def mandelbrot(c, n):
    z = 0
    for i in range(n):
        z = np.power(z, 2) + c
        if np.abs(z) >= 2:
            return i
    return n

@ray.remote
def gen_lines(start, stop, plane):
    vals = []
    for i in range(start, stop):
        vals.append([mandelbrot(plane[i, j], N) for j in range(800)])
    return vals


def generate():
    mandelbrot_plane = []
    print("Start rendering")
    win.fill((0, 0, 0))
    t1 = time.time()
    # gen_lines(0, 800)
    num_procs = 8
    tasks = [gen_lines.remote(i * 800 // num_procs, (i + 1) * 800 // num_procs, plane) for i in range(num_procs)]
    mandelbrot_plane_temp = np.array(ray.get(tasks))
    for section in mandelbrot_plane_temp:
        for line in section:
            mandelbrot_plane.append(line)
    mandelbrot_plane = np.array(mandelbrot_plane)

    for i in range(800):
        for j in range(800):
            win.set_at((i, j), colouring(mandelbrot_plane[i,j]) * np.array([1, 1, 1]))

    zoom_text = text_font.render(f"{round(0.005 / increment)}x", False, (255, 255, 255))
    pygame.draw.rect(win, color=(0,0,0), rect=pygame.Rect(0, 750, 40 + zoom_text.get_width(), 50))
    win.blit(zoom_text, (20, 750))

    pygame.image.save(win, "mandelbrot.png")
    print(f"time taken: {round(time.time() - t1, 4)}s\n")

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
                diff = max(np.abs(topleft.real - bottomright.real), np.abs(topleft.imag - bottomright.imag))
                increment = diff / 800
                mouse_down = False

                plane = np.array([[topleft + (k - i * 1j) * increment for i in range(800)] for k in range(800)])
                print(f"Zooming in at topleft {topleft} and increment {increment}\n")

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