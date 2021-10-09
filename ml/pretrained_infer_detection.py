# Copyright (c) 2017-present, Facebook, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Function `vis_bbox`, `vis_mask`, and `vis_class` are adapted from:
# https://github.com/facebookresearch/Detectron/blob/7aa91aaa5a85598399dc8d8413e05a06ca366ba7/detectron/utils/vis.py
##############################################################################

"""PyTorch object detection example."""

import argparse
import os

import cv2
import matplotlib.pyplot as plt
import numpy as np
import torch
import torchvision.models as models
import torchvision.transforms as trns
from PIL import Image

_GRAY = (218, 227, 218)
_GREEN = (18, 127, 15)
_WHITE = (255, 255, 255)


def vis_bbox(image, bbox, color=_GREEN, thick=1):
    """Visualizes a bounding box."""
    image = image.astype(np.uint8)
    bbox = list(map(int, bbox))
    x0, y0, x1, y1 = bbox
    cv2.rectangle(image, (x0, y0), (x1, y1), color, thickness=thick)
    return image


def run_object_detection_outer(model, image_path, transforms, threshold=0.5, output_path="out.png"):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    pimg = Image.open(image_path)
    display_image = run_object_detection_inner(
        model, pimg, transforms, threshold=0.5)

    plt.figure(figsize=(10, 6))
    plt.imshow(display_image)
    plt.xticks([])
    plt.yticks([])
    plt.savefig(output_path, bbox_inches="tight")


def run_object_detection_inner(model, pimg, transforms, threshold=0.5) -> Image:
    image = pimg.convert("RGB")
    image_tensor = transforms(image)
    outputs = model([image_tensor])[0]

    display_image = np.array(image)
    outputs = {k: v.numpy() for k, v in outputs.items()}

    for i, (bbox, label, score) in enumerate(zip(outputs["boxes"], outputs["labels"], outputs["scores"])):
        if score < threshold:
            continue

        display_image = vis_bbox(display_image, bbox)

    return display_image


if __name__ == "__main__":
    parser = argparse.ArgumentParser("PyTorch Object Detection")
    parser.add_argument("--image_path", type=str,
                        default="resources/sheep-herd-shepherd-hats-dog-meadow.jpg", help="path to image")
    parser.add_argument("--model_type", type=str,
                        default="fasterrcnn", help="fasterrcnn or maskrcnn")
    parser.add_argument("--output_path", type=str,
                        default="resources/out.png", help="path to save output image")

    # Parse arguments
    args = parser.parse_args()

    # Define image transforms
    transforms = trns.ToTensor()

    # Load model
    if args.model_type == "fasterrcnn":
        model = models.detection.fasterrcnn_resnet50_fpn(pretrained=True)
    elif args.model_type == "maskrcnn":
        model = models.detection.maskrcnn_resnet50_fpn(pretrained=True)
    else:
        raise AssertionError

    print(model)

    # Set model to eval mode
    model.eval()

    # Run model
    with torch.no_grad():
        run_object_detection_outer(model, args.image_path,
                                   transforms, output_path=args.output_path)
