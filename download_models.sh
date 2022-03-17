#!/bin/sh
gdown -O /code/backend/arcface_model/ https://drive.google.com/u/1/uc?id=1kIXFOld0ca9YphXVF0d1IZ55a-KcgEyZ

gdown -O /code/backend/checkpoints/ https://drive.google.com/u/1/uc?id=1HuyOoPhysQhI6T2d2xJFG83nsTkvXVlq
unzip /code/backend/checkpoints/checkpoints.zip  -d /code/backend/checkpoints
rm /code/backend/checkpoints/checkpoints.zip

gdown -O /code/backend/insightface_func/models/antelope/ https://drive.google.com/u/1/uc?id=1bKvOuXOQetzijUo0d9TNXsG9zVnECkXK
unzip -j /code/backend/insightface_func/models/antelope/antelope.zip -d /code/backend/insightface_func/models/antelope/
rm /code/backend/insightface_func/models/antelope/antelope.zip

gdown -O /code/backend/parsing_model/checkpoint/ https://drive.google.com/u/1/uc?id=1_UjidpSizppDHuLfr9WhaiVzeDdayBuV

gdown -O /code/backend/parsing_model/checkpoint/ https://download.pytorch.org/models/resnet18-5c106cde.pth