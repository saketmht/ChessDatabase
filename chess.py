import tkinter as tk
import tkinter.scrolledtext as scrolledtext
from PIL import ImageTk, Image
import math
import subprocess as sb
import time
import json
import threading
import traceback
import os

from frame import PieceImage, BoardFrame, GameNotation, AddOn, EngineEvals
from pieces import *

root = tk.Tk()
root.title('Chess')
root.state('normal')
# root.state('zoomed')
# root.configure(background='grey')

#Fixed values
startX = 40
startY = 0
pieceSize = 50
padding = 5
fonstSize = 15

#arrows and circles
lineX = 0
lineY = 0
arrows = []
circles = []
color = '#FF0000'

#moving pieces
movingPiece = None
moveNotation = []

evalLines = [None] * 400
evaluation = ''

LAN = []

#for engine use
againstAI = False
stopped = False
firstTime = True
analyzingThread = None
analyzingMode = False

curr_index = -1
# last_tag = ''

boardFrame = None
pieceImage = None
curr_board = None
gameNotation = None
addon = None
engineEval = None



#check if move is legal or not
def isPseudoLegal(x, y, mine, board):

	clone_board = board.clone()
	ret = False

	for clonePiece in clone_board.whitePieces if board.whitesMove else clone_board.blackPieces:
		if(clonePiece.movingThisPiece == True):
			taken = clone_board.getPieceAt(x, y)
			if(taken is not None):
				taken.isTaken = True
			if(isPawn(clonePiece.letter)):
				if(clonePiece.canEnpassant):
					if((clonePiece.isWhite and clonePiece.enpassant.matrixY == y+1) or (not clonePiece.isWhite and clonePiece.enpassant.matrixY == y-1)):
						clonePiece.enpassant.isTaken = True
			clonePiece.matrixX = x
			clonePiece.matrixY = y

	if((board.whitesMove and mine) or (not board.whitesMove and not mine)):
		targetX = clone_board.whitePieces[0].matrixX
		targetY = clone_board.whitePieces[0].matrixY
	else:
		targetX = clone_board.blackPieces[0].matrixX
		targetY = clone_board.blackPieces[0].matrixY

	for clonePiece in clone_board.blackPieces if ((board.whitesMove and mine) or (not board.whitesMove and not mine)) else clone_board.whitePieces:
		if(not clonePiece.isTaken and clonePiece.canMove(targetX, targetY, clone_board)):
			ret = True

	clone_board.destroy()
	return ret

#check if king in check or not
def isInCheck(white):
	global curr_board

	clone_board = curr_board.clone()
	ret = False

	if(white):
		targetX = clone_board.whitePieces[0].matrixX
		targetY = clone_board.whitePieces[0].matrixY
	else:
		targetX = clone_board.blackPieces[0].matrixX
		targetY = clone_board.blackPieces[0].matrixY

	for clonePiece in clone_board.blackPieces if white else clone_board.whitePieces:
		if(not clonePiece.isTaken and clonePiece.canMove(targetX, targetY, clone_board)):
			ret = True
			break

	clone_board.destroy()
	return ret

#pawn promotion
def promoteTo(event, piece, which, x, y, board):
	newpiece = None
	i = 0
	board.promotionTo = which
	piece.movingThisPiece = True
	whitesMove = board.whitesMove
	if(whitesMove):
		n = len(board.whitePieces)
		while i < n:
			if(board.whitePieces[i].movingThisPiece):
				if(which == 'Q'):
					newpiece = Queen(x, y, whitesMove, board.boardFrame, pieceImage.pieces_white[2])
				elif(which == 'B'):
					newpiece = Bishop(x, y, whitesMove, board.boardFrame, pieceImage.pieces_white[3])
				elif(which == 'R'):
					newpiece = Rook(x, y, whitesMove, board.boardFrame, pieceImage.pieces_white[0])
				elif(which == 'N'):
					newpiece = Knight(x, y, whitesMove, board.boardFrame, pieceImage.pieces_white[4])
				board.whitePieces[i] = newpiece
			i += 1
	else:
		n = len(board.blackPieces)
		while i < n:
			if(board.blackPieces[i].movingThisPiece):
				if(which == 'Q'):
					newpiece = Queen(x, y, whitesMove, board.boardFrame, pieceImage.pieces_black[2])
				elif(which == 'B'):
					newpiece = Bishop(x, y, whitesMove, board.boardFrame, pieceImage.pieces_black[3])
				elif(which == 'R'):
					newpiece = Rook(x, y, whitesMove, board.boardFrame, pieceImage.pieces_black[0])
				elif(which == 'N'):
					newpiece = Knight(x, y, whitesMove, board.boardFrame, pieceImage.pieces_black[4])
				board.blackPieces[i] = newpiece
			i += 1

	piece.movingThisPiece = False
	piece.isTaken = True
	piece.show()
	del piece

	if(not board.flipped):
		newpiece.pixelPosX = x*pieceSize + startX
		newpiece.pixelPosY = y*pieceSize + startY
	else:
		newpiece.pixelPosX = (7 - x)*pieceSize + startX
		newpiece.pixelPosY = (7 - y)*pieceSize + startY

	if(board.isClone):
		newpiece.piece = None
		
	newpiece.show()

	if(not board.autoPromote):
		event.widget.master.destroy()
	board.promotion = False

#game end
def isGameOver(board, static):
	# global enpassant

	ret = True
	for piece in board.whitePieces if board.whitesMove else board.blackPieces:
		if(not piece.isTaken):
			piece.movingThisPiece = True
			for x in range(0, 8):
				for y in range(0, 8):
					if(piece.canMove(x, y, board) is True and isPseudoLegal(x, y, True, board) is False):
						ret = False
						break
				if(not ret): break
			piece.movingThisPiece = False
			if(not ret): break

	board.enpassant = False
	board.castlingShort = False
	board.castlingLong = False

	result = ''

	if(not static and ret is True):
		last = moveNotation[-1]
		if(last != '1-0' and last != '0-1' and last != '1/2-1/2'):
			if last[-1] == '+' or last[-1] == '#':
				last = last[:-1]
				moveNotation[-1] = last + '#'
				if board.whitesMove:
					result = '0-1'
				else:
					result = '1-0'
			else:
				result = '1/2-1/2'

			moveNotation.append(result)
			gameNotation.changeGameNotation(moveNotation, callback)

		for piece in board.whitePieces:
			piece.isTaken = True
		for piece in board.blackPieces:
			piece.isTaken = True

		for each in range(0, engineEval.lines):
			for x in range(0, 3):
				engineEval.evalLines[each][x].configure(text='')

		# depth1.config(text='')
		# score1.config(text='')
		# line1.config(text='')
		# depth2.config(text='')
		# score2.config(text='')
		# line2.config(text='')
		# depth3.config(text='')
		# score3.config(text='')
		# line3.config(text='')

	return ret

def genFEN():
	pass

#load posn from FEN string
def loadFEN():
	#NOTE - some details left complete later
	# global pgnText
	global curr_board

	new()
	fenString = addon.pgnText.get(1.0, tk.END).strip().rstrip().split()
	addon.pgnText.delete(1.0, tk.END)
	
	try:
		curr_board.destroy()
		curr_board.whitesMove = True if fenString[1] == 'w' else False
		pieces = []
		x = 0
		y = 0
		for eachChar in fenString[0]:
			if(eachChar == '/'):
				x = 0
				y += 1
			elif(eachChar.isalpha()):
				if(eachChar.lower() == 'r'):
					pieces.append(Rook(x, y, eachChar.isupper()))
					x += 1
				elif(eachChar.lower() == 'n'):
					pieces.append(Knight(x, y, eachChar.isupper()))
					x += 1
				elif(eachChar.lower() == 'b'):
					pieces.append(Bishop(x, y, eachChar.isupper()))
					x += 1
				elif(eachChar.lower() == 'q'):
					pieces.append(Queen(x, y, eachChar.isupper()))
					x += 1
				elif(eachChar.lower() == 'k'):
					isWhite = eachChar.isupper()
					if(isWhite):
						curr_board.whitePieces.append(King(x, y, isWhite))
					else:
						curr_board.blackPieces.append(King(x, y, isWhite))
					x += 1
				elif(eachChar.lower() == 'p'):
					pieces.append(Pawn(x, y, eachChar.isupper()))
					x += 1
			else:
				x += int(eachChar)

		for piece in pieces:
			if(piece.isWhite):
				curr_board.whitePieces.append(piece)
			else:
				curr_board.blackPieces.append(piece)
		setCastlingRights(curr_board, fenString[2])
		curr_board.show()
		addon.pgnText.insert(tk.END, "FEN Loaded")
	except:
		new()
		addon.pgnText.insert(tk.END, "It is not a valid FEN String.")

def setCastlingRights(board, fenString):
	whiteShort = False
	whiteLong = False
	blackShort = False
	blackLong = False

	for eachChar in fenString:
		if(eachChar == 'K'):
			whiteShort = True
		elif(eachChar == 'Q'):
			whiteLong = True
		elif(eachChar == 'k'):
			blackShort = True
		elif(eachChar == 'q'):
			blackLong = True

	if(not whiteShort and not whiteLong):
		board.whitePieces[0].hasMoved = True

	if(not blackShort and not blackLong):
		board.blackPieces[0].hasMoved = True

	piece = board.getPieceAt(0, 0)
	if(piece and not piece.isWhite and piece.letter == 'R' and not blackLong):
		piece.hasMoved = True

	piece = board.getPieceAt(7, 0)
	if(piece and not piece.isWhite and piece.letter == 'R' and not blackShort):
		piece.hasMoved = True

	piece = board.getPieceAt(0, 7)
	if(piece and piece.isWhite and piece.letter == 'R' and not whiteLong):
		piece.hasMoved = True

	piece = board.getPieceAt(7, 7)
	if(piece and piece.isWhite and piece.letter == 'R' and not whiteShort):
		piece.hasMoved = True	

#SAN notation
def getSAN(piece, x, y, isAttacking, board):
	# global enpassant

	currMoveNotation = ''
	add = ''
	for otherpiece in board.whitePieces if piece.isWhite else board.blackPieces:
		if(not(piece.matrixX == otherpiece.matrixX and piece.matrixY == otherpiece.matrixY) and piece.letter == otherpiece.letter):
			if(otherpiece.canMove(x, y, board)):
				if(piece.matrixX == otherpiece.matrixX):
					add = str(8 - piece.matrixY)
				else:
					add = chr(ord('a') + piece.matrixX)

	if(board.enpassant is True):
		currMoveNotation = piece.letter + 'x' + chr(ord('a') + piece.enpassant.matrixX) + str(8 - piece.matrixY + (1 if piece.isWhite else -1))
	elif(board.castlingShort is True):
		currMoveNotation = 'O-O'
	elif(board.castlingLong is True):
		currMoveNotation = 'O-O-O'
	elif(isAttacking):
		currMoveNotation += piece.letter + add + 'x' + chr(ord('a') + x) + str(8 - y)
	elif(isPawn(piece.letter)):
		currMoveNotation += piece.letter + str(8 - y)
	else:
		currMoveNotation += piece.letter + add + chr(ord('a') + x) + str(8 - y)

	if(board.promotionTo != ''):
		currMoveNotation += '=' + board.promotionTo

	original = piece.movingThisPiece
	piece.movingThisPiece = True
	if(isPseudoLegal(x, y, False, board)):
		currMoveNotation += '+'
	piece.movingThisPiece = original

	if((currMoveNotation == 'Kg1' or currMoveNotation == 'Kg8') and piece.canCastleShort(6, (7 if piece.isWhite else 0), board) is True):
		currMoveNotation = 'O-O'
	elif((currMoveNotation == 'Kc1' or currMoveNotation == 'Kc8') and piece.canCastleLong(3, (7 if piece.isWhite else 0), board) is True):
		currMoveNotation = 'O-O-O'

	return currMoveNotation

#LAN notation
def getLAN(piece, x, y, board):
	currMoveNotation = chr(ord('a') + piece.matrixX) + str(8 - piece.matrixY) + chr(ord('a') + x) + str(8 - y)
	if(board.promotionTo != ''):
		currMoveNotation += board.promotionTo.lower()
		board.promotionTo = ''
	currMoveNotation += ' ' 
	return currMoveNotation

#from LAN to SAN
def LANtoSAN(move, board, static):
	# print(move)
	startX = ord(move[0]) - 97
	startY = 8 - int(move[1])

	piece = board.getPieceAt(startX, startY)
	assert(piece is not None)

	x = ord(move[2]) - 97
	y = 8 - int(move[3])

	isAttacking = False
	if(isPawn(piece.letter)):
		if(piece.isWhite and startY == 3):
			if(abs(startX - x) == 1 and board.isPieceAt(x, y) is False):
				isAttacking = True
		if(not piece.isWhite and startY == 4):
			if(abs(startX - x) == 1 and board.isPieceAt(x, y) is False):
				isAttacking = True

	if(board.isPieceAt(x, y) is True):
		isAttacking = True

	if(len(move) == 5):
		if(againstAI):
			board.autoPromote = True
		board.promotionTo = move[4].upper()

	ret = getSAN(piece, x, y, isAttacking, board)

	# print(ret)
	if(againstAI):
		piece.movingThisPiece = True
		moveTo(x, y, board, static)

	board.promotionTo = ''
	return ret

#fix notations

#update notations per move
def updateNotation(piece, x, y, isAttacking, board):
	global moveNotation
	global LAN

	currMoveNotation = getSAN(piece, x, y, isAttacking, board)

	LAN.append(getLAN(piece, x, y, board))
	moveNotation.append(currMoveNotation)

	gameNotation.changeGameNotation(moveNotation, callback)

#moving of pieces
def moveTo(x, y, board, static):
	global movingPiece
	global analyzingMode
	global moveNotation

	for piece in (board.whitePieces if board.whitesMove else board.blackPieces):
		if(piece.movingThisPiece is True):
			if(isPseudoLegal(x, y, True, board) is False and piece.canMove(x, y, board) is True):
				attacking = board.getPieceAt(x, y)
				if(attacking is not None):
					attacking.isTaken = True
					attacking.show()

				if(isPawn(piece.letter)):
					if((piece.isWhite and y == 0) or (not piece.isWhite and y == 7)):
						board.promotion = True
						if not board.autoPromote:
							popup_bonus(piece, x, y, board.whitesMove, board)
							while(board.promotion):
								root.update()
						else:
							promoteTo(None, piece, board.promotionTo, x, y, board)
							board.autoPromote = False

				if static is False:
					updateNotation(piece, x, y, True if attacking is not None else False, board)

				
				if(isPawn(piece.letter)):
					piece.letter = chr(ord('a') + x)

				#move the piece, change turns
				piece.move(x, y, board)
				
				if(board.enpassant):
					piece.enpassant.isTaken = True
					piece.enpassant.show()
					board.enpassant = False

				#if enpassant set to False
				if(board.whitesMove):
					for piece in board.whitePieces:
						if(piece.isTaken is False and isPawn(piece.letter)):
							piece.canEnpassant = False
				else:
					for piece in board.blackPieces:
						if(piece.isTaken is False and isPawn(piece.letter)):
							piece.canEnpassant = False

				#if castling
				if(board.castlingShort):
					# board.whitesMove = not board.whitesMove
					for piece in (board.whitePieces if board.whitesMove else board.blackPieces):
						if(piece.letter == 'R' and piece.isRight is True):
							piece.move(5,y, board)
					board.castlingShort = False

				if(board.castlingLong):
					# board.whitesMove = not board.whitesMove
					for piece in (board.whitePieces if board.whitesMove else board.blackPieces):
						if(piece.letter == 'R' and piece.isRight is False):
							piece.move(3,y, board)
					board.castlingLong = False

				if(static is False):
					stopThread()
					if(analyzingMode):
						startThread()

				board.whitesMove = not board.whitesMove
				isGameOver(board, static)
				return True
			else:
				piece.movingThisPiece = False
	return False

#mouse B1 press
def moveB1(event):
	global curr_board
	global movingPiece
	global arrows

	for each in arrows:
		boardFrame.canvas.delete(each)

	for each in circles:
		boardFrame.canvas.delete(each)
	arrows.clear()
	circles.clear()
	x = math.floor((event.x - startX)/pieceSize)
	y = math.floor((event.y - startY)/pieceSize)
	if(curr_board.flipped):
		x = 7 - x
		y = 7 - y

	movingPiece = curr_board.getPieceAt(x, y)
	if(movingPiece is not None and ((movingPiece.isWhite and not curr_board.whitesMove) or (movingPiece.isWhite is False and curr_board.whitesMove))):
		movingPiece = None

#mouse B1 motion
def motionB1(event):
	global curr_board
	global movingPiece
	
	if(movingPiece is None):
		return

	movingPiece.show(anchorPos='center', pixelPosX=event.x, pixelPosY=event.y)

#mouse B1 release
def releaseB1(event):
	global movingPiece
	global curr_index
	global curr_board
	# global last_tag
	
	if(movingPiece is None):
		return
	x = math.floor((event.x - startX)/pieceSize)
	y = math.floor((event.y - startY)/pieceSize)
	if(curr_board.flipped):
		x = 7 - x
		y = 7 - y

	while(curr_index != len(moveNotation) - 1):
		forward(True, moveNotation, curr_board, False)

	try:
		gameNotation.scrolledtext.tag_config(gameNotation.last_tag, foreground='black', font=('consolas', '12', 'normal')) 
		gameNotation.last_tag = 'tag' + str(len(moveNotation)-1)
		gameNotation.scrolledtext.tag_config(gameNotation.last_tag, foreground="black", background='#ADD8E6', font=('bold'))
	except:
		pass

	if(movingPiece is not None):
		movingPiece.movingThisPiece = True
		if(not moveTo(x, y, curr_board, False)):
			movingPiece.show()
		else:
			curr_index += 1
			if(againstAI):
				root.update()
				runEngine()
	else:
		movingPiece.show()

def create_circle(x, y, r, canvasName):
    x0 = x - r
    y0 = y - r
    x1 = x + r
    y1 = y + r
    return canvasName.create_oval(x0, y0, x1, y1, outline=color, width=3)

def moveB3(event):
	global lineX
	global lineY

	x = math.floor((event.x - startX)/pieceSize)
	y = math.floor((event.y - startY)/pieceSize)

	lineX = x*pieceSize + startX + pieceSize/2
	lineY = y*pieceSize + startY + pieceSize/2

	arrows.append(None)

def motionB3(event):
	if(arrows[-1]):
		boardFrame.canvas.delete(arrows[-1])

	x = math.floor((event.x - startX)/pieceSize)
	y = math.floor((event.y - startY)/pieceSize)

	newX = x*pieceSize + startX + pieceSize/2
	newY = y*pieceSize + startY + pieceSize/2

	arrows[-1] = boardFrame.canvas.create_line(lineX, lineY, newX, newY, width = 8, arrow=tk.LAST, arrowshape= (15, 15, 8), fill=color)

def releaseB3(event):
	if(arrows[-1]):
		boardFrame.canvas.delete(arrows[-1])

	x = math.floor((event.x - startX)/pieceSize)
	y = math.floor((event.y - startY)/pieceSize)

	newX = x*pieceSize + startX + pieceSize/2
	newY = y*pieceSize + startY + pieceSize/2

	arrows[-1] = boardFrame.canvas.create_line(lineX, lineY, newX, newY, width = 10, arrow=tk.LAST, arrowshape= (15, 15, 8), fill=color)
	
	if(newX == lineX and newY == lineY):
		circles.append(create_circle(newX, newY, pieceSize/2, boardFrame.canvas))

#check if letter betwn a-h
def isPawn(a):
	if(a >= 'a' and a <= 'h'):
		return True
	return False

#move through gamenotation forward by 1 move
def forward(static, moveNotation, board, fromBackward):
	global curr_index
	# global last_tag
	
	curr_index += 1
	if(curr_index >= len(moveNotation)):
		return

	notation = moveNotation[curr_index]
	n = len(notation)
	#check or mate notation
	if(notation[n-1] == '+' or notation[n-1] == '#'):
		notation = notation[:-1]
		n -= 1

	#promotion notation
	if(notation[n-2] == '='):
		board.autoPromote = True
		board.promotionTo = notation[n-1]
		notation = notation[:-2]
		n -= 2
		
	movingPieceLetter = notation[0]
	#castling notation
	if(movingPieceLetter == 'O'):
		if(n == 3):
			if(curr_index % 2 == 0):
				curr_board.whitePieces[0].movingThisPiece = True
				moveTo(6, 7, curr_board, static)
			else:
				curr_board.blackPieces[0].movingThisPiece = True
				moveTo(6, 0, curr_board, static)
		else:
			if(curr_index % 2 == 0):
				moving = True
				curr_board.whitePieces[0].movingThisPiece = True
				moveTo(2, 7, curr_board, static)
			else:
				moving = True
				curr_board.blackPieces[0].movingThisPiece = True
				moveTo(2, 0, curr_board, static)

	#pawn movement notation
	elif(n == 2):
		x = ord(notation[0]) - 97
		y = 8 - int(notation[1])
		for piece in (curr_board.whitePieces if curr_index % 2 == 0 else curr_board.blackPieces):
			if(piece.letter == movingPieceLetter and piece.canMove(x, y, curr_board)):
				piece.movingThisPiece = True
				moveTo(x, y, curr_board, static)
		
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
				moveTo(x, y, curr_board, static)

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
				moveTo(x, y, curr_board, static)

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
				moveTo(x, y, curr_board, static)

	elif(notation == '1/2-1/2'):
		myLabel.config(text="Game ended in a draw")
		return

	gameNotation.scrolledtext.tag_config(gameNotation.last_tag, foreground='black', background='white', font=('consolas', '12', 'normal')) 
	gameNotation.last_tag = 'tag' + str(curr_index)
	gameNotation.scrolledtext.tag_config(gameNotation.last_tag, foreground="black", background='#ADD8E6', font=('bold'))

	if(not fromBackward):
		stopThread()
		if(analyzingMode):
			startThread()

#move through gamenotation backward by 1move
def backward():
	global curr_index
	global curr_board
	# global last_tag

	temp = curr_index - 1

	curr_board.destroy()
	curr_board = Board(boardFrame, pieceImage)
	curr_board.show()
	curr_index = -1

	if(temp < 0):
		curr_index = -1
		return

	i = 0
	while i <= temp:
		forward(True, moveNotation, curr_board, True)
		i += 1

	gameNotation.scrolledtext.tag_config(gameNotation.last_tag, foreground='black', background='white', font=('consolas', '12', 'normal')) 
	gameNotation.last_tag = 'tag' + str(curr_index)
	gameNotation.scrolledtext.tag_config(gameNotation.last_tag, foreground="black", background='#ADD8E6', font=('bold'))
	stopThread()
	if(analyzingMode):
		startThread()
	# curr_index = temp

#new game
def new():
	global curr_board
	global curr_index
	global movingPiece
	global moveNotation
	global LAN
	global againstAI
	global playComputerButton
	global analyzingMode

	curr_board.destroy()
	curr_board = Board(boardFrame, pieceImage)
	curr_board.show()
	curr_index = -1
	movingPiece = None
	moveNotation = []
	LAN = []
	gameNotation.scrolledtext.configure(state='normal')
	gameNotation.scrolledtext.delete(1.0, tk.END)
	myLabel.config(text='')
	playComputerButton.config(text='Play Computer')
	againstAI = False
	stopThread()
	if(analyzingMode):
		startThread()

	for each in arrows:
		boardFrame.canvas.delete(each)

	arrows.clear()

	for each in circles:
		boardFrame.canvas.delete(each)

	circles.clear()

	# evalBar(0)

#flip the board
def flip():
	global curr_board

	curr_board.flipBoard()

#initialize engine
def initEngine():
	global engine

	file = os.getcwd() + '/stockfish13'
	engine = sb.Popen(file, stdin=sb.PIPE, stdout=sb.PIPE, stderr=sb.STDOUT)
	put(b'uci\n', inf_list, 0, b'isready\n', 'readyok')
	put(b'setoption name Hash value 128\n', inf_list, 0, b'isready\n', 'readyok')
	put(b'setoption name Multipv value 3\n', inf_list, 0, b'isready\n', 'readyok')
	myLabel.config(text='Engine Loaded')

#put commands to engine
def put(command, inf_list, tmp_time, stopText, stopMatch):

	engine.stdin.write(command)
	engine.stdin.flush()
	time.sleep(tmp_time)

	if command != "quit":
		engine.stdin.write(stopText)     
		engine.stdin.flush()
		while True:
			text = engine.stdout.readline().strip()
			res = text.decode().split()
			if len(res) > 0 and res[0] == stopMatch:
				inf_list.append(text)
				break
			elif text !='':
				inf_list.append(text)

	engine.stdout.flush()

def runAnalysis(LAN):
	global inf_list
	global myLabel
	global engine
	global curr_board
	global againstAI
	global evaluation

	if(engine is None):
		initEngine()

	lan = ''

	if(gameNotation.last_tag):
		cnt = int(gameNotation.last_tag[3:len(gameNotation.last_tag)])
		if(cnt >= 0):
			for each in range(cnt+1):
				lan += LAN[each]
	command = b'position startpos moves ' + lan.encode() + b'\n'
	print(command)
	engine.stdin.write(command)
	engine.stdin.flush()
	
	engine.stdin.write(b'go\n')     
	engine.stdin.flush()

	#white tunr - pos +, neg -
	#black turn - neg +, pos -
	while True:
		text = engine.stdout.readline().strip().decode().split()
		if(len(text) <= 0):
			continue
		if(text[0] == 'bestmove'):
			break
		if(text[0] != 'info' or text[3] != 'seldepth' or text[10] == 'lowerbound' or text[10] == 'upperbound'):
			continue
		try:
			#b'info depth 30 seldepth 37 multipv 1 score cp -25 
			#nodes 36537530 nps 922758 hashfull 1000 tbhits 0 time 39596 pv'
			depth = text[2] + '/' + text[4]
			score = ''
			lineInfo = ''
			cp = int(text[9])
			if(not curr_board.whitesMove):
				cp *= -1
			if(text[8] == 'mate'):
				score = ('+' if cp > 0 else '-') + 'M' + str(abs(cp))
			else:
				score = str(float(cp/100))
			line = text[6]
			clone_board = curr_board.clone()
			againstAI = True
			cnt = 0
			for each in text:
				if cnt >= 12:
					break
				if(len(each) == 4 or len(each) == 5):
					if(isPawn(each[0]) and isPawn(each[2]) and (not each[1].isalpha() and int(each[1]) >= 1 and int(each[1]) <= 8) and (not each[3].isalpha() and int(each[3]) >= 1 and int(each[3]))):
						cnt += 1
						try:
							moveInSAN = LANtoSAN(each, clone_board, True)
						except:
							break
						lineInfo += moveInSAN + ' '

			line = int(line) - 1
			engineEval.evalLines[line][0].config(text=depth)
			engineEval.evalLines[line][1].config(text=score)
			engineEval.evalLines[line][2].config(text=lineInfo)
			
			if(line == 0):
				evaluation = score

		except Exception as e:
			continue
		finally:
			clone_board.destroy()
			againstAI = False

def analysisMode():
	global analyzingMode

	if(againstAI):
		myLabel.config(text='Analysis cannot be done while playing againstAI')
		return

	analyzingMode = not analyzingMode

	if(analyzingMode):
		analysisButton.config(relief='sunken')
		startThread()
	else:
		stopThread()
		analysisButton.config(relief='raised')

def startThread():
	global LAN
	global analyzingThread

	analyzingThread = threading.Thread(target=runAnalysis, args=(LAN,), daemon=True)
	analyzingThread.start()

def stopThread():
	global analyzingThread
	global engine

	if(analyzingThread is None):
		return
	if(not analyzingThread.is_alive()):
		return

	engine.stdin.write(b'stop\n')
	engine.stdin.flush()

	while(analyzingThread.is_alive()):
		myLabel.config(text='◌')
		root.update()

	engine.stdin.write(b'isready\n')
	engine.stdin.flush()

	while True:
		text = engine.stdout.readline().strip()
		res = text.decode().split()
		if len(res) > 0 and res[0] == 'readyok':
			break

	for each in range(0, engineEval.lines):
			for x in range(0, 3):
				engineEval.evalLines[each][x].configure(text='')

	print("Stopped")

#choose commands for engine
def runEngine():
	global LAN
	global inf_list
	global engine
	global curr_board
	global analyzingMode
	# global last_tag
	global evaluation

	if isGameOver(curr_board, True) or analyzingMode:
		return
	if engine is None:
		initEngine()
	inf_list.clear()

	lan = ''

	if(gameNotation.last_tag):
		cnt = int(gameNotation.last_tag[3:len(gameNotation.last_tag)])
		if(cnt >= 0):
			for each in range(cnt+1):
				lan += LAN[each]
	command = b'position startpos moves ' + lan.encode() + b'\n'
	put(command, inf_list, 0, b'isready\n', 'readyok')

	command = b'go\n'
	put(command, inf_list, 2, b'stop\n', 'bestmove')

	result = inf_list[-1].decode().split()
	text = inf_list[-2].decode().split()
	inf_list.clear()

	move = ''
	try:
		move = LANtoSAN(result[1], curr_board, False)
		cp = int(text[9])
		if(not curr_board.whitesMove):
			cp *= -1
		if(text[8] == 'mate'):
			score = ('+' if cp > 0 else '-') + 'M' + str(abs(cp))
		else:
			score = str(float(cp/100))
		evaluation = score
	except:
		for each in result:
			if(len(each) == 4 or len(each) == 5):
				if(isPawn(each[0]) and isPawn(each[2]) and (not each[1].isalpha() and int(each[1]) >= 1 and int(each[1]) <= 8) and (not each[3].isalpha() and int(each[3]) >= 1 and int(each[3]))):
					move = LANtoSAN(each, curr_board, False)
					break
	myLabel.config(text='Best Move: ' + move)
	return move


def evalBar():
	global evalLines
	global evaluation

	# print(evaluation)
	edge = 0
	if(evaluation):
		if(evaluation[1] == 'M'):
			if(evaluation[0] == '+'):
				edge = 200
			else:
				edge = -200
		else:
			edge = min(float(evaluation)*40, 180)
			if(edge < -180):
				edge = -180
	# if()
	for y in range(1, 400):
		if(evalLines[y]):
			boardFrame.canvas.delete(evalLines[y])
		if(y == 0.5*400):
			evalLines[y] = boardFrame.canvas.create_line(0, y, startX-5, y, width=5, fill=color)
		elif(y == 0.125*400 or y == 0.25*400 or y == 0.375*400):
			evalLines[y] = boardFrame.canvas.create_line(0, y, startX-5, y, width=1, fill='black')
		elif(y == 0.625*400 or y == 0.75*400 or y == 0.875*400):
			evalLines[y] = boardFrame.canvas.create_line(0, y, startX-5, y, width=1, fill='black')
		elif(y < (0.5*400 - edge)): 
			evalLines[y] = boardFrame.canvas.create_line(0, y, startX-5, y, fill='grey')
		else: 
			evalLines[y] = boardFrame.canvas.create_line(0, y, startX, y, fill='#FAEBD7')
	root.after(100, evalBar)

#play against stockfish
def play_computer():
	global againstAI
	global engine
	global moveNotation

	if(analyzingMode):
		myLabel.config(text='Analysis cannot be done while playing againstAI')
		return

	if engine is None:
		initEngine()

	againstAI = not againstAI

	if(againstAI):
		playComputerButton.config(text='Vs Player', relief='sunken')
	else:
		playComputerButton.config(text='Vs Computer', relief='raised')

#stockfish vs stockfish
def compMode(board):
	global stopped
	global firstTime
	global engine
	global moveNotation
	global analyzingMode

	if(analyzingMode):
		myLabel.config(text='Analysis cannot be done while playing againstAI')
		return

	if(not firstTime):
		stopped = True
		return

	betweenEngine.config(relief='sunken')
	firstTime = False
	if engine is None:
		initEngine()

	if(curr_index != len(moveNotation) - 1):
		while(curr_index != len(moveNotation) - 1):
			forward(True, moveNotation, board, True)

	engineMoves=[]
	for each in moveNotation:
		engineMoves.append(each)
	while not isGameOver(board, False) and not stopped:
		engineMoves.append(runEngine())
		forward(False, engineMoves, board, True)
		root.update()

	betweenEngine.config(relief='raised')
	stopped = False
	firstTime = True

#promotion select window
def popup_bonus(piece, x, y, whitesMove, board):

	promotionWin = tk.Toplevel(root)
	promotionWin.title("Promote To")
	promotionWin.geometry("%dx%d+%d+%d" % (220, 60, pieceSize, pieceSize if whitesMove else pieceSize*7))
	promotionWin.overrideredirect(True) 

	rook = tk.Label(promotionWin, image=pieceImage.pieces_white[0] if whitesMove else pieceImage.pieces_black[0], anchor='nw')
	rook.grid(row=0, column=0)

	queen = tk.Label(promotionWin, image=pieceImage.pieces_white[2] if whitesMove else pieceImage.pieces_black[2], anchor='nw')
	queen.grid(row=0, column=1)

	bishop = tk.Label(promotionWin, image=pieceImage.pieces_white[3] if whitesMove else pieceImage.pieces_black[3], anchor='nw')
	bishop.grid(row=0, column=2)

	knight = tk.Label(promotionWin, image=pieceImage.pieces_white[4] if whitesMove else pieceImage.pieces_black[4], anchor='nw')
	knight.grid(row=0, column=3)

	rook.bind("<Button-1>",lambda event, piece=piece, x=x, y=y, which="R", board=board : promoteTo(event, piece, which, x, y, board))
	queen.bind("<Button-1>",lambda event, piece=piece, x=x, y=y, which="Q", board=board : promoteTo(event, piece, which, x, y, board))
	bishop.bind("<Button-1>",lambda event, piece=piece, x=x, y=y, which="B", board=board : promoteTo(event, piece, which, x, y, board))
	knight.bind("<Button-1>",lambda event, piece=piece, x=x, y=y, which="N", board=board : promoteTo(event, piece, which, x, y, board))

#search database for games
def searchDB(moveNotation):
	db = open('chessdotcomdb.json', 'r')
	data = json.load(db)
	addon.dbInfo.configure(state='normal')
	addon.dbInfo.delete(1.0, tk.END)

	asWhite = 0
	asBlack = 0
	nextWhite = {}
	nextBlack = {}
	for game in data['match']:
		n1 = len(moveNotation)
		n2 = len(game['moves'])
		flag = False
		i = 0
		j = 0
		while(i < n1 and j < n2 and moveNotation[i] == game['moves'][j]):
			i += 1
			j += 1

		if(i == n1 and j < n2):
			if(game['isWhite']):
				asWhite += 1
				try:
					nextWhite[game['moves'][j]] += 1
				except:
					nextWhite[game['moves'][j]] = 1
			else:
				asBlack += 1
				try:
					nextBlack[game['moves'][j]] += 1
				except:
					nextBlack[game['moves'][j]] = 1

	addon.dbInfo.insert(tk.END, 'You have reached this position as White %d times\n' % asWhite)

	for key, value in sorted(nextWhite.items(), key=lambda item: item[1], reverse=True):
		addon.dbInfo.insert(tk.END, 'Move: %s - %d times\n' % (key, value))

	addon.dbInfo.insert(tk.END, '\nYou have reached this position as Black %d times\n' % asBlack)

	for key, value in sorted(nextBlack.items(), key=lambda item: item[1], reverse=True):
		addon.dbInfo.insert(tk.END, 'Move: %s - %d times\n' % (key, value))

	addon.dbInfo.configure(state='disabled')

#load pgn
def loadPGN():
	global curr_index
	global curr_board

	new()
	moves = addon.pgnText.get('1.0', tk.END).split()
	print(moves)
	move = []
	length = len(moves)
	moveNo = 1
	j = 0
	while j < length:
		if(moves[j] == '{'):
			while(moves[j] != '}'):
				j += 1 
		if(moves[j] == (str(moveNo) + '.')): 
			turn = ""
			try:
				turn += moves[j]
				move.append(moves[j+1])
				move.append(moves[j+2])
				moveNo = moveNo + 1
			except:
				break
		j = j+1

	print(move)
	for each in move:
		forward(False, move, curr_board, True)

	addon.pgnText.delete(1.0, tk.END)
	addon.pgnText.insert(tk.END, "PGN Loaded\n")

engine = None
inf_list = []

def callback(event, tag, moveNo):
	global curr_index
	global analyzingMode

	index = event.widget.index("@%s,%s" % (event.x, event.y))
	tag_indices = list(event.widget.tag_ranges(tag))

	move = ''
	for start, end in zip(tag_indices[0::2], tag_indices[1::2]):
		if event.widget.compare(start, '<=', index) and event.widget.compare(index, '<', end):
			move = event.widget.get(start, end)
			move = move.strip().rstrip()
			break

	start = 0
	index = -1
	for each in range(len(moveNotation)):
		if(each % 2 == 0):
			start += 1
		if(moveNotation[each] == move and start == moveNo):
			index = each
			break

	assert(index != -1)
	curr_index = index + 1
	backward()



#Additional Text
myLabel = tk.Label(root, text="")
myLabel.grid(row=1, column=0)

#Go through game
arrowFrame = tk.Frame(root)
backwardButton = tk.Button(arrowFrame, text="<-", command=backward)
forwardButton = tk.Button(arrowFrame, text="->", command=lambda: forward(True, moveNotation, curr_board, False))
arrowFrame.grid(row=1, column=1)
backwardButton.grid(row=1, column=0, padx=padding, pady=padding)
forwardButton.grid(row=1, column=1, padx=padding, pady=padding)

#Major Buttons
buttonsRow0 = tk.Frame(root)
buttonsRow1 = tk.Frame(root)
newButton = tk.Button(buttonsRow0, text="New Game", command=new)
flipButton = tk.Button(buttonsRow0, text="Flip Board", command=flip)
analysisButton = tk.Button(buttonsRow0, text="Analysis Mode", command=analysisMode)
playComputerButton = tk.Button(buttonsRow1, text="Vs Computer", command=play_computer)
betweenEngine = tk.Button(buttonsRow1, text="Comp Vs Comp", command=lambda: compMode(curr_board))
buttonsRow0.grid(row=2, column=0)
buttonsRow1.grid(row=3, column=0)
newButton.grid(row=0, column=0, padx=padding, pady=padding)
flipButton.grid(row=0, column=1, padx=padding, pady=padding)
analysisButton.grid(row=0, column=2, padx=padding, pady=padding)
playComputerButton.grid(row=0, column=0, padx=padding, pady=padding)
betweenEngine.grid(row=0, column=1, padx=padding, pady=padding)

	
def init_canvas(boardFrame):
	boardFrame.canvas.create_image(startX,startY, image=pieceImage.boardImage, anchor="nw")
	boardFrame.canvas.bind('<Button-1>', moveB1)
	boardFrame.canvas.bind('<B1-Motion>', motionB1)
	boardFrame.canvas.bind('<ButtonRelease-1>', releaseB1)
	boardFrame.canvas.bind('<Button-3>', moveB3)
	boardFrame.canvas.bind('<B3-Motion>', motionB3)
	boardFrame.canvas.bind('<ButtonRelease-3>', releaseB3)

if __name__ == "__main__":
	pieceImage = PieceImage(root)
	boardFrame = BoardFrame(root)
	addon = AddOn(root)
	engineEval = EngineEvals(root, lines=3)
	
	addon.searchDbButton.configure(command=lambda: searchDB(moveNotation))
	addon.loadPGN.configure(command=loadPGN)
	addon.generateFEN.configure(command=genFEN)
	addon.loadFEN.configure(command=loadFEN)

	init_canvas(boardFrame)

	evalBar()
	gameNotation = GameNotation(root)
	curr_board = Board(boardFrame, pieceImage)
	curr_board.show()
	root.mainloop()
