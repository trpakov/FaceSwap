from fastapi import HTTPException
import os
import time
from urllib.parse import urlparse
from fastapi import FastAPI, UploadFile, Response, Request
from fastapi.responses import FileResponse, PlainTextResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import warnings; warnings.filterwarnings("ignore")
from backend.swapper import Swapper
import requests
from glob import glob
import aiohttp
GIPHY_API_KEY = 'TsGk4CCWHoRCoQxj1KqDUwzvw7xdSvtY'

app = FastAPI()

app.mount("/assets", StaticFiles(directory="frontend/assets"), name="assets")
# app.mount("/result", StaticFiles(directory="backend/results"), name="results")

@app.on_event("startup")
async def init():
    global swapper
    swapper = Swapper(use_cache=False)

@app.on_event("shutdown")
async def shutdown():
    swapper.save_cache()

@app.get("/")
async def root():
    return FileResponse('frontend/index.html')


@app.get("/img2img")
async def img2img():

    return FileResponse('frontend/img2img.html')


@app.get("/img2anim")
async def img2anim():
    return FileResponse('frontend/img2anim.html')


@app.post("/swap", tags=['swapping'], response_class=Response, description='Transefer face identity between two still images')
def swap(source: UploadFile, dest: UploadFile):

    source = source.file.read()
    dest = dest.file.read()

    result_img = swapper.swap(source, dest)

    # return Response(cv2.imencode('.jpg', result_img)[1].tostring(), media_type="image/jpeg")
    return PlainTextResponse(result_img)


@app.post("/swap/{dest_url:path}", tags=['swapping'], response_class=Response, description='Transefer face identity between two still images')
def swap_url(source: UploadFile, dest_url: str):

    source = source.file.read()
    dest = requests.get(dest_url, allow_redirects=True).content

    result_img = swapper.swap(source, dest)

    # return Response(cv2.imencode('.jpg', result_img)[1].tostring(), media_type="image/jpeg")
    return PlainTextResponse(result_img)

@app.get("/swap_urls", tags=['swapping'], response_class=Response, description='Transefer face identity between two still images')
def swap_urls(source_url: str, dest_url: str):

    source = requests.get(source_url, allow_redirects=True).content
    dest = requests.get(dest_url, allow_redirects=True).content

    result_img = swapper.swap(source, dest)

    # return Response(cv2.imencode('.jpg', result_img)[1].tostring(), media_type="image/jpeg")
    return PlainTextResponse(result_img)

@app.post("/swap_gif", tags=['swapping'], response_class=Response, description='Transefer face identity from source image to target video')
def swap_gif(source: UploadFile, dest: UploadFile):
    
    ext = dest.filename.split('.')[-1]

    source = source.file.read()
    dest = dest.file.read()
    
    result_img = swapper.swap_gif(source, dest, ext)

    # return Response(result_img, media_type=f"image/{ext}")
    return PlainTextResponse(result_img)

@app.post("/swap_gif/{dest_url:path}", tags=['swapping'], response_class=Response, description='Transefer face identity from source image to target video')
def swap_gif_url(source: UploadFile, dest_url: str):

    parsed_url = urlparse(dest_url)
    original_name = os.path.basename(parsed_url.path) 
    ext = original_name.split('.')[-1]

    source = source.file.read()
    dest = requests.get(dest_url, allow_redirects=True).content
    
    result_img = swapper.swap_gif(source, dest, ext)

    # return Response(result_img, media_type=f"image/{ext}")
    return PlainTextResponse(result_img)


@app.post("/swap_video", tags=['swapping'], response_class=Response, description='Transefer face identity from source to target video')
def swap_video(source: UploadFile, dest: UploadFile):
    
    ext = dest.filename.split('.')[-1]

    source = source.file.read()
    dest = dest.file.read()
    
    result_img = swapper.swap_video(source, dest, ext)

    # return Response(result_img, media_type=f"image/{ext}")
    return PlainTextResponse(result_img)


@app.get("/gif_search")
async def get_img(q: str, offset: int):
    
    params = {'q': q, 'offset': offset, 'api_key': GIPHY_API_KEY, 'limit': 30}
    async with aiohttp.request('GET', 'https://api.giphy.com/v1/gifs/search', params=params) as response:
        if response.status != 200: raise HTTPException(status_code=404)   
        data = await response.json()
        return JSONResponse(data)


@app.get("/{id}")
async def get_img(id: str):
    
    path = glob(f'backend/results/{id}.*')

    if len(path) == 1:
        return FileResponse(path[0])
    else:
        raise HTTPException(status_code=404, detail="Image not found")


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.perf_counter()
    response = await call_next(request)
    response.headers["X-Process-Time"] = str(time.perf_counter() - start_time)
    return response


if __name__ == '__main__':
    import uvicorn
    uvicorn.run('main:app', host="0.0.0.0", port=8000, reload=False)

