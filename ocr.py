import enum
import cnocr
from numpy import ndarray as Arr

ocr = cnocr.CnOcr()

def get_text(img: Arr) -> str:
	res = ocr.ocr(img)
	lst = sum(map(lambda tpl: tpl[0], res), start=[])
	return ''.join(lst)

def problem_strip(s: str) -> str:
	for i, c in enumerate(s):
		if ord(c) > 255 and c not in '心店、': # chinese char
			return s[i:]
	return ""