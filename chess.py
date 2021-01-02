import tkinter as tk
from PIL import ImageTk, Image
import math

root = tk.Tk()
root.attributes('-fullscreen', 1)

startX = 38
startY = 42
pieceSize = 65

moving = False
whitesMove = True
promotion = False
promoteTo = ''
flipped = False

myImg = ImageTk.PhotoImage(Image.open("board0.png").resize((pieceSize*8, pieceSize*8)))
board = tk.Canvas(root, bg='white', width=pieceSize*8, height=pieceSize*8)
Canvas_Image = board.create_image(0,0, image=myImg, anchor="nw")
board.pack()

rook_black = ImageTk.PhotoImage(Image.open("rook_black.png").resize((pieceSize, pieceSize)))
king_black = ImageTk.PhotoImage(Image.open("king_black.png").resize((pieceSize, pieceSize)))
queen_black = ImageTk.PhotoImage(Image.open("queen_black.png").resize((pieceSize, pieceSize)))
bishop_black = ImageTk.PhotoImage(Image.open("bishop_black.png").resize((pieceSize, pieceSize)))
knight_black = ImageTk.PhotoImage(Image.open("knight_black.png").resize((pieceSize, pieceSize)))
pawn_black = ImageTk.PhotoImage(Image.open("pawn_black.png").resize((pieceSize, pieceSize)))

pieces_black = [rook_black, king_black, queen_black, bishop_black, knight_black, pawn_black]

rook_white = ImageTk.PhotoImage(Image.open("rook_white.png").resize((pieceSize, pieceSize)))
king_white = ImageTk.PhotoImage(Image.open("king_white.png").resize((pieceSize, pieceSize)))
queen_white = ImageTk.PhotoImage(Image.open("queen_white.png").resize((pieceSize, pieceSize)))
bishop_white = ImageTk.PhotoImage(Image.open("bishop_white.png").resize((pieceSize, pieceSize)))
knight_white = ImageTk.PhotoImage(Image.open("knight_white.png").resize((pieceSize, pieceSize)))
pawn_white = ImageTk.PhotoImage(Image.open("pawn_white.png").resize((pieceSize, pieceSize)))

pieces_white = [rook_white, king_white, queen_white, bishop_white, knight_white, pawn_white]

class Pieces:
	def __init__(self, x, y, isWhite):
		self.matrixX = x
		self.matrixY = y
		self.pixelPosX = x*pieceSize
		self.pixelPosY = y*pieceSize
		self.isWhite = isWhite
		self.isTaken = False
		self.movingThisPiece = False

	def show():
		pass

	@staticmethod
	def withInBounds(x, y):
		if(x >= 0 and x < 8 and y >= 0 and y < 8):
			return True
		return False

	def move(self, x, y):
		global whitesMove

		self.matrixX = x
		self.matrixY = y
		if(not flipped):
			self.pixelPosX = x*pieceSize
			self.pixelPosY = y*pieceSize
		else:
			self.pixelPosX = (7 - x)*pieceSize
			self.pixelPosY = (7 - y)*pieceSize

		self.show()
		whitesMove = not whitesMove
		self.movingThisPiece = False

	def attackingAllies(self, x, y):
		global curr_board
		attacking = curr_board.getPieceAt(x, y)
		if(attacking is not None):
			if(attacking.isWhite == self.isWhite):
				return True
		return False

	def moveThroughPieces(self, x, y):
		global curr_board

		stepDirectionX = x - self.matrixX
		if(stepDirectionX > 0):
			stepDirectionX = 1
		elif(stepDirectionX < 0):
			stepDirectionX = -1
		stepDirectionY = y - self.matrixY
		if(stepDirectionY > 0):
			stepDirectionY = 1
		elif(stepDirectionY < 0):
			stepDirectionY = -1
		tempPosX = self.matrixX 
		tempPosY = self.matrixY
		tempPosX += stepDirectionX
		tempPosY += stepDirectionY
		while(tempPosX != x or tempPosY != y):
			if(curr_board.getPieceAt(tempPosX, tempPosY) is not None):
				return True
			tempPosX += stepDirectionX
			tempPosY += stepDirectionY

		return False


class King(Pieces):
	def __init__(self, x, y, isWhite):
		super().__init__(x, y, isWhite)
		self.letter = 'K'
		self.piece = pieces_white[1] if self.isWhite else pieces_black[1] 
		self.image= board.create_image(self.pixelPosX, self.pixelPosY, image=self.piece, anchor='nw')
		self.hasMoved = False

	def show(self):
		global board
		board.delete(self.image)
		if(not self.isTaken):
			self.image= board.create_image(self.pixelPosX, self.pixelPosY, image=self.piece, anchor='nw')

	def canMove(self, x, y):
		if(not self.withInBounds(x, y) or self.attackingAllies(x, y) or self.isTaken):
			return False
		if(abs(x - self.matrixX) == 0 and abs(y - self.matrixY) == 0):
			return False
		if(abs(x - self.matrixX) <= 1 and abs(y - self.matrixY) <= 1):
			hasMoved = True
			return True
		if(not self.hasMoved and (abs(x - self.matrixX <= 2) and (y - self.matrixY) == 0)):
			hasMoved = True
			return True
		return False

class Rook(Pieces):
	def __init__(self, x, y, isWhite):
		super().__init__(x, y, isWhite)
		self.letter = 'R'
		self.piece = pieces_white[0] if self.isWhite else pieces_black[0]
		self.image= board.create_image(self.pixelPosX, self.pixelPosY, image=self.piece, anchor='nw')

	def show(self):
		global board
		board.delete(self.image)
		if(not self.isTaken):
			self.image= board.create_image(self.pixelPosX, self.pixelPosY, image=self.piece, anchor='nw')

	def canMove(self, x, y):
		if(not self.withInBounds(x, y) or self.attackingAllies(x, y) or self.isTaken):
			return False
		if(abs(x - self.matrixX) == 0 and abs(y - self.matrixY) == 0):
			return False
		if(x == self.matrixX or y == self.matrixY):
			if(self.moveThroughPieces(x, y)):
				return False
			return True
		return False

class Queen(Pieces):
	def __init__(self, x, y, isWhite):
		super().__init__(x, y, isWhite)
		self.letter = 'Q'
		self.piece = pieces_white[2] if self.isWhite else pieces_black[2]
		self.image= board.create_image(self.pixelPosX, self.pixelPosY, image=self.piece, anchor='nw')

	def show(self):
		global board
		board.delete(self.image)
		if(not self.isTaken):
			self.image= board.create_image(self.pixelPosX, self.pixelPosY, image=self.piece, anchor='nw')

	def canMove(self, x, y):
		if(not self.withInBounds(x, y) or self.attackingAllies(x, y) or self.isTaken):
			return False
		if(abs(x - self.matrixX) == 0 and abs(y - self.matrixY) == 0):
			return False
		if(x == self.matrixX or y == self.matrixY):
			if(self.moveThroughPieces(x, y)):
				return False
			return True
		if(abs(x - self.matrixX) == abs(y - self.matrixY)):
			if(self.moveThroughPieces(x, y)):
				return False
			return True
		return False

class Bishop(Pieces):
	def __init__(self, x, y, isWhite):
		super().__init__(x, y, isWhite)
		self.letter = 'B'
		self.piece = pieces_white[3] if self.isWhite else pieces_black[3]
		self.image= board.create_image(self.pixelPosX, self.pixelPosY, image=self.piece, anchor='nw')

	def show(self):
		global board
		board.delete(self.image)
		if(not self.isTaken):
			self.image= board.create_image(self.pixelPosX, self.pixelPosY, image=self.piece, anchor='nw')

	def canMove(self, x, y):
		if(not self.withInBounds(x, y) or self.attackingAllies(x, y) or self.isTaken):
			return False
		if(abs(x - self.matrixX) == 0 and abs(y - self.matrixY) == 0):
			return False
		if(abs(x - self.matrixX) == abs(y - self.matrixY)):
			if(self.moveThroughPieces(x, y)):
				return False
			return True
		return False

class Knight(Pieces):
	def __init__(self, x, y, isWhite):
		super().__init__(x, y, isWhite)
		self.letter = 'N'
		self.piece = pieces_white[4] if self.isWhite else pieces_black[4]
		self.image= board.create_image(self.pixelPosX, self.pixelPosY, image=self.piece, anchor='nw')

	def show(self):
		global board
		board.delete(self.image)
		if(not self.isTaken):
			self.image= board.create_image(self.pixelPosX, self.pixelPosY, image=self.piece, anchor='nw')

	def canMove(self, x, y):
		if(not self.withInBounds(x, y) or self.attackingAllies(x, y) or self.isTaken):
			return False
		if(abs(x - self.matrixX) == 0 and abs(y - self.matrixY) == 0):
			return False
		if((abs(x - self.matrixX) == 2 and abs(y - self.matrixY) == 1) or (abs(x - self.matrixX) == 1 and abs(y - self.matrixY) == 2)):
			return True
		return False


class Pawn(Pieces):
	def __init__(self, x, y, isWhite):
		super().__init__(x, y, isWhite)
		self.firstMove = True
		self.letter = chr(ord('a') + x)
		self.piece = pieces_white[5] if self.isWhite else pieces_black[5]
		self.image= board.create_image(self.pixelPosX, self.pixelPosY, image=self.piece, anchor='nw')

	def show(self):
		global board
		board.delete(self.image)
		if(not self.isTaken):
			self.image= board.create_image(self.pixelPosX, self.pixelPosY, image=self.piece, anchor='nw')

	def canMove(self, x, y):
		if(not self.withInBounds(x, y) or self.attackingAllies(x, y) or self.isTaken):
			return False
		if(abs(x - self.matrixX) == 0 and abs(y - self.matrixY) == 0):
			return False
		attacking = curr_board.getPieceAt(x, y)
		if(attacking is not None):
			if(abs(x - self.matrixX) == abs(y - self.matrixY) and ((self.isWhite is True and (y - self.matrixY) == -1) or (self.isWhite is False and (y - self.matrixY) == 1))):
				self.firstMove = False
				return True
			return False
		if(x != self.matrixX or y == self.matrixY):
			return False

		if((self.isWhite and (y - self.matrixY == -1)) or (not self.isWhite and (y - self.matrixY == 1))):
			self.firstMove = False
			return True

		if(self.firstMove and ((self.isWhite and (y - self.matrixY == -2)) or (not self.isWhite and (y - self.matrixY == 2)))):
			if(self.moveThroughPieces(x, y)):
				return False
			self.firstTurn = False
			return True
		return False


class Board:
	def __init__(self):
		self.whitePieces = []
		self.blackPieces = []
		self.setUpBoard()

	def setUpBoard(self):
		self.whitePieces.append(King(4, 7, True))
		self.whitePieces.append(Queen(3, 7, True))
		self.whitePieces.append(Bishop(2, 7, True))
		self.whitePieces.append(Bishop(5, 7, True))
		self.whitePieces.append(Knight(1, 7, True))
		self.whitePieces.append(Rook(0, 7, True))
		self.whitePieces.append(Knight(6, 7, True))
		self.whitePieces.append(Rook(7, 7, True))

		self.whitePieces.append(Pawn(4, 6, True))
		self.whitePieces.append(Pawn(3, 6, True))
		self.whitePieces.append(Pawn(2, 6, True))
		self.whitePieces.append(Pawn(5, 6, True))
		self.whitePieces.append(Pawn(1, 6, True))
		self.whitePieces.append(Pawn(0, 6, True))
		self.whitePieces.append(Pawn(6, 6, True))
		self.whitePieces.append(Pawn(7, 6, True))

		self.blackPieces.append(King(4, 0, False))
		self.blackPieces.append(Queen(3, 0, False))
		self.blackPieces.append(Bishop(2, 0, False))
		self.blackPieces.append(Bishop(5, 0, False))
		self.blackPieces.append(Knight(1, 0, False))
		self.blackPieces.append(Rook(0, 0, False))
		self.blackPieces.append(Knight(6, 0, False))
		self.blackPieces.append(Rook(7, 0, False))

		self.blackPieces.append(Pawn(4, 1, False))
		self.blackPieces.append(Pawn(3, 1, False))
		self.blackPieces.append(Pawn(2, 1, False))
		self.blackPieces.append(Pawn(5, 1, False))
		self.blackPieces.append(Pawn(1, 1, False))
		self.blackPieces.append(Pawn(0, 1, False))
		self.blackPieces.append(Pawn(6, 1, False))
		self.blackPieces.append(Pawn(7, 1, False))

	def show(self):
		for piece in self.whitePieces:
			piece.show()

		for piece in self.blackPieces:
			piece.show()


	def getPieceAt(self, x, y):
		for piece in self.whitePieces:
			if(not piece.isTaken and piece.matrixX == x and piece.matrixY == y):
				return piece
		for piece in self.blackPieces:
			if(not piece.isTaken and piece.matrixX == x and piece.matrixY == y):
				return piece
		return None

	def isPieceAt(self, x, y):
		for piece in self.whitePieces:
			if(not piece.isTaken and piece.matrixX == x and piece.matrixY == y):
				return True
		for piece in self.blackPieces:
			if(not piece.isTaken and piece.matrixX == x and piece.matrixY == y):
				return True
		return False

	def flipBoard(self):
		global flipped

		for pieceWhite, pieceBlack in zip(self.whitePieces, self.blackPieces):
			if(flipped):
				pieceWhite.pixelPosX = pieceWhite.matrixX*pieceSize
				pieceWhite.pixelPosY = pieceWhite.matrixY*pieceSize
				pieceBlack.pixelPosX = pieceBlack.matrixX*pieceSize
				pieceBlack.pixelPosY = pieceBlack.matrixY*pieceSize
			else:
				pieceWhite.pixelPosX = (7 - pieceWhite.matrixX)*pieceSize
				pieceWhite.pixelPosY = (7 - pieceWhite.matrixY)*pieceSize
				pieceBlack.pixelPosX = (7 - pieceBlack.matrixX)*pieceSize
				pieceBlack.pixelPosY = (7 - pieceBlack.matrixY)*pieceSize
		self.show()
		flipped = not flipped

	def destroy(self):
		for pieceWhite, pieceBlack in zip(self.whitePieces, self.blackPieces):
			pieceWhite.isTaken = True
			pieceBlack.isTaken = True
		self.show()
		self.whitePieces.clear()
		self.blackPieces.clear()


curr_board = Board()
curr_board.show()
movingPiece = Pieces(0, 0, True)

def moveTo(x, y):
	global moving
	global whitesMove
	global movingPiece
	global promotion
	global promoteTo
	global curr_board

	print(moving)

	if(not moving):
		movingPiece = curr_board.getPieceAt(x, y)
		myLabel.config(text="X = " + str(x) + " " + "Y = " + str(y) + " " + movingPiece.letter)
		if((movingPiece is not None) and (movingPiece.isWhite == whitesMove) and (movingPiece.isTaken is False)):
			movingPiece.movingThisPiece = True
		else:
			return
	else:
		for piece in (curr_board.whitePieces if whitesMove else curr_board.blackPieces):
			if(piece.movingThisPiece is True):
				if(piece.canMove(x, y) is True):
					attacking = curr_board.getPieceAt(x, y)
					if(attacking is not None):
						attacking.isTaken = True
						attacking.show()
						print(piece.letter + 'x' + chr(ord('a') + x) + str(8 - y))
					elif(isinstance(piece, Pawn)):
						print(piece.letter + str(8 - y))
					else:
						print(piece.letter + chr(ord('a') + x) + str(8 - y))

					if(promotion):
						piece.isTaken = True
						piece.show()
						newPiece = Pieces(x, y, whitesMove)
						if(promoteTo == 'Q'):
							newPiece = Queen(x, y, whitesMove)
						elif(promoteTo == 'B'):
							newPiece = Bishop(x, y, whitesMove)
						elif(promoteTo == 'R'):
							newPiece = Rook(x, y, whitesMove)
						elif(promoteTo == 'N'):
							newPiece = Knight(x, y, whitesMove)

						promotion = False
						promoteTo = ''
						if(whitesMove):
							curr_board.whitePieces.append(newPiece)
						else:
							curr_board.blackPieces.append(newPiece)

						newPiece.show()
						whitesMove = not whitesMove
						piece.movingThisPiece = False
						moving = not moving
						return

					if(isinstance(piece, Pawn)):
						piece.letter = chr(ord('a') + x)

					# piece.matrixX = x
					# piece.matrixY = y
					# piece.pixelPosX = x*pieceSize
					# piece.pixelPosY = y*pieceSize
					# piece.show()
					# whitesMove = not whitesMove
					# piece.movingThisPiece = False
					piece.move(x, y)
				else:
					piece.movingThisPiece = False
	moving = not moving

def move(event):
	x = math.floor(event.x/pieceSize)
	y = math.floor(event.y/pieceSize)
	if(flipped):
		x = 7 - x
		y = 7 - y
	moveTo(x, y)

def char_range(c1, c2):
    for c in range(ord(c1), ord(c2)+1):
        yield chr(c)

def isPawn(a):
	for c in char_range('a', 'h'):
		if(a == c):
			return True
	return False

moves = ["e4", "e5", "Nf3", "Nc6", "Bc4", "Bc5", "O-O", "Nf6", "Nc3", "O-O", "d3", "h6", "Nd5", "d6", "a3", "a5", "Bd2", "Be6", "b4", "axb4", "axb4", "Rxa1", "Qxa1", "Bxd5", "exd5", "Nxb4", "Bxb4", "Bxb4", "Bb3", "Qd7", "c3", "Bc5", "d4", "exd4", "cxd4", "Bb6", "Nd2", "Qf5", "Nc4", "Nxd5", "Ne3", "Qe6", "Bxd5", "Qd7", "Bxb7", "c5", "Bf3", "cxd4", "Nd5", "Bc5", "Qb1", "Qf5", "Be4", "Qd7", "Qd3", "Re8", "f3", "Re5", "Kh1", "Qb7", "Nf6+", "gxf6", "Bxb7", "Re3", "Qf5", "d3", "Qxf6", "d2", "Qxh6", "Re1", "Qg5+", "Kf8", "Qxd2", "Rxf1#"]
curr_index = -1
def forward():
	global curr_index
	global moving
	global whitesMove
	global promotion
	global promoteTo

	curr_index += 1
	if(curr_index == len(moves)):
		return
	notation = moves[curr_index]
	n = len(notation)

	if(notation[n-1] == '+' or notation[n-1] == '#'):
		notation = notation[:-1]
		n -= 1

	if(notation[n-2] == '='):
		promotion = True
		promoteTo = notation[n-1]
		notation = notation[:-2]
		n -= 2
	
	movingPieceLetter = notation[0]
	if(movingPieceLetter == 'O'):
		if(n == 3):
			if(curr_index % 2 == 0):
				moving = True
				curr_board.whitePieces[7].movingThisPiece = True
				moveTo(5, 7)
				moving = True
				whitesMove = True
				curr_board.whitePieces[0].movingThisPiece = True
				moveTo(6, 7)
			else:
				moving = True
				curr_board.blackPieces[7].movingThisPiece = True
				moveTo(5, 0)
				moving = True
				whitesMove = False
				curr_board.blackPieces[0].movingThisPiece = True
				moveTo(6, 0)
		else:
			if(curr_index % 2 == 0):
				moving = True
				curr_board.whitePieces[7].movingThisPiece = True
				moveTo(3, 7)
				moving = True
				whitesMove = True
				curr_board.whitePieces[0].movingThisPiece = True
				moveTo(2, 7)
			else:
				moving = True
				curr_board.blackPieces[7].movingThisPiece = True
				moveTo(3, 0)
				moving = True
				whitesMove = False
				curr_board.blackPieces[0].movingThisPiece = True
				moveTo(2, 0)
		return

	if(n == 2):
		moving = True
		x = ord(notation[0]) - 97
		y = 8 - int(notation[1])
		for piece in (curr_board.whitePieces if curr_index % 2 == 0 else curr_board.blackPieces):
			if(piece.letter == movingPieceLetter and piece.canMove(x, y)):
				piece.movingThisPiece = True
				moveTo(x, y)
				return
		
	elif(n == 3):
		moving = True
		x = ord(notation[1]) - 97
		y = 8 - int(notation[2])
		for piece in (curr_board.whitePieces if curr_index % 2 == 0 else curr_board.blackPieces):
			if(piece.letter == movingPieceLetter and piece.canMove(x, y)):
				piece.movingThisPiece = True
				moveTo(x, y)
				return
	
	elif(n == 4):
		moving = True
		x = ord(notation[2]) - 97
		y = 8 - int(notation[3])

		for piece in (curr_board.whitePieces if curr_index % 2 == 0 else curr_board.blackPieces):
			if(piece.letter == movingPieceLetter and piece.isTaken is False and piece.canMove(x, y)):
				if(notation[1] != 'x'):
					if(isPawn(notation[1])):
						if(piece.matrixX != (ord(notation[1]) - 97)):
							continue
					else:
						if((8 - int(notation[1])) != piece.matrixY):
							continue
				piece.movingThisPiece = True
				moveTo(x, y)
				return
		
def new():
	global curr_board
	global curr_index
	global moving
	global whitesMove
	global promotion
	global promoteTo
	global movingPiece
	global flipped

	curr_board.destroy()
	curr_board = Board()
	curr_board.show()
	curr_index = -1
	moving = False
	whitesMove = True
	promotion = False
	promoteTo = ''
	flipped = False
	movingPiece = Pieces(0, 0, True)

def flip():
	curr_board.flipBoard()

myLabel = tk.Label(root, text="")
board.bind('<Button-1>', move)
forward_button = tk.Button(root, text="->", command=forward)
new_button = tk.Button(root, text="New Game", command=new)
flip_button = tk.Button(root, text="Flip Board", command=flip)
myLabel.pack()
forward_button.pack()
flip_button.pack()
new_button.pack()
root.mainloop()