import os.path
import datetime
import pickle
import xmlrpc.client
import tkinter as tk
import cv2
from PIL import Image, ImageTk
import face_recognition
import base64
import util
import tkinter.messagebox as messagebox

url = 'https://odoo195.odoo.com'
db = 'odoo195'
username = 'mohamed.azzam.1980@gmail.com'
api_key = 'f8c49e094aea2c8cfc9a5203bc95a30719a69cc5'

common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
uid = common.authenticate(db, username, api_key, {})

models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))

class App:
    def __init__(self):
        self.main_window = tk.Tk()
        self.main_window.title("Authentification BTS")
        icon_path = './files/bts.ico'  # Replace with the actual path to your ICO file
        self.main_window.iconbitmap(icon_path)
        self.main_window.geometry("1200x520+350+100")

        self.login_button_main_window = util.get_button(self.main_window, 'login', '#212D65', self.login)
        self.login_button_main_window.place(x=750, y=280)

        self.logout_button_main_window = util.get_button(self.main_window, 'logout', '#212D65', self.logout)
        self.logout_button_main_window.place(x=750, y=340)

        self.register_new_user_button_main_window = util.get_button(self.main_window, 'register new user', 'gray',
                                                                    self.register_new_user, fg='black')
        self.register_new_user_button_main_window.place(x=750, y=400)

        self.webcam_label = util.get_img_label(self.main_window)
        self.webcam_label.place(x=10, y=0, width=700, height=500)

        self.add_webcam(self.webcam_label)
        self.add_image()
        self.db_dir = './db'
        if not os.path.exists(self.db_dir):
            os.mkdir(self.db_dir)

        self.log_path = './log.txt'

    def add_image(self):
        image_path = './files/bts.jpg'  # Replace with the actual path to your image file
        image = Image.open(image_path)
        image = image.resize((150, 150))  # Adjust the size of the image as needed
        photo = ImageTk.PhotoImage(image=image)

        # Create a label and set the image
        image_label = tk.Label(self.main_window, image=photo)
        image_label.image = photo  # Save a reference to the image to prevent it from being garbage collected

        # Place the label at the desired location
        image_label.place(x=850, y=10)  # Adjust the coordinates as needed

    def add_webcam(self, label):
        if 'cap' not in self.__dict__:
            self.cap = cv2.VideoCapture(1)

        self._label = label
        self.process_webcam()

    def process_webcam(self):
        ret, frame = self.cap.read()

        self.most_recent_capture_arr = frame
        img_ = cv2.cvtColor(self.most_recent_capture_arr, cv2.COLOR_BGR2RGB)
        self.most_recent_capture_pil = Image.fromarray(img_)
        imgtk = ImageTk.PhotoImage(image=self.most_recent_capture_pil)
        self._label.imgtk = imgtk
        self._label.configure(image=imgtk)

        self._label.after(20, self.process_webcam)

    def login(self):
        # Load the stored image and face encodings from the database
        stored_images = os.listdir(self.db_dir)

        if len(stored_images) == 0:
            util.msg_box('Error!', 'No registered users found.')
            return

        # Capture the most recent image
        recent_image = self.most_recent_capture_arr.copy()
        recent_encoding = face_recognition.face_encodings(recent_image)

        if len(recent_encoding) == 0:
            util.msg_box('Error!', 'No face detected in the captured image.')
            return

        # Iterate over the stored images and compare with the recent image
        for image_file in stored_images:
            if image_file.endswith('.pickle'):  # Skip loading pickle files
                continue

            image_path = os.path.join(self.db_dir, image_file)
            with open(image_path, 'rb') as file:
                stored_image_data = file.read()

            stored_image = face_recognition.load_image_file(image_path)
            stored_encoding = face_recognition.face_encodings(stored_image)

            if len(stored_encoding) == 0:
                continue
            # Compare the face encodings
            match = face_recognition.compare_faces([stored_encoding[0]], recent_encoding[0])

            if match[0]:
                util.msg_box('Success!', 'Login successful. Welcome back, {}!'.format(image_file[:-4]))
                return

        util.msg_box('Error!', 'User not found.')
    def logout(self):
        name = util.recognize(self.most_recent_capture_arr, self.db_dir)

        if name in ['unknown_person', 'no_persons_found']:
            util.msg_box('Ups...', 'Unknown user. Please register new user or try again.')
        else:
            util.msg_box('Hasta la vista!', 'Goodbye, {}.'.format(name))
            current_time = datetime.datetime.now()
            formatted_time = current_time.strftime("%d/%m/%Y %H:%M:%S")
            search_domain = [('name', '=', name)]
            employee_ids = models.execute_kw(db, uid, api_key, 'hr.employee', 'search', [search_domain])

            if employee_ids:
                employee_id = employee_ids[0]
                employee_data = {'x_studio_date_de_sortie': formatted_time}

                models.execute_kw(db, uid, api_key, 'hr.employee', 'write', [[employee_id], employee_data])

                print("Check-out time updated for employee with ID:", employee_id)
            else:
                print("Employee with name", name, "not found.")

    def register_new_user(self):
        self.register_new_user_window = tk.Toplevel(self.main_window)
        self.register_new_user_window.geometry("1200x520+370+120")

        self.accept_button_register_new_user_window = util.get_button(self.register_new_user_window, 'Accept', 'green', self.accept_register_new_user)
        self.accept_button_register_new_user_window.place(x=750, y=340)

        self.try_again_button_register_new_user_window = util.get_button(self.register_new_user_window, 'Try again', 'red', self.try_again_register_new_user)
        self.try_again_button_register_new_user_window.place(x=750, y=400)

        self.capture_label = util.get_img_label(self.register_new_user_window)
        self.capture_label.place(x=10, y=0, width=700, height=500)

        self.add_img_to_label(self.capture_label)

        self.entry_text_register_new_user = util.get_entry_text(self.register_new_user_window)
        self.entry_text_register_new_user.place(x=750, y=100)

        self.entry_text_register_new_user_email = util.get_entry_text(self.register_new_user_window)
        self.entry_text_register_new_user_email.place(x=750, y=180)

        self.entry_text_register_new_user_mobile = util.get_entry_text(self.register_new_user_window)
        self.entry_text_register_new_user_mobile.place(x=750, y=250)

        self.text_label_register_new_user = util.get_text_label(self.register_new_user_window, 'Saisir Votre Nom:')
        self.text_label_register_new_user.place(x=750, y=60)

        self.text_label_register_new_user_email = util.get_text_label(self.register_new_user_window, 'Entrer Votre Email:')
        self.text_label_register_new_user_email.place(x=750, y=135)

        self.text_label_register_new_user_mobile = util.get_text_label(self.register_new_user_window, 'Entrer votre numéro:')
        self.text_label_register_new_user_mobile.place(x=750, y=210)

    def try_again_register_new_user(self):
        self.register_new_user_window.destroy()

    def add_img_to_label(self, label):
        imgtk = ImageTk.PhotoImage(image=self.most_recent_capture_pil)
        label.imgtk = imgtk
        label.configure(image=imgtk)

        self.register_new_user_capture = self.most_recent_capture_arr.copy()

    def start(self):
        self.main_window.mainloop()

    def accept_register_new_user(self):
        name = self.entry_text_register_new_user.get(1.0, "end-1c")
        email = self.entry_text_register_new_user_email.get(1.0, "end-1c")
        mobile = self.entry_text_register_new_user_mobile.get(1.0, "end-1c")

        embeddings = face_recognition.face_encodings(self.register_new_user_capture)[0]

        # Save as .pickle
        file_pickle = open(os.path.join(self.db_dir, '{}.pickle'.format(name)), 'wb')
        pickle.dump(embeddings, file_pickle)

        # Save as .png RGB color
        file_png = os.path.join(self.db_dir, '{}.png'.format(name))
        image_rgb = cv2.cvtColor(self.register_new_user_capture, cv2.COLOR_BGR2RGB)
        image_pil = Image.fromarray(image_rgb)
        image_pil.save(file_png)

        with open(file_png, 'rb') as file:
            image_data = file.read()
        image_data_base64 = base64.b64encode(image_data).decode('utf-8')
        current_time = datetime.datetime.now()
        formatted_time = current_time.strftime("%d/%m/%Y %H:%M:%S")
        employee_id = models.execute_kw(db, uid, api_key, 'hr.employee', 'create',
                                        [{'name': name, 'job_title': 'Systéme est reseaux informatique',
                                          'work_email': email, 'mobile_phone': mobile,
                                          'x_studio_date_darriv': "",
                                          'x_studio_date_de_sortie': "",
                                          'image_1920': image_data_base64}])

        util.msg_box('Success!', 'Welcome To BTS Center')
        self.register_new_user_window.destroy()


if __name__ == "__main__":
    app = App()
    app.start()
