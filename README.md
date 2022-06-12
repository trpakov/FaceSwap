# FaceSwap - Face Swapping Made Easy

## About
A web app that utilizes neural networks to bring state-of-the-art face swapping technology to the masses.

## Setup

All of the following commands assume that you are located in the project root directory.

### Running locally

1. Create a virtual Python environment using your preferred tool (venv, virtualenv, conda) to avoid conflicts:
```
python -m venv .venv
```

2. Install requirements from ```requirements.txt```:
```
python -m pip install -r requirements.txt
```

3. Execute ```download_models.sh``` to download the required ML models and place them in their appropriate places:
```
./download_models.sh
```

Alternatively, download the models manually from [here](https://drive.google.com/drive/folders/1uUpWzx6Cu6j61yiOcvlpc4u1lXA5lSA-?usp=sharing) and place them where required as specified in ```download_models.sh```.

4. Start the server by running ```main.py``` or issuing the following command:
```
uvicorn main:app --host 0.0.0.0 --port 8000
```
The frontend should be accessible from [http://localhost:8000/](http://localhost:8000/).

### Running with Docker

1. Build an image from the Dockerfile in the root directory:
```
docker build . -t faceswap
```

1. Run the docker image in a way that suits your needs:
```
docker run -it -p 8000:80 faceswap
```
Again, the frontend should be accessible from [http://localhost:8000/](http://localhost:8000/).