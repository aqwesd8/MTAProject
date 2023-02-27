# Display a runtext with double-buffering.
import sys
sys.path.append("matrix/bindings/python/samples")

from samplebase import SampleBase
from rgbmatrix import graphics
import time
from PIL import Image

### MATRIX HELPER FUNCTIONS ###

def fillRectangle(gx, canvas, xUL=0, yUL=0, xBR=63, yBR=31, color=graphics.Color(0,0,0)):
    if xUL>=xBR or yUL>=yBR:
        print("ERROR, bad rectangle boundaries.")
    else:
        for x in range(xUL,xBR+1):
            gx.DrawLine(canvas, x,yUL,x,yBR,color)

def printTrainBullet(canvas, x=6, y=6, r=0,b=0,g=0):
    pixMap = [[0,0,0,0,0,1,1,1,1,0,0,0,0,0],
    [0,0,0,1,1,1,1,1,1,1,1,0,0,0],
    [0,0,1,1,1,1,1,1,1,1,1,1,0,0],
    [0,1,1,1,0,0,0,0,0,0,1,1,1,0],
    [0,1,1,1,0,0,1,1,1,1,1,1,1,0],
    [1,1,1,1,0,0,1,1,1,1,1,1,1,1],
    [1,1,1,1,0,0,0,0,0,0,1,1,1,1],
    [1,1,1,1,1,1,1,1,0,0,1,1,1,1],
    [0,1,1,1,0,0,1,1,0,0,1,1,1,0],
    [0,1,1,1,1,0,0,0,0,1,1,1,1,0],
    [0,0,1,1,1,1,1,1,1,1,1,1,0,0],
    [0,0,0,1,1,1,1,1,1,1,1,0,0,0],
    [0,0,0,0,0,1,1,1,1,0,0,0,0,0]]
    for i in range(14):
        for j in range(13):
            color = (0,0,0) if pixMap[j][i]==0 else (r,b,g)
            canvas.SetPixel(i+(x-6),j+(y-6),color[0],color[1],color[2])

def scrollText(gx, canvas, leftBoundary, rightBoudary, height, color, text):
    text_length = graphics.DrawText(offscreen_canvas, font, pos, 20, textColor, my_text)

#hardcoded now, update for different trains
def printTrainBulletId(canvas, x, y, route_id):
    printTrainBullet(canvas, x, y, 0, 106, 9)

#position is 0 or 1
def printTrainLine(gx, canvas, route_id, font, min_font, destination, mins_left, position, text_frame):
    height = 7 + position*17
    bullet_position = (6, height)
    destination_position = (bullet_position[0]+10, height+int(font.baseline/2)-1)
    mins_left_position = (48, height+int(font.baseline/2)-1)
    text_color = gx.Color(100,100,100)
    left_boundary = destination_position[0]-1
    right_boundary = mins_left_position[0]-2

    text_width = gx.DrawText(canvas, font, destination_position[0]-text_frame, destination_position[1], text_color, destination)
    fillRectangle(gx, canvas, xBR=left_boundary, yUL=position*16, yBR=16+position*16)
    fillRectangle(gx, canvas, xUL=right_boundary, yUL=position*16, yBR=16+position*16)
    #image = Image.open("fiveTrain.ppm").convert('RGB')
    #image = image.resize(13,14)
    #canvas.SetImage(image, bullet_position[0],bullet_position[1])

    printTrainBulletId(canvas, bullet_position[0], bullet_position[1], route_id)

    gx.DrawText(canvas, min_font, mins_left_position[0], mins_left_position[1], text_color, "%sm"%(mins_left))

    return text_width-text_frame



class RunText(SampleBase):
    def __init__(self, *args, **kwargs):
        super(RunText, self).__init__(*args, **kwargs)
        self.parser.add_argument("-t", "--text", help="The text to scroll on the RGB LED panel", default="Hello world!")

    def run(self):
        offscreen_canvas = self.matrix.CreateFrameCanvas()
        font = graphics.Font()
        font.LoadFont("matrix/fonts/6x12.bdf")
        min_font = graphics.Font()
        min_font.LoadFont("matrix/fonts/5x8.bdf")
        textColor = graphics.Color(200, 200, 200)
        black = graphics.Color(0,0,0)
        pos = offscreen_canvas.width
        my_text = self.args.text
        time_step = 0.05
        freeze_time = 1.5

        pos1 = 0
        freeze1 = int(freeze_time/time_step) 
        pos2 = 0
        freeze2 = int(freeze_time/time_step) 
        while True:
            offscreen_canvas.Clear()
            #printTrainBullet(offscreen_canvas,x=31,y=16,r=0,b=106,g=9)
            # len = graphics.DrawText(offscreen_canvas, font, pos, 20, textColor, my_text)
            # pos -= 1
            # fillRectangle(graphics, offscreen_canvas, 0, 0, 24, offscreen_canvas.height, black)
            # if (pos + len < 24):
            #    pos = offscreen_canvas.width
            

            reset1 = printTrainLine(graphics, offscreen_canvas, "5", font, min_font, "Carroll St", 5, 0, pos1)
            reset2 = printTrainLine(graphics, offscreen_canvas, "5", font, min_font,"Coney Island - Stillwell Av", 10, 1, pos2)
            time.sleep(time_step)
            offscreen_canvas = self.matrix.SwapOnVSync(offscreen_canvas)

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



# Main function
if __name__ == "__main__":
    run_text = RunText()
    if (not run_text.process()):
        run_text.print_help()
