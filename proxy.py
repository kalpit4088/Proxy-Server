import socket
import os
import time                
import sys

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
          
host = ""
ports = 12345
CACHE_DIR = "./db"
dirname = "./db/"
#server binds to port 12345

if not os.path.isdir(CACHE_DIR):
    os.makedirs(CACHE_DIR)
    print 'created cache database'
try:
    s.bind((host, ports))
except:
    print('Binding Error')
    sys.exit(2)

s.listen(5)

print('Proxy server listening at 12345')

while True:

    #the caching array
    cache = []
    try:
        with open("cache", "r") as cache_var:
            cache = [w.strip() for w in cache_var.readlines()]
    except:
        print "Cache doesn't exist"

    print '\ncache = ', cache

    #setting up client
    r = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
    r.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)

    #server accepting connection from browser
    conn, addr = s.accept()

    #receiving request from browser
    data = conn.recv(1024)
    try:
        first_line = data.split('\n')[0]
        url = data.split(' ')[1]

        http_pos = url.find("://")     # find pos of http
        if http_pos == -1:
            temp = url
        else:
            temp = url[(http_pos+3):]

        port_pos = temp.find(":")

        webserver_pos = temp.find("/")

        if webserver_pos == -1:
            webserver_pos = len(temp)
        webserver = ""
        port = -1

        port = int((temp[(port_pos+1):])[:webserver_pos - port_pos - 1])
        webserver = temp[:port_pos]

    except Exception, e:
        pass

    print(url)
    data = data.decode('utf-8')

    #filtering all other requests
    if "localhost" != str(webserver) and  "127.0.0.1" != str(webserver) and "0.0.0.0" != str(webserver):
        continue

    #client connects to main server
    try:
        r.connect((host, port))
    except Exception as e:
        print 'Server error while connecting' 
        time.sleep(5)

    #getting the file name
    temp1 = data.split( )[1]
    filename = temp1.split("/")[3]

    if filename in cache:
        print(filename + " in cache")

        #generate request with If-Modified-Since header
        if_header = 'If-Modified-Since: ' + time.strftime("%a %b %d %H:%M:%S %Y", time.strptime(time.ctime(os.path.getmtime(dirname + filename)), "%a %b %d %H:%M:%S %Y")) + '\r\n\r\n'
        if_request = data[:-2] + if_header
        if_request = if_request.replace("http://" + webserver + ":" + str(port), "")

        #sending request to main server
        r.send(bytearray(if_request, 'utf-8'))

        #recieving if response from main server
        if_response = b''
        while True:
            packet = r.recv(1024)
            if not packet:
                break
            if_response += packet
        temporary = if_response[:228].decode('utf-8')
        response_code = temporary.split(' ')[1]

        #Not modified
        if response_code == "304":
            print("Not Modified")
            #open file in cache
            try:
                with open(dirname + filename, "rb") as f:
                    cache_response = f.read()
            except Exception as e:
                print("Error opening the file from cache")
                cache.remove(dirname + filename)

            #send response to browser
            conn.send(cache_response)

        #Modified
        elif response_code == "200":
            print("Modified")
            #update file in cache
            try:
                with open(dirname + filename, "wb") as f:
                    f.write(if_response)
            except Exception as e:
                print("Error opening the file from cache")
                cache.remove(dirname + filename)

            #send response to browser
            conn.send(if_response)

    else:
        print(filename + " not in cache")

        #forwarding request to main server
        request = data.replace("http://" + webserver + ":" + str(port), "")
        r.send(bytearray(request, 'utf-8'))

        #recieving response from main server
        response = b''
        while True:
            packet = r.recv(1024)
            if not packet:
                break
            response += packet

        #storing new file into cache
        if filename != '':
            #cache length is maxinmum of 3
            if len(cache) >= 3:
                cache.append(filename)
                temp_file = cache[0]
                cache.remove(temp_file)

                #remove the old file from the directory

                try:
                    os.remove(dirname + temp_file)
                except Exception as e:
                    print("ERROR: " + temp_file + " does not exist")

            else:
                cache.append(filename)

            #create new file for new entry in cache
            with open(dirname + filename, "wb") as new_file:
                new_file.write(response)

        #send response to browser
        conn.send(response)

    #update cache file with new entries
    with open("cache", "w") as cache_var:
        cache_list = "\n".join(cache)
        cache_var.write(cache_list)

    #close the server connection and client connection
    conn.close()
    r.close()
