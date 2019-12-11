import time
from tkinter import *
from threading import Thread

class TimerGUI:
    
    def __init__(self):
        self.gui = Tk()
        self.gui.title('mirrcub3r')

        self.timel = Label(self.gui, text='seconds', font=('Mono Bold', 150), name='time')
        self.timel.config(anchor=CENTER)
        self.timel.pack(expand=True)

        self.reset()
        
    def show(self, parallel):
        self.gui.after(0, lambda: Thread(target=parallel).start())
        self.gui.mainloop()

    def reset(self):
        self.running = False
        self.thread = Thread(target=self.run)
        self.update(0)

    def update(self, time):
        self.timel.configure(text='%.3f seconds' % time)

    def start(self):
        self.running = True
        self.thread.start()

    def stop(self):
        self.running = False

    def run(self):
        start = time.time()
        while self.running:
            time.sleep(.001)
            self.update(time.time() - start)

