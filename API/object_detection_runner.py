import numpy as np
import os
import six.moves.urllib as urllib
import sys
import tarfile
import tensorflow as tf
import zipfile
import json
import time
import glob
import PIL
from flask import Flask, request, Response
import jsonpickle
import cv2
import uuid

from io import StringIO
from PIL import Image

import matplotlib.pyplot as plt

import visualization_utils as vis_util
import label_map_util

from multiprocessing.dummy import Pool as ThreadPool

MINIMUM_CONFIDENCE = 0.1
IMAGE_RESOLUTION = [300,300]

PATH_TO_MODEL_DIR = 'C:/Users/edupt/Documents/models/ssd_inception_v2_coco/10943-04.12.18/output_inference_graph'

PATH_TO_LABELS = os.path.join(PATH_TO_MODEL_DIR, 'label_map.pbtxt')

PATH_TO_CKPT = os.path.join(PATH_TO_MODEL_DIR, 'frozen_inference_graph.pb') 

detection_graph = tf.Graph()
SESS = tf.Session(graph=detection_graph)

# Creating indexes for the object labels that correspond with the ID number.
label_map = label_map_util.load_labelmap(PATH_TO_LABELS)
categories = label_map_util.convert_label_map_to_categories(label_map, max_num_classes=sys.maxsize, use_display_name=True)
CATEGORY_INDEX = label_map_util.create_category_index(categories)

def load_image_into_numpy_array(image):
    (im_width, im_height) = image.size
    return np.array(image.getdata()).reshape(
        (im_height, im_width, 3)).astype(np.uint8)

def detect_objects(data):
    print("Started detecting")

    image = data
    image_np = load_image_into_numpy_array(image)
    image_np_expanded = np.expand_dims(image_np, axis=0)

    (boxes, scores, classes, num) = SESS.run([detection_boxes, detection_scores, detection_classes, num_detections], feed_dict={image_tensor: image_np_expanded})
    

    name_id_dict = vis_util.visualize_boxes_and_labels_on_image_array(
        image_np,
        np.squeeze(boxes),
        np.squeeze(classes).astype(np.int32),
        np.squeeze(scores),
        CATEGORY_INDEX,
        min_score_thresh=MINIMUM_CONFIDENCE,
        use_normalized_coordinates=True,
        line_thickness=8)

    return(name_id_dict)
# Load model into memory

print('Loading model...')
with detection_graph.as_default():
    od_graph_def = tf.GraphDef()
    with tf.gfile.GFile(PATH_TO_CKPT, 'rb') as fid:
        serialized_graph = fid.read()
        od_graph_def.ParseFromString(serialized_graph)
        tf.import_graph_def(od_graph_def, name='')


print('detecting...')
with detection_graph.as_default():
    image_tensor = detection_graph.get_tensor_by_name('image_tensor:0')
    detection_boxes = detection_graph.get_tensor_by_name('detection_boxes:0')
    detection_scores = detection_graph.get_tensor_by_name('detection_scores:0')
    detection_classes = detection_graph.get_tensor_by_name('detection_classes:0')
    num_detections = detection_graph.get_tensor_by_name('num_detections:0')