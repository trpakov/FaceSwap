import os
import shutil 
import cv2
import glob
import torch
import numpy as np
from backend.util.reverse2original import reverse2wholeimage
import moviepy.editor as mp
from moviepy.editor import AudioFileClip, VideoFileClip 
from moviepy.video.io.ImageSequenceClip import ImageSequenceClip
import uuid
from tempfile import TemporaryDirectory


def video_swap(video_obj, latent_id, swapper, ext, mode):
    

    with TemporaryDirectory() as temp:

        video_path = f'{temp}/video.{ext}'

        with open(video_path, 'wb') as buffer:
                    buffer.write(video_obj)

        video_audio_check = VideoFileClip(video_path)
        audio = True if video_audio_check.audio else False
        video_audio_check.close()

        if audio:
            video_audio_clip = AudioFileClip(video_path)

        video = cv2.VideoCapture(video_path)
        # ret = True
        frame_index = 0
        frame_count = int(video.get(cv2.CAP_PROP_FRAME_COUNT))

        fps = video.get(cv2.CAP_PROP_FPS)

        for frame_index in range(frame_count): 
            ret, frame = video.read()
            if  ret:

                detect_results = swapper.app.get(frame, swapper.options.crop_size, mode)

                if detect_results is not None:
                    frame_align_crop_list = detect_results[0]
                    frame_mat_list = detect_results[1]
                    swap_result_list = []
                    frame_align_crop_tensor_list = []
                    
                    for frame_align_crop in frame_align_crop_list:

                        frame_align_crop_tensor = swapper.to_tensor(cv2.cvtColor(frame_align_crop, cv2.COLOR_BGR2RGB))[None,...].to(torch.device('cuda:0' if torch.cuda.is_available() else 'cpu'))

                        swap_result = swapper.model(None,  frame_align_crop_tensor, latent_id, None, True)[0]
                        swap_result_list.append(swap_result)
                        frame_align_crop_tensor_list.append(frame_align_crop_tensor)                

                    result = reverse2wholeimage(frame_align_crop_tensor_list, swap_result_list, frame_mat_list, swapper.options.crop_size, frame, pasring_model=swapper.net, use_mask=swapper.options.use_mask, norm=swapper.spNorm)
                    cv2.imwrite(os.path.join(temp, 'frame_{:0>7d}.png'.format(frame_index)), result)

                else:
                    frame = frame.astype(np.uint8)
                    cv2.imwrite(os.path.join(temp, 'frame_{:0>7d}.png'.format(frame_index)), frame)
            else:
                break

        video.release()

        path = os.path.join(temp, '*.png')
        image_filenames = sorted(glob.glob(path))

        clips = ImageSequenceClip(image_filenames, fps = fps)

        if audio:
            clips = clips.set_audio(video_audio_clip)
            video_audio_clip.close()

        id = uuid.uuid4().hex
        clips.write_videofile(f'backend/results/{id}.{ext}', audio_codec='aac')
        clips.close()

    return id