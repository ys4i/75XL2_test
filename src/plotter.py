class RealTimePlotter:
    def __init__(self):
        self.fig, self.ax = plt.subplots()
        self.rotation_speed_data = []
        self.heart_rate_data = []
        self.line1, = self.ax.plot([], [], label='Rotation Speed (rpm)', color='blue')
        self.line2, = self.ax.plot([], [], label='Heart Rate (bpm)', color='red')
        self.ax.set_xlim(0, 100)  # Set x-axis limits
        self.ax.set_ylim(0, 300)  # Set y-axis limits
        self.ax.set_xlabel('Time (s)')
        self.ax.set_ylabel('Values')
        self.ax.legend()
        self.ax.grid()

    def initialize_plot(self):
        plt.ion()  # Turn on interactive mode
        plt.show()

    def update_plot(self, rotation_speed, heart_rate):
        self.rotation_speed_data.append(rotation_speed)
        self.heart_rate_data.append(heart_rate)

        # Update the data for the lines
        self.line1.set_xdata(range(len(self.rotation_speed_data)))
        self.line1.set_ydata(self.rotation_speed_data)

        self.line2.set_xdata(range(len(self.heart_rate_data)))
        self.line2.set_ydata(self.heart_rate_data)

        # Adjust x-axis limits if needed
        if len(self.rotation_speed_data) > 100:
            self.ax.set_xlim(len(self.rotation_speed_data) - 100, len(self.rotation_speed_data))

        self.fig.canvas.draw()
        self.fig.canvas.flush_events()