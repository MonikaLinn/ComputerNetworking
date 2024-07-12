import argparse
import sys
import os
import time
import csv
import socket

def parse():
  parser = argparse.ArgumentParser(description='Get port numbers + directory')
  parser.add_argument('-p', type=int, help='Port number', required=True)
  parser.add_argument('-d', type=str, help='Directory path', required=True)
  return parser.parse_args()

def main():
  args = parse()
  port = args.p
  dir = args.d

  if 0 <= port <= 1023 and port != 80:
    print("Well-known port number ", port, " entered - could cause a conflict.\n", port, dir, file=sys.stdout) #format change for vm
  elif port == 80:
    print(port, dir)
  elif 1024 <= port <= 49151:
    print("Registered port number ", port, " entered - could cause a conflict.\n", port, dir, file=sys.stdout)
  else: 
    print("Terminating program, port number is not allowed.",file=sys.stderr)
    sys.exit(1) 

  file_types = { 
    "html": "text/html", #room for changing file types 
    "zip": "application/zip",
    "png": "image/png",
    "gif": "image/gif",
    "jpg": "image/jpeg",
    "jpeg": "image/jpeg",
    "csv": "text/csv",
    "txt": "text/plain",
    "doc": "application/msword",
    "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
  }

  root_dir = dir.split('/') #Find root directory

  with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as serverSocket:
    server_ip = "0.0.0.0"
    serverSocket.bind((server_ip, port))
    serverSocket.listen(1)
    print("Welcome socket created: {}, {}\n".format(server_ip, port))
    while True:
      connectionSocket, addr = serverSocket.accept()
      client_ip, client_port = connectionSocket.getpeername()
      sentence = connectionSocket.recv(1024).decode()
      print("Connection socket created: {}, {}\n".format(client_ip, client_port))
      if sentence: 
        sentence_parts = sentence.split('\r\n')
        method, fname, version = sentence_parts[0].split()
        print(fname) #the requested file name
        stat_error = 0

        file_parts = fname.split(".")

        if not os.path.exists("/" + root_dir[1]): #If root directory is not found throw error
          print("Error: Root Directory not found")
          sys.exit(1)

        if not os.path.exists(dir + fname):
          stat_error = 1
          status_line = ("HTTP/1.1 404 Not Found")
          cur_time = time.strftime("%a, %d %b %Y %H:%M:%S GMT", time.gmtime())

          header_lines = "{status_line}\r\nDate: {cur_time}\r\nConnection: close\r\n\r\n".format(
            status_line=status_line,
            cur_time=cur_time
          )

          connectionSocket.send(header_lines.encode())
          connectionSocket.close()
          byte_s = 0
          print("Connection to {}, {} is closed\n".format(client_ip, client_port))

        elif method != "GET":
          stat_error = 1
          status_line = ("HTTP/1.1 501 Not Implemented")
          cur_time = time.strftime("%a, %d %b %Y %H:%M:%S GMT", time.gmtime())

          header_lines = "{status_line}\r\nDate: {cur_time}\r\nConnection: close\r\n\r\n".format(
            status_line=status_line,
            cur_time=cur_time
          )

          connectionSocket.send(header_lines.encode())
          connectionSocket.close()
          byte_s = 0
          print("Connection to {}, {} is closed\n".format(client_ip, client_port))

        elif version != "HTTP/1.1":
          stat_error = 1
          status_line = ("HTTP/1.1 505 HTTP Version Not Supported")
          cur_time = time.strftime("%a, %d %b %Y %H:%M:%S GMT", time.gmtime())

          header_lines = "{status_line}\r\nDate: {cur_time}\r\nConnection: close\r\n\r\n".format(
            status_line=status_line,
            cur_time=cur_time
          )

          connectionSocket.send(header_lines.encode())
          connectionSocket.close()
          byte_s = 0
          print("Connection to {}, {} is closed\n".format(client_ip, client_port))

        if method == 'GET' and stat_error == 0:
          file = open(dir + fname, 'rb')
          type_f = 2
          content = file.read()

          status_line = ("HTTP/1.1 200 OK")
          content_length = os.path.getsize(dir + fname)
          content_type = file_types[file_parts[1]]
          get_time = os.path.getmtime(dir + fname)
          time_last = time.gmtime(get_time)
          last_modified = time.strftime("%a, %d %b %Y %H:%M:%S GMT", time_last)
          cur_time = time.strftime("%a, %d %b %Y %H:%M:%S GMT", time.gmtime())
          file.close()

          header_lines = "{status_line}\r\nContent-Length: {content_length}\r\nContent-Type: {content_type}\r\nDate: {cur_time}\r\nLast-Modified: {last_modified}\r\nConnection: close\r\n\r\n".format(
            status_line=status_line,
            content_length=content_length,
            content_type=content_type,
            cur_time=cur_time,
            last_modified=last_modified
          )

          response = header_lines.encode() + content #Get info ready to send
          connectionSocket.send(response) #Send info to webpage
          byte_s = content_length

          connectionSocket.close()
          print("Connection to {}, {} is closed\n".format(client_ip, client_port))
        
        csvfile = open('majitoSocketeOutput.csv', 'a', newline='\n')
        write = csv.writer(csvfile)
        write.writerow(["Client request server","4-Tuple:", server_ip, port, client_ip, client_port, "Requested URL", fname, status_line, "Bytes Sent:", byte_s ])
        csvfile.close()

        txtfile = open('majitoHTTPResponses.txt', 'a', newline = '\n')
        txtfile.write(header_lines)
        txtfile.close()

if __name__ == "__main__":
  main()
