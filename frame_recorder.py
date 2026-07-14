import sys
import time
import datetime
import threading
import pathlib
import queue
import tkinter as tk

import numpy as np
import cv2
import PIL
import PIL.ImageTk

import suear_camera


class App(tk.Tk):
    def __init__(self, frame_queue, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.frame_queue = frame_queue

        self.title('ANESOK 401 frame recorder')
        self.geometry('+50+50')

        self.canvas = tk.Canvas(self, width=1280, height=720)
        self.canvas.grid(row=0, column=0)
        self.canvas_image = self.canvas.create_image(0, 0, anchor='nw', image=None)

        buttons_frame = tk.Frame(self)
        buttons_frame.grid(row=1)

        self.record_start_stop_button = tk.Button(buttons_frame, text='Start recording (or hit <space bar>)', command=self.on_record_start_stop_button,
                                                  height=5, width=100 , bg='gold')
        self.record_start_stop_button.grid(row=0, column=0)

        self.mirror_image = tk.IntVar(value=1)
        mirror_checkbutton = tk.Checkbutton(buttons_frame, text='Mirror image', variable=self.mirror_image)
        mirror_checkbutton.grid(row=0, column=1)

        self.bind('<space>', lambda event: self.on_record_start_stop_button())
        self.focus_force()

        self.record = False

    def on_record_start_stop_button(self):
        self.record = not self.record
        self.record_start_stop_button.config(text='Stop recording (or hit <space bar>)' if self.record else 'Start recording (or hit <space bar>)')

    def update(self):
        new_images = []
        while True:
            if self.frame_queue.empty():
                break
            frame_index, frame_data, frame_time = self.frame_queue.get_nowait()

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

    def mainloop(self, *args, **kwargs):
        def update():
            window.update()
            window.after(5, update)
        window.after(1, update)
        super().mainloop(*args, **kwargs)


def video_loop(client, frame_queue, stop_event):
    while not stop_event.is_set():
        frame = client.get_frame()
        if frame is not None and frame.complete and not frame_queue.full():
            frame_queue.put_nowait((frame.index, np.array(frame.data, np.uint8), datetime.datetime.now(datetime.timezone.utc)))


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

    video_loop_thread = threading.Thread(target=video_loop, args=(client, frame_queue, stop_event), daemon=True)
    video_loop_thread.start()

    window = App(frame_queue)

    try:
        response = client.open_video()

        window.mainloop()

    except Exception as ex:
        print(ex)
        print('window.destroy()')
        window.destroy()
    finally:
        stop_event.set()
        print('video_loop_thread.join()')
        video_loop_thread.join(2)
        print('client.disconnect()')
        client.disconnect()
