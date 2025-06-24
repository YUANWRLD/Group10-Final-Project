# Group10-Final-Project
MACHINE LEARNING IN ENGINEERING SCIENCE - Final Project

## Introduction

> This project provides a user-friendly image style prediction tool based on U-Net deep learning models. It supports three styles—3D, Comic, and Beauty—and allows users to easily apply style transformation to a batch of images through a graphical interface. Ideal for creative applications, AI-based image styling, or batch processing pipelines.

## Installation & Requirements

**Python Version**: `==3.7.16`

### Dependencies

Install the required packages with pip:

```bash
pip install tensorflow==2.10.0 pillow==9.5.0 numpy==1.21.6 flet==0.19.0
```
## How to run

```sh
git clone https://github.com/YUANWRLD/Group10-Final-Project.git
cd Group10-Final-Project
python main.py
```
## Model Type

Pre-trained U-Net models in .keras format, accepting RGB images as input

## Developer Guide

The UI is built using flet, and can be easily extended to support more models or features.
You can replace the .keras model files as long as they accept input in the shape (H, W, 3) and output a predicted image/mask.

All outputs are automatically saved in a folder named after the selected model (output(3d), output(comic), etc.) for easy versioning and comparison.