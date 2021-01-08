import tkinter as tk
import tkinter.scrolledtext as scrolledtext
from PIL import ImageTk, Image
import math
import subprocess as sb
import time

root = tk.Tk()
# root.attributes('-fullscreen', 1)
root.state('zoomed')

startX = 38
startY = 42
pieceSize = 65

whitesMove = True
promotion = False
flipped = False
castlingShort = False
castlingLong = False
movingPiece = None
moveNotation = []
LAN = ''
againstAI = False
promotionWin = None

def char_range(c1, c2):
    for c in range(ord(c1), ord(c2)+1):
        yield chr(c)

myImg = ImageTk.PhotoImage(Image.open("board0.png").resize((pieceSize*8, pieceSize*8)))
displayBoard = tk.Canvas(root, bg='white', width=pieceSize*8, height=pieceSize*8)
Canvas_Image = displayBoard.create_image(0,0, image=myImg, anchor="nw")
displayBoard.grid(row=0, column=0)

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
		self.hasMoved = False

	def show():
		pass

	def clone(self):
		pass

	@staticmethod
	def withInBounds(x, y):
		if(x >= 0 and x < 8 and y >= 0 and y < 8):
			return True
		return False

	def move(self, x, y):
		global whitesMove

		self.hasMoved = True
		if(isPawn(self.letter)):
			if((self.isWhite and y == 0) or (not self.isWhite and y == 7)):
				popup_bonus(self, x, y)

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

	def attackingAllies(self, x, y, board):
		attacking = board.getPieceAt(x, y)
		if(attacking is not None):
			if(attacking.isWhite == self.isWhite):
				return True
		return False

	def moveThroughPieces(self, x, y, board):

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
			if(board.getPieceAt(tempPosX, tempPosY) is not None):
				return True
			tempPosX += stepDirectionX
			tempPosY += stepDirectionY

		return False


class King(Pieces):
	def __init__(self, x, y, isWhite):
		super().__init__(x, y, isWhite)
		self.letter = 'K'
		self.piece = pieces_white[1] if self.isWhite else pieces_black[1] 
		self.image= displayBoard.create_image(self.pixelPosX, self.pixelPosY, image=self.piece, anchor='nw')
	
	def show(self, anchorPos= None, pixelPosX= None, pixelPosY= None):
		displayBoard.delete(self.image)
		if(not self.isTaken):
			self.image= displayBoard.create_image(self.pixelPosX if pixelPosX is None else pixelPosX, self.pixelPosY if pixelPosY is None else pixelPosY, image=self.piece, anchor='nw' if anchorPos is None else anchorPos)

	def canMove(self, x, y, board):
		global castlingShort
		global castlingLong

		if(not self.withInBounds(x, y) or self.attackingAllies(x, y, board) or self.isTaken):
			return False
		if(abs(x - self.matrixX) == 0 and abs(y - self.matrixY) == 0):
			return False
		if(abs(x - self.matrixX) <= 1 and abs(y - self.matrixY) <= 1):
			return True
		#castling
		if(not self.hasMoved and (y - self.matrixY) == 0) and (abs(x - self.matrixX <= 2)):
			if(x - self.matrixX == 2):
				#shortcastle
				tempY = 7 if self.isWhite else 0
				for piece in board.blackPieces if self.isWhite else board.whitePieces:
					if(not piece.isTaken and (piece.canMove(5, tempY, board) or piece.canMove(6, tempY, board) or board.isPieceAt(5, tempY))):
						return False
				for piece in board.whitePieces if self.isWhite else board.blackPieces:
					if(not piece.isTaken and piece.letter == 'R' and piece.isRight is True and piece.hasMoved is False):
						castlingShort = True
						return True
			elif(x - self.matrixX == -2):
				#long castle
				tempY = 7 if self.isWhite else 0
				for piece in board.blackPieces if self.isWhite else board.whitePieces:
					if(not piece.isTaken and (piece.canMove(2, tempY, board) or piece.canMove(3, tempY, board) or board.isPieceAt(3, tempY))):
						return False
				for piece in board.whitePieces if self.isWhite else board.blackPieces:
					if(not piece.isTaken and piece.letter == 'R' and piece.isRight is False and piece.hasMoved is False):
						castlingLong = True
						return True		
		return False

	def clone(self):
		cloneObj = King(self.matrixX, self.matrixY, self.isWhite)
		cloneObj.isTaken = self.isTaken
		cloneObj.movingThisPiece = self.movingThisPiece
		cloneObj.hasMoved = self.hasMoved
		return cloneObj

class Rook(Pieces):
	def __init__(self, x, y, isWhite):
		super().__init__(x, y, isWhite)
		self.isRight = True if x == 7 else False
		self.letter = 'R'
		self.piece = pieces_white[0] if self.isWhite else pieces_black[0]
		self.image= displayBoard.create_image(self.pixelPosX, self.pixelPosY, image=self.piece, anchor='nw')

	def show(self, anchorPos = None, pixelPosX= None, pixelPosY= None):
		displayBoard.delete(self.image)
		if(not self.isTaken):
			self.image= displayBoard.create_image(self.pixelPosX if pixelPosX is None else pixelPosX, self.pixelPosY if pixelPosY is None else pixelPosY, image=self.piece, anchor='nw' if anchorPos is None else anchorPos)

	def canMove(self, x, y, board):
		if(not self.withInBounds(x, y) or self.attackingAllies(x, y, board) or self.isTaken):
			return False
		if(abs(x - self.matrixX) == 0 and abs(y - self.matrixY) == 0):
			return False
		if(x == self.matrixX or y == self.matrixY):
			if(self.moveThroughPieces(x, y, board)):
				return False
			return True
		return False

	def clone(self):
		cloneObj = Rook(self.matrixX, self.matrixY, self.isWhite)
		cloneObj.isTaken = self.isTaken
		cloneObj.movingThisPiece = self.movingThisPiece
		cloneObj.hasMoved = self.hasMoved
		return cloneObj

class Queen(Pieces):
	def __init__(self, x, y, isWhite):
		super().__init__(x, y, isWhite)
		self.letter = 'Q'
		self.piece = pieces_white[2] if self.isWhite else pieces_black[2]
		self.image= displayBoard.create_image(self.pixelPosX, self.pixelPosY, image=self.piece, anchor='nw')

	def show(self, anchorPos= None, pixelPosX= None, pixelPosY= None):
		displayBoard.delete(self.image)
		if(not self.isTaken):
			self.image= displayBoard.create_image(self.pixelPosX if pixelPosX is None else pixelPosX, self.pixelPosY if pixelPosY is None else pixelPosY, image=self.piece, anchor='nw' if anchorPos is None else anchorPos)

	def canMove(self, x, y, board):
		if(not self.withInBounds(x, y) or self.attackingAllies(x, y, board) or self.isTaken):
			return False
		if(abs(x - self.matrixX) == 0 and abs(y - self.matrixY) == 0):
			return False
		if(x == self.matrixX or y == self.matrixY):
			if(self.moveThroughPieces(x, y, board)):
				return False
			return True
		if(abs(x - self.matrixX) == abs(y - self.matrixY)):
			if(self.moveThroughPieces(x, y, board)):
				return False
			return True
		return False

	def clone(self):
		cloneObj = Queen(self.matrixX, self.matrixY, self.isWhite)
		cloneObj.isTaken = self.isTaken
		cloneObj.hasMoved = self.hasMoved
		cloneObj.movingThisPiece = self.movingThisPiece
		return cloneObj

class Bishop(Pieces):
	def __init__(self, x, y, isWhite):
		super().__init__(x, y, isWhite)
		self.letter = 'B'
		self.piece = pieces_white[3] if self.isWhite else pieces_black[3]
		self.image= displayBoard.create_image(self.pixelPosX, self.pixelPosY, image=self.piece, anchor='nw')

	def show(self, anchorPos= None, pixelPosX= None, pixelPosY= None):
		displayBoard.delete(self.image)
		if(not self.isTaken):
			self.image= displayBoard.create_image(self.pixelPosX if pixelPosX is None else pixelPosX, self.pixelPosY if pixelPosY is None else pixelPosY, image=self.piece, anchor='nw' if anchorPos is None else anchorPos)

	def canMove(self, x, y, board):
		if(not self.withInBounds(x, y) or self.attackingAllies(x, y, board) or self.isTaken):
			return False
		if(abs(x - self.matrixX) == 0 and abs(y - self.matrixY) == 0):
			return False
		if(abs(x - self.matrixX) == abs(y - self.matrixY)):
			if(self.moveThroughPieces(x, y, board)):
				return False
			return True
		return False

	def clone(self):
		cloneObj = Bishop(self.matrixX, self.matrixY, self.isWhite)
		cloneObj.isTaken = self.isTaken
		cloneObj.hasMoved = self.hasMoved
		cloneObj.movingThisPiece = self.movingThisPiece
		return cloneObj

class Knight(Pieces):
	def __init__(self, x, y, isWhite):
		super().__init__(x, y, isWhite)
		self.letter = 'N'
		self.piece = pieces_white[4] if self.isWhite else pieces_black[4]
		self.image= displayBoard.create_image(self.pixelPosX, self.pixelPosY, image=self.piece, anchor='nw')

	def show(self, anchorPos= None, pixelPosX= None, pixelPosY= None):
		displayBoard.delete(self.image)
		if(not self.isTaken):
			self.image= displayBoard.create_image(self.pixelPosX if pixelPosX is None else pixelPosX, self.pixelPosY if pixelPosY is None else pixelPosY, image=self.piece, anchor='nw' if anchorPos is None else anchorPos)

	def canMove(self, x, y, board):
		if(not self.withInBounds(x, y) or self.attackingAllies(x, y, board) or self.isTaken):
			return False
		if(abs(x - self.matrixX) == 0 and abs(y - self.matrixY) == 0):
			return False
		if((abs(x - self.matrixX) == 2 and abs(y - self.matrixY) == 1) or (abs(x - self.matrixX) == 1 and abs(y - self.matrixY) == 2)):
			return True
		return False

	def clone(self):
		cloneObj = Knight(self.matrixX, self.matrixY, self.isWhite)
		cloneObj.isTaken = self.isTaken
		cloneObj.movingThisPiece = self.movingThisPiece
		cloneObj.hasMoved = self.hasMoved
		return cloneObj

class Pawn(Pieces):
	def __init__(self, x, y, isWhite):
		super().__init__(x, y, isWhite)
		self.letter = chr(ord('a') + x)
		self.piece = pieces_white[5] if self.isWhite else pieces_black[5]
		self.image= displayBoard.create_image(self.pixelPosX, self.pixelPosY, image=self.piece, anchor='nw')
		self.canEnpassant = False
		self.enpassant = Pieces(0, 0, True)

	def show(self, anchorPos= None, pixelPosX= None, pixelPosY= None):
		displayBoard.delete(self.image)
		if(not self.isTaken):
			self.image= displayBoard.create_image(self.pixelPosX if pixelPosX is None else pixelPosX, self.pixelPosY if pixelPosY is None else pixelPosY, image=self.piece, anchor='nw' if anchorPos is None else anchorPos)

	def canMove(self, x, y, board):

		if(not self.withInBounds(x, y) or self.attackingAllies(x, y, board) or self.isTaken):
			return False
		if(abs(x - self.matrixX) == 0 and abs(y - self.matrixY) == 0):
			return False

		#enpassant on white's turn
		if(self.canEnpassant is True):
			if(self.isWhite):
				if(y == (self.enpassant.matrixY - 1) and x == self.enpassant.matrixX):
					self.enpassant.isTaken = True
					self.enpassant.show()
					return True
			else:
				if(y == (self.enpassant.matrixY + 1) and x == self.enpassant.matrixX):
					self.enpassant.isTaken = True
					self.enpassant.show()
					return True

		attacking = board.getPieceAt(x, y)
		if(attacking is not None):
			if(abs(x - self.matrixX) == abs(y - self.matrixY) and ((self.isWhite is True and (y - self.matrixY) == -1) or (self.isWhite is False and (y - self.matrixY) == 1))):
				return True
			return False
		if(x != self.matrixX or y == self.matrixY):
			return False

		if((self.isWhite and (y - self.matrixY == -1)) or (not self.isWhite and (y - self.matrixY == 1))):
			return True

		if(not self.hasMoved and ((self.isWhite and (y - self.matrixY == -2)) or (not self.isWhite and (y - self.matrixY == 2)))):
			if(self.moveThroughPieces(x, y, board)):
				return False
			if(self.isWhite):
				for piece in board.blackPieces:
					if(piece.isTaken is False and isPawn(piece.letter) and piece.matrixY == 4 and abs(ord(self.letter) - ord(piece.letter)) == 1):
						piece.canEnpassant = True
						piece.enpassant = self
			else:
				for piece in board.whitePieces:
					if(piece.isTaken is False and isPawn(piece.letter) and piece.matrixY == 3 and abs(ord(self.letter) - ord(piece.letter)) == 1):
						piece.canEnpassant = True
						piece.enpassant = self
			return True
		return False

	def clone(self):
		cloneObj = Pawn(self.matrixX, self.matrixY, self.isWhite)
		cloneObj.isTaken = self.isTaken
		cloneObj.movingThisPiece = self.movingThisPiece
		cloneObj.hasMoved = self.hasMoved
		return cloneObj

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

	def clone(self):
		clone = Board()
		clone.destroy()
		n = len(self.whitePieces)

		i = 0
		while i < n:
			clone.whitePieces.append(self.whitePieces[i].clone())
			i += 1

		n = len(self.blackPieces)
		i = 0
		while i < n:
			clone.blackPieces.append(self.blackPieces[i].clone())
			i += 1

		return clone

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
clone_board = None

def isInCheck(x, y, mine):
	global curr_board

	clone_board = curr_board.clone()
	ret = False

	for clonePiece in clone_board.whitePieces if whitesMove else clone_board.blackPieces:
		if(clonePiece.movingThisPiece == True):
			taken = clone_board.getPieceAt(x, y)
			if(taken is not None):
				taken.isTaken = True
			clonePiece.matrixX = x
			clonePiece.matrixY = y

	if((whitesMove and mine) or (not whitesMove and not mine)):
		targetX = clone_board.whitePieces[0].matrixX
		targetY = clone_board.whitePieces[0].matrixY
	else:
		targetX = clone_board.blackPieces[0].matrixX
		targetY = clone_board.blackPieces[0].matrixY

	for clonePiece in clone_board.blackPieces if ((whitesMove and mine) or (not whitesMove and not mine)) else clone_board.whitePieces:
		if(not clonePiece.isTaken and clonePiece.canMove(targetX, targetY, clone_board)):
			ret = True

	clone_board.destroy()
	return ret

def promoteTo(event, piece, which, x, y):
	global whitesMove
	global curr_board
	global promotionWin

	newpiece = None
	i = 0
	piece.movingThisPiece = True
	if(not whitesMove):
		n = len(curr_board.whitePieces)
		while i < n:
			if(curr_board.whitePieces[i].movingThisPiece):
				if(which == 'Q'):
					newpiece = Queen(x, y, not whitesMove)
				elif(which == 'B'):
					newpiece = Bishop(x, y, not whitesMove)
				elif(which == 'R'):
					newpiece = Rook(x, y, not whitesMove)
				elif(which == 'N'):
					newpiece = Knight(x, y, not whitesMove)
				curr_board.whitePieces[i] = newpiece
			i += 1
	else:
		n = len(curr_board.blackPieces)
		while i < n:
			if(curr_board.blackPieces[i].movingThisPiece):
				if(which == 'Q'):
					newpiece = Queen(x, y, not whitesMove)
				elif(which == 'B'):
					newpiece = Bishop(x, y, not whitesMove)
				elif(which == 'R'):
					newpiece = Rook(x, y, not whitesMove)
				elif(which == 'N'):
					newpiece = Knight(x, y, not whitesMove)
				curr_board.blackPieces[i] = newpiece
			i += 1

	piece.movingThisPiece = False
	piece.isTaken = True
	piece.show()
	del piece
	
	if(not flipped):
		newpiece.pixelPosX = x*pieceSize
		newpiece.pixelPosY = y*pieceSize
	else:
		newpiece.pixelPosX = (7 - x)*pieceSize
		newpiece.pixelPosY = (7 - y)*pieceSize

	promotionWin.destroy()

def getSAN(piece, x, y, isAttacking):

	global curr_board
	global whitesMove
	global castlingShort
	global castlingLong

	currMoveNotation = ''
	add = ''
	for otherpiece in curr_board.whitePieces if whitesMove else curr_board.blackPieces:
		if(not(piece.matrixX == otherpiece.matrixX and piece.matrixY == otherpiece.matrixY) and piece.letter == otherpiece.letter):
			if(otherpiece.canMove(x, y, curr_board)):
				if(piece.matrixX == otherpiece.matrixX):
					add = str(8 - piece.matrixY)
				else:
					add = chr(ord('a') + piece.matrixX)
	if(castlingShort is True):
		currMoveNotation = 'O-O'
	elif(castlingLong is True):
		currMoveNotation = 'O-O-O'
	elif(isAttacking):
		currMoveNotation += piece.letter + add + 'x' + chr(ord('a') + x) + str(8 - y)
	elif(isPawn(piece.letter)):
		currMoveNotation += piece.letter + str(8 - y)
	else:
		currMoveNotation += piece.letter + add + chr(ord('a') + x) + str(8 - y)

	if(isPawn(piece.letter)):
		if((piece.isWhite and y == 0) or (not piece.isWhite and y == 7)):
			currMoveNotation += '=Q'
			if((piece.isWhite and curr_board.blackPieces[0].matrixY == 0) or (not piece.isWhite and curr_board.whitePieces[0].matrixY == 7)):
				currMoveNotation += '+'

	if(isInCheck(x, y, False)):
		currMoveNotation += '+'

	return currMoveNotation

def getLAN(piece, x, y):
	currMoveNotation = chr(ord('a') + piece.matrixX) + str(8 - piece.matrixY) + chr(ord('a') + x) + str(8 - y) + ' '
	return currMoveNotation

def LANtoSAN(move):
	global curr_board

	startX = ord(move[0]) - 97
	startY = 8 - int(move[1])

	piece = curr_board.getPieceAt(startX, startY)
	assert(piece is not None)

	x = ord(move[2]) - 97
	y = 8 - int(move[3])

	isAttacking = False
	if(curr_board.isPieceAt(x, y) is True):
		isAttacking = True

	ret = getSAN(piece, x, y, isAttacking)
	if(againstAI):
		piece.movingThisPiece = True
		moveTo(x, y, curr_board)

	return ret

def updateNotation(piece, x, y, isAttacking):
	global moveNotation
	global LAN

	currMoveNotation = getSAN(piece, x, y, isAttacking)

	LAN += getLAN(piece, x, y)
	moveNotation.append(currMoveNotation)
	allmoves = ''
	moveNo = 1

	gameNotaion.configure(state='normal')
	gameNotaion.delete(1.0, tk.END)
	for move in range(len(moveNotation)):
		if(move % 2 == 0):
			allmoves = str(moveNo) + '. '
			allmoves += moveNotation[move] + '\t'
			# moveNo += 1
			gameNotaion.insert(tk.END, allmoves, 'tag')
			# gameNotaion.insert(tk.END,  moveNotation[move] + '\t', 'tag')
			moveNo += 1
		else:
			# allmoves += moveNotation[move]
			# allmoves += '\n'
			gameNotaion.insert(tk.END, moveNotation[move] + '\n', 'tag1')
	
	# gameNotaion.insert(tk.INSERT, allmoves, 'tag')
	gameNotaion.see(tk.END)
	gameNotaion.configure(state='disabled')

def moveTo(x, y, board):
	global whitesMove
	global movingPiece
	global promotion
	global castlingShort
	global castlingLong

	for piece in (board.whitePieces if whitesMove else board.blackPieces):
		if(piece.movingThisPiece is True):
			if(piece.canMove(x, y, board) is True and isInCheck(x, y, True) is False):
				attacking = board.getPieceAt(x, y)
				if(attacking is not None):
					attacking.isTaken = True
					attacking.show()

				updateNotation(piece, x, y, True if attacking is not None else False)
				if(isinstance(piece, Pawn)):
					piece.letter = chr(ord('a') + x)
				#move the piece, change turns
				piece.move(x, y)
				
				#if enpassant set to False
				if(not whitesMove):
					for piece in board.whitePieces:
						if(piece.isTaken is False and isPawn(piece.letter)):
							piece.canEnpassant = False
				else:
					for piece in board.blackPieces:
						if(piece.isTaken is False and isPawn(piece.letter)):
							piece.canEnpassant = False

				#if castling
				if(castlingShort):
					whitesMove = not whitesMove
					for piece in (board.whitePieces if whitesMove else board.blackPieces):
						if(piece.letter == 'R' and piece.isRight is True):
							piece.move(5,y)
					castlingShort = False

				if(castlingLong):
					whitesMove = not whitesMove
					for piece in (board.whitePieces if whitesMove else board.blackPieces):
						if(piece.letter == 'R' and piece.isRight is False):
							piece.move(3,y)
					castlingLong = False

				return True
			else:
				piece.movingThisPiece = False
	return False

#mouse movement
x = 0
y = 0

def move(event):
	global x
	global y
	global curr_board
	global movingPiece

	x = math.floor(event.x/pieceSize)
	y = math.floor(event.y/pieceSize)
	if(flipped):
		x = 7 - x
		y = 7 - y
	movingPiece = curr_board.getPieceAt(x, y)
	if(movingPiece is not None and ((movingPiece.isWhite and not whitesMove) or (movingPiece.isWhite is False and whitesMove))):
		movingPiece = None

def motion(event):
	global curr_board
	global movingPiece
	
	if(movingPiece is None):
		return

	tempPixelPosX =	event.x
	tempPixelPosY = event.y
	movingPiece.show(anchorPos='center', pixelPosX=tempPixelPosX, pixelPosY=tempPixelPosY)

def release(event):
	global movingPiece
	
	if(movingPiece is None):
		return
	x = math.floor(event.x/pieceSize)
	y = math.floor(event.y/pieceSize)
	if(flipped):
		x = 7 - x
		y = 7 - y
	if(movingPiece is not None):
		movingPiece.movingThisPiece = True
		if(not moveTo(x, y, curr_board)):
			movingPiece.show()
		else:
			if(againstAI):
				runEngine()
	else:
		movingPiece.show()

def isPawn(a):
	for c in char_range('a', 'h'):
		if(a == c):
			return True
	return False

moves = ['e4','d5','exd5','c6','dxc6','Bd7','cxb7','Nc6','bxa8=Q+']
curr_index = -1

def forward():
	global curr_index
	
	curr_index += 1
	if(curr_index >= len(moves)):
		return

	notation = moves[curr_index]
	n = len(notation)

	#check or mate notation
	if(notation[n-1] == '+' or notation[n-1] == '#'):
		notation = notation[:-1]
		n -= 1

	#promotion notation
	if(notation[n-2] == '='):
		notation = notation[:-2]
		n -= 2
	
	movingPieceLetter = notation[0]
	#castling notation
	if(movingPieceLetter == 'O'):
		if(n == 3):
			if(curr_index % 2 == 0):
				curr_board.whitePieces[0].movingThisPiece = True
				moveTo(6, 7, curr_board)
			else:
				curr_board.blackPieces[0].movingThisPiece = True
				moveTo(6, 0, curr_board)
		else:
			if(curr_index % 2 == 0):
				moving = True
				curr_board.whitePieces[0].movingThisPiece = True
				moveTo(2, 7, curr_board)
			else:
				moving = True
				curr_board.blackPieces[0].movingThisPiece = True
				moveTo(2, 0, curr_board)
		return

	#pawn movement notation
	if(n == 2):
		x = ord(notation[0]) - 97
		y = 8 - int(notation[1])
		for piece in (curr_board.whitePieces if curr_index % 2 == 0 else curr_board.blackPieces):
			if(piece.letter == movingPieceLetter and piece.canMove(x, y, curr_board)):
				piece.movingThisPiece = True
				moveTo(x, y, curr_board)
				return
		
	#normal piece movement notation
	elif(n == 3):
		if(notation == '1-0'):
			myLabel.config(text="Game won by white")
			return
		elif(notation == '0-1'):
			myLabel.config(text="Game won by black")
			return
		x = ord(notation[1]) - 97
		y = 8 - int(notation[2])
		for piece in (curr_board.whitePieces if curr_index % 2 == 0 else curr_board.blackPieces):
			if(piece.letter == movingPieceLetter and piece.isTaken is False and piece.canMove(x, y, curr_board)):
				piece.movingThisPiece = True
				moveTo(x, y, curr_board)
				return
	#captures notation
	elif(n == 4):
		x = ord(notation[2]) - 97
		y = 8 - int(notation[3])

		for piece in (curr_board.whitePieces if curr_index % 2 == 0 else curr_board.blackPieces):
			if(piece.letter == movingPieceLetter and piece.isTaken is False and piece.canMove(x, y, curr_board)):
				if(notation[1] != 'x'):
					if(isPawn(notation[1])):
						if(piece.matrixX != (ord(notation[1]) - 97)):
							continue
					else:
						if((8 - int(notation[1])) != piece.matrixY):
							continue
				piece.movingThisPiece = True
				moveTo(x, y, curr_board)
				return
	#2 possible capture notation Raxe6
	elif(n == 5):
		x = ord(notation[3]) - 97
		y = 8 - int(notation[4])
		for piece in (curr_board.whitePieces if curr_index % 2 == 0 else curr_board.blackPieces):
			if(piece.letter == movingPieceLetter and piece.isTaken is False and piece.canMove(x, y, curr_board)):
				if(isPawn(notation[1])):
					if(piece.matrixX != (ord(notation[1]) - 97)):
						continue
				else:
					if(piece.matrixY != (8 - int(notation[1]))):
						continue
				piece.movingThisPiece = True
				moveTo(x, y, curr_board)
				return

	elif(notation == '1/2-1/2'):
		myLabel.config(text="Game ended in a draw")
		return

def backward():
	global curr_index

	temp = curr_index - 1

	new()
	if(temp < 0):
		curr_index = -1
		return

	i = 0
	while i <= temp:
		forward()
		i += 1
	curr_index = temp

#new game
def new():
	global curr_board
	global curr_index
	global whitesMove
	global promotion
	global movingPiece
	global flipped
	global moveNotation
	global LAN
	global compMove
	global againstAI
	global play_computer_button

	print(LAN)
	curr_board.destroy()
	curr_board = Board()
	curr_board.show()
	curr_index = -1
	whitesMove = True
	promotion = False
	flipped = False
	movingPiece = Pieces(0, 0, True)
	moveNotation = []
	LAN = ''
	gameNotaion.configure(state='normal')
	gameNotaion.delete(1.0, tk.END)
	myLabel.config(text='')
	play_computer_button.config(text='Play Against Computer')
	compMove = ''
	againstAI = False

#flip the board
def flip():
	curr_board.flipBoard()

engine = None
def initEngine():
	global engine

	engine = sb.Popen('D:\\CPP\\Chess\\stockfish12.exe', stdin=sb.PIPE, stdout=sb.PIPE, stderr=sb.STDOUT)
	put(b'uci\n', inf_list, 0)
	myLabel.config(text='Engine Loaded')

def put(command, inf_list, tmp_time):

	engine.stdin.write(command)
	engine.stdin.flush()
	time.sleep(tmp_time)

	if command != "quit":
		engine.stdin.write(b'isready\n')     
		engine.stdin.flush()
		while True:
			text = engine.stdout.readline().strip()
			if text == (b'readyok'):
				break
			elif text !='':
				inf_list.append(text)

	engine.stdout.flush()
inf_list = []
compMove = ''

def runEngine():
	global LAN
	global inf_list
	global compMove
	global engine

	if engine is None:
		initEngine()
	inf_list.clear()
	command = b'position startpos moves ' + LAN.encode() + b'\n'

	put(command, inf_list, 0)

	put(b'd\n', inf_list, 0)

	command = b'go movetime 1000\n'
	put(command, inf_list, 2)

	result = inf_list[-1].decode().split()
	inf_list.clear()
	print(result)
	myLabel.config(text='Best Move: ' + LANtoSAN(result[1]))

def play_computer():
	global againstAI
	global engine

	if engine is None:
		initEngine()

	againstAI = not againstAI

	if(againstAI):
		play_computer_button.config(text='Stop Playing Against Computer')
	else:
		play_computer_button.config(text='Play Against Computer')


def callback(event):
	global gameNotaion
	# get the index of the mouse click
	index = event.widget.index("@%s,%s" % (event.x, event.y))
	event.widget.focus_set()
	#get the indices of all "adj" tags
	tag_indices = list(event.widget.tag_ranges('tag'))
	gameNotaion.configure(state='normal')
	text = ''
	# iterate them pairwise (start and end index)
	for start, end in zip(tag_indices[0::2], tag_indices[1::2]):
    # check if the tag matches the mouse click index
		if event.widget.compare(start, '<=', index) and event.widget.compare(index, '<', end):
        # return string between tag start and end
			gameNotaion.tag_add(tk.SEL, start, end)
			print(start, end, event.widget.get(start, end))
			text = event.widget.get(start, end)

	print(text)
	highlight_pattern(gameNotaion, text, 'tag')
	gameNotaion.configure(state='disabled')

def highlight_pattern(gameNotaion, pattern, tag, start="1.0", end="end", regexp=False):
	'''Apply the given tag to all text that matches the given pattern

	If 'regexp' is set to True, pattern will be treated as a regular
	expression according to Tcl's regular expression syntax.
	'''

	start = gameNotaion.index(start)
	end = gameNotaion.index(end)
	gameNotaion.mark_set("matchStart", start)
	gameNotaion.mark_set("matchEnd", start)
	gameNotaion.mark_set("searchLimit", end)

	count = tk.IntVar()
	while True:
		index = gameNotaion.search(pattern, "matchEnd","searchLimit",count=count, regexp=regexp)
		if index == "": break
		if count.get() == 0: break # degenerate pattern which matches zero-length strings
		gameNotaion.mark_set("matchStart", index)
		gameNotaion.mark_set("matchEnd", "%s+%sc" % (index, count.get()))
		gameNotaion.tag_add('highlight', "matchStart", "matchEnd")

def popup_bonus(piece, x, y):
	global whitesMove
	global promotionWin

	promotionWin = tk.Toplevel()
	promotionWin.title("Promote To")
	promotionWin.geometry("%dx%d+%d+%d" % (280, 65, pieceSize, pieceSize if whitesMove else pieceSize*7))
	promotionWin.overrideredirect(True) 

	rook = tk.Label(promotionWin, image=pieces_white[0] if whitesMove else pieces_black[0], anchor='nw')
	rook.grid(row=0, column=0)

	queen = tk.Label(promotionWin, image=pieces_white[2] if whitesMove else pieces_black[2], anchor='nw')
	queen.grid(row=0, column=1)

	bishop = tk.Label(promotionWin, image=pieces_white[3] if whitesMove else pieces_black[3], anchor='nw')
	bishop.grid(row=0, column=2)

	knight = tk.Label(promotionWin, image=pieces_white[4] if whitesMove else pieces_black[4], anchor='nw')
	knight.grid(row=0, column=3)

	rook.bind("<Button-1>",lambda event, piece=piece, x=x, y=y, which="R" : promoteTo(event, piece, which, x, y))
	queen.bind("<Button-1>",lambda event, piece=piece, x=x, y=y, which="Q" : promoteTo(event, piece, which, x, y))
	bishop.bind("<Button-1>",lambda event, piece=piece, x=x, y=y, which="B" : promoteTo(event, piece, which, x, y))
	knight.bind("<Button-1>",lambda event, piece=piece, x=x, y=y, which="N" : promoteTo(event, piece, which, x, y))

gameNotaion = tk.scrolledtext.ScrolledText(root, state='disabled', width = 15, height=30)
gameNotaion['font'] = ('consolas', '12')
gameNotaion.tag_bind("tag", "<Button-1>", callback)
myLabel = tk.Label(root, text="")
displayBoard.bind('<Button-1>', move)
displayBoard.bind('<B1-Motion>', motion)
displayBoard.bind('<ButtonRelease-1>', release)
arrow_frame = tk.Frame(root)
arrow_frame.grid(row=1, column=1)
forward_button = tk.Button(arrow_frame, text="->", command=forward)
backward_button = tk.Button(arrow_frame, text="<-", command=backward)
runEngine_button = tk.Button(root, text="Best Move", command=runEngine)
new_button = tk.Button(root, text="New Game", command=new)
flip_button = tk.Button(root, text="Flip Board", command=flip)
play_computer_button = tk.Button(root, text="Play Against Computer", command=play_computer)
gameNotaion.grid(row=0, column=1, sticky='nw')
myLabel.grid(row=1, column=0)
forward_button.grid(row=1, column=2)
backward_button.grid(row=1, column=1)
flip_button.grid(row=2, column=1)
new_button.grid(row=2, column=0)
runEngine_button.grid(row=3, column=1)
play_computer_button.grid(row=3, column=0)
root.mainloop()
