import socket 
import threading 
from tkinter import *
from tkinter.scrolledtext import ScrolledText
from PIL import Image,ImageTk
import json
import ast
import requests
import time


HOST = "127.0.0.1"  # Địa chỉ loopback (có thể thay bằng ipv4 local)
SERVER_PORT = 65432 
FORMAT = "utf8"
LOGIN = "login"

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #AF_INET thực hiện trên ipv4, SOCK_STREAM sử dụng tcp thay vì  SOCK_DGRAM:udp
Client_list=[] #Lưu địa chỉ và tài khoản
data=[] #lưu data lấy từ web
Client_conn=[] #lưu client connect để ngắt kết nối

#################### CÁC HÀM XỬ LÝ ##########################
def Insert_Thread(conn, addr): #Thêm 1 luông mới
    thr = threading.Thread(target=handleClient, args=(conn, addr))# tách 1 luồng mới chỉ riêng 1 hàm và các đổi số của hàm đó, sau đó làm các bước tiếp trong main
    thr.daemon = True #True thì khi chạy hết hàm main sẽ kết thúc các luồng, False là 1 luồng kết thúc main thì k ảnh hưởng với các luồng còn lại đang chạy
    thr.start()

def Update_active():
    text_area.delete(1.0,END) #Xóa hết trong scroller
    for acc in Client_list:
        text_area.insert(END,acc+"\n")# Ghi lại tát cả acc

def recvList(conn):
    list = []
    item = conn.recv(1024).decode(FORMAT)
    while (item != "end"):
        list.append(item)
        conn.sendall(item.encode(FORMAT))
        item = conn.recv(1024).decode(FORMAT)
    return list

def client_Login(conn: socket, addr):
    conn.sendall("0".encode(FORMAT))
    account=conn.recv(1024).decode(FORMAT) # nhận 1 string "mk,tk" tu client
    account=account.split(',') 
    with open('data_user.json', 'r') as myfile:
        data_acc=myfile.read()
        data_acc=ast.literal_eval(data_acc) #Chuyen sang dict
    if ((account[0] in data_acc) and (str(data_acc[account[0]])==account[1])):
        conn.sendall("Login_success".encode(FORMAT))#True là đăng nhập đúng
        Client_list.append(str(addr)+" with account: "+account[0]+"\n   Action: ")
        Update_active()
    else: 
        conn.sendall("Login_fail".encode(FORMAT)) #False là đăng nhập sai

def client_Register(conn: socket):
    conn.sendall("0".encode(FORMAT))
    account=conn.recv(1024).decode(FORMAT) # nhận 1 string "mk,tk" tu client
    account=account.split(',') 
    with open('data_user.json', 'r') as myfile: #Dọc file json luu data
        data_acc=myfile.read()
        data_acc=ast.literal_eval(data_acc) #Chuyen sang dict
    if (account[0] in data_acc):
        conn.sendall("Register_fail".encode(FORMAT))
    else : # Dong y va them tai khoan mat khau vao data user
        conn.sendall("Register_success".encode(FORMAT))
        data_acc[account[0]]=account[1]
        data_acc=json.dumps(data_acc)
        with open('data_user.json', 'w') as fp: #ghi vao file json data
            fp.write(data_acc)

def client_Quit(conn: socket, addr):
    conn.close() # Đóng kết nói client
    for acc in Client_list: # Duyệt để tìm client cần xóa vì không biết tài khoản
        if(acc.find(str(addr))!=-1):
            Client_list.remove(acc)
    Client_conn.remove(conn)
    Update_active()

def client_Convert(conn: socket):
    conn.sendall("0".encode(FORMAT))
    day_convert=conn.recv(1024).decode(FORMAT) #một chuỗi ngày tháng
    with open('data.json', 'r') as myfile: #Dạng lưu file là {"ngay-thang-nam":[....]]}
        data_file=myfile.read()
        data_file=ast.literal_eval(data_file)
        if day_convert in data_file: #kiếm tra có data không
            conn.sendall("Convert_success".encode(FORMAT))
            list_info=conn.recv(1024).decode(FORMAT)
            list_info=list_info.split(',')#0 la amount 1 la from 2 to
            amount=int(list_info[0])
            currency_from=1 #mặc định 1 là VND
            currency_to=1 #mặc định 1 là VND
            data_file=data_file[day_convert]
            for item in data_file:
                if item["currency"]==list_info[1]:
                    currency_from=item["sell"]
                if item["currency"]==list_info[2]:
                    currency_to=item["sell"]
            result=amount*currency_from/currency_to
            conn.sendall(str(round(result,2)).encode(FORMAT))
        else:
            conn.sendall("Convert_fail".encode(FORMAT))

def client_Logout(conn:socket,addr):
    conn.sendall("0".encode(FORMAT))
    for acc in Client_list: # Duyệt để tìm client cần xóa vì không biết tài khoản
        if(acc.find(str(addr))!=-1):
            Client_list.remove(acc)
    Update_active()

def client_Ratetable(conn:socket):
    conn.send(str(data).encode(FORMAT))

def client_Searchtable(conn:socket):
    conn.sendall("0".encode(FORMAT))#để không bị trùng dữ liệu
    day=conn.recv(1024).decode(FORMAT)# Nhận str "ngay,thang,nam"
    with open('data.json', 'r') as myfile: #Dạng lưu file là {"ngay-thang-nam":[....]]}
        data_file=myfile.read()
        data_file=ast.literal_eval(data_file)
        if day in data_file: #kiếm tra có data không
            conn.sendall("Tabledata_success".encode(FORMAT))
            conn.send(str(data_file[day]).encode(FORMAT))
        else: conn.sendall("Tabledata_fail".encode(FORMAT))

def insert_datafile(data):
    with open('data.json', 'r') as myfile: #Dạng lưu file là {"ngay-thang-nam":[....]]}
        data_file=myfile.read()
        data_file=ast.literal_eval(data_file) #Chuyen sang dict
        t=time.localtime()#Lấy thòi gian hien tai
        day=str(t.tm_mday)+"-"+str(t.tm_mon)+"-"+str(t.tm_year)#s để lưu ngày-tháng-năm
        data_file[day]=data # Cập nhật lại data vì nếu trùng thì thay đổi còn k trùng thì thêm
        data_file=json.dumps(data_file)
        with open('data.json', 'w') as fp: #ghi vao file json data
            fp.write(data_file)

def Logout():
    for conn in Client_conn:
        conn.sendall("quit".encode(FORMAT)) #server gửi thông báo kết thúc
        conn.close()
    s.close() #tắt server
    root.destroy()

def handleClient(conn, addr):
    while(True):
        try: # Bắt trường hợp client mất kết nối đột ngột
            option=conn.recv(1024).decode(FORMAT)
            if(option=="login"):
                client_Login(conn, addr)
            elif(option=="register"):
                client_Register(conn)
            elif(option=="quit"):
                client_Quit(conn,addr)
                break
            elif(option=="convert"):
                client_Convert(conn)
            elif(option=="ratetable"):
                client_Ratetable(conn)
            elif(option=="searchtable"):
                client_Searchtable(conn)
            elif(option=="logout"):
                client_Logout(conn,addr)
            index=0 #dùng vị trí để tham chiếu
            for information in Client_list:
                if(str(addr) in information):
                    Client_list[index]=information+" - "+option
                index+=1
            Update_active()
        except: # khi không thể nhận option vi client mat ket noi
            client_Quit(conn,addr)
            break
    
def startServer():
    s.bind((HOST, SERVER_PORT)) #Ràng buộc địa chỉ và số cổng tạo thành máy chủ
    s.listen()
    global data
    data=Get_data()
    insert_datafile(data)
    while (True):
        try: #nếu socket đóng thì k bị lỗi
            conn, addr = s.accept()
            Client_conn.append(conn)
            Insert_Thread(conn, addr)
        except:
            pass

def reset_data():
    start=time.time()# Biến để căn thời gian reset data
    while(True):
        if(time.time()-start>=1800): #Khi thời gian quá 1800 thì cập nhật lại dữ liệu khi client yêu cầu gì đó
            data=Get_data()
            insert_datafile(data)


def Login(textbox_acc,textbox_pass):
    acc=textbox_acc.get()
    passs=textbox_pass.get()
    if(acc=="admin" and passs=="admin"):
        Active_Screen.tkraise()
        button_logout=Button(Active_Screen,text="LOG OUT",font=('Arial',10,'bold'),bg="#007ACC",bd=3,width=10,command=Logout)   
        button_logout.place(x=265,y=360)
        serverThread = threading.Thread(target=startServer)
        serverThread.daemon = True #True thì khi chạy hết hàm main sẽ kết thúc các luồng, False là 1 luồng kết thúc main thì k ảnh hưởng với các luồng còn lại đang chạy
        serverThread.start()#Tạo luồng để server đứng đợi không đụng độ tkinter ở active screen
        Reset_data=threading.Thread(target=reset_data)
        Reset_data.daemon = True #True thì khi chạy hết hàm main sẽ kết thúc các luồng, False là 1 luồng kết thúc main thì k ảnh hưởng với các luồng còn lại đang chạy
        Reset_data.start()
    else:
        text_Error=Label(Login_Screen,text="Error! Please try again.",font=('Arial',9,'bold'),fg="#FF0000",bg="#B0E3F2")
        text_Error.place(x=275,y=255)

def Get_data():
    url="https://vapi.vnappmob.com/api/request_api_key?scope=exchange_rate" #link lấy api key
    apikey=requests.get(url).json()['results'] #Nhận api từ web
    headers = { "Authorization": "Bearer " + apikey } #Phần headers request
    data = requests.get('https://vapi.vnappmob.com/api/v2/exchange_rate/vcb', headers=headers).json()['results']#data là 1 list gồm nhiều dict, mỗi dict là 1 loại tiền
    return data

root=Tk()
root.title("Currency")
root.geometry("600x400")
root.iconbitmap("logo.ico")
back_ground=Image.open("money.jpg")
render=ImageTk.PhotoImage(back_ground.resize((600, 400)))

Login_Screen=Frame(root, width=600, height=400)
Login_Screen.pack()
Login_Screen.grid_propagate(0)#Giũ nguyên khung
img=Label(Login_Screen,image=render)
img.place(x=0,y=0)
name=Label(Login_Screen,text="Login for Server",fg="#1E1E1E",bd=2,bg="#9AB2BC")#bg là back_ground color
name.config(font=("Transformers Movie",30))
name.place(x=130,y=70)
text_Acount=Label(Login_Screen,text="Account:",font=('Arial',10,'bold'),fg="#1E1E1E")
text_Acount.place(x=210,y=160)
textbox_acc=Entry(Login_Screen,font=('Arial',10,'bold'), width=15)
textbox_acc.place(x=285,y=160)
text_Acount=Label(Login_Screen,text="Password:",font=('Arial',10,'bold'),fg="#1E1E1E")
text_Acount.place(x=210,y=190)
textbox_pass=Entry(Login_Screen,font=('Arial',10,'bold'), width=15)
textbox_pass.place(x=285,y=190)
button_login=Button(Login_Screen,text="LOG IN",font=('Arial',10,'bold'),bg="#007ACC",bd=3,width=10,command=lambda: Login(textbox_acc,textbox_pass))   
button_login.place(x=295,y=220)

############################
Active_Screen=Frame(root,bg="black",width=600, height=400)
Active_Screen.place(x=0,y=0)
Active_Screen.grid_propagate(0)
img=Label(Active_Screen,image=render)
img.place(x=0,y=0)
name1=Label(Active_Screen,text="ACTIVE ACCOUNT",fg="#1E1E1E",bd=2,bg="#9AB2BC")#bg là back_ground color
name1.config(font=("Transformers Movie",30))
name1.place(x=145,y=2)
text_area = ScrolledText(Active_Screen,width=58,height=19,font=('Arial',10,'bold'),bg="#EDE9DE")
text_area.place(x=90,y=50)

Login_Screen.tkraise()
root.mainloop()

