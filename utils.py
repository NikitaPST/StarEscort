import time

def get_tick_count():
    return int(round(time.time() * 1000))

def crop_y_by_x(start, end, ax):
    return -1 * ((start[1]-end[1])*ax + (start[0]*end[1] - start[1]*end[0])) // (end[0] - start[0])

def crop_x_by_y(start, end, ay):
    return -1 * ((end[0]-start[0])*ay + (start[0]*end[1] - start[1]*end[0])) // (start[1] - end[1])