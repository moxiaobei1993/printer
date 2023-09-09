import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
from tkinterdnd2 import DND_FILES, TkinterDnD
import os,hashlib,webbrowser,paramiko
#设置默认路径
current_dir = os.path.dirname(os.path.abspath(__file__)) 
os.chdir(current_dir)
print(os.getcwd())

# root = tk.Tk()
root = TkinterDnD.Tk() #增加了拖拽支持
root.title("后台打印PDF")
icon = tk.PhotoImage(file='icon.png')
root.iconphoto(False, icon)

# # 标签
labels = [] 
labels.append(tk.Label(root, text="1.输入PDF地址").grid(row=0, column=0, sticky='w'))
labels.append(tk.Label(root, text="2.主机地址账号密码").grid(row=1, column=0, sticky='w'))
labels.append(tk.Label(root, text="3.选择打印机").grid(row=2, column=0, sticky='w'))
labels.append(tk.Label(root, text="4.打印机设置").grid(row=3, column=0, sticky='w'))
labels.append(tk.Label(root, text="5.打印份数").grid(row=4, column=0, sticky='w'))
labels.append(tk.Label(root, text="建议1份，多次打印，方便取消").grid(row=4, column=2, sticky='w', columnspan=2, rowspan=1))
labels.append(tk.Label(root, text="可拖拽PDF\n到此窗口").grid(row=1, column=4, sticky='w', columnspan=1, rowspan=2))
zhaugntai = tk.StringVar()
zhaugntai.set('请开始打印')
lb = tk.Label(root, textvariable=zhaugntai,fg='green').grid(row=5, column=1, sticky='w', columnspan=4, rowspan=1)


# 文本框
entry1 = tk.Entry(root,width=41) 
entry2 = tk.Entry(root,width=15)
entry3 = tk.Entry(root,width=12)
entry4 = tk.Entry(root,width=12,show="*")
entry5 = tk.Entry(root,width=12)
entry1.grid(row=0, column=1, sticky='w', columnspan=3)
entry2.grid(row=1, column=1, sticky='w')
entry3.grid(row=1, column=2, sticky='w')
entry4.grid(row=1, column=3, sticky='w')
entry5.grid(row=4, column=1, sticky='w')
# entry1.insert(0,'可拖拽')
entry2.insert(0,'192.168.1.108')
entry3.insert(0,'root')
entry4.insert(0,'自己输入密码')
entry5.insert(0,'1')

# 2个单选按钮
printers = tk.IntVar(value=1)
rb1 = tk.Radiobutton(root, text="brother", variable=printers, value=1).grid(row=2, column=1)  
rb2 = tk.Radiobutton(root, text="espon(双面即单面)", variable=printers, value=2).grid(row=2, column=2, columnspan=2)


# 3个单选按钮  
settings = tk.IntVar(value=1)
rb3 = tk.Radiobutton(root, text="双面打印", variable=settings, value=1).grid(row=3, column=1)  
rb4 = tk.Radiobutton(root, text="偶数页", variable=settings, value=2).grid(row=3, column=2)
rb5 = tk.Radiobutton(root, text="奇数页", variable=settings, value=3).grid(row=3, column=3)



# 选择文件按钮  
def select_file():
    filetypes = [('PDF Files', '*.pdf')]
    filename = filedialog.askopenfilename(filetypes=filetypes)
    entry1.delete(0, tk.END)
    entry1.insert(0, filename)
btn = tk.Button(root, text="选择文件", command=select_file).grid(row=0, column=4) 

# 拖拽选择文件， 
def handle_drop(event):
    file_path = event.data
    entry1.delete(0, tk.END)
    entry1.insert(0, file_path) if file_path.lower().endswith(".pdf") else entry1.insert(0, "请选择PDF文件")
# 设置整个UI窗口为拖拽区域
root.drop_target_register(DND_FILES)
root.dnd_bind('<<Drop>>', handle_drop)

# root.tk.call('tkdnd', 'bind', root, '<Drop>', get_file_path)

def read_ini():
    import configparser
    # 创建配置解析器对象
    config = configparser.ConfigParser()

    # 读取ini文件
    config.read('windows.ini', encoding='utf-8')

    # 获取配置项的值
    PDFname=config.get('config','PDFname')
    ssh = config.get('config','ssh')
    username = config.get('config','username')
    printer=int(config.get('config','printer'))
    number=int(config.get('config','number'))
    setting=int(config.get('config','setting'))
    #显示到UI上
    entry1.delete(0, "end")
    entry2.delete(0, "end")
    entry3.delete(0, "end")
    entry5.delete(0, "end")
    entry1.insert(0,PDFname)
    entry2.insert(0,ssh)
    entry3.insert(0,username)
    entry5.insert(0,number)
    printers.set(value=printer)
    settings.set(value=setting)

def write_ini():
    import configparser
    # 创建配置解析器对象
    config = configparser.ConfigParser()
    config.read("windows.ini", encoding='utf-8')
    # 获取控件的内容
    PDFname = str(entry1.get())
    ssh = entry2.get()
    username = entry3.get()
    number = str(entry5.get())
    printer = str(printers.get())
    setting = str(settings.get())
    config['config']['PDFname'] = PDFname
    config['config']['ssh'] = ssh
    config['config']['username'] = username
    config['config']['number'] = number
    config['config']['printer'] = printer
    config['config']['setting'] = setting

    with open('windows.ini', 'w', encoding='utf-8') as f:
        config.write(f)
btn3 = tk.Button(root, text="读配置", command=read_ini).grid(row=3, column=4) 
btn4 = tk.Button(root, text="写配置", command=write_ini).grid(row=4, column=4) 

def get_md5(file_path):
    md5_obj = hashlib.md5()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            md5_obj.update(chunk)
    return md5_obj.hexdigest()

def startPrint():
    # 获取控件的内容
    zhaugntai.set('开始打印')
    ssh = entry2.get()
    username = entry3.get()
    passwd = entry4.get()
    # print(passwd)
    PDFname = str(entry1.get())
    remoteFileName = "/root/"+os.path.basename(PDFname)
    number = str(entry5.get())
    printer = int(printers.get())
    setting = int(settings.get())
    if printer ==1:
        printerSelected = "Driverless_DCP-T725DW" #Armbian_DCP-T725DW
    elif printer ==2:
        printerSelected = "EPSON_3"
    if setting==1:
        pageSET =' '
        double = ' -o sides=two-sided-long-edge '
    elif setting==2: #偶数
        pageSET =' -o page-set=even '
        double = ' '
    elif setting==3: #奇数
        pageSET =' -o page-set=odd '
        double = ' '

    # 判断是否设置选择错误
    if (printer ==1 and setting==2 or setting==3) or (printer ==2 and setting==1 ):
        messagebox.showinfo('错误','brother要选择双面打印\nespon的双面打印就是单面，建议先打偶数页，再打奇数页')
        return
    

    # 这里写功能代码
    lp =  'lp -d '+ printerSelected +double+pageSET+' -o media=A4 -n ' +number +' -o fit-to-page '  + remoteFileName
    print(lp)


    # 创建 SSH 客户端对象
    ssh_client = paramiko.SSHClient()
    # 设置 SSH 客户端对象的安全策略
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    # 连接到远程服务器
    ssh_client.connect(hostname=ssh, username=username, password=passwd)
    #获取服务器PDF的md5
    stdin, stdout, stderr = ssh_client.exec_command( 'md5sum ' +remoteFileName)
    output = stdout.readlines()
    output.append('a') #为空的时候不能比较，添加一个a
    remote_md5 = output[0].split()[0] 
    # print(remote_md5)
    local_md5 = get_md5(PDFname) 
    # print(local_md5)
    if output == [] or remote_md5 != local_md5:
        zhaugntai.set('正在推送PDF到服务器，时长看PDF大小')
        # 创建 SFTP 客户端对象
        sftp_client = ssh_client.open_sftp()
        # 推送本地文件到远程服务器
        sftp_client.put(PDFname, remoteFileName)
        # 关闭 SFTP 客户端对象
        sftp_client.close()
    zhaugntai.set('推送完成正在打印')

    # 执行命令
    stdin, stdout, stderr = ssh_client.exec_command(lp)
    # 获取命令的输出
    output = stdout.readlines()
    zhaugntai.set(output)

    # 关闭 SSH 连接
    ssh_client.close()
    webbrowser.open("https://192.168.1.108:631/jobs/")


btn2 = tk.Button(root, text="开始打印", command=startPrint).grid(row=5, column=0) 

root.mainloop()


# nuitka --windows-disable-console --standalone --enable-plugin=tk-inter printer.py