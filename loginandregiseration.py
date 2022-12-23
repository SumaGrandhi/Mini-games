
import tkinter as tk
from tkinter import messagebox
from tkinter import *
import random
import time
import os
import sys
import mysql.connector
mydb=mysql.connector.connect(host="localhost",user="root",passwd="anikapandey",database="office")

#from typing import List, Any



def loginPage(logdata):
    sup.destroy()
    global login
    login = Tk()

    user_name = StringVar()
    password = StringVar()

    login_canvas = Canvas(login, width=720, height=440, bg="blue")
    login_canvas.pack()

    login_frame = Frame(login_canvas, bg="white")
    login_frame.place(relwidth=0.8, relheight=0.8, relx=0.1, rely=0.1)

    heading = Label(login_frame, text="Game App Login", fg="black", bg="white")
    heading.config(font=('calibri 40'))
    heading.place(relx=0.2, rely=0.1)

    # USER NAME
    ulabel = Label(login_frame, text="Username", fg='black', bg='white')
    ulabel.place(relx=0.21, rely=0.4)
    uname = Entry(login_frame, bg='#d3d3d3', fg='black', textvariable=user_name)
    uname.config(width=42)
    uname.place(relx=0.31, rely=0.4)

    # PASSWORD
    plabel = Label(login_frame, text="Password", fg='black', bg='white')
    plabel.place(relx=0.215, rely=0.5)
    pas = Entry(login_frame, bg='#d3d3d3', fg='black', show="*", textvariable=password)
    pas.config(width=42)
    pas.place(relx=0.31, rely=0.5)

    def check():
        for a, b, c, d in logdata:
            if b == uname.get() and c == pas.get():
                menu()
                break
            elif uname.get()=="" and pas.get()=="":
                error = Label(login_frame, text="username or password not entered!", fg='black', bg='white')
                error.place(relx=0.37, rely=0.7)

        else:
            error = Label(login_frame, text="Wrong Username or Password!", fg='black', bg='white')
            error.place(relx=0.37, rely=0.7)

    # LOGIN BUTTON
    log = Button(login_frame, text='Login', padx=5, pady=5, width=5, command=check)
    log.configure(width=15, height=1, activebackground="#33B5E5", relief=FLAT)
    log.place(relx=0.4, rely=0.6)

    login.mainloop()

def forgotpassword():
        sup.destroy()
        global flogin
        flogin = Tk()

        user_name = StringVar()
        password = StringVar()

        login_canvas = Canvas(flogin, width=720, height=440, bg="blue")
        login_canvas.pack()

        login_frame = Frame(login_canvas, bg="white")
        login_frame.place(relwidth=0.8, relheight=0.8, relx=0.1, rely=0.1)

        heading = Label(login_frame, text="FORGOT PASSWORD", fg="black", bg="white")
        heading.config(font=('calibri 40'))
        heading.place(relx=0.2, rely=0.1)

        # USER NAME
        ulabel = Label(login_frame, text="Username", fg='black', bg='white')
        ulabel.place(relx=0.21, rely=0.4)
        uname = Entry(login_frame, bg='#d3d3d3', fg='black', textvariable=user_name)
        uname.config(width=42)
        uname.place(relx=0.31, rely=0.4)

        # PASSWORD
        plabel = Label(login_frame, text="Password", fg='black', bg='white')
        plabel.place(relx=0.215, rely=0.5)
        pas = Entry(login_frame, bg='#d3d3d3', fg='black', show="*", textvariable=password)
        pas.config(width=42)
        pas.place(relx=0.31, rely=0.5)

        def changepassword():
            username = uname.get()
            password = pas.get()
            mycursor = mydb.cursor()
            mycursor.execute("UPDATE game set PASSWORD='%s'where USERNAME='%s'" % (password, username))
            mydb.commit()
            mycursor.execute('SELECT * FROM game')
            z = mycursor.fetchall()
            print(z)
            mydb.close()

        # FORGOT PASSWORD BUTTON
        fog = Button(login_frame, text='change password', padx=5, pady=5, width=5, command=changepassword)
        fog.configure(width=15, height=1, activebackground="#33B5E5", relief=FLAT)
        fog.place(relx=0.4, rely=0.6)

        flogin.mainloop()

def signUpPage():
    root.destroy()
    global sup
    sup = Tk()

    fname = StringVar()
    uname = StringVar()
    passW = StringVar()
    country = StringVar()

    sup_canvas = Canvas(sup, width=720, height=440, bg="blue")
    sup_canvas.pack()

    sup_frame = Frame(sup_canvas, bg="white")
    sup_frame.place(relwidth=0.8, relheight=0.8, relx=0.1, rely=0.1)

    heading = Label(sup_frame, text="Game App SignUp", fg="black", bg="white")
    heading.config(font=('calibri 40'))
    heading.place(relx=0.2, rely=0.1)

    # full name
    flabel = Label(sup_frame, text="Full Name", fg='black', bg='white')
    flabel.place(relx=0.21, rely=0.4)
    fname = Entry(sup_frame, bg='#d3d3d3', fg='black', textvariable=fname)
    fname.config(width=42)
    fname.place(relx=0.31, rely=0.4)

    # username
    ulabel = Label(sup_frame, text="Username", fg='black', bg='white')
    ulabel.place(relx=0.21, rely=0.5)
    user = Entry(sup_frame, bg='#d3d3d3', fg='black', textvariable=uname)
    user.config(width=42)
    user.place(relx=0.31, rely=0.5)

    # password
    plabel = Label(sup_frame, text="Password", fg='black', bg='white')
    plabel.place(relx=0.215, rely=0.6)
    pas = Entry(sup_frame, bg='#d3d3d3', fg='black', show="*", textvariable=passW)
    pas.config(width=42)
    pas.place(relx=0.31, rely=0.6)

    # country
    clabel = Label(sup_frame, text="Country", fg='black', bg='white')
    clabel.place(relx=0.215, rely=0.7)
    c = Entry(sup_frame, bg='#d3d3d3', fg='black', textvariable=country)
    c.config(width=42)
    c.place(relx=0.31, rely=0.7)

    def addUserToDataBase():
        fullname = fname.get()
        username = user.get()
        password = pas.get()
        country = c.get()
        mycursor = mydb.cursor()
        mycursor.execute("INSERT INTO game(FULLNAME,USERNAME,PASSWORD,COUNTRY) VALUES ('%s','%s','%s','%s')"%(fullname, username, password, country))
        mydb.commit()
        mycursor.execute('SELECT * FROM game')
        z= mycursor.fetchall()
        print(z)
        mydb.close()
        loginPage(z)

    def gotoLogin():
        mycursor = mydb.cursor()
        mycursor.execute('SELECT * FROM game')
        z = mycursor.fetchall()
        loginPage(z)


    # signup BUTTON
    sp = Button(sup_frame, text='SignUp', padx=5, pady=5, width=5, command=addUserToDataBase, bg='green')
    sp.configure(width=15, height=1, activebackground="#33B5E5", relief=FLAT)
    sp.place(relx=0.4, rely=0.8)

    log = Button(sup_frame, text='Already have a Account?', padx=5, pady=5, width=5, command=gotoLogin, bg="white",fg='blue')
    log.configure(width=16, height=1, activebackground="#33B5E5", relief=FLAT)
    log.place(relx=0.4, rely=0.9)
    fog = Button(sup_frame, text='Forgot password?', padx=5, pady=5, width=5, command=forgotpassword, bg="white",fg='blue')
    fog.configure(width=16, height=1, activebackground="#33B5E5", relief=FLAT)
    fog.place(relx=0.7, rely=0.9)
    sup.mainloop()

def menu():
    login.destroy()
    global menu
    menu = Tk()


    menu_canvas = Canvas(menu, width=720, height=440, bg="blue")
    menu_canvas.pack()

    menu_frame = Frame(menu_canvas, bg="white")
    menu_frame.place(relwidth=0.8, relheight=0.8, relx=0.1, rely=0.1)

    wel = Label(menu_canvas, text=' W E L C O M E  T O  G A M E S T A T I O N ', fg="white", bg="#101357")
    wel.config(font=('Broadway 22'))
    wel.place(relx=0.1, rely=0.02)

    def flappygame():
        os.system('python fb.py')
    b = Button(menu,text="play flappy bird game", command=flappygame)
    b.pack()
    def gem():
        os.system('python gemdazzle.py')
    g = Button(menu, text="play gem dazzle game", command=gem)
    g.pack()
    def connect4():
        os.system('python connect4.py')
    f = Button(menu, text="play connect4 game", command=connect4)
    f.pack()
    def quizz():
        os.system('python StartQuizz.py')
    l = Button(menu, text="play quizz game", command=quizz)
    l.pack()
    def logout():
        MsgBox = messagebox.askquestion('Exit Application', 'Do you want to quit the application?')
        if MsgBox == 'yes':
           menu.destroy()
        else:
            messagebox.showinfo('not exited')

    log2 = Button(menu, text="logout",command=logout,bg='brown',fg='white')
    log2.pack()
    mainloop()






def start():
    global root
    root = Tk()
    canvas = Canvas(root, width=720, height=440)
    canvas.grid(column=0, row=1)
    img = PhotoImage(file="loginbackground.png")
    canvas.create_image(50, 10, image=img, anchor=NW)

    button = Button(root, text='Start', command=signUpPage)
    button.configure(width=102, height=2, activebackground="#33B5E5", bg='green', relief=RAISED)
    button.grid(column=0, row=2)

    root.mainloop()


if __name__ == '__main__':
    start()

