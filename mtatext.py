# Display a runtext with double-buffering.
import sys
sys.path.append("matrix/bindings/python/samples")

from samplebase import SampleBase
from rgbmatrix import graphics
import time
from PIL import Image

import requests
import json
from threading import Thread
from queue import Queue
import mta

### MATRIX HELPER FUNCTIONS ###

def fillRectangle(gx, canvas, xUL=0, yUL=0, xBR=63, yBR=31, color=graphics.Color(0,0,0)):
    if xUL>=xBR or yUL>=yBR:
        print("ERROR, bad rectangle boundaries.")
    else:
        for x in range(xUL,xBR+1):
            gx.DrawLine(canvas, x,yUL,x,yBR,color)


def scrollText(gx, canvas, leftBoundary, rightBoudary, height, color, text):
    text_length = graphics.DrawText(offscreen_canvas, font, pos, 20, textColor, my_text)

#hardcoded now, update for different trains
def printTrainBulletId(canvas, x, y, route_id):
    image = Image.open("pixelMaps/%strain.ppm"%(route_id)).convert('RGB')
    canvas.SetImage(image, x, y)

#position is 0 or 1
def printTrainLine(gx, canvas, route_id, font, min_font, destination, mins_left, position, text_frame):
    height = 7 + position*19#7
    bullet_position = (0, height - 7) #was 6,height
    destination_position = (bullet_position[0]+16, height+int(font.baseline/2)-1)
    mins_left_position = (48, height+int(font.baseline/2)-1)
    text_color = gx.Color(100,100,100)
    left_boundary = destination_position[0]-1
    right_boundary = mins_left_position[0]-2

    text_width = gx.DrawText(canvas, font, destination_position[0]-text_frame, destination_position[1], text_color, destination)
    fillRectangle(gx, canvas, xBR=left_boundary, yUL=position*16, yBR=16+position*16)
    fillRectangle(gx, canvas, xUL=right_boundary, yUL=position*16, yBR=16+position*16)
    printTrainBulletId(canvas, bullet_position[0], bullet_position[1], route_id)

    gx.DrawText(canvas, min_font, mins_left_position[0], mins_left_position[1], text_color, "%sm"%(mins_left))

    return text_width-text_frame

def getTrains(stations):
    station_string = ",".join(stations) if len(stations)>1 else stations[0]
    #response = requests.get("http://localhost:5000/train-schedule/%s"%(station_string))
    return mta.train_schedule(stations)


class GetTrainsThread(Thread):
    def __init__(self, stations, queue):
        Thread.__init__(self)
        self.trains = []
        self.stations = stations
        self.queue = queue
    
    def setTrains(self, trains):
        self.trains = trains

    def run(self):
        self.trains = getTrains(self.stations)
        self.queue.put(self.trains)

class GetFramesThread(Thread):
    
    def __init__(self, stations, queue, matrix):
        Thread.__init__(self)
        self.MAX_FRAMES = 24
        self.queue = queue
        self.matrix = matrix
        self.stations = stations
        self.canvases = [self.matrix.CreateFrameCanvas() for i in range(self.MAX_FRAMES)]


    def run(self):
        i = 0
        font = graphics.Font()
        font.LoadFont("matrix/fonts/6x12.bdf")
        min_font = graphics.Font()
        min_font.LoadFont("matrix/fonts/5x8.bdf")
        textColor = graphics.Color(200, 200, 200)
        black = graphics.Color(0,0,0)
        pos = self.canvases[0].width
        stations = self.stations
        time_step = 0.08
        freeze_time = 2.5
        train_update_time = 30
        secondary_switch_time = 15
        trains_queue = Queue()

        pos1 = 0
        freeze1 = int(freeze_time/time_step) 
        pos2 = 0
        freeze2 = int(freeze_time/time_step) 
        train_update = 0
        switch_time = int(secondary_switch_time/time_step)
        trains = None
        secondary_train = 1
        primary_train = 0

        while True:
            if self.queue.qsize()<self.MAX_FRAMES:
                self.canvases[i].Clear()

                if train_update==0 and trains_queue.qsize()==0:
                    train_thread = GetTrainsThread(stations,trains_queue)
                    train_thread.start()
                    train_update = int(train_update_time/time_step)

                if(trains_queue.qsize()>0):
                    trains = trains_queue.get()
                
                if trains:
                    if switch_time==0:
                        secondary_train = max(1,(secondary_train+2)%len(trains))
                        primary_train = secondary_train-1
                        switch_time = int(secondary_switch_time/time_step)
                    else:
                        switch_time-=1

                    reset1 = printTrainLine(graphics, self.canvases[i], trains[primary_train]["route_id"], font, min_font, trains[primary_train]["destination"], trains[primary_train]["mins_left"], 0, pos1)
                    if len(trains) > 1:
                        reset2 = printTrainLine(graphics, self.canvases[i], trains[secondary_train]["route_id"], font, min_font,trains[secondary_train]["destination"], trains[secondary_train]["mins_left"], 1, pos2)
                    else:
                        reset2 = -1
                
                self.queue.put(self.canvases[i])

                if trains:
                    if pos1==0 and freeze1>0:
                        freeze1-=1
                    else:
                        pos1+=1
                        freeze1 = int(freeze_time/time_step)

                    if pos2==0 and freeze2>0:
                        freeze2-=1
                    else:
                        pos2+=1
                        freeze2 = int(freeze_time/time_step) 


                    if reset1<0:
                        pos1 = 0
                    if reset2<0:
                        pos2 = 0

                train_update-=1
                i = (i+1)%self.MAX_FRAMES




class RunText(SampleBase):
    def __init__(self, *args, **kwargs):
        super(RunText, self).__init__(*args, **kwargs)
        self.parser.add_argument("-s", "--stations", help="List of stations", nargs="*", default=["F21"])

    def run(self):
        # offscreen_canvas = self.matrix.CreateFrameCanvas()
        # font = graphics.Font()
        # font.LoadFont("matrix/fonts/6x12.bdf")
        # min_font = graphics.Font()
        # min_font.LoadFont("matrix/fonts/5x8.bdf")
        # textColor = graphics.Color(200, 200, 200)
        # black = graphics.Color(0,0,0)
        # pos = offscreen_canvas.width
        # stations = self.args.stations
        time_step = 0.08
        # freeze_time = 2.5
        # train_update_time = 30
        # secondary_switch_time = 15
        # trains_queue = Queue()

        # pos1 = 0
        # freeze1 = int(freeze_time/time_step) 
        # pos2 = 0
        # freeze2 = int(freeze_time/time_step) 
        # train_update = 0
        # switch_time = int(secondary_switch_time/time_step)
        # trains = None
        # secondary_train = 1
        # primary_train = 0

        stations = self.args.stations
        frame_q = Queue()
        main_thread = GetFramesThread(stations, frame_q, self.matrix)
        main_thread.start()
        while True:
            now = time.time()
            if frame_q.qsize()>0:
                offscreen_canvas = frame_q.get()

                self.matrix.SwapOnVSync(offscreen_canvas)

            # offscreen_canvas.Clear()

            # if train_update==0 and trains_queue.qsize()==0:
            #     train_thread = GetTrainsThread(stations,trains_queue)
            #     train_thread.start()
            #     train_update = int(train_update_time/time_step)

            # if(trains_queue.qsize()>0):
            #     trains = trains_queue.get()
            
            # if trains:
            #     if switch_time==0:
            #         secondary_train = max(1,(secondary_train+2)%len(trains))
            #         primary_train = secondary_train-1
            #         switch_time = int(secondary_switch_time/time_step)
            #     else:
            #         switch_time-=1

            #     reset1 = printTrainLine(graphics, offscreen_canvas, trains[primary_train]["route_id"], font, min_font, trains[primary_train]["destination"], trains[primary_train]["mins_left"], 0, pos1)
            #     if len(trains) > 1:
            #         reset2 = printTrainLine(graphics, offscreen_canvas, trains[secondary_train]["route_id"], font, min_font,trains[secondary_train]["destination"], trains[secondary_train]["mins_left"], 1, pos2)
            #     else:
            #         reset2 = -1
            
            # offscreen_canvas = self.matrix.SwapOnVSync(offscreen_canvas)
            
            
            # if trains:
            #     if pos1==0 and freeze1>0:
            #         freeze1-=1
            #     else:
            #         pos1+=1
            #         freeze1 = int(freeze_time/time_step)

            #     if pos2==0 and freeze2>0:
            #         freeze2-=1
            #     else:
            #         pos2+=1
            #         freeze2 = int(freeze_time/time_step) 


            #     if reset1<0:
            #         pos1 = 0
            #     if reset2<0:
            #         pos2 = 0

            # train_update-=1
            elasped = time.time()-now

            time.sleep(max(0,(time_step - elasped)))



# Main function
if __name__ == "__main__":
    run_text = RunText()
    if (not run_text.process()):
        run_text.print_help()
