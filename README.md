# Air-Gesture-Control

## Introduction
This repo contains the code of the course project for Computer Vision Spring 2023 at UT Dallas. We trained object detection models for hand gesture recognition and developed a system that can be used to control computers (with normal RGB camera) using hand gestures in real time.


## Dataset


We use the HAGRID dataset for training our object detection model. Details can be checked [here][1].

## Model

We use the detectron2 framework for training our model. The model architecture we selected is Faster RCNN with RPN enhancement and ResNet-101 as backbone to extract the features. Details can be checked at [detectron2 model zoo][2].

## Results
We have evaluated our trained using both mAP and classification metrics such as F1 (there is only gesture in each image in our case). Detailed results are shown in the following table.

![exp results][9]

Also, we have visualized some object detection results on test dataset of HAGRID as shown below.

![visulizations][10]


## Demo
We show one of simple example of using our system to control the music playing along with the volume level. Note that our recording software records the sounds even after the system is muted, so you can still hear the music in our demo video. But in reality, you cannot hear anything. The demo video can be accessed by clicking the following image.

[![Demo video cover][7]][6]


## Install
To train the object detection model, you will need `pytorch`, `detectron2` and `opencv-python` installed with CUDA support on your server computer.

To deploy our air gesture control system, you will need to install
- Client: `opencv-python` and `pyautogui` if you want to use our system to control the keyboard or mouses.
- Server: `pytorch`, `detectron2`, `numpy` and `opencv-python`.

Note that you can deploy the server and client in a single machine or two machines, **be sure to change related piece of code for connection (such as the ip and port)**.

## Usage
### Train a Model from Scratch
All codes that are related to train an object detection model is included in `train-model` directory.
```python
# you need to first download the dataset
# by default, we keep only 2500 images from 6 classes randomly.
# the images are randomly selected from different users
# if you need more data from more classes, visit HAGRID in reference section
# only linux system is supported
! python download.py

# next we pre-process the data
# we randomly selected 1000 images for train and 100 for test
# for each of the 6 classes
# images are downsampled
# we also put datasets and annotations in a certain structure such that we can use the convertor
# provided by HAGRID
! python process.py

# convert data fromat to COCO
# the convertor is from HAGRID but I fixed one of the bug inside
# you might need to change the directory in convert_conf.yaml
# constants.py is a file needed for this convertor
! python hagrid_to_coco.py convert_conf.yaml
```

Now you have all the datasets ready, you can use one of the two notebooks `hand-gesture-detectron2` and `hand-gesture-detr` provided to train your own model. Note that in our project we uses `detectron2` as we find DETR are hard to train.

### Deploy Our System
Our system contains both the server and client program and it is communicating through socket. For the server script `serv.py`, you will need to specify the path to your trained model (or our model checkpoint provided below), also you will need CUDA devices to run this script.

For Client script, you can run on any system with Python installed (windows/linux/macos), the `config.json` file defines the mapping between gestures/movements to certain actions. In our case, since it is all keyboard events, it is very simple to setup.


## Performance
This system keeps using the GPU for computation, and it need about 4GB of CUDA memory in our case.

If your PC is power enough, you can deploy the server and client on your local machine and you can reach about 25 fps.

If you want you PC to be cool or you need GPU for gaming or you don't have any CUDA device, you can deploy the server program on another machine with CUDA devices. You can still achieve about 6 fps on a 100 Mbps WAN network.


## Other Resources
- Slides is public available [here][4] and is included in this repo as well.
- I have also recorded an example presentation for our project [here][5] (the slide used in the video is not up to date, but differences are minor).
- Project report is included in this repository as well.
- The trained model checkpoint can be accessed [here][8], you can download it and use this model for testing (**you might need to change the model path in `serv.py` script depending where you put this model file and the name of this file, default is `models/model_final.pth`**).


## Future Works
Our system is not limited to control the keyboard. **Any actions that can be implemented using Python is compatible with our framework**. You are welcome to adapt our system for your own purpose.

Current system is only limited to 6 gestures and we are only consider one type of moving gesture in our current implementation, I will probably add support for multiple movement gestures and make this system more easier to deploy if requested by many users.


## References
- [Detectron2][2]
- [HAGRID Dataset][1]
- [A tutorial for how to use detectron2 on balloon dataset][3]


[1]:https://github.com/hukenovs/hagrid
[2]:https://github.com/facebookresearch/detectron2
[3]:https://www.youtube.com/watch?v=cQUs4mRpmW4&t=466s
[4]:https://docs.google.com/presentation/d/1AxDUzTkS4aJCZbP1iYxaSrCN2YyE-6ErSfTAlImxW3w/edit?usp=sharing
[5]:https://drive.google.com/file/d/1B2cX-r_9Q-iwnQF3iLbrAx6WdEExQKsy/view?usp=share_link
[6]:https://drive.google.com/file/d/1b2qHICTMi3W8hW2be9iSXtXbFZEKMITk/view?usp=share_link
[7]:https://github.com/LeonDong1993/Air-Gesture-Control/blob/main/figures/demo_pic.png
[8]:https://drive.google.com/file/d/1eOWmCaFwJX28Uow3nN36t2_4qDM27rU2/view?usp=share_link
[9]:https://github.com/LeonDong1993/Air-Gesture-Control/blob/main/figures/results.png
[10]:https://github.com/LeonDong1993/Air-Gesture-Control/blob/main/figures/visulizations.png