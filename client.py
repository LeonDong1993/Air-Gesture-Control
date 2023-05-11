import cv2, pyautogui
import numpy as np
import socket, zlib
import time
import json

with open('config.json') as f:
	keymap = json.load(f)

print(keymap)
# Set up the client socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(('192.168.18.134', 8000))

ACTION = 1

def analysis_direction(history):

	def helper(sequence):
		slopes = np.diff(sequence)
		avg_grad = np.mean(slopes)
		return avg_grad

	l, x, y = list(zip(*history))
	dx = helper(x)
	dy = helper(y)
	if abs(dx) > abs(dy) + 5:
		if dx > 0:
			return 'left'
		else:
			return 'right'
	elif abs(dy) > abs(dx) +5:
		if dy > 0:
			return 'down'
		else:
			return 'up'

	return 'none'

def main():
	cap = cv2.VideoCapture(0)
	st = time.time()
	frames = 0

	history = []
	last_gesture = None
	last_gesture_count = 0
	special_gestures = {'fist'}
	last_detect = 1
	# a big value for init, not meaningful
	fps = 60

	while True:
		frames += 1
		# Capture an image from the camera
		ret, frame = cap.read()

		# Encode the image data as a JPEG image
		_, img_data = cv2.imencode('.jpg', frame)
		img_data = zlib.compress(img_data)

		# Send the length of the image data to the server
		img_len = len(img_data)
		client_socket.sendall(img_len.to_bytes(4, byteorder='big'))
		client_socket.sendall(img_data)

		# Received the detected information
		result_len = int.from_bytes(client_socket.recv(4), byteorder='big')
		result_str = b''
		while len(result_str) < result_len:
			packet = client_socket.recv(min(4096, result_len - len(result_str)))
			if not packet: break
			result_str += packet

		result = eval(result_str.decode())
		if len(result) > 0 :
			x1,y1,x2,y2,label = result
			x1 = int(x1)
			y1 = int(y1)
			x2 = int(x2)
			y2 = int(y2)
			cv2.rectangle(frame, (x1,y1), (x2,y2), (0,0,255), 2)
			cv2.putText(frame, label, (x1, y1), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 2)
			cx = (x1+x2) // 2
			cy = (y1+y2) // 2

			if label not in special_gestures:
				# standard gesture, do action if appear certain times
				if last_gesture is None:
					last_gesture = label
					last_gesture_count += 1
				elif last_gesture == label:
					last_gesture_count += 1
				else:
					last_gesture = label
					last_gesture_count = 1
			else:
				history.append([label, cx, cy])

			last_detect = frames

		else:
			# reset all history stat
			if frames - last_detect > fps * 2:
				history = []
				last_gesture = None
				last_gesture_count = 0

		# detect fix gesture
		if ACTION and last_gesture_count >= fps * 0.9:
			print('Detected gesture {}, execute action {}'.format(last_gesture, keymap[last_gesture]))
			pyautogui.hotkey( * keymap[last_gesture].split(',') )
			last_gesture = None
			last_gesture_count  = 0

		# detection movement gesture
		if ACTION and len(history) > fps * 1.2:
			direction = analysis_direction(history)
			history = []
			if direction != 'none':
				print('Detected moving {}, execute action {}'.format(direction, keymap[direction]))
				pyautogui.hotkey( * keymap[direction].split(',') )
			else:
				print('Gesture detected but no movement')

		# compute current fps and show on preview
		elapsed = time.time() - st
		fps = round(frames / elapsed, 1)
		cv2.putText(frame, 'fps:' + str(fps), (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,0,0), 2)

		cv2.imshow("Gesture", frame)
		if cv2.waitKey(1) == ord('q'):
			break

	# Release the camera and close the connection to the server
	cap.release()
	client_socket.close()


if __name__ == '__main__':
	if not ACTION:
		print('Action disabled for gesture demo!')
	main()

