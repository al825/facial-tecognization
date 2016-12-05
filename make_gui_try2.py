import tkinter as tk
from build_model_gui import BestModel
import pandas as pd
import sklearn 
import numpy as np
import random

from matplotlib import pyplot as plt
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure


import my_func
import time
from eye_identifier import EyeCenterIdentifier, GridSearch
from image_preprocess import imanorm, histeq, imaderiv
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split


class EyeCenterApp(tk.Tk):
    def __init__(self, width, height, best_model, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.geometry('{}x{}'.format(width, height))
        self.wm_title('Eye Center Prediction')
        self.resizable(width=False, height=False)
        self.container = tk.Frame(self)
        self.container.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)  
        self.best_model = best_model
        self.frames = {}
        self.init_page(StartPage)
        self.show_frame(StartPage)
        
    def init_page(self, page, *args, **kwargs):
        self.frames[page] = page(self.container, self, *args, **kwargs)
        #self.frames[page].config(height=height)
        #self.frames[page].config(width=width)
        self.frames[page].grid(row=0, column=0, sticky="nsew")
        
        
    def show_frame(self, page):
        self.frames[page].tkraise()
        
    def process_data(self):
        self.best_model.process_data()
        
    def build_model(self):
        self.best_model.build_model()
        
        
class StartPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.parent = parent
        self.controller = controller
        self.create_widgets()
    
    def create_widgets(self): 
        self.instruction = tk.Label(self, text='Eye Center Recognization')
        self.instruction.config(font=("Courier", 20))
        self.instruction.place(relx=0.5, rely=0.3, anchor=tk.CENTER)
        self.button = tk.Button(self, text = 'START', command=self.click_start)
        self.button.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
     
    def click_start(self):
        self.controller.init_page(PageOne)
        self.controller.show_frame(PageOne)
        self.controller.after(1000, self.controller.process_data)
        self.controller.after(1000, self.controller.build_model)
        self.controller.after(1000, self.controller.init_page, PageTwo)
        #self.controller.init_page(PageTwo)
        self.controller.after(1000, self.controller.show_frame, PageTwo)
        #print('page2')
        #self.controller.frames[PageOne].pd()
        #self.controller.frames[PageOne].visible = True
        #time.sleep(5)
        #
        #print(self.controller.frames[PageOne].visible)
        #if self.controller.frames[PageOne].visible:
         #   time.sleep(20)
        # process the data and build the model
        #self.controller.process_data()
        #self.controller.build_model()
        
        #self.controller.show_frame(PageTwo)
        #print("Shown the PageTwo")
        #time.sleep(5)
        
                    
        
class PageOne(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.parent = parent
        self.controller = controller
        self.create_widgets()
    
    def create_widgets(self): 
        self.label = tk.Label(self,text='Creating Model')
        self.label.config(font=("Courier", 20))
        self.label.place(relx=0.4, rely=0.4, anchor=tk.CENTER)
        

     
        
class PageTwo(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.parent = parent
        self.controller = controller
        self.buttons = {}
        self.create_widgets()
        
    def create_widgets(self):
        self.label = tk.Label(self, text='Predict')
        self.label.config(font=("Courier", 20))
        self.label.grid(row=0, column=0, columnspan=5)
        for i in range(10):
            img = tk.PhotoImage(file="dan4.gif")    
            ima_button = ImageButton(self, index = i, image=img)
            self.buttons['button_'.format(i)] = ima_button
            ima_button.config(command=self.buttons['button_'.format(i)].click_button)
            ima_button.image = img # keep a reference!
            ima_button.grid(row=int(i/5)+1, column=i-int(i/5)*5+1, padx=5, pady=5)
            

        

    
class PageThree(tk.Frame):
    def __init__(self, parent, controller, index):
        tk.Frame.__init__(self, parent)
        self.parent = parent
        self.controller = controller
        self.index = index
        self.mse = self.controller.best_model.make_prediction(index=index)
        self.create_widgets()
        self.p1 = None
        
    def create_widgets(self):
        label1 = tk.Label(self, text='Predict')
        label1.config(font=("Courier", 10))
        label1.pack()
        
        figure, ax = self.controller.best_model.draw_face(self.index, 96)
        canvas = FigureCanvasTkAgg(figure, self)
        canvas.show()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)  
        canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
        
        #self.figure = figure
        self.ax = ax
        self.canvas = canvas
        
        button_back = tk.Button(self, text='Make another prediction', command=lambda: self.controller.show_frame(PageTwo))
        button_back.pack(side=tk.BOTTOM)       
        label2 = tk.Label(self, text="MSE: {:.2f}".format(self.mse))
        label2.pack()
        
        check_box1 = CheckBox(self, "Predicted Eye Centers")
        check_box2 = CheckBox(self, "True Eye Centers")
        check_box3 = CheckBox(self, "Benchmark Models")
        
                  
class CheckBox(tk.Checkbutton):
    def __init__(self, parent, text):
        self.cv = tk.IntVar()
        self.parent = parent
        self.text=text
        tk.Checkbutton.__init__(self, parent, text=text, variable=self.cv, onvalue=1, offvalue=0, command=self.check_box)
        self.pack()
        self.p = None
        
        
    def check_box(self):
        if self.text == 'Predicted Eye Centers':
            values = self.parent.controller.best_model.data_pred.loc[self.parent.controller.best_model.data_pred['id'] == self.parent.index]
            color='blue'
        elif self.text == 'True Eye Centers':
            values = self.parent.controller.best_model.test_pos.iloc[self.parent.index]
            color='green'
        else:
            values = self.parent.controller.best_model.mean_pos
            color='red'
            
        if self.cv.get() == 1:
            self.p, = self.parent.ax.plot((values['left_eye_center_x'], values['right_eye_center_x']), (values['left_eye_center_y'], values['right_eye_center_y']), marker='.', color=color, linestyle="None")
            self.parent.canvas.draw()
        else:
            if self.p:
                self.p.remove()
                self.parent.canvas.draw()
            
        
class ImageButton(tk.Button):
    def __init__(self, parent, index, *args, **kwargs):
        tk.Button.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.index = index
     
    def click_button(self):
        
        self.parent.controller.init_page(PageThree, index=self.index)
        self.parent.controller.show_frame(PageThree)
        # make the prediction
        
        

        
    
    
        
        
        

if __name__ == '__main__':        
    step_size = (1, 1)
    N_steps = (8, 4)
    clf = RandomForestClassifier(bootstrap=True, class_weight=None, criterion='gini',
            max_depth=None, max_features='auto', max_leaf_nodes=None,
            min_impurity_split=1e-07, min_samples_leaf=1,
            min_samples_split=2, min_weight_fraction_leaf=0.0,
            n_estimators=50, n_jobs=1, oob_score=False, random_state=312,
            verbose=0, warm_start=False)
    best_model= BestModel(clf, step_size, N_steps)
    
    root = EyeCenterApp(width=500, height=800, best_model=best_model)
    root.mainloop()    
    
    
#Note: for image, 1. use paint to adjust the format; 2. do not forget to keep a reference

    


