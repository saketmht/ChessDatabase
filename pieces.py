#Fixed values
startX = 40
startY = 0
pieceSize = 50
padding = 5
fonstSize = 15

def isPawn(a):
	if(a >= 'a' and a <= 'h'):
		return True
	return False

class Pieces:
	def __init__(self, x, y, isWhite, boardFrame):
		self.matrixX = x
		self.matrixY = y
		self.pixelPosX = x*pieceSize + startX
		self.pixelPosY = y*pieceSize + startY
		self.boardFrame = boardFrame
		self.image = None
		self.isWhite = isWhite
		self.isTaken = False
		self.movingThisPiece = False
		self.hasMoved = False

	def show(self, anchorPos= None, pixelPosX= None, pixelPosY= None):
		if(self.image is not None):
			self.boardFrame.canvas.delete(self.image)
		if(not self.isTaken):
			self.image= self.boardFrame.canvas.create_image(self.pixelPosX if pixelPosX is None else pixelPosX, self.pixelPosY if pixelPosY is None else pixelPosY, image=self.piece, anchor='nw' if anchorPos is None else anchorPos)

	def clone(self):
		pass

	@staticmethod
	def withInBounds(x, y):
		if(x >= 0 and x < 8 and y >= 0 and y < 8):
			return True
		return False

	def move(self, x, y, board):
		self.hasMoved = True

		self.matrixX = x
		self.matrixY = y

		if(not board.flipped):
			self.pixelPosX = x*pieceSize + startX
			self.pixelPosY = y*pieceSize + startY
		else:
			self.pixelPosX = (7 - x)*pieceSize + startX
			self.pixelPosY = (7 - y)*pieceSize + startY

		self.show()
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
	def __init__(self, x, y, isWhite, boardFrame, pieceImage):
		super().__init__(x, y, isWhite, boardFrame)
		self.letter = 'K'
		self.piece = pieceImage

	def canMove(self, x, y, board):
		if(not self.withInBounds(x, y) or self.attackingAllies(x, y, board) or self.isTaken):
			return False
		if(abs(x - self.matrixX) == 0 and abs(y - self.matrixY) == 0):
			return False
		if(abs(x - self.matrixX) <= 1 and abs(y - self.matrixY) <= 1):
			return True
		#castling
		if(self.canCastleShort(x, y, board)):
			board.castlingShort = True
			return True
		if(self.canCastleLong(x, y, board)):
			board.castlingLong = True
			return True
		return False

	def canCastleShort(self, x, y, board):
		if(not self.hasMoved and (y - self.matrixY) == 0) and (abs(x - self.matrixX <= 2)):
			if(x - self.matrixX == 2):
				#shortcastle
				tempY = 7 if self.isWhite else 0
				for piece in board.blackPieces if self.isWhite else board.whitePieces:
					if(not piece.isTaken and (piece.canMove(5, tempY, board) or piece.canMove(6, tempY, board) or board.isPieceAt(5, tempY))):
						return False
				for piece in board.whitePieces if self.isWhite else board.blackPieces:
					if(not piece.isTaken and piece.letter == 'R' and (piece.matrixX == 7 and (piece.matrixY == 7 if self.isWhite else piece.matrixY == 0)) and piece.hasMoved is False):
						return True		
		return False

	def canCastleLong(self, x, y, board):
		if(not self.hasMoved and (y - self.matrixY) == 0) and (abs(x - self.matrixX <= 2)):
			if(x - self.matrixX == -2):
				#long castle
				tempY = 7 if self.isWhite else 0
				for piece in board.blackPieces if self.isWhite else board.whitePieces:
					if(not piece.isTaken and (piece.canMove(2, tempY, board) or piece.canMove(3, tempY, board) or board.isPieceAt(3, tempY))):
						return False
				for piece in board.whitePieces if self.isWhite else board.blackPieces:
					if(not piece.isTaken and piece.letter == 'R' and (piece.matrixX == 0 and (piece.matrixY == 7 if self.isWhite else piece.matrixY == 0)) and piece.hasMoved is False):
						return True		
		return False

	def clone(self):
		cloneObj = King(self.matrixX, self.matrixY, self.isWhite, self.boardFrame, self.piece)
		cloneObj.isTaken = self.isTaken
		cloneObj.piece = None
		cloneObj.movingThisPiece = self.movingThisPiece
		cloneObj.hasMoved = self.hasMoved
		return cloneObj

class Rook(Pieces):
	def __init__(self, x, y, isWhite, boardFrame, pieceImage):
		super().__init__(x, y, isWhite, boardFrame)
		self.isRight = True if x == 7 else False
		self.letter = 'R'
		self.piece = pieceImage

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
		cloneObj = Rook(self.matrixX, self.matrixY, self.isWhite, self.boardFrame, self.piece)
		cloneObj.isTaken = self.isTaken
		cloneObj.piece = None
		cloneObj.movingThisPiece = self.movingThisPiece
		cloneObj.hasMoved = self.hasMoved
		return cloneObj

class Queen(Pieces):
	def __init__(self, x, y, isWhite, boardFrame, pieceImage):
		super().__init__(x, y, isWhite, boardFrame)
		self.letter = 'Q'
		self.piece = pieceImage

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
		cloneObj = Queen(self.matrixX, self.matrixY, self.isWhite, self.boardFrame, self.piece)
		cloneObj.isTaken = self.isTaken
		cloneObj.piece = None
		cloneObj.hasMoved = self.hasMoved
		cloneObj.movingThisPiece = self.movingThisPiece
		return cloneObj

class Bishop(Pieces):
	def __init__(self, x, y, isWhite, boardFrame, pieceImage):
		super().__init__(x, y, isWhite, boardFrame)
		self.letter = 'B'
		self.piece = pieceImage

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
		cloneObj = Bishop(self.matrixX, self.matrixY, self.isWhite, self.boardFrame, self.piece)
		cloneObj.isTaken = self.isTaken
		cloneObj.piece = None
		cloneObj.hasMoved = self.hasMoved
		cloneObj.movingThisPiece = self.movingThisPiece
		return cloneObj

class Knight(Pieces):
	def __init__(self, x, y, isWhite, boardFrame, pieceImage):
		super().__init__(x, y, isWhite, boardFrame)
		self.letter = 'N'
		self.piece = pieceImage

	def canMove(self, x, y, board):
		if(not self.withInBounds(x, y) or self.attackingAllies(x, y, board) or self.isTaken):
			return False
		if(abs(x - self.matrixX) == 0 and abs(y - self.matrixY) == 0):
			return False
		if((abs(x - self.matrixX) == 2 and abs(y - self.matrixY) == 1) or (abs(x - self.matrixX) == 1 and abs(y - self.matrixY) == 2)):
			return True
		return False

	def clone(self):
		cloneObj = Knight(self.matrixX, self.matrixY, self.isWhite, self.boardFrame, self.piece)
		cloneObj.isTaken = self.isTaken
		cloneObj.piece = None
		cloneObj.movingThisPiece = self.movingThisPiece
		cloneObj.hasMoved = self.hasMoved
		return cloneObj

class Pawn(Pieces):
	def __init__(self, x, y, isWhite, boardFrame, pieceImage):
		super().__init__(x, y, isWhite, boardFrame)
		self.letter = chr(ord('a') + x)
		self.piece = pieceImage
		self.canEnpassant = False
		self.enpassant = None

	def canMove(self, x, y, board):
		# global enpassant

		if(not self.withInBounds(x, y) or self.attackingAllies(x, y, board) or self.isTaken):
			return False
		if(abs(x - self.matrixX) == 0 and abs(y - self.matrixY) == 0):
			return False

		#enpassant on white's turn
		if(self.canEnpassant is True):
			if(self.isWhite):
				if(y == (self.enpassant.matrixY - 1) and x == self.enpassant.matrixX):
					board.enpassant = True
					return True
			else:
				if(y == (self.enpassant.matrixY + 1) and x == self.enpassant.matrixX):
					board.enpassant = True
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
		cloneObj = Pawn(self.matrixX, self.matrixY, self.isWhite, self.boardFrame, self.piece)
		cloneObj.isTaken = self.isTaken
		cloneObj.piece = None
		cloneObj.movingThisPiece = self.movingThisPiece
		cloneObj.hasMoved = self.hasMoved
		cloneObj.canEnpassant = self.canEnpassant
		cloneObj.enpassant = self.enpassant
		return cloneObj

class Board:
	def __init__(self, boardFrame, pieceImage):
		self.whitePieces = []
		self.blackPieces = []
		self.castlingShort = False
		self.castlingLong = False
		self.flipped = False
		self.whitesMove = True
		self.promotion = False
		self.autoPromote = False
		self.promotionTo = ''
		self.enpassant = False
		self.isClone = False
		self.boardFrame = boardFrame
		self.pieceImage = pieceImage
		self.setUpBoard()

	def setUpBoard(self):
		self.whitePieces.append(King(4, 7, True, self.boardFrame, self.pieceImage.pieces_white[1]))
		self.whitePieces.append(Queen(3, 7, True, self.boardFrame, self.pieceImage.pieces_white[2]))
		self.whitePieces.append(Bishop(2, 7, True, self.boardFrame, self.pieceImage.pieces_white[3]))
		self.whitePieces.append(Bishop(5, 7, True, self.boardFrame, self.pieceImage.pieces_white[3]))
		self.whitePieces.append(Knight(1, 7, True, self.boardFrame, self.pieceImage.pieces_white[4]))
		self.whitePieces.append(Rook(0, 7, True, self.boardFrame, self.pieceImage.pieces_white[0]))
		self.whitePieces.append(Knight(6, 7, True, self.boardFrame, self.pieceImage.pieces_white[4]))
		self.whitePieces.append(Rook(7, 7, True, self.boardFrame, self.pieceImage.pieces_white[0]))

		self.whitePieces.append(Pawn(4, 6, True, self.boardFrame, self.pieceImage.pieces_white[5]))
		self.whitePieces.append(Pawn(3, 6, True, self.boardFrame, self.pieceImage.pieces_white[5]))
		self.whitePieces.append(Pawn(2, 6, True, self.boardFrame, self.pieceImage.pieces_white[5]))
		self.whitePieces.append(Pawn(5, 6, True, self.boardFrame, self.pieceImage.pieces_white[5]))
		self.whitePieces.append(Pawn(1, 6, True, self.boardFrame, self.pieceImage.pieces_white[5]))
		self.whitePieces.append(Pawn(0, 6, True, self.boardFrame, self.pieceImage.pieces_white[5]))
		self.whitePieces.append(Pawn(6, 6, True, self.boardFrame, self.pieceImage.pieces_white[5]))
		self.whitePieces.append(Pawn(7, 6, True, self.boardFrame, self.pieceImage.pieces_white[5]))

		self.blackPieces.append(King(4, 0, False, self.boardFrame, self.pieceImage.pieces_black[1]))
		self.blackPieces.append(Queen(3, 0, False, self.boardFrame, self.pieceImage.pieces_black[2]))
		self.blackPieces.append(Bishop(2, 0, False, self.boardFrame, self.pieceImage.pieces_black[3]))
		self.blackPieces.append(Bishop(5, 0, False, self.boardFrame, self.pieceImage.pieces_black[3]))
		self.blackPieces.append(Knight(1, 0, False, self.boardFrame, self.pieceImage.pieces_black[4]))
		self.blackPieces.append(Rook(0, 0, False, self.boardFrame, self.pieceImage.pieces_black[0]))
		self.blackPieces.append(Knight(6, 0, False, self.boardFrame, self.pieceImage.pieces_black[4]))
		self.blackPieces.append(Rook(7, 0, False, self.boardFrame, self.pieceImage.pieces_black[0]))

		self.blackPieces.append(Pawn(4, 1, False, self.boardFrame, self.pieceImage.pieces_black[5]))
		self.blackPieces.append(Pawn(3, 1, False, self.boardFrame, self.pieceImage.pieces_black[5]))
		self.blackPieces.append(Pawn(2, 1, False, self.boardFrame, self.pieceImage.pieces_black[5]))
		self.blackPieces.append(Pawn(5, 1, False, self.boardFrame, self.pieceImage.pieces_black[5]))
		self.blackPieces.append(Pawn(1, 1, False, self.boardFrame, self.pieceImage.pieces_black[5]))
		self.blackPieces.append(Pawn(0, 1, False, self.boardFrame, self.pieceImage.pieces_black[5]))
		self.blackPieces.append(Pawn(6, 1, False, self.boardFrame, self.pieceImage.pieces_black[5]))
		self.blackPieces.append(Pawn(7, 1, False, self.boardFrame, self.pieceImage.pieces_black[5]))

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
		clone = Board(self.boardFrame, self.pieceImage)
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

		clone.castlingShort = self.castlingShort
		clone.castlingLong = self.castlingLong
		clone.whitesMove = self.whitesMove
		clone.enpassant = self.enpassant
		clone.isClone = True
		for each in clone.whitePieces if clone.whitesMove else clone.blackPieces:
			if(isPawn(each.letter) and each.canEnpassant):
				x = each.enpassant.matrixX
				y = each.enpassant.matrixY 
				for eachB in clone.blackPieces if clone.whitesMove else clone.whitePieces:
					if(eachB.matrixX == x and eachB.matrixY == y):
						each.enpassant = eachB
						break
				break

		return clone

	def flipBoard(self):
		for pieceWhite in self.whitePieces:
			if(self.flipped):
				pieceWhite.pixelPosX = pieceWhite.matrixX*pieceSize + startX
				pieceWhite.pixelPosY = pieceWhite.matrixY*pieceSize + startY
			else:
				pieceWhite.pixelPosX = (7 - pieceWhite.matrixX)*pieceSize + startX
				pieceWhite.pixelPosY = (7 - pieceWhite.matrixY)*pieceSize + startY

		for pieceBlack in self.blackPieces:
			if(self.flipped):
				pieceBlack.pixelPosX = pieceBlack.matrixX*pieceSize + startX
				pieceBlack.pixelPosY = pieceBlack.matrixY*pieceSize + startY
			else:
				pieceBlack.pixelPosX = (7 - pieceBlack.matrixX)*pieceSize + startX
				pieceBlack.pixelPosY = (7 - pieceBlack.matrixY)*pieceSize + startY

		self.show()
		self.flipped = not self.flipped

	def destroy(self):
		for piece in self.whitePieces:
			piece.isTaken = True
		for piece in self.blackPieces:
			piece.isTaken = True
		self.show()
		self.whitePieces.clear()
		self.blackPieces.clear()

