import tkinter as tk
from turtle import RawTurtle, ScrolledCanvas, TurtleScreen

def execute_command(event=None):
    command = command_entry.get()
    try:
        if command.startswith("rotate(") and command.endswith(")"):
            angle = int(command[7:-1])  # Extract the angle from "rotate(angle)"
            turtle.right(angle)
        elif command.startswith("forward(") and command.endswith(")"):
            distance = int(command[8:-1])  # Extract the distance from "forward(distance)"
            turtle.forward(distance)
        else:
            status_label.config(text="Invalid command! Try rotate(90) or forward(100).", fg="red")
            return
        status_label.config(text="Command executed successfully!", fg="green")
    except Exception as e:
        status_label.config(text=f"Error: {e}", fg="red")
    finally:
        # Clear the text input field after executing the command
        command_entry.delete(0, tk.END)

# Create main Tkinter window
root = tk.Tk()
root.title("Turtle Command App")

# Turtle canvas frame
canvas_frame = tk.Frame(root)
canvas_frame.pack(fill=tk.BOTH, expand=True)

# Create a canvas and attach a TurtleScreen
canvas = ScrolledCanvas(canvas_frame, width=800, height=800)
canvas.pack(fill=tk.BOTH, expand=True)
turtle_screen = TurtleScreen(canvas)

# Create a RawTurtle
turtle = RawTurtle(turtle_screen)
# turtle.speed(1)

# Input and status frame
input_frame = tk.Frame(root)
input_frame.pack(fill=tk.X)

# Text input for commands
command_label = tk.Label(input_frame, text="Command:")
command_label.pack(side=tk.LEFT, padx=5)

command_entry = tk.Entry(input_frame)
command_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
command_entry.bind("<Return>", execute_command)

# Status label
status_label = tk.Label(root, text="Enter a command and press Enter.", fg="blue")
status_label.pack(fill=tk.X, pady=5)

# Run the application
root.mainloop()
