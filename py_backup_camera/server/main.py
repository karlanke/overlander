from .mock_camera import MockCamera
from typing import Dict
from fastapi import FastAPI, WebSocket
from fastapi.responses import FileResponse
import pathlib
import cv2
import gpiozero
from contextlib import contextmanager
import asyncio
import uuid

from .mock_relay import MockRelay
from .images import create_fake_file

path = pathlib.Path(__file__).parent.absolute()
app = FastAPI()

open_sockets: Dict[uuid.UUID, WebSocket] = {}

current_relay = None


@contextmanager
def get_hardware():
    try:
        # define a video capture object
        vid = cv2.VideoCapture(0)
        vid.set(cv2.CAP_PROP_BUFFERSIZE, 1)
    except Exception:
        vid = MockCamera()

    RELAY_PIN = 14

    # Triggered by the output pin going high: active_high=True
    # Initially off: initial_value=False
    global current_relay
    if not current_relay:
        try:
            current_relay = gpiozero.OutputDevice(RELAY_PIN, active_high=False, initial_value=False)
        except gpiozero.exc.BadPinFactory:
            current_relay = MockRelay()

    yield vid, current_relay

    # After the loop release the cap object
    vid.release()

    # and the relay
    current_relay = None

    try:
        # Destroy all the windows
        cv2.destroyAllWindows()
    except Exception:
        pass


@app.on_event('shutdown')
def shutdown():
    for socket in open_sockets:
        socket.close()


@app.get('/')
def index():
    return FileResponse(f'{path}/static/index.html', headers={'Cache-Control': 'no-cache'})


async def send_video_frame(vid: cv2.VideoCapture, websocket: WebSocket):
    ret, frame = vid.read()
    if not ret:
        print("No frame returned")
        with open(f'{path}/static/there-is-no-connected-camera-mac.jpg', 'rb') as f:
            img = f.read()
            await websocket.send_bytes(img)
    else:
        ret, img = cv2.imencode('.png', frame)
        await websocket.send_bytes(img.tobytes())


@app.websocket("/stream")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    id = uuid.uuid4()
    open_sockets[id] = websocket
    fake_png = create_fake_file()
    await websocket.send_bytes(fake_png.getvalue())
    fake_png.close()

    with get_hardware() as (vid, relay):
        read_task = asyncio.create_task(websocket.receive_text())

        while True:
            try:
                write_task = asyncio.create_task(send_video_frame(vid, websocket))

                done, pending = await asyncio.wait([read_task, write_task], return_when=asyncio.FIRST_COMPLETED)

                if read_task in done:
                    # if the read task is finished, process the result and start a new read and wait for the current write
                    # otherwise, the write is done and just loop again on the same read
                    result = read_task.result()
                    resource, action = tuple(result.split('|'))
                    if resource == 'light':
                        if action == 'on':
                            relay.on()
                        else:
                            relay.off()
                    read_task = asyncio.create_task(websocket.receive_text())
                    if pending:
                        await asyncio.wait(pending)

            except Exception as e:
                print(e)
                break

    print('Websocket disconnected')
    del open_sockets[id]
