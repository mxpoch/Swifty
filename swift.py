import cv2 
import torch
import numpy as np
import time

# loading in the MiDaS model
model_type = "MiDaS_small"
midas = torch.hub.load("intel-isl/MiDaS", model_type)

# switching to GPU
device = torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")
midas.to(device)
midas.eval()

# loading in the transforms for webcam processing
midas_transforms = torch.hub.load("intel-isl/MiDaS", "transforms")

if model_type == "DPT_Large" or model_type == "DPT_Hybrid":
    transform = midas_transforms.dpt_transform
else:
    transform = midas_transforms.small_transform

    cap = cv2.VideoCapture(0)

while cap.isOpened():
    # collecting the image from the camera
    success, img = cap.read()
    start = time.time()

    # converting to RGB
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    # apply input transforms 
    input_batch = transform(img).to(device)
    # prediction and resize to original resolution
    with torch.no_grad():
        # storing the prediction from the model
        prediction = midas(input_batch)
        # reshaping
        prediction = torch.nn.functional.interpolate(
            prediction.unsqueeze(1),
            size=img.shape[:2],
            mode="bicubic",
            align_corners=False,
        ).squeeze()
    # moving the prediction matrix from GPU and post-processing
    depth_map = prediction.to('cpu').numpy()
    # normalizing the depthmap with MINMAX between 0 and 1 
    depth_map = cv2.normalize(depth_map, None, 0, 1, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_64F)
    
    # calculating FPS
    end = time.time()
    totalTime = end-start 
    fps = 1/totalTime
    
    # converting back to BGR to display with openCV
    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    # converting to colors between 0 and 255
    depth_map = (depth_map*255).astype(np.uint8)
    # cool themes B)
    depth_map = cv2.applyColorMap(depth_map, cv2.COLORMAP_MAGMA)

    # display
    cv2.putText(img, f'FPS: {int(fps)}', (20,70), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0,255,0), 2)
    cv2.imshow('Image', img)
    cv2.imshow('Depth Map', depth_map)

    # halt on esc key
    if cv2.waitKey(5) & 0xFF == 27:
        break 
# releasing the camera
cap.release()