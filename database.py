import csv
import difflib
from typing import Union
import utils
from utils import ST

class Problem:
	def __init__(self, arg: Union[tuple, dict]) -> None:
		self.key = ""
		self.problem = ""
		self.n = 0
		self.status = 'undefined'
		self.choices = ["slot"] * 4
		self.select = [False] * 4
		if isinstance(arg, tuple):
			self.problem = arg[0]
			self.key = self.problem[5: 10] if len(self.problem) >= 10 else "nokey"
			self.n = len(arg[1])
			for i, choice in enumerate(arg[1]):
				self.choices[i] = choice
		if isinstance(arg, dict):
			self.key = arg['key']
			self.problem = arg['problem']
			self.n = int(arg['n'])
			self.status = arg['status']
			for i in range(4):
				self.choices[i] = arg[f'choice_{i}']
				self.select[i] = arg[f'select_{i}'] == '1'
	def to_dict(self) -> dict[str, str]:
		res = {
			'key': self.key,
			'problem': self.problem,
			'n': str(self.n),
			'status': self.status
		}
		for i in range(4):
			res[f'choice_{i}'] = self.choices[i]
			res[f'select_{i}'] = '1' if self.select[i] else '0'
		return res

def load(filename: str = '') -> dict[str, Problem]:
	db = {}
	with open(fname if filename == '' else filename, 'r', newline='') as csvfile:
		reader = csv.DictReader(csvfile)
		for row in reader:
			db[row['key']] = Problem(row)
	return db

def save(db: dict[str, Problem]) -> None:
	with open(fname_, 'w', newline='') as csvfile:
		writer = csv.DictWriter(csvfile, field)
		writer.writeheader()
		for row in db.values():
			writer.writerow(row.to_dict())

def query(db: dict[str, Problem], P: Problem) -> tuple[str, list[bool]]:
	key = P.key
	known = None
	if key in db:
		known = db[key]
	elif ST.drop:
		matcher = difflib.SequenceMatcher()
		matcher.set_seq1(P.problem)
		for data in db.values():
			matcher.set_seq2(data.problem)
			ratio = matcher.quick_ratio()
			if ratio > ST.problem_thresh:
				print("drop success.")
				known = data
				break
		else:
			print("drop fail.")
	if known is None:#or known.status == 'undefined':
		return 'undefined', []
	if known.status == 'manual':
		return 'manual', []
	if ST.debug:
		print(known.problem)
		print(known.choices)
	# then match the choices
	answer: list[bool] = []
	matcher = difflib.SequenceMatcher()
	def get_ratio(s: str) -> float:
		matcher.set_seq2(s)
		return matcher.quick_ratio()
	for i in range(P.n):
		choice = P.choices[i]
		matcher.set_seq1(choice)
		ratios = [get_ratio(choice) for choice in known.choices]
		idx = ratios.index(max(ratios))
		answer.append(known.select[idx])
	return known.status, answer


field = ['key', 'problem', 'n', 'status'] + [f'{prefix}_{i}' for i in range(4) for prefix in ('choice', 'select')]
fname = "database.csv"
fname_ = "database_.csv"