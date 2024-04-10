import tkinter as tk
from tkinter import font as tkFont
from PIL import Image, ImageTk
import requests
import json
import os
import uuid
import dlib
detector = dlib.get_frontal_face_detector()
import cv2
import numpy as np
import random
class FaceRegisterGUI:
    def __init__(self):
        self.current_frame_faces_cnt = 0  
        self.ss_cnt = 0  
        
        self.win = tk.Tk()
        self.win.title("Register Face by Camera")
        self.win.geometry("1500x1000")

        self.frame_left_camera = tk.Frame(self.win)
        self.label = tk.Label(self.win)
        self.label.pack(side=tk.LEFT)
        self.frame_left_camera.pack()

        self.frame_right_info = tk.Frame(self.win)
        self.input_name = tk.Entry(self.frame_right_info)
        self.input_age = tk.Entry(self.frame_right_info)
        self.input_gender = tk.Entry(self.frame_right_info)
        self.input_language = tk.Entry(self.frame_right_info)
        self.input_disability = tk.Entry(self.frame_right_info)
        self.input_designation = tk.Entry(self.frame_right_info)
        self.input_department = tk.Entry(self.frame_right_info)
        self.input_email = tk.Entry(self.frame_right_info)
        self.input_phone = tk.Entry(self.frame_right_info)  
        self.input_address = tk.Entry(self.frame_right_info)  
        
        self.input_name_char = ""
        self.label_warning = tk.Label(self.frame_right_info)
        self.label_face_cnt = tk.Label(self.frame_right_info, text="Faces in current frame: ")
        self.log_all = tk.Label(self.frame_right_info)

        self.font_title = tkFont.Font(family='Helvetica', size=20, weight='bold')
        self.font_step_title = tkFont.Font(family='Helvetica', size=15, weight='bold')

        self.path_photos_from_camera = "index/"
        self.current_face_dir = ""
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
        self.face_folder_created_flag = False

        self.cap = cv2.VideoCapture(0)  

        self.pre_work_mkdir()
        self.GUI_info()
        self.process()
        
    def GUI_get_input_name(self):
        self.input_name_char = self.input_name.get()
        self.create_face_folder()
    
    def get_details(self):
        self.input_age_char = self.input_age.get()
        self.input_language_char = self.input_language.get()
        self.input_gender_char = self.input_gender.get()
        self.input_disability_char = self.input_disability.get()
        self.input_designation_char = self.input_designation.get()
        self.input_departement_char = self.input_department.get()
        self.input_email_char = self.input_email.get()
        self.input_phone_char = self.input_phone.get()  
        self.input_address_char =  self.input_address.get() 
        print(self.input_age_char, self.input_language_char  , self.input_gender_char
              , self.input_disability_char, self.input_designation_char, self.input_departement_char,
              self.input_email_char, self.input_phone_char, self.input_address_char)
    
    def GUI_info(self):
        tk.Label(self.frame_right_info, text="Face register", font=self.font_title).grid(row=0, column=0, columnspan=3, sticky=tk.W, padx=2, pady=20)

        tk.Label(self.frame_right_info, text="Faces in current frame: ").grid(row=3, column=0, columnspan=2, sticky=tk.W, padx=5, pady=2)
        self.label_face_cnt.grid(row=3, column=2, columnspan=3, sticky=tk.W, padx=5, pady=2)

        self.label_warning.grid(row=4, column=0, columnspan=3, sticky=tk.W, padx=5, pady=2)

        tk.Label(self.frame_right_info, font=self.font_step_title, text="Step 2: Input Information").grid(row=6, column=0, columnspan=3, sticky=tk.W, padx=5, pady=20)

        tk.Label(self.frame_right_info, text="Name: ").grid(row=8, column=0, sticky=tk.W, padx=5, pady=0)
        self.input_name.grid(row=8, column=1, sticky=tk.W, padx=0, pady=2)
        tk.Button(self.frame_right_info, text='Input Name', command=self.GUI_get_input_name).grid(row=8, column=3, padx=5, pady=5, sticky=tk.W)

        # Column 1
        tk.Label(self.frame_right_info, text="Age: ").grid(row=10, column=0, sticky=tk.W, padx=5, pady=0)
        self.input_age.grid(row=10, column=1, sticky=tk.W, padx=0, pady=2)
        
        tk.Label(self.frame_right_info, text="Gender: ").grid(row=12, column=0, sticky=tk.W, padx=5, pady=0)
        self.input_gender.grid(row=12, column=1, sticky=tk.W, padx=0, pady=2)
        
        tk.Label(self.frame_right_info, text="Language: ").grid(row=14, column=0, sticky=tk.W, padx=5, pady=0)
        self.input_language.grid(row=14, column=1, sticky=tk.W, padx=0, pady=2)
        
        tk.Label(self.frame_right_info, text="Disability: ").grid(row=16, column=0, sticky=tk.W, padx=5, pady=0)
        self.input_disability.grid(row=16, column=1, sticky=tk.W, padx=0, pady=2)
        
        tk.Label(self.frame_right_info, text="Address: ").grid(row=18, column=0, sticky=tk.W, padx=5, pady=0)
        self.input_address.grid(row=18, column=1, sticky=tk.W, padx=0, pady=2)      
        
        # Column 2
        tk.Label(self.frame_right_info, text="Designation: ").grid(row=10, column=2, sticky=tk.W, padx=5, pady=0)
        self.input_designation.grid(row=10, column=3, sticky=tk.W, padx=0, pady=2)
        
        tk.Label(self.frame_right_info, text="Department: ").grid(row=12, column=2, sticky=tk.W, padx=5, pady=0)
        self.input_department.grid(row=12, column=3, sticky=tk.W, padx=0, pady=2)
        
        tk.Label(self.frame_right_info, text="Email: ").grid(row=14, column=2, sticky=tk.W, padx=5, pady=0)
        self.input_email.grid(row=14, column=3, sticky=tk.W, padx=0, pady=2)
        
        tk.Label(self.frame_right_info, text="Phone: ").grid(row=16, column=2, sticky=tk.W, padx=5, pady=0)
        self.input_phone.grid(row=16, column=3, sticky=tk.W, padx=0, pady=2)
        
        tk.Button(self.frame_right_info, text='Input Fields', command=self.get_details).grid(row=18, column=3, padx=5, pady=5, sticky=tk.W)

        tk.Label(self.frame_right_info, font=self.font_step_title, text="Step 3: Save face image").grid(row=24, column=0, columnspan=3, sticky=tk.W, padx=5, pady=20)

        tk.Button(self.frame_right_info, text='Save current face', command=self.save_current_face).grid(row=26, column=0, columnspan=4, sticky=tk.W)

        self.log_all.grid(row=28, column=0, columnspan=4, sticky=tk.W, padx=5, pady=20)

        self.frame_right_info.pack()
    
    def pre_work_mkdir(self):
        if not os.path.isdir(self.path_photos_from_camera):
            os.mkdir(self.path_photos_from_camera)
    
    
    def create_face_folder(self):
        if self.input_name_char:
            self.current_face_dir = os.path.join(self.path_photos_from_camera,
                                                 "person_" + str(random.randint(0,1000)) + "_" + self.input_name_char)
        else:
            self.current_face_dir = os.path.join(self.path_photos_from_camera, "person_" + str(random.randint(0,1000)))

        os.makedirs(self.current_face_dir)
        self.log_all["text"] = "\"" + self.current_face_dir + "/\" created!"
        self.ss_cnt = 0  
        self.face_folder_created_flag = True 
    
    def get_frame(self):
        try:
            if self.cap.isOpened():
                ret, frame = self.cap.read()
                frame = cv2.resize(frame, (640,480))
                return ret, cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        except Exception as e:
            print("Error: ", e)
        
    
    def save_current_face(self):
        if not self.face_folder_created_flag:
            self.log_all["text"] = "Please run step 2!"
            return

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

        self.log_all["text"] = "\"" + os.path.join(self.current_face_dir, f"img_face_{self.ss_cnt}.jpg") + "\" saved!"
        self.face_ROI_image = cv2.cvtColor(self.face_ROI_image, cv2.COLOR_BGR2RGB)

        cv2.imwrite(os.path.join(self.current_face_dir, f"img_face_{self.ss_cnt}.jpg"), self.face_ROI_image)

    
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
    
    def generate_unique_id(self):
        return str(uuid.uuid4())
        
    def get_info_json(self):
        faceId = str(self.input_name_char + self.generate_unique_id())
        
        info = {
            "FaceId":  self.remove_spaces(faceId),
            "Name": self.input_name_char,
            "Age": self.input_age_char,
            "Gender": self.input_gender_char,
            "Language": self.input_language_char,
            "Disability": self.input_disability_char,
            "Designation": self.input_designation_char,
            "Department": self.input_departement_char,
            "Email": self.input_email_char,
            "Phone": self.input_phone_char,
            "Address": self.input_address_char,
            # "ImagePaths": [os.path.join(self.current_face_dir, f"img_face_{i}.jpg") for i in range(1, self.ss_cnt + 1)]
            "ImagePaths": [os.path.abspath(os.path.join(self.current_face_dir, f"img_face_{i}.jpg")) for i in range(1, self.ss_cnt + 1)]

        }
        return info

    def run(self):
        self.win.mainloop()
    
    def remove_spaces(self,string):
        no_spaces_string = ''.join(string.split())
        return no_spaces_string
        
    def register_face(self,data):
        try:
            response = requests.post('http://localhost:8000/register', json=data)
            if response.status_code == 200:
                print('done_200')
            else:
                print('done_400')
        except requests.exceptions.RequestException as e:
            print(e)

def main():
    Face_Register_con = FaceRegisterGUI()
    Face_Register_con.run()
    print('1')
    data = Face_Register_con.get_info_json()
    print('data_done')
    output = Face_Register_con.register_face(data)
    print(output)

if __name__ == '__main__':
    main()
