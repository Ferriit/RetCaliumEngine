import pygame as pg
import tkinter as tk
import sys
import math


root = tk.Tk()

pg.init()

WIDTH, HEIGHT = (root.winfo_screenwidth(), root.winfo_screenheight())

window = pg.display.set_mode((WIDTH, HEIGHT)) # Set the screen resolution to the monitor's resolution

Points = []

WorldSpacePoints = []

Lines = []

#AllowNewPoint = True

zoom = 1
Offset = (0, 0)

print(f"{WIDTH}x{HEIGHT}")

run = True
panning = False

font = pg.font.SysFont(None, 36)  # None = default font, 36 = font size



def world_to_screen(x, y, offset, zoom, screen_width, screen_height):
    ox, oy = offset
    sx = (x - screen_width / 2) * zoom + screen_width / 2 + ox
    sy = (y - screen_height / 2) * zoom + screen_height / 2 + oy
    return sx, sy


def DrawGrid(surface, width, height, offset, zoom, spacing=100, color=(50, 50, 50)):
    ox, oy = offset

    grid_spacing = spacing

    # Compute world coords of screen edges (in the same coordinate system as points)
    left_world = (0 - ox - width/2) / zoom + width/2
    right_world = (width - ox - width/2) / zoom + width/2
    top_world = (0 - oy - height/2) / zoom + height/2
    bottom_world = (height - oy - height/2) / zoom + height/2

    # Start drawing lines at nearest multiple of grid spacing
    start_x = grid_spacing * (left_world // grid_spacing)
    start_y = grid_spacing * (top_world // grid_spacing)

    x = start_x
    while x <= right_world:
        sx, _ = world_to_screen(x, 0, offset, zoom, width, height)
        pg.draw.line(surface, color, (sx, 0), (sx, height))
        x += grid_spacing

    y = start_y
    while y <= bottom_world:
        _, sy = world_to_screen(0, y, offset, zoom, width, height)
        pg.draw.line(surface, color, (0, sy), (width, sy))
        y += grid_spacing


def RenderList(window, Points, MarkedIDX, MarkedForLinking: tuple[int, int]):
    Bevel = 5
    Size = 36
    ListFont = pg.font.SysFont(None, Size - Bevel)

    Visible = math.floor(HEIGHT / Size)
    Visible = Visible - Visible % 2

    if MarkedIDX > Visible / 2 and len(Points) + 8 > Visible:
        Offset = (MarkedIDX - (Visible / 2)) * Size
    else:
        Offset = 0
    
    pg.draw.rect(window, (25, 25, 25), (WIDTH - 200, 0, 200, HEIGHT))
    for i in range(len(Points)):
        Color = (0, 128, 255) if i != MarkedIDX else (0, 255, 255)
        if i in MarkedForLinking:
            Color = (255, 0, 0) if i != MarkedIDX else (255, 196, 196)

        pg.draw.rect(window, Color, (WIDTH - (200 - Bevel), Bevel + (i + 1) * Size - Offset, 200 - 2 * Bevel, Size - 2 * Bevel))       # Render box for text
        px, py = Points[i]
        PointLabel = ListFont.render(f"({px}, {py})", True, (255, 255, 255) if i != MarkedIDX else (0, 0, 0))
        window.blit(PointLabel, (WIDTH - (200 - Bevel) + Bevel / 2, (Bevel * 1.5) + (i + 1) * Size - Offset))

    pg.draw.rect(window, (25, 25, 25), (WIDTH - 200, 0, 200, Size))
    ListLabel = ListFont.render(f"Points:", True, (255, 255, 255))
    window.blit(ListLabel, (WIDTH - 195, 5))

ListPointer = 0

MarkedForLinking = (-1, -1)

while run:
    window.fill((0, 0, 0))
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            sys.exit()

        elif event.type == pg.KEYDOWN:
            # Scrolling up and down in the list
            if event.key == pg.K_UP and len(Points) > 1:
                ListPointer -= 1
                ListPointer %= max(0, len(Points))

            elif event.key == pg.K_DOWN and len(Points) > 1:
                ListPointer += 1
                ListPointer %= max(0, len(Points))

            # Deleting points
            elif event.key == pg.K_BACKSPACE and len(Points) > 0:
                Points.pop(ListPointer)
                WorldSpacePoints.pop(ListPointer)
                ListPointer -= 1
                if len(Points) > 1:
                    ListPointer %= len(Points)
                else:
                    ListPointer = 0

            # Linking Points
            elif event.key == pg.K_RETURN:
                ShiftPressed = pg.key.get_pressed()[pg.K_LSHIFT] or pg.key.get_pressed()[pg.K_RSHIFT]
                if not ShiftPressed:
                    FM, LM = MarkedForLinking               # First Marked, Last Marked
                    
                    if ListPointer == FM:
                        FM = -1

                    elif ListPointer == LM:
                        LM = -1

                    elif FM == -1:
                        FM = ListPointer

                    elif LM == -1:
                        LM = ListPointer

                    else:
                        LM = -1
                        FM = -1

                    MarkedForLinking = FM, LM

                else:
                    FM, LM = MarkedForLinking
                    Lines.append((FM, LM))
                    FM = -1
                    LM = -1
                    MarkedForLinking = FM, LM

        elif event.type == pg.MOUSEBUTTONDOWN:
            MouseButtons = pg.mouse.get_pressed()
            ox, oy = Offset
            if MouseButtons[0] or MouseButtons[2]:          # Place points
                mx, my = pg.mouse.get_pos()
                wx = (mx - WIDTH / 2) / zoom + WIDTH / 2 - ox / zoom
                wy = (my - HEIGHT / 2) / zoom + HEIGHT / 2 - oy / zoom
                if (wx, wy) not in Points and (round(wx / 100) * 100, round(wy / 100) * 100) not in Points:
                    Points.append((wx, wy) if MouseButtons[0] else (round(wx / 100) * 100, round(wy / 100) * 100))
                    WorldSpacePoints.append((round(wx) / 100, round(wy) / 100) if MouseButtons[0] else (round(wx / 100), round(wy / 100)))
    
            elif MouseButtons[1]:
                pg.mouse.get_rel()
                panning = True

        elif event.type == pg.MOUSEWHEEL:
            # Current mouse position on screen
            mx, my = pg.mouse.get_pos()

            # Convert screen pos to world pos (before zoom change)
            wx_before = (mx - WIDTH / 2 - Offset[0]) / zoom + WIDTH / 2
            wy_before = (my - HEIGHT / 2 - Offset[1]) / zoom + HEIGHT / 2

            # Update zoom (clamp zoom to avoid too small or too large values)
            zoom_factor = (2 + event.y) / 2
            zoom_new = zoom * zoom_factor
            zoom_new = max(0.1, min(zoom_new, 10))  # Clamp zoom between 0.1 and 10
            zoom = zoom_new

            # Convert mouse pos to world pos (after zoom change)
            wx_after = (mx - WIDTH / 2 - Offset[0]) / zoom + WIDTH / 2
            wy_after = (my - HEIGHT / 2 - Offset[1]) / zoom + HEIGHT / 2

            # Adjust offset so the point under the cursor stays fixed
            ox, oy = Offset
            ox += (wx_after - wx_before) * zoom
            oy += (wy_after - wy_before) * zoom
            Offset = (ox, oy)


        elif event.type == pg.MOUSEBUTTONUP:
            panning = False

    if panning:
        ox, oy = Offset
        cx, cy = pg.mouse.get_rel()
        ox += cx
        oy += cy
        Offset = ox, oy

    #MouseButtons = pg.mouse.get_pressed()
    #if MouseButtons[0]:                                             # Process LMB
    #    if AllowNewPoint:
    #        Points.append(pg.mouse.get_pos())                  # Add new point to list
    #    else:
    #        Points[len(Points) - 1] = pg.mouse.get_pos()  # Replace point in list

    DrawGrid(window, WIDTH, HEIGHT, Offset, zoom)

    RenderList(window, WorldSpacePoints, ListPointer, MarkedForLinking)


    # Draw Lines
    for i in range(len(Lines)):
        FM, LM = Lines[i]
        fx, fy = Points[FM]
        lx, ly = Points[LM]
        pg.draw.line(window, (255, 0, 0), world_to_screen(fx, fy, Offset, zoom, WIDTH, HEIGHT), world_to_screen(lx, ly, Offset, zoom, WIDTH, HEIGHT), 2)


    # Draw Points
    ox, oy = Offset
    for i in range(len(Points)):
        x, y = Points[i]
        x = (x - WIDTH / 2) * zoom + WIDTH / 2 + ox
        y = (y - HEIGHT / 2) * zoom + HEIGHT / 2 + oy
        Color = (0, 255, 0) if i != ListPointer else (255, 255, 0)
        
        if i in MarkedForLinking:
            Color = (255, 128, 255) if i != ListPointer else (255, 196, 196)

        pg.draw.aacircle(window, Color, (x, y), max(7.5 * zoom, 1))

        ax, ay = WorldSpacePoints[i]
        PositionSurface = font.render(f"({ax}, {ay})", True, Color)
        window.blit(PositionSurface, (x + max(2, 7.5 * zoom), y))


    pg.display.flip()
