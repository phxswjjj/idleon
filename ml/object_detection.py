
import cv2
import numpy as np
import torch
import torch.nn.functional as F
import torchvision.datasets as datasets
import torchvision.models as models
import torchvision.transforms as trns
import torchvision.transforms as transforms
from PIL import Image

if __name__ == '__main__':
    import os
    import sys

    sys.path.append(os.path.realpath('.'))

    if not __package__:
        __package__ = 'ml'

_GRAY = (218, 227, 218)
_GREEN = (18, 127, 15)
_WHITE = (255, 255, 255)

_DATASET_DIR_PATH = r'resources\dataset'
_MODEL_DIR_PATH = os.path.join(_DATASET_DIR_PATH, 'model')
_PRETRAIN_MODEL_PATH = os.path.join(_MODEL_DIR_PATH, 'final_model.pth')


def vis_bbox(image: Image, bbox, color=_GREEN, thick=1) -> Image:
    """Visualizes a bounding box."""
    image = image.astype(np.uint8)
    bbox = list(map(int, bbox))
    x0, y0, x1, y1 = bbox
    cv2.rectangle(image, (x0, y0), (x1, y1), color, thickness=thick)
    return image


class Detection():
    def __init__(self, model=None, transforms=None, threshold=0.5):
        if not model:
            model = models.detection.fasterrcnn_resnet50_fpn(pretrained=True)
        model.eval()
        self.model = model

        if not transforms:
            transforms = trns.ToTensor()
        self.transforms = transforms

        self.threshold = threshold

    def predict(self, pimage) -> Image:
        model = self.model
        transforms = self.transforms
        threshold = self.threshold

        image = pimage.convert("RGB")
        image_tensor = transforms(image)
        outputs = model([image_tensor])[0]

        display_image = np.array(image)
        with torch.no_grad():
            outputs = {k: v.numpy() for k, v in outputs.items()}

        for i, (bbox, label, score) in enumerate(zip(outputs["boxes"], outputs["labels"], outputs["scores"])):
            if score < threshold:
                continue

            display_image = vis_bbox(display_image, bbox)

        return display_image


if __name__ == '__main__':

    inputSize = 224
    transforms = trns.Compose([
        transforms.Resize(inputSize),
        transforms.CenterCrop(inputSize),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ])

    from .train_model import VGG16_model
    model = torch.load(_PRETRAIN_MODEL_PATH)

    objDetection = Detection(model=model, transforms=transforms)

    pimg = Image.open('resources/tmp.jpg')
    display_img = objDetection.predict(pimg)

    display_img = np.array(display_img)
    display_img = Image.fromarray(cv2.cvtColor(display_img, cv2.COLOR_BGR2RGB))
    display_img = np.array(display_img)

    cv2.imshow('view', display_img)
    cv2.waitKey()
    cv2.destroyAllWindows()