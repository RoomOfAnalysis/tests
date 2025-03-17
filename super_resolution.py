# for RTX 1080
# conda create -n sr_mockup python=3.7
# conda activate sr_mockup
# pip install ISR

# https://github.com/idealo/image-super-resolution/issues/197#issue-877826405
# pip install 'h5py==2.10.0' --force-reinstall

# If this call came from a _pb2.py file, your generated code is out of date and must be regenerated with protoc >= 3.19.0.
# If you cannot immediately regenerate your protos, some other possible workarounds are:
#  1. Downgrade the protobuf package to 3.20.x or lower.
#  2. Set PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=python (but this will use pure-Python parsing and will be much slower).
# pip install 'protobuf==3.20.1' --force-reinstall

# 2025-03-17 14:58:12.430198: I tensorflow/core/platform/cpu_feature_guard.cc:142] Your CPU supports instructions that this TensorFlow binary was not compiled to use: AVX
# pip uninstall tensorflow
# pip install tensorflow-gpu==2.1.0

# Could not load dynamic library 'cudart64_101.dll'; dlerror: cudart64_101.dll not found
# conda install -c conda-forge cudatoolkit=10.1

# Could not load dynamic library 'cudnn64_7.dll'; dlerror: cudnn64_7.dll not found
# conda install -c conda-forge cudnn=7.6


# for RTX 3080, it requires a newer cudatoolkit and cudnn
# according to tensorflow's doc: https://www.tensorflow.org/install/pip#windows-native
# TensorFlow 2.10 was the last TensorFlow release that supported GPU on native-Windows
# conda install -c conda-forge cudatoolkit=11.2 cudnn=8.1.0
# pip install "tensorflow<2.11"
# pip uninstall isr
# pip install isr --no-deps
# pip install 'h5py==2.10.0' --force-reinstall


# usage:
# python .\super_resolution.py C:\Users\Harold\Downloads\samples\sr\baboon.png C:\Users\Harold\Downloads\samples\sr\out.png


import sys
import numpy as np
from PIL import Image
from ISR.models import RDN, RRDN


img = Image.open(sys.argv[1])
lr_img = np.array(img)

# models will be downloaded and stored in `C:\Users\Harold\.keras\datasets`

# RDN: psnr-large, psnr-small, noise-cancel
# rdn = RDN(weights='psnr-small')
# sr_img = rdn.predict(lr_img)

# RRDN: gans
rrdn = RRDN(weights='gans')
sr_img = rrdn.predict(lr_img)

res = Image.fromarray(sr_img)
res.save(sys.argv[2])
