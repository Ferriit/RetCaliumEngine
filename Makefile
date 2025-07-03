CXX = g++
CXXFLAGS = -Wall -O2
LDFLAGS = -lglfw -lGLEW -lGL
SRC = renderer.cpp maploader.cpp
OBJ = $(SRC:.cpp=.o)
TARGET = renderer
MAPEDITOR = MapEditor
VENV_DIR = venv/bin/activate  # Change this if your venv is in a different folder

all: $(TARGET) $(MAPEDITOR) clean

$(TARGET): $(OBJ)
	$(CXX) -o $@ $^ $(LDFLAGS)

%.o: %.cpp
	$(CXX) $(CXXFLAGS) -c $< -o $@


$(MAPEDITOR):
	@echo "Building MapEditor using venv..."
	@. $(VENV_DIR) && pyinstaller --onefile mapeditor.py && deactivate


clean:
	rm -f *.o
	rm -rf build __pycache__ *.spec
	
	mkdir build
	mv renderer build/
	mv dist/mapeditor build
	rm -rf dist

install:
	@echo "Installing dependencies (GLFW, GLEW, Mesa, Python, Pip)..."
	@if [ -x "$$(command -v pacman)" ]; then \
		sudo pacman -S --needed glfw glew mesa python python-pip; \
	elif [ -x "$$(command -v apt)" ]; then \
		sudo apt update && sudo apt install -y libglfw3-dev libglew-dev mesa-common-dev python3 python3-pip; \
	elif [ -x "$$(command -v dnf)" ]; then \
		sudo dnf install -y glfw-devel glew-devel mesa-libGL-devel python3 python3-pip; \
	elif [ -x "$$(command -v zypper)" ]; then \
		sudo zypper install -y glfw-devel glew-devel Mesa-libGL-devel python3 python3-pip; \
	else \
		echo "Unsupported package manager. Install GLFW, GLEW, Mesa, Python, and Pip manually."; \
	fi

