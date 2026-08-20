import socket
import threading
import random as r
import json
import mysql.connector as mysql

HOST = "127.0.0.1"
SERVER_HOST = "127.0.0.1"
PORT = 4848

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen()

clients = []
userids = [] 

conn = mysql.connect(
    host = SERVER_HOST,
    user = "root",
    passwd = "root"
)

cursor = conn.cursor(buffered=True)

cursor.execute("create database if not exists resq")
cursor.execute("use resq")
cursor.execute("create table if not exists users(uid int primary key, uname varchar(50) not null, passwd varchar(50) not null)")
cursor.execute("create table if not exists reports(uid int primary key, location varchar(100) not null, npa varchar(100) not null, taccd varchar(100) not null)")

def reg_login(uid, uname, passwd):
    result = cursor.execute("select * from users where uid = %s and uname = %s and passwd = %s",(uid, uname, passwd))
    if result:
        return "login_success"
    else:
        cursor.execute("insert into users values(%s ,%s ,%s )",(uid, uname, passwd))
        conn.commit()
        return "register_success"

def recv_exact(sock, size):
    data = b""
    while len(data) < size:
        chunk = sock.recv(size - len(data))
        if not chunk:
            return None
        data += chunk
    return data


def send_packet(sock, packet):
    data = json.dumps(packet).encode()
    length = len(data).to_bytes(4, "big")
    sock.sendall(length + data)


def recv_packet(sock):
    header = recv_exact(sock, 4)

    if not header:
        return None

    length = int.from_bytes(header, "big")
    data = recv_exact(sock, length)

    if not data:
        return None

    return json.loads(data.decode())

def random_id():
    num = r.randint(00000,100000)
    while num in userids:
        num = r.randint(00000,100000)

    return num

def save_report(uid, location, npa, taccd):
    cursor.execute("insert into reports values(%s, %s, %s, %s) where uid = %s",(uid, location, npa, taccd, uid))
    conn.commit()

def fetch_reports(uid):
    cursor.execute("select * from report where uid = %s", (uid,))
    reports = cursor.fetchall()
    return reports

def handle(client, uid):
    try:
        while True:
            packet = recv_packet(client)
            if not packet:
                None
            packet_type = packet["type"]
            if packet_type == "new_report":
                location = packet["location"]
                npa = packet["npa"]
                taccd = packet["taccd"]
                save_report(uid,location,npa,taccd)
            elif packet_type == "view_reports":
                reports = fetch_reports(uid)
                send_packet(client, {"type":"reports", "reports":reports})
    except:
        if client in clients:
            index = clients.index(client)
            clients.pop(index)
            userids.pop(index)
        client.close()

def recv():
    while True:
        try:
            client, address = server.accept()
            print(f"connected client at {address}")
            login_data = recv_packet(client) 
            if not login_data:
                    client.close()
                    break
            uname = login_data["uname"]
            passwd = login_data["passwd"]
            print(f"uname:  {uname}\npasswd:  {passwd}")
            result = reg_login(uid, uname, passwd)
            send_packet(client, {"type":result,"uid":uid})
            uid = random_id()
            clients.append(client)
            userids.append(uid)
            print(clients)
            print(userids)
            handle_thread = threading.Thread(target=handle, args=(client, uid), daemon=True)
            handle_thread.start()
        except Exception as e:
            print(f"Error: {e}")

print("server is running...")
recv()