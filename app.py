from flask import Flask, render_template, request, jsonify
from board import ChessBoard


app = Flask(__name__)
# Create a global chess board instance
chess_board = ChessBoard()

@app.route('/')
def index():
    """Render the main chess game page"""
    return render_template('index.html')

@app.route('/api/board', methods=['GET'])
def get_board():
    """Return the current state of the chess board"""
    return jsonify(chess_board.get_board_state())

@app.route('/api/move', methods=['POST'])
def make_move():
    """Process a move request from the frontend"""
    data = request.get_json()
    from_pos = data.get('from')
    to_pos = data.get('to')
    
    # Validate and make the move
    result = chess_board.move_piece(from_pos, to_pos)
    
    # Return the result and new board state
    return jsonify({
        'success': result['valid'],
        'message': result.get('message', ''),
        'board': chess_board.get_board_state(),
        'check': chess_board.is_in_check(),
        'checkmate': chess_board.is_checkmate(),
        'current_player': chess_board.get_current_player()
    })

@app.route('/api/reset', methods=['POST'])
def reset_game():
    """Reset the chess game to initial state"""
    chess_board.reset()
    return jsonify({
        'success': True,
        'board': chess_board.get_board_state(),
        'current_player': chess_board.get_current_player()
    })

if __name__ == '__main__':
    app.run(debug=True, port=5001)
