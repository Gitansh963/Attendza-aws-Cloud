import dlib
import numpy as np
import cv2
import os
import tkinter as tk
from tkinter import font as tkFont
from PIL import Image, ImageTk
import subprocess
import json
import boto3
from playsound import playsound
import os
import pygame
import threading
import time
import glob
import requests
# Use frontal face detector of Dlib
detector = dlib.get_frontal_face_detector()

class Face_Register:
    def __init__(self):
        self.intrude = 0
        self.current_frame_faces_cnt = 0  
        self.ss_cnt = 0  
        
        self.win = tk.Tk()
        self.win.title("Attendce through Face by Camera")
        self.win.geometry("1500x1000")

        self.frame_left_camera = tk.Frame(self.win)
        self.label = tk.Label(self.win)
        self.label.pack(side=tk.LEFT)
        self.frame_left_camera.pack()

        self.frame_right_info = tk.Frame(self.win)

        
        self.label_warning = tk.Label(self.frame_right_info)
        self.label_face_cnt = tk.Label(self.frame_right_info, text="Faces in current frame: ")
        self.log_all = tk.Label(self.frame_right_info)

        self.font_title = tkFont.Font(family='Helvetica', size=20, weight='bold')
        self.font_step_title = tkFont.Font(family='Helvetica', size=15, weight='bold')

        self.path_photos_from_camera = "index/"
        self.current_face_dir = "index/"
        self.font = cv2.FONT_ITALIC

        self.current_frame = np.ndarray
        self.face_ROI_image = np.ndarray
        self.face_ROI_width_start = 0
        self.face_ROI_height_start = 0
        self.face_ROI_width = 0
        self.face_ROI_height = 0
        self.ww = 0
        self.hh = 0

        self.out_of_range_flag = False

        self.cap = cv2.VideoCapture(0)  

        self.pre_work_mkdir()
        self.GUI_info()
        self.process()

    def GUI_info(self):
        tk.Label(self.frame_right_info, text="Face detection", font=self.font_title).grid(row=0, column=0, columnspan=3, sticky=tk.W, padx=2, pady=20)

        tk.Label(self.frame_right_info, text="Faces in current frame: ").grid(row=3, column=0, columnspan=2, sticky=tk.W, padx=5, pady=2)
        self.label_face_cnt.grid(row=3, column=2, columnspan=3, sticky=tk.W, padx=5, pady=2)

        self.label_warning.grid(row=4, column=0, columnspan=3, sticky=tk.W, padx=5, pady=2)

        tk.Label(self.frame_right_info, font=self.font_step_title, text="Save face image").grid(row=24, column=0, columnspan=3, sticky=tk.W, padx=5, pady=20)

        tk.Button(self.frame_right_info, text='Press for attendance', command=self.save_current_face).grid(row=26, column=0, columnspan=4, sticky=tk.W)

        self.log_all.grid(row=28, column=0, columnspan=4, sticky=tk.W, padx=5, pady=20)

        self.frame_right_info.pack()


        
    def pre_work_mkdir(self):
        if not os.path.isdir(self.path_photos_from_camera):
            os.mkdir(self.path_photos_from_camera)


    def removeAudio(self):
        mp3_files = glob.glob('*.mp3')
        for mp3_file in mp3_files:
            try:
                # Try to remove the .mp3 file
                os.remove(mp3_file)
                print(f'{mp3_file} removed')
            except Exception as e:
                print(e)
                print(f'Error removing {mp3_file}')
                continue
        
    def save_current_face(self):
        self.removeAudio()
        
        if self.current_frame_faces_cnt != 1:
            self.log_all["text"] = "No face in current frame!"
            return

        if self.out_of_range_flag:
            self.log_all["text"] = "Please do not go out of range!"
            return

        self.ss_cnt += 1
        self.face_ROI_image = np.zeros((int(self.face_ROI_height * 2), self.face_ROI_width * 2, 3), np.uint8)

        for ii in range(self.face_ROI_height * 2):
            for jj in range(self.face_ROI_width * 2):
                self.face_ROI_image[ii][jj] = self.current_frame[self.face_ROI_height_start - self.hh + ii][self.face_ROI_width_start - self.ww + jj]

        self.log_all["text"] = "\"" + os.path.join(self.current_face_dir, f"img_face.jpg") + "\" saved!"
        self.face_ROI_image = cv2.cvtColor(self.face_ROI_image, cv2.COLOR_BGR2RGB)
        cv2.imwrite(os.path.join(self.current_face_dir, f"img_face.jpg"), self.face_ROI_image)
        data= {"Image": os.path.abspath(os.path.join(self.current_face_dir, f"img_face.jpg"))}

        
        try:
            response = requests.post('http://localhost:8000/mark', json=data)
            if response.status_code == 200:
                print(response.json())
                response = response.json()
                try:
                    user = response['user']
                    user_name = user['Name']['S']
                    self.log_all["text"] = "Attendance marked successfully for " + user_name
                    random = str(int(time.time()))
                    text = "Attendance marked successfully for " + user_name
                    file_name = user_name + random + ".mp3"
                    self.text_to_speech(text, "Joanna", file_name)
                    self.play_audio(file_name)
                except Exception as e:
                    print("Error: ", e)
                    if(self.intrude==3):
                        data= {"Image": os.path.abspath(os.path.join(self.current_face_dir, f"img_face.jpg"))}
                        response = requests.post('http://localhost:8000/intruder', json=data)
                        if response.status_code == 200:
                            try:
                                text = "Warning! your face is not recognised, you have been marked as intruder. \nIf you try again, you will be reported to the authorities.\n If you are an employee, please contact the admin."
                                if os.path.exists("warning.mp3"):
                                    pass
                                else:
                                    self.text_to_speech(text, "Joanna", "warning.mp3")
                                self.play_audio("warning.mp3")
                                self.log_all["text"] = text 
                                self.intrude = 0
                            except Exception as e:
                                print("Error: ", e)
                        
                    else:
                        self.intrude += 1
                        
                        text = "Face not recognised, Error occurred while marking attendance, please try again"
                        if os.path.exists("error.mp3"):
                            pass
                        else:
                            self.text_to_speech(text, "Joanna", "error.mp3")
                        self.play_audio("error.mp3")
                        self.log_all["text"] = "Face not recognised, Error occurred while marking attendance, please try again"   
            else:
                self.log_all["text"] = "Challice error"                

        except requests.exceptions.RequestException as e:
            print(e)

    def play_audio(self, file_path):
        pygame.mixer.init()
        pygame.mixer.music.load(file_path)
        pygame.mixer.music.play()
        
        
    def text_to_speech(self,text, voice_id, output_file):
        polly = boto3.client('polly')
        response = polly.synthesize_speech(
            Text=text,
            VoiceId=voice_id,
            OutputFormat='mp3'
        )
        
        with open(output_file, 'wb') as file:
            file.write(response['AudioStream'].read())
        
    def get_frame(self):
        try:
            if self.cap.isOpened():
                ret, frame = self.cap.read()
                frame = cv2.resize(frame, (640,480))
                return ret, cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        except Exception as e:
            print("Error: ", e)

    def process(self):
        ret, self.current_frame = self.get_frame()
        faces = detector(self.current_frame, 0)
        
        if ret:
            self.label_face_cnt["text"] = str(len(faces))
            if len(faces) != 0:
                for k, d in enumerate(faces):
                    self.face_ROI_width_start = d.left()
                    self.face_ROI_height_start = d.top()
                    self.face_ROI_height = (d.bottom() - d.top())
                    self.face_ROI_width = (d.right() - d.left())
                    self.hh = int(self.face_ROI_height / 2)
                    self.ww = int(self.face_ROI_width / 2)

                    if (d.right() + self.ww) > 640 or (d.bottom() + self.hh > 480) or (d.left() - self.ww < 0) or (d.top() - self.hh < 0):
                        self.label_warning["text"] = "OUT OF RANGE"
                        self.label_warning['fg'] = 'red'
                        self.out_of_range_flag = True
                        color_rectangle = (255, 0, 0)
                    else:
                        self.out_of_range_flag = False
                        self.label_warning["text"] = ""
                        color_rectangle = (255, 255, 255)
                    self.current_frame = cv2.rectangle(self.current_frame,
                                                       tuple([d.left() - self.ww, d.top() - self.hh]),
                                                       tuple([d.right() + self.ww, d.bottom() + self.hh]),
                                                       color_rectangle, 2)
            self.current_frame_faces_cnt = len(faces)

            img_Image = Image.fromarray(self.current_frame)
            img_PhotoImage = ImageTk.PhotoImage(image=img_Image)
            self.label.img_tk = img_PhotoImage
            self.label.configure(image=img_PhotoImage)

        self.win.after(20, self.process)

    

    def run(self):
        self.win.mainloop()

def main():
    Face_Register_con = Face_Register()
    Face_Register_con.run()
    
    
if __name__ == '__main__':
    main()