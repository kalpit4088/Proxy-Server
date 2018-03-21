# Assignment 2 - Proxy Server
An HTTP proxy server implemented via python socket programming with caching

## Authors
1. Kalpit Pokra - 20161134
2. Kanav Gupta - 20161151

## State Diagram for Proxy Server

![State Diagram](https://www.codeproject.com/KB/web-cache/ExploringCaching/cache_array.jpg)

## Description
- `proxy.py` is the main proxy file
- Proxy runs on some specific ports, some ports are reserved for clients and some for servers
- `end_systems` folder contains the server and the client codes
	- Client keeps asking any file [1-10].data/txt from server by GET or POST method
	- Server listens to specified port and serves any file as asked
- Proxy works as middleman between the server and client and it does caching, authentication, etc
- Only GET requests are handled

## Features
- Receives the request from client and pass it to the server after necessary parsing
- Cache has limited size, so if the cache is full and proxy wants to store another response then it removes the least recently asked cached response. Cache limit can be set by setting up the constant in *proxy.py* file

## How to run

#### Proxy
- `python proxy.py` to run proxy server on port 12345

#### Server
- run server in *end_systems/server/* directory

- `python server.py` to run server on port 20000


## Screenshots

- Browser Responses

![Response 1](./Screenshots/1.png)


![Response 2](./Screenshots/2.png)



