from PIL import ImageTk, Image
import tkinter as tk

#Fixed values
startX = 40
startY = 0
pieceSize = 50
padding = 5
fonstSize = 15

class PieceImage:
	def __init__(self, master):
		self.master = master
		self.backgroundImage = ImageTk.PhotoImage(Image.open("assets/101403-0.161844ff.jpg").resize((self.master.winfo_width(), self.master.winfo_height())))
		self.boardImage = ImageTk.PhotoImage(Image.open("assets/board0.png").resize((pieceSize*8, pieceSize*8)))
		self.pieces_black = []
		self.pieces_white = []
		self.initBlackPieces()
		self.initWhitePieces()

	def initBlackPieces(self):
		self.pieces_black.append(ImageTk.PhotoImage(Image.open("assets/pieces/rook_black.png").resize((pieceSize, pieceSize))))
		self.pieces_black.append(ImageTk.PhotoImage(Image.open("assets/pieces/king_black.png").resize((pieceSize, pieceSize))))
		self.pieces_black.append(ImageTk.PhotoImage(Image.open("assets/pieces/queen_black.png").resize((pieceSize, pieceSize))))
		self.pieces_black.append(ImageTk.PhotoImage(Image.open("assets/pieces/bishop_black.png").resize((pieceSize, pieceSize))))
		self.pieces_black.append(ImageTk.PhotoImage(Image.open("assets/pieces/knight_black.png").resize((pieceSize, pieceSize))))
		self.pieces_black.append(ImageTk.PhotoImage(Image.open("assets/pieces/pawn_black.png").resize((pieceSize, pieceSize))))

	def initWhitePieces(self):
		self.pieces_white.append(ImageTk.PhotoImage(Image.open("assets/pieces/rook_white.png").resize((pieceSize, pieceSize))))
		self.pieces_white.append(ImageTk.PhotoImage(Image.open("assets/pieces/king_white.png").resize((pieceSize, pieceSize))))
		self.pieces_white.append(ImageTk.PhotoImage(Image.open("assets/pieces/queen_white.png").resize((pieceSize, pieceSize))))
		self.pieces_white.append(ImageTk.PhotoImage(Image.open("assets/pieces/bishop_white.png").resize((pieceSize, pieceSize))))
		self.pieces_white.append(ImageTk.PhotoImage(Image.open("assets/pieces/knight_white.png").resize((pieceSize, pieceSize))))
		self.pieces_white.append(ImageTk.PhotoImage(Image.open("assets/pieces/pawn_white.png").resize((pieceSize, pieceSize))))

class BoardFrame:
	def __init__(self, master):
		self.master = master
		self.frame = tk.Frame(self.master, bg='#A0522D')
		self.canvas = tk.Canvas(self.frame, width=pieceSize*8 + startX, height=pieceSize*8 + startY)
		# self.init_canvas()
		self.place()

	def place(self):
		# self.frame.lift()
		self.frame.grid(row=0, column=0)
		self.canvas.grid(row=0, column=0, padx=padding, pady=padding)

class GameNotation:
	def __init__(self, master):
		self.master = master
		self.frame = tk.Frame(self.master)
		self.scrolledtext = tk.scrolledtext.ScrolledText(self.frame, state='disabled', width = 20, height=21, bg='#DCDCDC')
		self.scrolledtext['font'] = ('consolas', '12')
		self.last_tag = ''
		self.place()

	def place(self):
		self.frame.grid(row=0, column=1)
		self.scrolledtext.grid(row=0, column=0, sticky='nw', padx=padding, pady=padding)

	def changeGameNotation(self, moveNotation, callback):
		# global last_tag

		allmoves = ''
		moveNo = 1
		tag_count = 0
		self.scrolledtext.configure(state='normal')
		self.scrolledtext.delete(1.0, tk.END)

		for tag in self.scrolledtext.tag_names():
			self.scrolledtext.tag_delete(tag)

		for move in range(len(moveNotation)):
			allmoves = ''
			if(move % 2 == 0):
				if(moveNotation[move] != '1-0' and moveNotation[move] != '0-1' and moveNotation[move] != '1/2-1/2'):
					allmoves += str(moveNo) + ('.  ' if moveNo <= 9 else '. ')
				self.scrolledtext.insert(tk.END, allmoves)
				moveNo += 1

				allmoves = ''
				curr_tag = 'tag' + str(tag_count)
				left = 8 - len(moveNotation[move])
				allmoves = moveNotation[move]
				self.scrolledtext.insert(tk.END, allmoves, curr_tag)
				self.scrolledtext.insert(tk.END, (' ' * left))
			else:
				allmoves = moveNotation[move]
				curr_tag = 'tag' + str(tag_count)
				self.scrolledtext.insert(tk.END, allmoves, curr_tag)
				self.scrolledtext.insert(tk.END, '\n')

			self.scrolledtext.tag_bind(curr_tag, "<Button-1>", lambda event, tag = curr_tag, moveNo=moveNo-1: callback(event, tag, moveNo))
			tag_count += 1
		
		self.last_tag = 'tag' + str(tag_count - 1)
		self.scrolledtext.tag_config(self.last_tag, foreground="black", background='#ADD8E6', font=('bold'))
		self.scrolledtext.see(tk.END)
		self.scrolledtext.configure(state='disabled')

class AddOn:
	def __init__(self, master):
		self.master = master
		self.frame = tk.Frame(self.master)
		self.addonButtons = tk.Frame(self.frame)
		self.dbInfo = tk.scrolledtext.ScrolledText(self.frame, state='disabled', width = 40, height = 15)
		self.pgnText = tk.scrolledtext.ScrolledText(self.frame, width=40, height = 5)
		self.searchDbButton = tk.Button(self.frame, text='Search DB')
		self.loadPGN = tk.Button(self.addonButtons, text="Load PGN")
		self.generateFEN = tk.Button(self.addonButtons, text="Generate FEN")
		self.loadFEN = tk.Button(self.addonButtons, text="Load FEN")
		
		self.place()

	def place(self):
		self.frame.grid(row=0, column=2, sticky='nw', padx=padding, pady=padding)
		self.dbInfo.grid(row=0, column=0, padx=padding, pady=padding)
		self.searchDbButton.grid(row=1, column=0, padx=padding, pady=padding)
		self.pgnText.grid(row=2, column=0, padx=padding, pady=padding)
		self.addonButtons.grid(row=5, column=0)
		self.loadPGN.grid(row=0, column=0, padx=padding, pady=padding)
		self.loadFEN.grid(row=0, column=1, padx=padding, pady=padding)
		self.generateFEN.grid(row=0, column=2, padx=padding, pady=padding)

class EngineEvals:
	def __init__(self, master, lines=3):
		self.master = master
		self.frame = tk.Frame(self.master)
		self.lines = lines
		self.headers = self.init_header()
		self.evalLines = self.init_lines()
		self.place()

	def init_header(self):
		header0 = tk.Label(self.frame, text="Depth", anchor='w', width = 5, font=("Courier", fonstSize))
		header1 = tk.Label(self.frame, text="Score", anchor='w', width = 5, font=("Courier", fonstSize))
		header2 = tk.Label(self.frame, text="Line", anchor='w', width = 50, font=("Courier", fonstSize))

		return [header0, header1, header2]

	def init_lines(self):

		lines = []
		for each in range(0, self.lines):
			depth = tk.Label(self.frame, text='', anchor='w', width=5, font=("Courier", fonstSize))
			score = tk.Label(self.frame, text='', anchor='w', width = 5, font=("Courier", fonstSize))
			line = tk.Label(self.frame, text='',anchor='w', width = 50, font=("Courier", fonstSize))

			lines.append([depth, score, line])

		return lines

	def place(self):
		self.frame.grid(row=4, column=0)

		for head in range(0, len(self.headers)):
			self.headers[head].grid(row=0, column=head+1)

		for line in range(0, self.lines):
			self.evalLines[line][0].grid(row=line+1, column = 1) 
			self.evalLines[line][1].grid(row=line+1, column = 2) 
			self.evalLines[line][2].grid(row=line+1, column = 3) 


