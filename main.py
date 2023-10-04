# The server responds with mock data from files. (http://0.0.0.0:8000)

#-----------------------------------------------------
# pass range wirh header by...
# curl -o myfile.txt -r 0-2000 http://localhost:8000/items/5

# http://127.0.0.1:8000/api/userapps/v1/u/appidlist
# curl -X POST -d 'post body test' http://127.0.0.1:8000/api/userapps/v1/u/appidlist

# get response data file from Android device.
# adb pull /storage/emulated/0/Android/data/com.hhh.vvv.test/cache/dbgPayload


from fastapi import FastAPI,  Response,Header, Request, File
from fastapi.responses import FileResponse, StreamingResponse, PlainTextResponse
from typing import Optional
from typing import Annotated
import random, os, asyncio

import socket
hostname=socket.gethostname()
print('hostname:', hostname,'[', socket.gethostbyname(hostname),']')
print('work dir',os.getcwd())


app = FastAPI()


@app.exception_handler(Exception)
async def validation_exception_handler(request, exc):
    print(str(exc),request)
    return PlainTextResponse("Something went wrong", status_code=400)


# Set the path to the file you want to serve
fileName = 'SteamSetup.exe'
# file_path = '/D/Downloads/VC_redist.x64.exe'
file_path = f'D:\Downloads\{fileName}'
file_size = os.path.getsize(file_path)
headerFile = {
    'Content-Disposition': f'attachment; filename={fileName}',
    'Content-Length': str(file_size)
}

# Route that serves the file download
#@app.get("/download/0")
#async def download_file(request: Request):

@app.get("/download/{filename:path}")
async def download_file(filename: str,request: Request, response: Response):

    print('download:',filename)

    async def generate():
        with open(file_path, "rb") as file:
            # Set the chunk size to control how many bytes are sent at a time
            chunk_size = 1024
            bytes_sent = 0
            while True:
                # Read a chunk of data from the file
                data = file.read(chunk_size)
                if not data: break

                # Send the data to the client
                yield data

                if bytes_sent%300==0:
                    #print('sent',bytes_sent)
                    #await asyncio.sleep(0.3)  # Slow down the download speed by delaying the response
                    await asyncio.sleep(bytes_sent/1024/1024)


                # Update the bytes sent counter
                bytes_sent += len(data)

                # If we've sent a certain number of bytes, close the connection
                if bytes_sent >= 1024*1024*2 * 99999999:
                    # await asyncio.sleep(60*15)
                    #request.scope["stream"].close()
                    break

    return StreamingResponse(generate(), media_type='application/octet-stream') # use [filename] as the download file name.
    # return StreamingResponse(generate(), headers=headerFile, media_type='application/octet-stream') # use [fileName] as the download file name. (Content-Disposition: attachment; filename=SteamSetup.exe)


@app.post("/{route_path:path}")
@app.get("/{route_path:path}")
async def read_file(route_path: str, response: Response, request: Request):

    def hashCode(string):
        h = 0
        for char in string: h = 31 * h + ord(char)
        return h & 0xFFFFFFFF

    # Read the POST request body as a string
    body = await request.body()
    body_str = body.decode("utf-8")  # Assuming the content is UTF-8 encoded

    # Replace forward slashes with percent signs in the file name
    file_name = route_path.replace('/', '%')

    # Set the path to the file you want to read
    file_path = f'dbgPayload/{file_name}.{hashCode(body_str):x}.txt'
    print('route_path:',route_path, ', body_str:[', body_str, '], file=', file_path )

    if not os.path.exists(file_path):
        print(file_path, 'does not exist!')
        return

    # Read the first line of the file as the HTTP status code
    with open(file_path) as file:
        http_code = int(file.readline())

        # Read the rest of the file as the response body
        body = file.read()

    # Set the response status code and body
    #response.status_code = http_code
    #return body

    response.status_code = http_code
    return Response(content=body, media_type='application/json')

#@app.route("/{route_path:path}", methods=["POST", "GET"])
#async def read_file(route_path: str, request: Request):
#    # Replace any forward slashes with %
#    file_name = route_path.replace('/', ' %')

#    # Load the file and extract the HTTP status code and body
#    with open(file_name, "r") as file:
#        # Read the first line to get the HTTP status code
#        http_code = int(file.readline())

#        # Read the rest of the file to get the response body
#        body = file.read()

#    # Return the response with the HTTP status code and body
#    return PlainTextResponse(content=body, status_code=http_code)

















# test ---------------------------------(may not reachable)


@app.get("/download/1")
async def download_file(request: Request):

    # Simulate a failed download midway by randomly sending only a portion of the file
    file_size = os.path.getsize(file_path)
    range_start = 0
    range_end = random.randint(range_start, file_size)
    headers = {'Content-Range': f'bytes {range_start}-{range_end}/{file_size}'}
    headers.update(headerFile)
    print(headers)

    return FileResponse(file_path, headers=headers, media_type='application/octet-stream')



# Route that serves the file download
@app.get("/download")
async def download_file(request: Request):

    # Simulate a failed download midway by randomly sending only a portion of the file
    file_size = os.path.getsize(file_path)
    range_header = request.headers.get('Range', None)
    print('range_header:',range_header)
    if range_header is not None:
        range_start = int(range_header.split('-')[0])
        range_end = random.randint(range_start, file_size)
        headers = {'Content-Range': f'bytes {range_start}-{range_end}/{file_size}'}
        headers.update(headerFile)
        print(headers)

        return FileResponse(file_path, headers=headers, media_type='application/octet-stream')
    else:
        return FileResponse(file_path, media_type='application/octet-stream')




@app.get("/download/x")
#async def download_file(response: Response, range: Optional[str] = Header(None)): # AttributeError: 'coroutine' object has no attribute 'encode'
#async def download_file(response: Response, range: Optional[str] = None):
async def download_file(response: Request, range: Annotated[list[str] | None, Header()] = None):


    file_size = os.path.getsize(file_path)
    print('range:',range)

    # Parse the Range header, if present
    #if range:
    #    range_header = range.strip().lower()
    #    if not range_header.startswith("bytes="):
    #        range_header = ""
    #    else:
    #        range_header = range_header[6:]

    #    if range_header:
    #        range_parts = range_header.split("-")
    #        range_start = int(range_parts[0])
    #        range_end = min(int(range_parts[1]), file_size - 1)
    #    else:
    #        range_start = 0
    #        range_end = file_size - 1
    #else:
    #    # Simulate a failed download midway by randomly sending only a portion of the file
    #    range_start = 0
    #    range_end = random.randint(0, file_size - 1)

    range_start = 0
    range_end = file_size - 1

    headers = {
        "Content-Disposition": 'attachment; filename="myfile.txt"',
        "Content-Range": f"bytes {range_start}-{range_end}/{file_size}",
    }



async def send_file(response: Response):
    with open(file_path, "rb") as f:
        f.seek(range_start)
        buffer_size = 1024
        bytes_sent = 0
        while bytes_sent < (range_end - range_start + 1):
            chunk_size = min(buffer_size, range_end - range_start + 1 - bytes_sent)
            chunk = f.read(chunk_size)
            if not chunk:
                break
            await asyncio.sleep(1)  # Slow down the download speed by delaying the response
            response.body.write(chunk)
            response.body.flush()
            bytes_sent += len(chunk)
            if bytes_sent >= (range_end - range_start + 1):
                break

    response.status_code = 206 if range else 200
    response.headers.update(headers)
    response.raw_headers.append((b"Accept-Ranges", b"bytes"))

    return Response(content=send_file(response), media_type="application/octet-stream")



@app.get("/items/0")
async def read_items(x_token: Annotated[list[str] | None, Header()] = None):
    print('@0x_token', x_token)
    return {"X-Token values": x_token}

@app.get("/items/1")
async def read_items(strange_header: Annotated[str | None, Header(convert_underscores=False)] = None):
    print('@0strange_header', strange_header)
    return {"strange_header": strange_header}

@app.get("/items/2")
async def read_items(user_agent: Annotated[str | None, Header()] = None):
    print('@0user_agent', user_agent)
    return {"User-Agent": user_agent}

@app.get("/items/3")
async def read_items(range: Annotated[str | None, Header()] = None):
    print('@range', range)
    return {"range": range}

@app.get("/items/4")
async def read_items(response: Request, range: Annotated[list[str] | None, Header()] = None):
    print('@range', range, 'response' , response)
    return {"range": range}

@app.get("/items/5")
async def read_items(response: Response, range: Optional[str] = Header(None)):
    print('@range', range, 'response' , response)
    return {"range": range}









# -----------------------------------------------

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
