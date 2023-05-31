import socket
from tkinter import *
from tkinter import ttk
from PIL import Image,ImageTk
import time
import ast
import threading

HOST = "127.0.0.1" # Địa chỉ loopback (có thể thay bằng ipv4 local)
SERVER_PORT = 65432 
FORMAT = "utf8" 
LOGIN = "login"
list=['VND','USD','AUD','CAD','CHF','CNY','DKK','EUR','GBP','HKD','JPY','KRW','LAK','MYR','NOK','NZD','RUB','SEK','SGD','THB','TWD']

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

def sendList(client, list):
    for item in list:
        client.sendall(item.encode(FORMAT))
        client.recv(1024)#wait response
    msg = "end"
    client.send(msg.encode(FORMAT))

def server_response():
    while(True):
        try:
            mess_response=client.recv(2048).decode(FORMAT) #Đúng nhận reponse
            if(mess_response=="0"): #0 là server gửi lại để không bi trùng
                continue
            elif(mess_response=="Login_success"):
                Error_loginscr.config(text="")
                Menu_Screen.tkraise()
            elif(mess_response=="Login_fail"):
                Error_loginscr.config(text="Error! Please try again")
            elif(mess_response=="Register_success"):
                Error_registerscr.config(text="")
                Login_Screen.tkraise()
            elif(mess_response=="Register_fail"):
                Error_registerscr.config(text="Error! Please try again")
            elif(mess_response=="Convert_success"):
                info=[] #danh sách lưu số lượng đon vi đổi
                info.append(textbox_Amount.get())
                info.append(Combobox_From.get())
                info.append(Combobox_To.get())
                client.sendall((info[0]+","+info[1]+","+info[2]).encode(FORMAT))
                result=client.recv(1024).decode(FORMAT)
                textbox_Result.delete(0,END)
                textbox_Result.insert(END,result+" "+info[2])
            elif(mess_response=="Convert_fail"):
                textbox_Result.delete(0,END)
                textbox_Result.insert(END,"Data isn't available")
            elif(mess_response[0]=='['): #Nếu mess là data thì showw ra màn hình
                DATA = ast.literal_eval(mess_response)#nhận nguyên list data tu sv va chuyen thanh dict
                theme=['  Buy Cash','  Buy Transfer','  Currency','  Sell']
                col=0
                for t in theme:
                    e = Entry(Rate_table_Screen, width=15, fg='blue',font=('Arial',10,'bold'))
                    e.insert(END,t)
                    e.grid(row=0, column=col)
                    col+=1
                c=0
                r=1
                for item in DATA:#duyet list(moi key la 1 dict)
                    for key in item:
                        e = Entry(Rate_table_Screen, width=15, fg='blue',font=('Arial',9,'bold'))
                        e.insert(END,item[key])
                        e.grid(row=r, column=c)
                        c+=1
                    r+=1
                    c=0
            elif(mess_response=="Tabledata_success"):
                text_err.config(text="")
                data_table = ast.literal_eval(client.recv(2048).decode(FORMAT))
                c=0
                r=1
                for item in data_table:#duyet list(moi key la 1 dict)
                    for key in item:
                        e = Entry(Rate_table_Screen, width=15, fg='blue',font=('Arial',9,'bold'))
                        e.insert(END,item[key])
                        e.grid(row=r, column=c)
                        c+=1
                    r+=1
                    c=0
            elif(mess_response=="Tabledata_fail"):  
                text_err.config(text="Data isn't available")
            elif(mess_response=="quit"):
                Server_Stop_Screen.tkraise()
        except: #Nếu không bắt được thông tin server thì mở màn hình server stop
            Server_Stop_Screen.tkraise()

def submit_IP(textbox_IP):
    IP=textbox_IP.get()
    if(IP==HOST):
        try:
            client.connect( (HOST, SERVER_PORT) )
            Thead_svreponse=threading.Thread(target=server_response)#Tạo luồng phụ để nghe client response
            Thead_svreponse.daemon=True
            Thead_svreponse.start()
            Login_Screen.tkraise()          
        except:
            Error.config(text="Error! Server Not found")
    else:
        Error.config(text="Error! Please try again")

def client_Login():
    account = [] 
    account.append(textbox_acc.get())
    account.append(textbox_pass.get())
    if(account[0]=="" or account[1]==""): #Kiểm tra nếu tk mk trong thi thông báo
        Error_loginscr.config(text="Error! Please try again")
    else: 
        client.sendall("login".encode(FORMAT))
        client.sendall((account[0]+","+account[1]).encode(FORMAT))

def Handle_Register():
    account = [] 
    account.append(textbox_acc1.get())
    account.append(textbox_pass1.get())
    if(account[0]=="" or account[1]==""): #Kiểm tra nếu tk mk trong thi thông báo
        Error=Label(Register_Screen,text="Error! Try again",fg="#1E1E1E",bd=2,bg="#9AB2BC")#bg là back_ground color
        Error.place(x=235,y=280)
    else:
        client.sendall("register".encode(FORMAT))
        client.sendall((account[0]+","+account[1]).encode(FORMAT))
        

def client_Register():
    Register_Screen.tkraise()
    
def client_Quit():
    client.sendall("quit".encode(FORMAT))
    client.close()
    root.destroy()

def client_Quit_svout():
    root.destroy()

def client_Convert():
    Convert_Screen.tkraise()

def client_Back():
    Menu_Screen.tkraise()

def client_Result_Convert():#Hàm nhận kết quả chuyển đổi
    amount=textbox_Amount.get()
    if(amount!=""):
        client.sendall("convert".encode(FORMAT))
        day_convert=str(Combobox_Day.get())+"-"+str(Combobox_Month.get())+"-"+str(Combobox_Year.get())
        client.sendall(day_convert.encode(FORMAT))

def client_Rate_table():
    Rate_table_Screen.tkraise()
    client.sendall("ratetable".encode(FORMAT))
        
def client_Searchtable():
    client.sendall("searchtable".encode(FORMAT))
    list_day=[]
    list_day.append(Combobox_Day2.get())
    list_day.append(Combobox_Month2.get())
    list_day.append(Combobox_Year2.get())
    client.sendall((list_day[0]+"-"+list_day[1]+"-"+list_day[2]).encode(FORMAT))

def client_Logout():
    Login_Screen.tkraise()
    client.sendall("logout".encode(FORMAT))




#------------------Tkinter-----------------
root=Tk()
root.title("Currency")
root.geometry("600x400")
root.iconbitmap("logo.ico")
back_ground=Image.open("money.jpg")
render=ImageTk.PhotoImage(back_ground.resize((600, 400)))

#################################

IP_Screen=Frame(root, width=600, height=400)
IP_Screen.place(x=0,y=0)
IP_Screen.grid_propagate(0)#Giũ nguyên khung
img=Label(IP_Screen,image=render)
img.place(x=0,y=0)
name=Label(IP_Screen,text="Enter IP Server",fg="#1E1E1E",bd=2,bg="#9AB2BC")#bg là back_ground color
name.config(font=("Transformers Movie",25))
name.place(x=160,y=100)
text_IP=Label(IP_Screen,text="IP Address:",font=('Arial',9,'bold'),fg="#1E1E1E")
text_IP.place(x=200,y=160)
textbox_IP=Entry(IP_Screen, width=15,font=('Arial',10,'bold'))
textbox_IP.place(x=270,y=160)
button_login=Button(IP_Screen,text="Submit",font=('Arial',10,'bold'),bg="#007ACC",bd=3,width=10,command=lambda: submit_IP(textbox_IP))   
button_login.place(x=275,y=190)
Error=Label(IP_Screen,text="",bg="#C1E1EC",fg="#FF0000",bd=2,font=('Arial',9,'bold'))#bg là back_ground color
Error.place(x=255,y=230)


#################################
Login_Screen=Frame(root, width=600, height=400)
Login_Screen.place(x=0,y=0)
Login_Screen.grid_propagate(0)#Giũ nguyên khung
img=Label(Login_Screen,image=render)
img.place(x=0,y=0)
name=Label(Login_Screen,text="LOG IN",fg="#1E1E1E",bd=2,bg="#9AB2BC")#bg là back_ground color
name.config(font=("Transformers Movie",30))
name.place(x=250,y=70)
text_Acount=Label(Login_Screen,text="Account:",font=('Arial',10,'bold'),fg="#1E1E1E")
text_Acount.place(x=210,y=160)
textbox_acc=Entry(Login_Screen, width=20,font=('Arial',10,'bold'))
textbox_acc.place(x=280,y=160)
text_Pass=Label(Login_Screen,text="Password:",font=('Arial',10,'bold'),fg="#1E1E1E")
text_Pass.place(x=210,y=190)
textbox_pass=Entry(Login_Screen,font=('Arial',10,'bold'), width=20)
textbox_pass.place(x=280,y=190)
button_login=Button(Login_Screen,text="LOG IN",font=('Arial',10,'bold'),bg="#007ACC",bd=3,width=10,command=client_Login)   
button_login.place(x=300,y=218)
button_register=Button(Login_Screen,text="REGISTER",font=('Arial',10,'bold'),bg="#007ACC",bd=3,width=10,command=client_Register)   
button_register.place(x=300,y=253)
Error_loginscr=Label(Login_Screen,text="",bg="#C1E1EC",fg="#FF0000",bd=2,font=('Arial',9,'bold'))#bg là back_ground color
Error_loginscr.place(x=280,y=285)
###############################

Register_Screen=Frame(root, width=600, height=400)
Register_Screen.place(x=0,y=0)
Register_Screen.grid_propagate(0)#Giũ nguyên khung
img=Label(Register_Screen,image=render)
img.place(x=0,y=0)
name=Label(Register_Screen,text="REGISTER",fg="#1E1E1E",bd=2,bg="#9AB2BC")#bg là back_ground color
name.config(font=("Transformers Movie",30))
name.place(x=230,y=70)
text_Acount=Label(Register_Screen,text="Account:",font=('Arial',10,'bold'),fg="#1E1E1E")
text_Acount.place(x=210,y=160)
textbox_acc1=Entry(Register_Screen, width=20)
textbox_acc1.place(x=280,y=160)
text_Acount=Label(Register_Screen,text="Password:",font=('Arial',10,'bold'),fg="#1E1E1E")
text_Acount.place(x=210,y=190)
textbox_pass1=Entry(Register_Screen, width=20)
textbox_pass1.place(x=280,y=190)
button_register=Button(Register_Screen,text="REGISTER",font=('Arial',10,'bold'),bg="#007ACC",bd=3,width=10,command=Handle_Register)   
button_register.place(x=300,y=240)
Error_registerscr=Label(Register_Screen,text="",bg="#C1E1EC",fg="#FF0000",bd=2,font=('Arial',9,'bold'))#bg là back_ground color
Error_registerscr.place(x=280,y=270)

############################
Menu_Screen=Frame(root,bg="black",width=600, height=400)
Menu_Screen.place(x=0,y=0)
Menu_Screen.grid_propagate(0)
img=Label(Menu_Screen,image=render)
img.place(x=0,y=0)
name=Label(Menu_Screen,text="MENU",fg="#1E1E1E",bd=2,bg="#9AB2BC")#bg là back_ground color
name.config(font=("Transformers Movie",30))
name.place(x=270,y=60)
button_convert=Button(Menu_Screen,text="CONVERT",font=('Arial',10,'bold'),bg="#007ACC",bd=3,width=20,command=client_Convert)   
button_convert.place(x=240,y=135)
button_tablerate=Button(Menu_Screen,text="RATE TABLE",font=('Arial',10,'bold'),bg="#007ACC",bd=3,width=20,command=client_Rate_table)   
button_tablerate.place(x=240,y=170)
button_logout=Button(Menu_Screen,text="LOG OUT",bg="#007ACC",font=('Arial',10,'bold'),bd=3,width=20,command=client_Logout)   
button_logout.place(x=240,y=205)
button_quit=Button(Menu_Screen,text="QUIT",bg="#007ACC",font=('Arial',10,'bold'),bd=3,width=20,command=client_Quit)   
button_quit.place(x=240,y=240)

############################
Convert_Screen=Frame(root,bg="black",width=600, height=400)
Convert_Screen.place(x=0,y=0)
Convert_Screen.grid_propagate(0)
img=Label(Convert_Screen,image=render)
img.place(x=0,y=0)
name=Label(Convert_Screen,text="CONVERT",fg="#1E1E1E",bd=2,bg="#9AB2BC")#bg là back_ground color
name.config(font=("Transformers Movie",30))
name.place(x=250,y=60)
text_Day=Label(Convert_Screen,text="Day:", fg="#1E1E1E")
text_Day.place(x=210,y=130)
Combobox_Day=ttk.Combobox(Convert_Screen,width=5)
Combobox_Day['value']=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31]
Combobox_Day.current(time.localtime().tm_mday-1)
Combobox_Day.place(x=240,y=130)
text_Month=Label(Convert_Screen,text="Month:", fg="#1E1E1E")
text_Month.place(x=305,y=130)
Combobox_Month=ttk.Combobox(Convert_Screen,width=5)
Combobox_Month['value']=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
Combobox_Month.current(time.localtime().tm_mon-1)
Combobox_Month.place(x=350,y=130)
text_Year=Label(Convert_Screen,text="Year:", fg="#1E1E1E")
text_Year.place(x=417,y=130)
Combobox_Year=ttk.Combobox(Convert_Screen,width=5)
Combobox_Year['value']=[2018,2019,2020,2021]
Combobox_Year.current(3)
Combobox_Year.place(x=450,y=130)
text_Amount=Label(Convert_Screen,text="Amount:", fg="#1E1E1E")
text_Amount.place(x=210,y=160)
textbox_Amount=Entry(Convert_Screen, width=20)
textbox_Amount.place(x=300,y=160)
text_From=Label(Convert_Screen,text="From:",fg="#1E1E1E")
text_From.place(x=210,y=190)
Combobox_From=ttk.Combobox(Convert_Screen,width=10)
Combobox_From['value']=list
Combobox_From.current(1)
Combobox_From.place(x=210,y=210)
text_To=Label(Convert_Screen,text="To:",fg="#1E1E1E")
text_To.place(x=360,y=190)
Combobox_To=ttk.Combobox(Convert_Screen,width=10)
Combobox_To['value']=list
Combobox_To.current(0)
Combobox_To.place(x=360,y=210)
text_Result=Label(Convert_Screen,text="Result:", fg="#1E1E1E")
text_Result.place(x=210,y=240)
textbox_Result=Entry(Convert_Screen, width=20)
textbox_Result.place(x=300,y=240)
button_convert1=Button(Convert_Screen,text="CONVERT",font=('Arial',10,'bold'),bg="#007ACC",bd=3,width=20,command=client_Result_Convert)   
button_convert1.place(x=245,y=270)
button_back=Button(Convert_Screen,text="BACK",font=('Arial',10,'bold'),bg="#007ACC",bd=3,width=20,command=client_Back)   
button_back.place(x=245,y=300)

############################
Rate_table_Screen=Frame(root,bg="black",width=600, height=400)
Rate_table_Screen.place(x=0,y=0)
Rate_table_Screen.grid_propagate(0)
img=Label(Rate_table_Screen,image=render)
img.place(x=0,y=0)
text_Ratecurr=Label(Rate_table_Screen,text="RATE TABLE",fg="#1E1E1E",bd=2,bg="#9AB2BC")#bg là back_ground color
text_Ratecurr.config(font=("Transformers Movie",22))
text_Ratecurr.place(x=435,y=2)
text_Day=Label(Rate_table_Screen,text="Day:", fg="#1E1E1E")
text_Day.place(x=460,y=120)
Combobox_Day2=ttk.Combobox(Rate_table_Screen,width=5)
Combobox_Day2['value']=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31]
Combobox_Day2.current(time.localtime().tm_mday-1)
Combobox_Day2.place(x=515,y=120)
text_Month=Label(Rate_table_Screen,text="Month:", fg="#1E1E1E")
text_Month.place(x=460,y=150)
Combobox_Month2=ttk.Combobox(Rate_table_Screen,width=5)
Combobox_Month2['value']=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
Combobox_Month2.current(time.localtime().tm_mon-1)
Combobox_Month2.place(x=515,y=150)
text_Year=Label(Rate_table_Screen,text="Year:", fg="#1E1E1E")
text_Year.place(x=460,y=180)
Combobox_Year2=ttk.Combobox(Rate_table_Screen,width=5)
Combobox_Year2['value']=[2018,2019,2020,2021]
Combobox_Year2.current(3)
Combobox_Year2.place(x=515,y=180)
button_back2=Button(Rate_table_Screen,text="SEARCH BY DAY",font=('Arial',10,'bold'),bg="#007ACC",bd=3,width=15,command=client_Searchtable)   
button_back2.place(x=455,y=240)
button_back2=Button(Rate_table_Screen,text="BACK",font=('Arial',10,'bold'),bg="#007ACC",bd=3,width=15,command=client_Back)   
button_back2.place(x=455,y=275)
text_err=Label(Rate_table_Screen,text="",font=('Arial',10), fg="#1E1E1E",bg="#79A7B6")
text_err.place(x=467,y=218)

#############################################################
Server_Stop_Screen=Frame(root,bg="black",width=600, height=400)
Server_Stop_Screen.place(x=0,y=0)
Server_Stop_Screen.grid_propagate(0)
img=Label(Server_Stop_Screen,image=render)
img.place(x=0,y=0)
text_sv_stop=Label(Server_Stop_Screen,text="SERVER HAS STOPPED",fg="#1E1E1E",bd=2,bg="#9AB2BC")#bg là back_ground color
text_sv_stop.config(font=("Transformers Movie",40))
text_sv_stop.place(x=55,y=80)
button_quit1=Button(Server_Stop_Screen,text="QUIT",font=('Arial',10,'bold'),bg="#007ACC",bd=3,width=20,command=client_Quit_svout)   
button_quit1.place(x=230,y=245)

IP_Screen.tkraise()
root.mainloop()




