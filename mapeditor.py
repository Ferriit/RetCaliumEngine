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

Sections = []
SectionHeights = []

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


def RenderPointsList(window, Points, MarkedIDX, MarkedForLinking: tuple[int, int]):
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


def RenderLineList(window, Points, MarkedIDX, MarkedForLinking: tuple[int, int]):
    Bevel = 5
    Size = 36
    ListFont = pg.font.SysFont(None, Size - Bevel)


    Visible = math.floor(HEIGHT / Size)
    Visible = Visible - Visible % 2

    if MarkedIDX > Visible / 2 and len(Points) + 8 > Visible:
        Offset = (MarkedIDX - (Visible / 2)) * Size
    else:
        Offset = 0
    
    pg.draw.rect(window, (25, 25, 25), (WIDTH - 400, 0, 200, HEIGHT))
    for i in range(len(Points)):
        Color = (255, 0, 0) if i != MarkedIDX else (255, 255, 255)
        if i in MarkedForLinking:
            Color = (255, 0, 0) if i != MarkedIDX else (255, 196, 196)

        pg.draw.rect(window, Color, (WIDTH - (400 - Bevel), Bevel + (i + 1) * Size - Offset, 200 - 2 * Bevel, Size - 2 * Bevel))       # Render box for text
        px, py = Points[i]
        PointLabel = ListFont.render(f"{WorldSpacePoints[px]}, {WorldSpacePoints[py]}", True, (255, 255, 255) if i != MarkedIDX else (0, 0, 0))
        window.blit(PointLabel, (WIDTH - (400 - Bevel) + Bevel / 2, (Bevel * 1.5) + (i + 1) * Size - Offset))

    pg.draw.rect(window, (25, 25, 25), (WIDTH - 400, 0, 200, Size))
    ListLabel = ListFont.render(f"Lines:", True, (255, 255, 255))
    window.blit(ListLabel, (WIDTH - 395, 5))


def RenderSectionList(window, Points, MarkedIDX, MarkedForLinking: tuple[int, int]):
    Bevel = 5
    Size = 36
    ListFont = pg.font.SysFont(None, Size - Bevel)

    Visible = math.floor(HEIGHT / Size)
    Visible = Visible - Visible % 2

    if MarkedIDX > Visible / 2 and len(Points) + 8 > Visible:
        Offset = (MarkedIDX - (Visible / 2)) * Size
    else:
        Offset = 0
    
    pg.draw.rect(window, (25, 25, 25), (WIDTH - 600, 0, 200, HEIGHT))
    for i in range(len(Points)):
        Color = (255, 255, 0) if i != MarkedIDX else (255, 255, 255)
        if i in MarkedForLinking:
            Color = (255, 0, 0) if i != MarkedIDX else (255, 196, 196)

        pg.draw.rect(window, Color, (WIDTH - (600 - Bevel), Bevel + (i + 1) * Size - Offset, 200 - 2 * Bevel, Size - 2 * Bevel))       # Render box for text
        #px, py = Points[i]
        PointLabel = ListFont.render(f"[{i}]", True, (0, 0, 0))
        window.blit(PointLabel, (WIDTH - (600 - Bevel) + Bevel / 2, (Bevel * 1.5) + (i + 1) * Size - Offset))

    pg.draw.rect(window, (25, 25, 25), (WIDTH - 600, 0, 200, Size))
    ListLabel = ListFont.render(f"Sections:", True, (255, 255, 255))
    window.blit(ListLabel, (WIDTH - 595, 5))


ListPointer = 0
LineListPointer = 0
SectionListPointer = 0
SelectedList = 0        # 0 for PointsList, 1 for LineList, 2 for SectionList when selecting which one to interact with

MarkedForLinking = (-1, -1)

LinesMarkedForLinking = []

poly_surf = pg.Surface((WIDTH, HEIGHT), pg.SRCALPHA)

while run:
    window.fill((0, 0, 0))
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            sys.exit()

        elif event.type == pg.KEYDOWN:
            # Scrolling up and down in the points list
            if event.key == pg.K_UP and len(Points) > 1 and SelectedList == 0:
                ListPointer -= 1
                ListPointer %= max(0, len(Points))

            elif event.key == pg.K_DOWN and len(Points) > 1 and SelectedList == 0:
                ListPointer += 1
                ListPointer %= max(0, len(Points))

            # Scrolling up and down in the lines list
            elif event.key == pg.K_UP and len(Lines) > 1 and SelectedList == 1:
                LineListPointer -= 1
                LineListPointer %= max(0, len(Lines))

            elif event.key == pg.K_DOWN and len(Lines) > 1 and SelectedList == 1:
                LineListPointer += 1
                LineListPointer %= max(0, len(Lines))

            # Deleting points
            elif event.key == pg.K_BACKSPACE and len(Points) > 0 and SelectedList == 0:
                Points.pop(ListPointer)
                WorldSpacePoints.pop(ListPointer)

                PoppedAmount = 0

                Lines = [line for line in Lines if ListPointer not in line]

                ListPointer -= 1
                if len(Points) > 1:
                    ListPointer %= len(Points)
                else:
                    ListPointer = 0


            # Deleting Lines
            elif event.key == pg.K_BACKSPACE and len(Lines) > 0 and SelectedList == 1:
                Lines.pop(LineListPointer)
                LineListPointer -= 1
                if len(Lines) > 1:
                    LineListPointer %= len(Points)
                else:
                    LineListPointer = 0

                if len(Lines) == 0:
                    SelectedList = 0

            # Linking Points
            elif event.key == pg.K_RETURN and SelectedList == 0:
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

                if (FM, LM) not in Lines and (LM, FM) not in Lines:
                    MarkedForLinking = FM, LM

                if FM != -1 and LM != -1: 
                    if (FM, LM) not in Lines and (LM, FM) not in Lines and FM != -1 and LM != -1:
                        Lines.append((FM, LM))
                    FM = -1
                    LM = -1
                    MarkedForLinking = FM, LM

            # Join lines to section if Shift + Enter, clear list if Ctrl + Enter, add to list if Enter
            elif event.key == pg.K_RETURN and SelectedList == 1:
                Keys = pg.key.get_pressed()
                if Keys[pg.K_LCTRL] or Keys[pg.K_RCTRL]:
                    LinesMarkedForLinking = 0

                elif Keys[pg.K_LSHIFT] or Keys[pg.K_RSHIFT]:
                    # Sort before comparing to normalize order
                    current_section_sorted = sorted(LinesMarkedForLinking)
                    if not any(sorted(path) == current_section_sorted for path in Sections):
                        Sections.append(LinesMarkedForLinking[:])  # Copy to avoid shared reference
                        LinesMarkedForLinking = []
 
                else:
                    if Lines[LineListPointer] not in LinesMarkedForLinking:
                        LinesMarkedForLinking.append(LineListPointer)
                    
                    else:
                        LinesMarkedForLinking = []

            elif event.key in (pg.K_LCTRL, pg.K_RCTRL):
                    SelectedList += 1
                    SelectedList %= 3

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


    poly_surf.fill((0, 0, 0, 0))


    # Draw Sections
    for i in range(len(Sections)):
        AveragePosition = (0, 0)
        DrawPoints = []
        Iterations = 0
        for j in Sections[i]:
            FM, LM = Lines[j]
            p1, p2 = Points[FM], Points[LM]
            x1, y1 = p1
            x2, y2 = p2
            
            ax, ay = AveragePosition
            ax += x1 + x2
            ay += y1 + y2
            AveragePosition = ax, ay

            DrawPoints.append(world_to_screen(x1, y1, Offset, zoom, WIDTH, HEIGHT))
            DrawPoints.append(world_to_screen(x2, y2, Offset, zoom, WIDTH, HEIGHT))
            Iterations += 1

        ax, ay = AveragePosition
        ax /= Iterations * 2
        ay /= Iterations * 2
        AveragePosition = world_to_screen(ax, ay, Offset, zoom, WIDTH, HEIGHT)

        pg.draw.polygon(window, (128, 128, 0), DrawPoints)

        SectionText = font.render(f"[{i}]", True, (0, 0, 255))
        text_rect = SectionText.get_rect(center=AveragePosition)
        window.blit(SectionText, text_rect)

    DrawGrid(window, WIDTH, HEIGHT, Offset, zoom)

    # Draw Lines
    for i in range(len(Lines)):
        FM, LM = Lines[i]
        fx, fy = Points[FM]
        lx, ly = Points[LM]
        Color = (255, 0, 0) if i != LineListPointer else (255, 255, 255)
        if SelectedList == 0:
            Color = (255, 0, 0)

        pg.draw.line(window, Color, world_to_screen(fx, fy, Offset, zoom, WIDTH, HEIGHT), world_to_screen(lx, ly, Offset, zoom, WIDTH, HEIGHT), 2)


    # Draw Points
    ox, oy = Offset
    for i in range(len(Points)):
        x, y = Points[i]
        x = (x - WIDTH / 2) * zoom + WIDTH / 2 + ox
        y = (y - HEIGHT / 2) * zoom + HEIGHT / 2 + oy
        Color = (0, 255, 0) if i != ListPointer else (255, 255, 255)

        
        if i in MarkedForLinking:
            Color = (255, 128, 255) if i != ListPointer else (255, 64, 64)

        if SelectedList == 1:
            Color = (0, 255, 0)

        pg.draw.aacircle(window, Color, (x, y), max(7.5 * zoom, 1))

        ax, ay = WorldSpacePoints[i]
        PositionSurface = font.render(f"({ax}, {ay})", True, Color)
        window.blit(PositionSurface, (x + max(2, 7.5 * zoom), y))

    RenderLineList(window, Lines, LineListPointer if SelectedList == 1 else -1, (-1, -1))
    RenderPointsList(window, WorldSpacePoints, ListPointer if SelectedList == 0 else -1, MarkedForLinking)
    RenderSectionList(window, Sections, -1, (-1, -1))

    pg.display.flip()
