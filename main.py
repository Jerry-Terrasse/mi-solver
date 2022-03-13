import cv2
from numpy import ndarray as Arr
import typing

from airtest.core import api as air

import recognizer as rcg
from recognizer import Rect
import ocr
import database
import utils
from utils import ST

fname = "screen.jpg"

def cut(img: Arr, r: Rect) -> Arr:
	return img[r.p1_int[1]: r.p2_int[1], r.p1_int[0]: r.p2_int[0]].copy()

def go_next(target=air.Template("templates/next.jpg")):
	if ST.quick_next:
		if ST.next_pos:
			air.touch(ST.next_pos)
		else:
			ST.next_pos = air.touch(target)
	else:
		air.touch(target)


def work():
	air.init_device("Android")
	db = database.load()
	fails = int() # times of unexpected failure
	guesses: list[str] = []
	if ST.log_answer:
		ST.log_cnt = int()

	while True:
		# get image
		air.snapshot(fname)
		img = cv2.imread(fname)
		boxes = rcg.recognize(img)
		if boxes is None:
			try:
				point = air.loop_find(air.Template("templates/finish.jpg", rgb=True), timeout=1)
			except air.TargetNotFoundError:
				fails += 1
				if fails > fail_thresh:
					break
				continue
			# air.touch(point)
			break
		line, choices_box = boxes
		
		# get text
		problem_box = Rect((line.x1, line.y1, choices_box[0].x2, choices_box[0].y1)) # problem is between the line and the first choice
		problem_img = cut(img, problem_box)
		choices_img = [cut(img, box) for box in choices_box]
		problem = ocr.get_text(problem_img)
		problem = ocr.problem_strip(problem)
		choices = [ocr.get_text(choice) for choice in choices_img]
		print(problem)
		print(choices)

		# search for answer
		P = database.Problem((problem, choices))
		status, answer = database.query(db, P)
		if status == 'manual' or status == 'undefined':
			print("!!!!!")
			input("waiting for manual operation...")
			if status == 'undefined':
				db[P.key] = P
		else:
			if status == 'guess':
				guesses.append(problem)
			# submit answer
			for i in range(P.n):
				if answer[i]:
					point = choices_box[i].center
					air.touch(point)
		if ST.log_answer:
			ST.log_cnt += 1
			air.snapshot(ST.log_path % (ST.log_cnt))
		go_next()
		air.sleep(1)
	database.save(db)
	print("Guesses:")
	for problem in guesses:
		print(problem)
				
fail_thresh = 10

if __name__ == '__main__':
	work()