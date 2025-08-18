class ChessBoard:
    def __init__(self):
        """Initialize a new chess board with pieces in starting positions"""
        self.reset()
    
    def reset(self):
        """Reset the board to the starting position"""
        # Initialize an 8x8 board
        self.board = [[None for _ in range(8)] for _ in range(8)]
        
        # Set up the current player (white goes first)
        self.current_player = 'white'
        
        # Track kings' positions for check/checkmate detection
        self.king_positions = {'white': (7, 4), 'black': (0, 4)}
        
        # Set up pawns
        for col in range(8):
            self.board[1][col] = {'type': 'pawn', 'color': 'black', 'has_moved': False}
            self.board[6][col] = {'type': 'pawn', 'color': 'white', 'has_moved': False}
        
        # Set up rooks
        self.board[0][0] = {'type': 'rook', 'color': 'black', 'has_moved': False}
        self.board[0][7] = {'type': 'rook', 'color': 'black', 'has_moved': False}
        self.board[7][0] = {'type': 'rook', 'color': 'white', 'has_moved': False}
        self.board[7][7] = {'type': 'rook', 'color': 'white', 'has_moved': False}
        
        # Set up knights
        self.board[0][1] = {'type': 'knight', 'color': 'black'}
        self.board[0][6] = {'type': 'knight', 'color': 'black'}
        self.board[7][1] = {'type': 'knight', 'color': 'white'}
        self.board[7][6] = {'type': 'knight', 'color': 'white'}
        
        # Set up bishops
        self.board[0][2] = {'type': 'bishop', 'color': 'black'}
        self.board[0][5] = {'type': 'bishop', 'color': 'black'}
        self.board[7][2] = {'type': 'bishop', 'color': 'white'}
        self.board[7][5] = {'type': 'bishop', 'color': 'white'}
        
        # Set up queens
        self.board[0][3] = {'type': 'queen', 'color': 'black'}
        self.board[7][3] = {'type': 'queen', 'color': 'white'}
        
        # Set up kings
        self.board[0][4] = {'type': 'king', 'color': 'black', 'has_moved': False}
        self.board[7][4] = {'type': 'king', 'color': 'white', 'has_moved': False}
        
        # Game state
        self.game_over = False
        self.winner = None
    
    def get_board_state(self):
        """Return the current state of the board for the frontend"""
        return {
            'board': self.board,
            'current_player': self.current_player,
            'game_over': self.game_over,
            'winner': self.winner
        }
    
    def get_current_player(self):
        """Return the current player's color"""
        return self.current_player
    
    def move_piece(self, from_pos, to_pos):
        """
        Attempt to move a piece from from_pos to to_pos
        from_pos and to_pos are tuples of (row, col)
        Returns a dict with the result of the move attempt
        """
        from_row, from_col = from_pos
        to_row, to_col = to_pos
        
        # Check if positions are valid
        if not self._is_valid_position(from_row, from_col) or not self._is_valid_position(to_row, to_col):
            return {'valid': False, 'message': 'Invalid position'}
        
        # Check if there's a piece at the starting position
        piece = self.board[from_row][from_col]
        if piece is None:
            return {'valid': False, 'message': 'No piece at starting position'}
        
        # Check if it's the correct player's turn
        if piece['color'] != self.current_player:
            return {'valid': False, 'message': "It's not your turn"}
        
        # Check if the move is valid for this piece
        if not self._is_valid_move(from_pos, to_pos):
            return {'valid': False, 'message': 'Invalid move for this piece'}
        
        # Make the move
        captured_piece = self.board[to_row][to_col]
        self.board[to_row][to_col] = piece
        self.board[from_row][from_col] = None
        
        # Update king position if king was moved
        if piece['type'] == 'king':
            self.king_positions[piece['color']] = (to_row, to_col)
        
        # Mark that the piece has moved (for pawns, kings, rooks)
        if 'has_moved' in piece:
            piece['has_moved'] = True
        
        # Check if the move puts the player in check (illegal)
        if self.is_in_check(piece['color']):
            # Undo the move
            self.board[from_row][from_col] = piece
            self.board[to_row][to_col] = captured_piece
            if piece['type'] == 'king':
                self.king_positions[piece['color']] = (from_row, from_col)
            return {'valid': False, 'message': 'This move would put you in check'}
        
        # Switch to the other player's turn
        self.current_player = 'black' if self.current_player == 'white' else 'white'
        
        # Check for checkmate
        if self.is_checkmate():
            self.game_over = True
            self.winner = 'black' if self.current_player == 'white' else 'white'
        
        return {'valid': True}
    
    def _is_valid_position(self, row, col):
        """Check if a position is on the board"""
        return 0 <= row < 8 and 0 <= col < 8
    
    def _is_valid_move(self, from_pos, to_pos):
        """Check if a move is valid for the piece at from_pos"""
        from_row, from_col = from_pos
        to_row, to_col = to_pos
        piece = self.board[from_row][from_col]
        target = self.board[to_row][to_col]
        
        # Can't capture your own piece
        if target and target['color'] == piece['color']:
            return False
        
        # Different movement rules for each piece type
        if piece['type'] == 'pawn':
            return self._is_valid_pawn_move(from_pos, to_pos)
        elif piece['type'] == 'rook':
            return self._is_valid_rook_move(from_pos, to_pos)
        elif piece['type'] == 'knight':
            return self._is_valid_knight_move(from_pos, to_pos)
        elif piece['type'] == 'bishop':
            return self._is_valid_bishop_move(from_pos, to_pos)
        elif piece['type'] == 'queen':
            return self._is_valid_queen_move(from_pos, to_pos)
        elif piece['type'] == 'king':
            return self._is_valid_king_move(from_pos, to_pos)
        
        return False
    
        def _is_valid_pawn_move(self, from_pos, to_pos):
        
            from_row, from_col = from_pos
            to_row, to_col = to_pos
            piece = self.board[from_row][from_col]
            target = self.board[to_row][to_col]
            
            # Direction depends on color
            direction = -1 if piece['color'] == 'white' else 1
            
            # Regular move (1 square forward)
            if from_col == to_col and to_row == from_row + direction and target is None:
                return True
            
            # Initial double move
            if (not piece['has_moved'] and from_col == to_col and 
                to_row == from_row + 2 * direction and 
                self.board[from_row + direction][from_col] is None and 
                target is None):
                return True
            
            # Capture diagonally
            if (abs(from_col - to_col) == 1 and to_row == from_row + direction and 
                target is not None and target['color'] != piece['color']):
                return True
            
            # TODO: En passant (not implemented in this basic version)
            
            return False
    
    def _is_valid_rook_move(self, from_pos, to_pos):
        """Check if a rook move is valid"""
        from_row, from_col = from_pos
        to_row, to_col = to_pos
        
        # Rooks move horizontally or vertically
        if from_row != to_row and from_col != to_col:
            return False
        
        # Check if path is clear
        return self._is_path_clear(from_pos, to_pos)
    
    def _is_valid_knight_move(self, from_pos, to_pos):
        """Check if a knight move is valid"""
        from_row, from_col = from_pos
        to_row, to_col = to_pos
        
        # Knights move in an L-shape: 2 squares in one direction and 1 in the perpendicular direction
        row_diff = abs(to_row - from_row)
        col_diff = abs(to_col - from_col)
        
        return (row_diff == 2 and col_diff == 1) or (row_diff == 1 and col_diff == 2)
    
    def _is_valid_bishop_move(self, from_pos, to_pos):
        """Check if a bishop move is valid"""
        from_row, from_col = from_pos
        to_row, to_col = to_pos
        
        # Bishops move diagonally
        if abs(to_row - from_row) != abs(to_col - from_col):
            return False
        
        # Check if path is clear
        return self._is_path_clear(from_pos, to_pos)
    
    def _is_valid_queen_move(self, from_pos, to_pos):
        """Check if a queen move is valid"""
        # Queens can move like rooks or bishops
        return self._is_valid_rook_move(from_pos, to_pos) or self._is_valid_bishop_move(from_pos, to_pos)
    
    def _is_valid_king_move(self, from_pos, to_pos):
        """Check if a king move is valid"""
        from_row, from_col = from_pos
        to_row, to_col = to_pos
        
        # Kings move one square in any direction
        row_diff = abs(to_row - from_row)
        col_diff = abs(to_col - from_col)
        
        # TODO: Castling (not implemented in this basic version)
        
        return row_diff <= 1 and col_diff <= 1
    
    def _is_path_clear(self, from_pos, to_pos):
        """Check if the path between from_pos and to_pos is clear of pieces"""
        from_row, from_col = from_pos
        to_row, to_col = to_pos
        
        # Determine direction of movement
        row_step = 0 if from_row == to_row else (1 if to_row > from_row else -1)
        col_step = 0 if from_col == to_col else (1 if to_col > from_col else -1)
        
        # Check each square along the path (excluding start and end)
        row, col = from_row + row_step, from_col + col_step
        while (row, col) != (to_row, to_col):
            if self.board[row][col] is not None:
                return False
            row += row_step
            col += col_step
        
        return True
    
    def is_in_check(self, color=None):
        """Check if the specified color's king is in check"""
        if color is None:
            color = self.current_player
        
        king_row, king_col = self.king_positions[color]
        opponent_color = 'black' if color == 'white' else 'white'
        
        # Check if any opponent piece can capture the king
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if piece and piece['color'] == opponent_color:
                    if self._is_valid_move((row, col), (king_row, king_col)):
                        return True
        
        return False
    
    def is_checkmate(self):
        """Check if the current player is in checkmate"""
        if not self.is_in_check():
            return False
        
        # Try all possible moves for all pieces of the current player
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if piece and piece['color'] == self.current_player:
                    # Try moving this piece to every square
                    for to_row in range(8):
                        for to_col in range(8):
                            if self._is_valid_move((row, col), (to_row, to_col)):
                                # Make the move temporarily
                                captured_piece = self.board[to_row][to_col]
                                self.board[to_row][to_col] = piece
                                self.board[row][col] = None
                                
                                # Update king position if king was moved
                                original_king_pos = None
                                if piece['type'] == 'king':
                                    original_king_pos = self.king_positions[piece['color']]
                                    self.king_positions[piece['color']] = (to_row, to_col)
                                
                                # Check if still in check
                                still_in_check = self.is_in_check(self.current_player)
                                
                                # Undo the move
                                self.board[row][col] = piece
                                self.board[to_row][to_col] = captured_piece
                                if original_king_pos:
                                    self.king_positions[piece['color']] = original_king_pos
                                
                                # If any move gets out of check, it's not checkmate
                                if not still_in_check:
                                    return False
        
        # If no move can get out of check, it's checkmate
        return True