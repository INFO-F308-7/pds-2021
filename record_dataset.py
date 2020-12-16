import gym
import numpy as np
import imageio
import os
import sys
from pyglet.window import key

from data import LEFT, RIGHT, GO, ACTIONS 
from car_racing import *

samples_each_classes = 3000
SEED = np.random.randint(1,100000)

def action_to_id(a):
    if all(a == [-1, 0, 0]): return LEFT
    elif all(a == [1, 0, 0]): return RIGHT
    else:
        return GO

if __name__=='__main__':

    if len(sys.argv) < 2:
        sys.exit("Usage : python record_dataset.py path")
    
    env = CarRacing()
    env.reset()
    env.seed(SEED)   # seed the circuit 

    folder = sys.argv[1]
    images = os.path.join(folder, "images")
    labels = os.path.join(folder, "labels.txt")
    os.makedirs(images, exist_ok=True)

    a = np.array([0.0, 0.0, 0.0])

    def key_press(k, mod):
        global restart
        if k==key.LEFT:  a[0] = -1.0
        if k==key.RIGHT: a[0] = +1.0
        if k==key.UP:    a[1] = +1.0
        if k==key.DOWN:  a[2] = +0.8   # set 1.0 for wheels to block to zero rotation
    def key_release(k, mod):
        if k==key.LEFT  and a[0]==-1.0: a[0] = 0
        if k==key.RIGHT and a[0]==+1.0: a[0] = 0
        if k==key.UP:    a[1] = 0
        if k==key.DOWN:  a[2] = 0

    env.viewer.window.on_key_press = key_press
    env.viewer.window.on_key_release = key_release
    env.reset()
    env.seed(SEED)   # seed the circuit 
    for i in range(100):
        env.step([0, 0, 0])

    file_labels = open(labels, 'w')
    samples_saved = {a: 0 for a in ACTIONS}

    i = 0
    isopen = True
    while isopen:
        env.reset()
        env.seed(SEED)   # seed the circuit
        while True:
            s, r, done, info = env.step(a)
            action_id = action_to_id(a)
            if done:
                break
            if samples_saved[action_id] < samples_each_classes:
                samples_saved[action_id] += 1
                samples_each_classes
                imageio.imwrite(os.path.join(folder, 'images', 'img-%s.jpg' % i ), s)
                file_labels.write('%s %s\n' % ('img-%s.jpg' % i, action_id))
                file_labels.flush()
                i += 1
                print(samples_saved,"  ", i)
            isopen = env.render()
            #or not int(env.tile_label.text)
            if not isopen:
                break
    env.close()
