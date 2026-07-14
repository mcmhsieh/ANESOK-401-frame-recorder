import sys
import time
import datetime
import threading
import pathlib
import queue

import numpy as np
import cv2
import PIL
import PIL.ImageTk

import tkinter as tk

import suear_camera


if __name__ == '__main__':

    client = suear_camera.SuearClient()
    client.connect()

    print(f'Device: {client.vendor} {client.model} {client.version}  (Serial number: {client.serial_num})')
    print(f'Battery: {client.battery_level}% ({"C" if client.is_charging else "Not c"}harging)')

    print('battery_level', client.battery_level)
    print('model', client.model)
    print('serial_num', client.serial_num)
    print('vendor', client.vendor)
    print('version', client.version)
    print('ssid', client.ssid)
    print('capacity', client.capacity)
    print('is_charging', client.is_charging)

    stop_event = threading.Event()
    frame_queue = queue.Queue()

    def video_loop():
        while not stop_event.is_set():
            frame = client.get_frame()
            if frame is not None and frame.complete and not frame_queue.full():
                frame_queue.put_nowait((frame.index, np.array(frame.data, np.uint8), datetime.datetime.now(datetime.timezone.utc)))

    video_loop_thread = threading.Thread(target=video_loop, args=(), daemon=True)
    video_loop_thread.start()

    class MainWindow():

        def __init__(self, main):

            self.canvas = tk.Canvas(main, width=1280, height=720)
            self.canvas.grid(row=0, column=0)
            self.canvas_image = self.canvas.create_image(0, 0, anchor='nw', image=None)

            buttons_frame = tk.Frame(main)
            buttons_frame.grid(row=1)

            self.record_start_stop_button = tk.Button(buttons_frame, text='Start recording (or hit <space bar>)', command=self.on_record_start_stop_button,
                                                      height=5, width=100 , bg='gold')
            self.record_start_stop_button.grid(row=0, column=0)

            self.mirror_image = tk.IntVar(value=1)
            mirror_checkbutton = tk.Checkbutton(buttons_frame, text='Mirror image', variable=self.mirror_image)
            mirror_checkbutton.grid(row=0, column=1)

            main.bind('<space>', lambda event: self.on_record_start_stop_button())
            main.focus_force()

            self.record = False

        def on_record_start_stop_button(self):
            self.record = not self.record
            self.record_start_stop_button.config(text='Stop recording (or hit <space bar>)' if self.record else 'Start recording (or hit <space bar>)')

        def update(self):
            new_images = []
            while True:
                if frame_queue.empty():
                    break
                frame_index, frame_data, frame_time = frame_queue.get_nowait()

                image = cv2.imdecode(frame_data, cv2.IMREAD_ANYCOLOR | cv2.IMREAD_ANYDEPTH)
                image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

                new_images.append((frame_index, frame_time, image))

                if self.record:
                    filename = f'{frame_time.strftime("%Y%m%d-%H%M%S%f")}.{frame_index:03d}.jpg'
                    output_path = pathlib.Path('./captured_frames') / filename
                    output_path.parent.mkdir(parents=True, exist_ok=True)
                    frame_data.tofile(output_path)

            if len(new_images) > 0:
                frame_index, frame_time, image = new_images[-1]

                if self.mirror_image.get():
                    image = np.fliplr(image)

                self.image = PIL.ImageTk.PhotoImage(PIL.Image.fromarray(image))
                self.canvas.itemconfig(self.canvas_image, image=self.image)


    try:
        response = client.open_video()

        root = tk.Tk()
        window = MainWindow(root)
        root.geometry('+50+50')

        def update():
            window.update()
            root.after(5, update)
        root.after(1, update)
        root.mainloop()

    finally:
        stop_event.set()
        print('video_loop_thread.join()')
        video_loop_thread.join(2)
        print('client.disconnect()')
        client.disconnect()
        print('root.destroy()')
        try:
            root.destroy()
        except tk.TclError as ex:
            # can't invoke "destroy" command: application has been destroyed
            print(ex)
