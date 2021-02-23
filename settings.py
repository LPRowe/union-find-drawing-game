a, b, c = 51, 153, 255
color_wheel = ((c, a, a), (c, b, a), (c, c, a), (b, c, a), (a, c, a), 
               (a, c, b), (a, c, c), (a, b, c), (a, a, c), 
               (b, a, c), (c, a, c), (c, a, b), (b, b, b))

settings = {"WIDTH": 800,               # window width
            "HEIGHT": 800,              # window height
            "SLEEP_TIME": 0,            # sleep between iterations to reduce the frame rate
            "LOCK_TIME": 0.2,           # delay between allowed input actions (seconds)
            "COLOR_WHEEL": color_wheel, # tuple of (R, G, B) colors
            "BRIGHTNESS": 200           # pixel intensity [0, 255]
            }