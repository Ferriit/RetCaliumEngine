CXX = g++
CXXFLAGS = -Wall -O2
LDFLAGS = -lglfw -lGLEW -lGL
SRC = renderer.cpp maploader.cpp
OBJ = $(SRC:.cpp=.o)
TARGET = renderer

all: $(TARGET)

$(TARGET): $(OBJ)
	$(CXX) -o $@ $^ $(LDFLAGS)

%.o: %.cpp
	$(CXX) $(CXXFLAGS) -c $< -o $@

clean:
	rm -f *.o $(TARGET)


install:
	@echo "Installing dependencies (GLFW, GLEW, Mesa)..."
	@if [ -x "$$(command -v pacman)" ]; then \
		sudo pacman -S --needed glfw glew mesa; \
	elif [ -x "$$(command -v apt)" ]; then \
		sudo apt update && sudo apt install -y libglfw3-dev libglew-dev mesa-common-dev; \
	elif [ -x "$$(command -v dnf)" ]; then \
		sudo dnf install glfw-devel glew-devel mesa-libGL-devel; \
	elif [ -x "$$(command -v zypper)" ]; then \
		sudo zypper install glfw-devel glew-devel Mesa-libGL-devel; \
	else \
		echo "Unsupported package manager. Install GLFW, GLEW, and Mesa manually."; \
	fi

