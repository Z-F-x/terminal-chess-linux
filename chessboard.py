import curses
import random

pieces = {
    'r': '♜', 'n': '♞', 'b': '♝', 'q': '♛', 'k': '♚', 'p': '♟',
    'R': '♖', 'N': '♘', 'B': '♗', 'Q': '♕', 'K': '♔', 'P': '♙',
    '■': '■', '□': '□'
}

points = {
    'p': 1, 'P': 1,
    'n': '3+', 'N': '3+',
    'b': 3, 'B': 3,
    'r': 5, 'R': 5,
    'q': 9, 'Q': 9,
    'k': 0, 'K': 0  # Kings are invaluable
}

board = [
    ['r', 'n', 'b', 'q', 'k', 'b', 'n', 'r'],
    ['p', 'p', 'p', 'p', 'p', 'p', 'p', 'p'],
    ['■', '□', '■', '□', '■', '□', '■', '□'],
    ['□', '■', '□', '■', '□', '■', '□', '■'],
    ['■', '□', '■', '□', '■', '□', '■', '□'],
    ['□', '■', '□', '■', '□', '■', '□', '■'],
    ['P', 'P', 'P', 'P', 'P', 'P', 'P', 'P'],
    ['R', 'N', 'B', 'Q', 'K', 'B', 'N', 'R']
]

en_passant_target = None  # To track en passant opportunities
captured_by_white = []
captured_by_black = []

def print_board(stdscr, board):
    stdscr.clear()
    max_y, max_x = stdscr.getmaxyx()  # Get the size of the terminal window

    if max_y < 20 or max_x < 40:  # Check if terminal is too small
        stdscr.addstr(0, 0, "Terminal too small to display the board.")
        stdscr.refresh()
        return

    stdscr.addstr(0, 0, "  a b c d e f g h")
    
    for i, row in enumerate(board):
        stdscr.addstr(i + 1, 0, f"{8 - i} ")
        for j, piece in enumerate(row):
            stdscr.addstr(f"{pieces.get(piece, piece)} ")  # Display piece or square
        stdscr.addstr(f"{8 - i}")
    
    stdscr.addstr(9, 0, "  a b c d e f g h")

    # Display captured pieces and points
    if max_x >= 40:
        stdscr.addstr(2, 20, "Captured by White:")
        for idx, cap_piece in enumerate(captured_by_white):
            stdscr.addstr(3 + idx, 20, f"{pieces[cap_piece]} : {points[cap_piece]}")
        
        stdscr.addstr(6, 20, "Captured by Black:")
        for idx, cap_piece in enumerate(captured_by_black):
            stdscr.addstr(7 + idx, 20, f"{pieces[cap_piece]} : {points[cap_piece]}")
    
    stdscr.refresh()

def is_valid_move(board, move, color):
    global en_passant_target
    if len(move) != 4:
        return False
    start = move[:2]
    end = move[2:]
    if not (start[0] in 'abcdefgh' and start[1] in '12345678' and end[0] in 'abcdefgh' and end[1] in '12345678'):
        return False
    start_col, start_row = ord(start[0]) - ord('a'), 8 - int(start[1])
    end_col, end_row = ord(end[0]) - ord('a'), 8 - int(end[1])

    piece = board[start_row][start_col]
    target = board[end_row][end_col]

    if piece == '■' or piece == '□':
        return False

    if color == 'white' and not piece.isupper():
        return False
    if color == 'black' and not piece.islower():
        return False

    # Avoid moving into a square with a friendly piece
    if piece.isupper() and target.isupper():
        return False
    if piece.islower() and target.islower():
        return False

    # Movement rules for different pieces
    if piece.lower() == 'p':  # Pawn
        return is_valid_pawn_move(board, piece, start_row, start_col, end_row, end_col, color)
    elif piece.lower() == 'r':  # Rook
        return is_valid_rook_move(board, piece, start_row, start_col, end_row, end_col)
    elif piece.lower() == 'n':  # Knight
        return is_valid_knight_move(start_row, start_col, end_row, end_col)
    elif piece.lower() == 'b':  # Bishop
        return is_valid_bishop_move(board, piece, start_row, start_col, end_row, end_col)
    elif piece.lower() == 'q':  # Queen
        return is_valid_queen_move(board, piece, start_row, start_col, end_row, end_col)
    elif piece.lower() == 'k':  # King
        return is_valid_king_move(start_row, start_col, end_row, end_col)

    return False

def is_valid_pawn_move(board, piece, start_row, start_col, end_row, end_col, color):
    global en_passant_target
    direction = 1 if piece.islower() else -1  # Black pawns move down, white pawns move up
    start_piece = board[start_row][start_col]
    target_piece = board[end_row][end_col]
    # Moving forward
    if start_col == end_col:
        if target_piece in ['■', '□']:
            if end_row == start_row + direction:
                return True
            if end_row == start_row + 2 * direction and (start_row == 1 or start_row == 6):
                between_piece = board[start_row + direction][start_col]
                if between_piece in ['■', '□']:
                    return True
    # Diagonal capture
    elif abs(start_col - end_col) == 1 and end_row == start_row + direction:
        if target_piece != '■' and target_piece != '□':
            return True
        elif (end_row, end_col) == en_passant_target:
            return True
    return False

def is_valid_rook_move(board, piece, start_row, start_col, end_row, end_col):
    if start_row != end_row and start_col != end_col:
        return False
    step_row = 0 if start_row == end_row else (1 if end_row > start_row else -1)
    step_col = 0 if start_col == end_col else (1 if end_col > start_col else -1)
    current_row, current_col = start_row + step_row, start_col + step_col
    while (current_row != end_row or current_col != end_col):
        if board[current_row][current_col] != '■' and board[current_row][current_col] != '□':
            return False
        current_row += step_row
        current_col += step_col
    return True

def is_valid_bishop_move(board, piece, start_row, start_col, end_row, end_col):
    if abs(start_row - end_row) != abs(start_col - end_col):
        return False
    step_row = 1 if end_row > start_row else -1
    step_col = 1 if end_col > start_col else -1
    current_row, current_col = start_row + step_row, start_col + step_col
    while (current_row != end_row and current_col != end_col):
        if board[current_row][current_col] != '■' and board[current_row][current_col] != '□':
            return False
        current_row += step_row
        current_col += step_col
    return True

def is_valid_queen_move(board, piece, start_row, start_col, end_row, end_col):
    return is_valid_rook_move(board, piece, start_row, start_col, end_row, end_col) or \
           is_valid_bishop_move(board, piece, start_row, start_col, end_row, end_col)

def is_valid_knight_move(start_row, start_col, end_row, end_col):
    return (abs(start_row - end_row) == 2 and abs(start_col - end_col) == 1) or \
           (abs(start_row - end_row) == 1 and abs(start_col - end_col) == 2)

def is_valid_king_move(start_row, start_col, end_row, end_col):
    return max(abs(start_row - end_row), abs(start_col - end_col)) == 1

def move_piece(board, move, color):
    global en_passant_target
    start = move[:2]
    end = move[2:]
    start_col, start_row = ord(start[0]) - ord('a'), 8 - int(start[1])
    end_col, end_row = ord(end[0]) - ord('a'), 8 - int(end[1])

    piece = board[start_row][start_col]
    target_piece = board[end_row][end_col]

    # Handle en passant capture
    if piece.lower() == 'p' and abs(start_col - end_col) == 1 and (target_piece == '■' or target_piece == '□'):
        if (color == 'white' and (end_row, end_col) == en_passant_target):
            captured_piece = board[end_row + 1][end_col]
            board[end_row + 1][end_col] = '■' if (end_row + 1 + end_col) % 2 == 0 else '□'
            captured_by_white.append(captured_piece)
        elif color == 'black' and (end_row, end_col) == en_passant_target:
            captured_piece = board[end_row - 1][end_col]
            board[end_row - 1][end_col] = '■' if (end_row - 1 + end_col) % 2 == 0 else '□'
            captured_by_black.append(captured_piece)

    # Capture
    elif target_piece != '■' and target_piece != '□':
        if color == 'white':
            captured_by_white.append(target_piece)
        else:
            captured_by_black.append(target_piece)

    # Move piece
    board[start_row][start_col] = '■' if (start_row + start_col) % 2 == 0 else '□'  # Restore square color
    board[end_row][end_col] = piece

    # Update en passant target
    if piece.lower() == 'p' and abs(end_row - start_row) == 2:
        en_passant_target = ( (start_row + end_row) // 2, start_col )
    else:
        en_passant_target = None  # Reset if not a double pawn move

def get_all_legal_moves(board, color):
    moves = []
    for row in range(8):
        for col in range(8):
            piece = board[row][col]
            if (color == 'white' and piece.isupper()) or (color == 'black' and piece.islower()):
                for r in range(8):
                    for c in range(8):
                        move = f"{chr(col + ord('a'))}{8 - row}{chr(c + ord('a'))}{8 - r}"
                        if is_valid_move(board, move, color):
                            moves.append(move)
    return moves

def ai_make_move(board, color):
    legal_moves = get_all_legal_moves(board, color)
    if legal_moves:
        random_move = random.choice(legal_moves)
        move_piece(board, random_move, color)
        return random_move
    else:
        return None  # No legal moves, game over

def play_chess(stdscr):
    curses.curs_set(0)
    global en_passant_target

    stdscr.addstr(10, 0, "Do you want to play as 'white' or 'black'? ")
    stdscr.clrtoeol()
    player_color = stdscr.getstr(10, 38).decode('utf-8').lower()

    if player_color not in ['white', 'black']:
        stdscr.addstr(11, 0, "Invalid choice. Defaulting to 'white'.")
        player_color = 'white'

    ai_color = 'black' if player_color == 'white' else 'white'

    print_board(stdscr, board)

    while True:
        if player_color == 'white':  # Player's turn if white
            stdscr.addstr(11, 0, "Enter move (e.g., e2e4) or 'exit' to quit: ")
            stdscr.clrtoeol()
            move = stdscr.getstr(11, 40).decode('utf-8').lower()

            if move == "exit":
                break

            if is_valid_move(board, move, player_color):
                move_piece(board, move, player_color)
                print_board(stdscr, board)
            else:
                stdscr.addstr(12, 0, "Illegal move, try again.")
                stdscr.refresh()
                continue

            ai_move = ai_make_move(board, ai_color)
            if ai_move:
                stdscr.addstr(12, 0, f"AI moves {ai_move}   ")
                print_board(stdscr, board)
            else:
                stdscr.addstr(12, 0, "AI has no legal moves. You win!")
                stdscr.refresh()
                break
        else:  # AI moves first if player is black
            ai_move = ai_make_move(board, ai_color)
            if ai_move:
                stdscr.addstr(11, 0, f"AI moves {ai_move}   ")
                print_board(stdscr, board)
            else:
                stdscr.addstr(11, 0, "AI has no legal moves. You win!")
                stdscr.refresh()
                break

            stdscr.addstr(12, 0, "Enter move (e.g., e2e4) or 'exit' to quit: ")
            stdscr.clrtoeol()
            move = stdscr.getstr(12, 40).decode('utf-8').lower()

            if move == "exit":
                break

            if is_valid_move(board, move, player_color):
                move_piece(board, move, player_color)
                print_board(stdscr, board)
            else:
                stdscr.addstr(13, 0, "Illegal move, try again.")
                stdscr.refresh()
                continue

        # Clear messages if enough space
        if stdscr.getmaxyx()[0] > 14:
            stdscr.move(13, 0)
            stdscr.clrtoeol()
            stdscr.move(14, 0)
            stdscr.clrtoeol()

    stdscr.addstr(14, 0, "Game over. Press any key to exit.")
    stdscr.getch()

curses.wrapper(play_chess)

