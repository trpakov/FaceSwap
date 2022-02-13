from functools import partial
import io
import cv2
import torch
from PIL import Image
import torch.nn.functional as F
from torchvision import transforms
from backend.models.models import create_model
from backend.options.test_options import TestOptions
from backend.insightface_func.face_detect import Face_Detector
from backend.util.reverse2original import reverse2wholeimage
import os
from backend.util.norm import SpecificNorm
from backend.parsing_model.model import BiSeNet
from cachetools import cachedmethod, LRUCache
from cachetools.keys import hashkey
import numpy as np
from fastapi import HTTPException
import pickle
import uuid
from backend.util.gif_swap import gif_swap
from backend.util.video_swap import video_swap


class Swapper:
    

    @staticmethod
    def to_tensor(array):
        tensor = torch.from_numpy(array)
        img = tensor.transpose(0, 1).transpose(0, 2).contiguous()
        return img.float().div(255)


    def __init__(self, use_cache=True):

        self.use_cache = use_cache
        if self.use_cache:
            if os.path.exists('backend/cache/cache.pkl'):
                with open('backend/cache/cache.pkl', 'rb') as cache:
                    self.cache = pickle.load(cache)
            else:
                self.cache = LRUCache(maxsize=100)

        self.transformer_Arcface = transforms.Compose([
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
        ])

        self.options = TestOptions().parse()
        self.options.Arc_path = 'backend/arcface_model/arcface_checkpoint.tar'
        self.options.use_mask = True

        self.model = create_model(self.options)
        self.model.eval()

        self.spNorm = SpecificNorm()
        self.app = Face_Detector(name='antelope', root='backend/insightface_func/models')
        self.app.prepare(ctx_id= 0, det_thresh=0.6, det_size=(640,640))

        if self.options.use_mask:
                n_classes = 19
                self.net = BiSeNet(n_classes=n_classes)
                self.net.to(torch.device('cuda:0' if torch.cuda.is_available() else 'cpu'))
                save_pth = os.path.join('backend/parsing_model/checkpoint', '79999_iter.pth')
                self.net.load_state_dict(torch.load(save_pth)) if torch.cuda.is_available() else self.net.load_state_dict(torch.load(save_pth, map_location=torch.device('cpu')))
                self.net.eval()


    @cachedmethod(lambda self: self.cache, key=partial(lambda  id, _, *args, **kwargs: hashkey(id, *args, **kwargs), '_swap'))
    def _swap(self, source_img, dest_img, mode='single'):

        source_np = np.frombuffer(source_img, np.uint8)
        dest_np = np.frombuffer(dest_img, np.uint8)

        source_img = cv2.imdecode(source_np, cv2.IMREAD_COLOR)
        dest_img = cv2.imdecode(dest_np, cv2.IMREAD_COLOR)

        with torch.no_grad():

            try:
                source_img_align_crop, _ = self.app.get(source_img, self.options.crop_size, 'single')
            except TypeError as e:
                raise HTTPException(status_code=404, detail='No faces detected in source image.')

            source_img_align_crop_pil = Image.fromarray(cv2.cvtColor(source_img_align_crop[0], cv2.COLOR_BGR2RGB)) 
            source_img = self.transformer_Arcface(source_img_align_crop_pil)
            img_id = source_img.view(-1, source_img.shape[0], source_img.shape[1], source_img.shape[2])

            # convert numpy to tensor
            img_id = img_id.to(torch.device('cuda:0' if torch.cuda.is_available() else 'cpu'))

            #create latent id
            img_id_downsample = F.interpolate(img_id, size=(112,112))
            latend_id = self.model.netArc(img_id_downsample)
            latend_id = F.normalize(latend_id, p=2, dim=1)

            ############## Forward Pass ######################

            try:
                dest_img_align_crop_list, dest_img_mat_list = self.app.get(dest_img, self.options.crop_size, mode)
            except TypeError as e:
                raise HTTPException(status_code=404, detail='No faces detected in destination image.')

            swap_result_list = []
            dest_img_align_crop_tensor_list = []

            for dest_img_align_crop in dest_img_align_crop_list:

                dest_img_align_crop_tensor = Swapper.to_tensor(cv2.cvtColor(dest_img_align_crop, cv2.COLOR_BGR2RGB))[None, ...].to(torch.device('cuda:0' if torch.cuda.is_available() else 'cpu'))

                swap_result = self.model(None, dest_img_align_crop_tensor, latend_id, None, True)[0]
                swap_result_list.append(swap_result)
                dest_img_align_crop_tensor_list.append(dest_img_align_crop_tensor)           

            result_image = reverse2wholeimage(dest_img_align_crop_tensor_list, swap_result_list, dest_img_mat_list, self.options.crop_size, dest_img, pasring_model=self.net, use_mask=self.options.use_mask, norm=self.spNorm)

            id = uuid.uuid4().hex
            cv2.imwrite(f'backend/results/{id}.png', result_image)
            return f'{id}' #f'/result/{id}.png'

    def swap(self, source_img, dest_img, mode='single'):

        if self.use_cache:
            return self._swap(source_img, dest_img, mode)
        else:
            return self._swap.__wrapped__(self, source_img, dest_img, mode)


    @cachedmethod(lambda self: self.cache, key=partial(lambda  id, _, *args, **kwargs: hashkey(id, *args, **kwargs), '_swap_gif'))
    def _swap_gif(self, source_img, dest_gif, ext, mode='single'):

        source_np = np.frombuffer(source_img, np.uint8)
        # dest_np = np.frombuffer(dest_video, np.uint8)

        source_img = cv2.imdecode(source_np, cv2.IMREAD_COLOR)
        dest_gif = Image.open(io.BytesIO(dest_gif))

        with torch.no_grad():

            try:
                source_img_align_crop, _ = self.app.get(source_img, self.options.crop_size, 'single')
            except TypeError as e:
                raise HTTPException(status_code=404, detail='No faces detected in source image.')

            source_img_align_crop_pil = Image.fromarray(cv2.cvtColor(source_img_align_crop[0], cv2.COLOR_BGR2RGB)) 
            source_img = self.transformer_Arcface(source_img_align_crop_pil)
            img_id = source_img.view(-1, source_img.shape[0], source_img.shape[1], source_img.shape[2])

            # convert numpy to tensor
            img_id = img_id.to(torch.device('cuda:0' if torch.cuda.is_available() else 'cpu'))

            #create latent id
            img_id_downsample = F.interpolate(img_id, size=(112,112))
            latend_id = self.model.netArc(img_id_downsample)
            latend_id = F.normalize(latend_id, p=2, dim=1)

            return gif_swap(dest_gif, latend_id, self, ext, mode)

    def swap_gif(self, source_img, dest_gif, ext, mode='single'):

        if self.use_cache:
            return self._swap_gif(source_img, dest_gif, ext, mode)
        else:
            return self._swap_gif.__wrapped__(self, source_img, dest_gif, ext, mode)


    @cachedmethod(lambda self: self.cache, key=partial(lambda  id, _, *args, **kwargs: hashkey(id, *args, **kwargs), '_swap_video'))
    def _swap_video(self, source_img, dest_video, ext, mode='single'):

        source_np = np.frombuffer(source_img, np.uint8)
        # dest_np = np.frombuffer(dest_video, np.uint8)

        source_img = cv2.imdecode(source_np, cv2.IMREAD_COLOR)
        # dest_gif = Image.open(io.BytesIO(dest_gif))

        with torch.no_grad():

            try:
                source_img_align_crop, _ = self.app.get(source_img, self.options.crop_size, 'single')
            except TypeError as e:
                raise HTTPException(status_code=404, detail='No faces detected in source image.')

            source_img_align_crop_pil = Image.fromarray(cv2.cvtColor(source_img_align_crop[0], cv2.COLOR_BGR2RGB)) 
            source_img = self.transformer_Arcface(source_img_align_crop_pil)
            img_id = source_img.view(-1, source_img.shape[0], source_img.shape[1], source_img.shape[2])

            # convert numpy to tensor
            img_id = img_id.to(torch.device('cuda:0' if torch.cuda.is_available() else 'cpu'))

            #create latent id
            img_id_downsample = F.interpolate(img_id, size=(112,112))
            latend_id = self.model.netArc(img_id_downsample)
            latend_id = F.normalize(latend_id, p=2, dim=1)

            return video_swap(dest_video, latend_id, self, ext, mode)


    def swap_video(self, source_img, dest_video, ext, mode='single'):

        if self.use_cache:
            return self._swap_video(source_img, dest_video, ext, mode)
        else:
            return self._swap_video.__wrapped__(self, source_img, dest_video, ext, mode)           


    def save_cache(self):

        if self.use_cache:
            with open('backend/cache/cache.pkl', 'wb') as cache:
                pickle.dump(self.cache, cache)



