#!/usr/bin/env python
# coding: utf-8

# import neccessary libararies
import numpy as np
import pdb, sys
import os, json, cv2
import socket
import threading
import torch, zlib

import detectron2
from detectron2.engine import DefaultPredictor
from detectron2.config import get_cfg
from detectron2 import model_zoo


if len(sys.argv) <= 1:
    print('Please tell me which cuda device to run on, e.g. cuda:0')
    exit(0)

# ------------------- MAIN LOGIC ----------------------- #

model_config_file = 'COCO-Detection/faster_rcnn_R_101_FPN_3x.yaml'

cfg = get_cfg()
cfg.MODEL.DEVICE = sys.argv[1]
cfg.merge_from_file(model_zoo.get_config_file(model_config_file))
cfg.OUTPUT_DIR = './models'
cfg.MODEL.ROI_HEADS.NUM_CLASSES = 6
cfg.MODEL.WEIGHTS = os.path.join(cfg.OUTPUT_DIR, "model_final.pth")
cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = 0.8

predictor = DefaultPredictor(cfg)
classes = ['fist', 'like', 'ok', 'one', 'peace', 'stop']
MAX_RECV = 20480


def do_detection(img):
    outputs = predictor(img)
    pred_score = outputs['instances'].scores.detach().cpu().numpy()

    if pred_score.size == 0:
        ret = []
    else:
        ind = np.argmax(pred_score)
        pred_classes = outputs['instances'].pred_classes.detach().cpu().numpy()
        pred_boxes = outputs['instances'].pred_boxes.tensor.cpu().numpy()
        ret = list(pred_boxes[ind])
        ret.append(classes[pred_classes[ind]])

    return str(ret)

def handle_client(client_socket, addr):
    try:
        while True:
            # Receive the length of the image data from the client
            data_len = int.from_bytes(client_socket.recv(4), byteorder='big')

            # Receive the image data from the client
            img_data = b''
            while len(img_data) < data_len:
                packet = client_socket.recv(min(MAX_RECV, data_len - len(img_data)))
                if not packet: break
                img_data += packet

            # Do detection and return the detected position and gesture
            img_data = zlib.decompress(img_data)
            img = cv2.imdecode(np.frombuffer(img_data, dtype=np.uint8), cv2.IMREAD_COLOR)

            result = do_detection(img)
            result_str = str(result)
            result_len = len(result_str)
            client_socket.sendall(result_len.to_bytes(4, byteorder='big'))
            client_socket.sendall(result_str.encode())

    except:
        print(f"Connection from {addr} closed.")
        client_socket.close()


if __name__ == '__main__':
    # Set up a socket to listen for incoming connections
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('localhost', 8000))
    server_socket.listen()

    # Wait for clients to connect
    print('Waiting for clients to connect...')
    while True:
        client_socket, addr = server_socket.accept()
        print(f"Connection from {addr} established.")

        # Handle the client in a separate thread
        client_thread = threading.Thread(target=handle_client, args=(client_socket, addr))
        client_thread.start()

