import pygame as pg
import tkinter as tk
import sys
import math
from collections import defaultdict, deque


root = tk.Tk()

pg.init()

WIDTH, HEIGHT = (root.winfo_screenwidth(), root.winfo_screenheight())

window = pg.display.set_mode((WIDTH, HEIGHT)) # Set the screen resolution to the monitor's resolution

Points = []

WorldSpacePoints = []

Lines = []
Portals = []

Sections = []
SectionHeights = []
SectionFloors = []

#AllowNewPoint = True

zoom = 1
Offset = (0, 0)

print(f"{WIDTH}x{HEIGHT}")

run = True
panning = False

font = pg.font.SysFont(None, 36)  # None = default font, 36 = font size
sectionfont = pg.font.SysFont(None, 24)


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


def RenderLineList(window, Points, MarkedIDX, MarkedForLinking, Portals):
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
        if type(MarkedForLinking) != int:
            if i in MarkedForLinking:
                Color = (128, 0, 0) if i != MarkedIDX else (255, 196, 196)

        if Portals[i] == 1:
            Color = (128, 0, 128) if i != MarkedIDX else (255, 128, 255)

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
        PointLabel = ListFont.render(f"[{i}], ({round(SectionHeights[i] * 10) / 10}m, {round(SectionFloors[i] * 10) / 10}m)", True, (0, 0, 0))
        window.blit(PointLabel, (WIDTH - (600 - Bevel) + Bevel / 2, (Bevel * 1.5) + (i + 1) * Size - Offset))

    pg.draw.rect(window, (25, 25, 25), (WIDTH - 600, 0, 200, Size))
    ListLabel = ListFont.render(f"Sections:", True, (255, 255, 255))
    window.blit(ListLabel, (WIDTH - 595, 5))


def MakeClockwiseSection(Points, Lines, Section, Clockwise=True):
    """
    Returns a list of point indices forming a connected, non-self-intersecting loop.
    Points   : list of (x, y) tuples
    Lines    : list of (i, j) tuples of point-indices
    Section  : list of indices into Lines
    Clockwise: desired winding order
    """
    # 1) Build adjacency from selected lines
    adjacency = defaultdict(list)
    for lineIndex in Section:
        a, b = Lines[lineIndex]
        adjacency[a].append(b)
        adjacency[b].append(a)

    # 2) Find a starting point (one with only one neighbor if it's an open path)
    start = None
    for pointIdx, neighbors in adjacency.items():
        if len(neighbors) == 1:
            start = pointIdx
            break
    if start is None:
        start = next(iter(adjacency))  # Closed loop

    # 3) Traverse the loop/path
    visited = set()
    orderedIndices = []

    current = start
    prev = None
    while True:
        orderedIndices.append(current)
        visited.add(current)
        neighbors = adjacency[current]

        # Choose the next unvisited neighbor (prefer avoiding backtracking)
        nextPoint = None
        for neighbor in neighbors:
            if neighbor != prev and neighbor not in visited:
                nextPoint = neighbor
                break

        if nextPoint is None:
            break  # Done

        prev, current = current, nextPoint

    # 4) If clockwise direction is desired, compute area and reverse if needed
    def signedArea(indices):
        area = 0
        n = len(indices)
        for i in range(n):
            x1, y1 = Points[indices[i]]
            x2, y2 = Points[indices[(i + 1) % n]]
            area += (x1 * y2 - x2 * y1)
        return area / 2

    area = signedArea(orderedIndices)
    isClockwise = area < 0
    if isClockwise != Clockwise:
        orderedIndices.reverse()

    return orderedIndices


ListPointer = 0
LineListPointer = 0
SectionListPointer = 0
SelectedList = 0        # 0 for PointsList, 1 for LineList, 2 for SectionList when selecting which one to interact with

MarkedForLinking = (-1, -1)

LinesMarkedForLinking = []

poly_surf = pg.Surface((WIDTH, HEIGHT), pg.SRCALPHA)

def AdjustIndex(i, RemovedIndex):
    return i - 1 if i > RemovedIndex else i

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

            # Scrolling up and down in the sections list
            elif event.key == pg.K_UP and len(Sections) > 1 and SelectedList == 2:
                SectionListPointer -= 1
                SectionListPointer %= max(0, len(Sections))

            elif event.key == pg.K_DOWN and len(Sections) > 1 and SelectedList == 2:
                SectionListPointer += 1
                SectionListPointer %= max(0, len(Sections))

            # Deleting points
            elif event.key == pg.K_BACKSPACE and len(Points) > 0 and SelectedList == 0:
                Points.pop(ListPointer)
                WorldSpacePoints.pop(ListPointer)

                FlattenedSections = [[i for lineindex in section for i in Lines[lineindex]] for section in Sections]

                SectionsToRemove = set()
                for i in range(len(FlattenedSections)):
                    if ListPointer in FlattenedSections[i]:
                        SectionsToRemove.add(i)


                Sections = [item for i, item in enumerate(Sections) if i not in SectionsToRemove]
                SectionFloors = [item for i, item in enumerate(SectionFloors) if i not in SectionsToRemove]
                SectionHeights = [item for i, item in enumerate(SectionHeights) if i not in SectionsToRemove]

                Lines = [line for line in Lines if ListPointer not in line]

                Lines = [tuple(AdjustIndex(i, ListPointer) for i in line) for line in Lines]

                ListPointer -= 1
                if len(Points) == 0:
                    ListPointer = 0
                else:
                    ListPointer %= len(Points)


            # Deleting Lines
            elif event.key == pg.K_BACKSPACE and len(Lines) > 0 and SelectedList == 1:
                Lines.pop(LineListPointer)

                NewSections = []
                for section in Sections:
                    if LineListPointer in section:
                        # Skip sections containing the removed line
                        continue
                    # Shift line indices greater than removed index down by 1
                    ShiftedSection = [idx - 1 if idx > LineListPointer else idx for idx in section]
                    NewSections.append(ShiftedSection)

                Sections = NewSections

                LineListPointer -= 1
                if len(Lines) == 0:
                    SelectedList = 0
                
                else:
                    LineListPointer %= len(Lines)

            elif event.key == pg.K_BACKSPACE and len(Sections) > 0 and SelectedList == 2:
                Sections.pop(SectionListPointer)
                SectionHeights.pop(SectionListPointer)
                SectionFloors.pop(SectionListPointer)
                SectionListPointer -= 1
                if len(Sections) == 0:
                    SelectedList = 1

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
                        Portals.append(0)
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
                        Sections.append(MakeClockwiseSection(Points, Lines, LinesMarkedForLinking[:]))  # Copy to avoid shared reference
                        SectionHeights.append(1)
                        SectionFloors.append(1)
                        LinesMarkedForLinking = []
 
                else:
                    if LineListPointer != LinesMarkedForLinking:
                        LinesMarkedForLinking.append(LineListPointer)
                    
                    else:
                        LinesMarkedForLinking = []

            elif event.key in (pg.K_LCTRL, pg.K_RCTRL):
                    SelectedList += 1
                    if len(Lines) == 0:
                        SelectedList = 0

                    elif len(Sections) == 0:
                        SelectedList %= 2
                        
                    else:
                        SelectedList %= 3

            # Make a line a portal
            elif event.key == pg.K_p and SelectedList == 1:
                Portals[LineListPointer] += 1
                Portals[LineListPointer] %= 2


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

    Keys = pg.key.get_pressed()
    if Keys[pg.K_RIGHT] and SelectedList == 2:
        if Keys[pg.K_LSHIFT] or Keys[pg.K_RSHIFT]:
            SectionFloors[SectionListPointer] += 0.01
            SectionFloors[SectionListPointer] = round(SectionFloors[SectionListPointer] * 100) / 100
        else:
            SectionHeights[SectionListPointer] += 0.01
            SectionHeights[SectionListPointer] = round(SectionHeights[SectionListPointer] * 100) / 100

    if Keys[pg.K_LEFT] and SelectedList == 2:
        if Keys[pg.K_LSHIFT] or Keys[pg.K_RSHIFT]:
            SectionFloors[SectionListPointer] -= 0.01
            SectionFloors[SectionListPointer] = round(SectionFloors[SectionListPointer] * 100) / 100
        else:
            SectionHeights[SectionListPointer] -= 0.01
            SectionHeights[SectionListPointer] = round(SectionHeights[SectionListPointer] * 100) / 100

    if Keys[pg.K_r] and SelectedList == 2:
        if Keys[pg.K_RSHIFT] or Keys[pg.K_LSHIFT]:
            SectionFloors[SectionListPointer] = round(SectionFloors[SectionListPointer])
        else:
            SectionHeights[SectionListPointer] = round(SectionHeights[SectionListPointer])

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

        Color = (128, 128, 0)if i != SectionListPointer else (196, 196, 196)
        if SelectedList in (0, 1):
            Color = (128, 128, 0)

        print(i, Sections[i])

        SectionSurface = pg.Surface((WIDTH, HEIGHT), pg.SRCALPHA)
        pg.draw.polygon(SectionSurface, Color, DrawPoints)
        
        window.blit(SectionSurface, (0, 0))

        SectionText = sectionfont.render(f"[{i}]\n{SectionHeights[i]}m\n{SectionFloors[i]}m", True, (0, 0, 255) if i != SectionListPointer and SelectedList == 2 else (0, 0, 0))

        text_rect = SectionText.get_rect(center=AveragePosition)
        window.blit(SectionText, text_rect)

    DrawGrid(window, WIDTH, HEIGHT, Offset, zoom)

    # Draw Lines
    for i in range(len(Lines)):
        FM, LM = Lines[i]
        fx, fy = Points[FM]
        lx, ly = Points[LM]
        Color = (255, 0, 0) if i != LineListPointer else (255, 255, 255)
        if SelectedList in (0, 2):
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

        if SelectedList in (1, 2):
            Color = (0, 255, 0)

        pg.draw.aacircle(window, Color, (x, y), max(7.5 * zoom, 1))

        ax, ay = WorldSpacePoints[i]
        PositionSurface = font.render(f"({ax}, {ay})", True, Color)
        window.blit(PositionSurface, (x + max(2, 7.5 * zoom), y))

    RenderLineList(window, Lines, LineListPointer if SelectedList == 1 else -1, LinesMarkedForLinking, Portals)
    RenderPointsList(window, WorldSpacePoints, ListPointer if SelectedList == 0 else -1, MarkedForLinking)
    RenderSectionList(window, Sections, SectionListPointer if SelectedList == 2 else -1, (-1, -1))

    pg.display.flip()
