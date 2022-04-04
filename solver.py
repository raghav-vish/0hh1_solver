import pyautogui
import time
import PIL.ImageGrab
import z3
import sys

size=int(sys.argv[1])

time.sleep(2)
start_positions={}
start_positions[4]=(834,487)
start_positions[6]=(959,493)
start_positions[8]=(1082,493)
start_positions[10]=(825,615)
start_positions[12]=(957,617)

click_positions={}
click_positions[4]=[[(720,320)]]
click_positions[6]=[[(695,300)]]
click_positions[8]=[[(680,285)]]
click_positions[10]=[[(675,275)]]
click_positions[12]=[[(670,275)]]
delta={}
delta[4]=150
delta[6]=105
delta[8]=80
delta[10]=62
delta[12]=52
for i in range(1,size):
	click_positions[size][0].append((click_positions[size][0][i-1][0]+delta[size], click_positions[size][0][i-1][1]))
for i in range(1,size):
	click_positions[size].append([])
	for j in range(size):
		click_positions[size][i].append((click_positions[size][i-1][j][0], click_positions[size][i-1][j][1]+delta[size]))

def read_from_screen():
	arr=[]
	p = PIL.ImageGrab.grab().load()
	for i in range(size):
		arr.append([])
		for j in range(size):
			c = p[click_positions[size][i][j][0], click_positions[size][i][j][1]]
			if(c==(0,89,190)):
				arr[i].append(1)
			elif(c==(255,213,0)):
				arr[i].append(0)
			else:
				arr[i].append(None)
	return arr

time.sleep(2)
pyautogui.click(start_positions[size][0], start_positions[size][1])
time.sleep(2)
puzzle = read_from_screen()

positions = [
	(x, y) for x in range(size) for y in range(size)
]

symbols = {
	(x, y): z3.Int("v{};{}".format(x, y)) for x, y in positions
}

rows = []
columns = []

for x in range(size):
	row = [symbols[x, y] for y in range(size)]
	rows.append(row)

for y in range(size):
	column = [symbols[x, y] for x in range(size)]
	columns.append(column)

rows_and_columns = rows + columns
solver = z3.Solver()

for x, y in positions:
	value = puzzle[x][y]

	if value is None:
		continue

	solver.add(symbols[x, y] == value)

for symbol in symbols.values():
	solver.add(z3.Or([symbol == 0, symbol == 1]))

for values in rows_and_columns:
	solver.add(z3.Sum(values) == size // 2)

for lines in [rows, columns]:
	solver.add(z3.Not(z3.Or([z3.And([a == b for a, b in zip(line_a, line_b)])
											for line_a in lines
											for line_b in lines
											if line_a != line_b])))

if size > 2:
	for window in rows_and_columns:
		for i in range(size - 2):
			a, b, c = window[i:i + 3]
			solver.add(z3.Not(z3.And([a == b, b == c])))

if solver.check() != z3.sat:
	print('Error')

model = solver.model()
result = {
	position: model.evaluate(symbol) for position, symbol in symbols.items()
}
solved_puzzle = [
	[result[x, y].as_long() for y in range(size)] for x in range(size)
]

for i in range(size):
	for j in range(size):
		if(solved_puzzle[i][j]!=puzzle[i][j]):
			if(solved_puzzle[i][j]==0):
				pyautogui.click(click_positions[size][i][j][0], click_positions[size][i][j][1])
			else:
				pyautogui.doubleClick(click_positions[size][i][j][0], click_positions[size][i][j][1])

# grey/blank - 42,42,42
# blue - 0, 89, 190
# yellow - 255, 213, 0

# 0 - yellow
# 1 - blue
