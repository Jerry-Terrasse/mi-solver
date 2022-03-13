from typing import Union
import cv2
import numpy as np
from numpy import ndarray as Arr

class Rect:
	def __init__(self, tpl: tuple) -> None:
		self.x1 = float(tpl[0])
		self.y1 = float(tpl[1])
		self.x2 = float(tpl[2])
		self.y2 = float(tpl[3])
	@staticmethod
	def from_xywh(tpl: tuple) -> 'Rect':
		return Rect((tpl[0], tpl[1], tpl[0]+tpl[2], tpl[1]+tpl[3]))
	def __repr__(self) -> str:
		return f"Rect({self.x1}, {self.y1}, {self.x2}, {self.y2})"
	@property
	def p1_int(self) -> tuple:
		return (int(self.x1), int(self.y1))
	@property
	def p2_int(self) -> tuple:
		return (int(self.x2), int(self.y2))
	@property
	def p1(self) -> tuple:
		return (self.x1, self.y1)
	@property
	def p2(self) -> tuple:
		return (self.x2, self.y2)
	@property
	def center(self) -> tuple:
		return ((self.x1+self.x2) / 2, (self.y1+self.y2) / 2)

bg_color = ((250, 250, 250), (255, 255, 255))
red = (0, 0, 255)
W = int()
H = int()

def show(img: Arr) -> None:
	img = cv2.resize(img, (W//2, H//2))
	cv2.imshow("w", img)
	cv2.waitKey(0)
	cv2.destroyAllWindows()

def recognize(img: Arr) -> Union[None, tuple[Rect, list[Rect]]]:
	global W, H
	H, W = img.shape[:2]
	res_line: Union[None, Rect] = None
	res_choice: list[Rect] = []

	img = cv2.GaussianBlur(img, (5, 5), 5)
	mask = cv2.inRange(img, bg_color[0], bg_color[1])
	edges = cv2.Canny(mask, 120, 120)
	contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
	for contour in contours:
		if isChoice(contour):
			res_choice.append(Rect.from_xywh(cv2.boundingRect(contour)))
			continue
		if isLine(contour):
			res_line = Rect.from_xywh(cv2.boundingRect(contour))
			continue
	if res_line is None or len(res_choice) <= 1:
		return None
	res_choice = [choice for choice in res_choice if choice.y1 > res_line.y2]
	res_choice.sort(key=lambda rect: rect.y1)
	# for debug:
	if __name__ == '__main__':
		for box in [res_line]+res_choice:
			cv2.rectangle(img, box.p1_int, box.p2_int, red, thickness=2)
		show(img)
	return res_line, res_choice

def isLine(contour: Arr) -> bool:
	box = cv2.boundingRect(contour)
	x, y, w, h = box
	ratio = h / w
	return w > W/2 and ratio < 0.06

def isChoice(contour: Arr) -> bool:
	box = cv2.boundingRect(contour)
	x, y, w, h = box
	return h > H/20 and w > W*0.7 and y < H*0.85


if __name__ == '__main__':
	img = cv2.imread("bug.jpg")
	print(recognize(img))