import socket
import threading
import random as r
import json
import mysql.connector as mysql
import traceback

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
cursor.execute("create table if not exists reports(report_id int auto_increment primary key, uid int not null, location varchar(100) not null, npa varchar(100) not null, taccd varchar(100) not null, status bool not null default true)")

def reg_login(uname, passwd):
    cursor.execute("select * from users where uname = %s and passwd = %s",(uname, passwd))
    result = cursor.fetchone()
    if result:
        return ["login_success", result[0]]
    else:
        uid = random_id()
        cursor.execute("insert into users values(%s ,%s ,%s )",(uid, uname, passwd))
        conn.commit()
        return ["register_success", uid]


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
    while True:
        num = r.randint(00000,100000)
        cursor.execute("select uid from users where uid = %s",(num,))
        if cursor.fetchone() is None:
            return num


def save_report(uid, location, npa, taccd, status=True):
    cursor.execute("insert into reports(uid, location, npa, taccd, status) values(%s, %s, %s, %s, %s)",(uid, location, npa, taccd, status))
    conn.commit()

def fetch_reports(uid):
    cursor.execute("select location, npa, taccd, status from reports where uid = %s order by report_id desc", (uid,))
    reports = cursor.fetchall()
    return reports

def handle(client, uid):
    try:
        while True:
            packet = recv_packet(client)
            if not packet:
                break
            packet_type = packet["type"]
            if packet_type == "new_report":
                location = packet["location"]
                npa = packet["npa"]
                taccd = packet["taccd"]
                save_report(uid,location,npa,taccd)
            elif packet_type == "view_reports":
                reports = fetch_reports(uid)
                send_packet(client, {"type":"reports", "reports":reports})
    except Exception as e:
        print(e)
        traceback.print_exc()
    finally:
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
            result = reg_login(uname, passwd)
            if result[0] == "login_success":
                uid = result[1]
                send_packet(client, {"type":result[0],"uid":uid})
                clients.append(client)
                userids.append(uid)
                print(clients)
                print(userids)
                handle_thread = threading.Thread(target=handle, args=(client, uid), daemon=True)
                handle_thread.start()
            elif result[0] == "register_success":
                uid = result[1]
                send_packet(client, {"type":result[0],"uid":uid})
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