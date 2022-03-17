import os 
import cv2
import glob
import torch
import numpy as np
from backend.util.reverse2original import reverse2wholeimage
from subprocess import call
import uuid
from tempfile import TemporaryDirectory


def gif_swap(anim, latent_id, swapper, ext, mode):

    # if os.path.exists('backend/temp'):
    #     shutil.rmtree('backend/temp')
    # os.mkdir('backend/temp')

    durations = []

    with TemporaryDirectory() as temp:
    
        for frame_num in range(anim.n_frames):
            anim.seek(frame_num)
            frame = np.array(anim.convert('RGB'))[:,:,::-1]
            durations.append(anim.info['duration'])

            detect_results = swapper.app.get(frame, swapper.options.crop_size, mode)
        
            if detect_results is not None:
                frame_align_crop_list = detect_results[0]
                frame_mat_list = detect_results[1]
                swap_result_list = []
                frame_align_crop_tensor_list = []

                for frame_align_crop in frame_align_crop_list:
                    frame_align_crop_tensor = swapper.to_tensor(cv2.cvtColor(frame_align_crop, cv2.COLOR_BGR2RGB))[None,...].to(torch.device('cuda:0' if torch.cuda.is_available() else 'cpu'))

                    swap_result = swapper.model(None, frame_align_crop_tensor, latent_id, None, True)[0]
                    swap_result_list.append(swap_result)
                    frame_align_crop_tensor_list.append(frame_align_crop_tensor)

                result = reverse2wholeimage(frame_align_crop_tensor_list, swap_result_list, frame_mat_list, swapper.options.crop_size, frame, pasring_model=swapper.net, use_mask=swapper.options.use_mask, norm=swapper.spNorm)
                cv2.imwrite(os.path.join(temp, 'frame_{:0>7d}.png'.format(anim.tell())), result)

            else:
                cv2.imwrite(os.path.join(temp, 'frame_{:0>7d}.png'.format(anim.tell())), frame)

        path = os.path.join(temp, '*.png')
        image_filenames = sorted(glob.glob(path))

        durations = np.array(durations) / 10
        command = 'convert'

        for image_filename, duration in zip(image_filenames, durations):
            command += f' -delay {duration} {image_filename}'

        id = uuid.uuid4().hex
        command += f' -layers Optimize backend/results/{id}.{ext}' if ext != 'png' else f' -layers Optimize APNG:backend/results/{id}.{ext}'
        call(command, shell=True)
    
    # with open(f'backend/results/{id}.{ext}', 'rb') as f:
    #     result = f.read()

    return id #result