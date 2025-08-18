javascript
document.addEventListener('DOMContentLoaded', function() {
    // DOM elements
    const chessBoard = document.getElementById('chess-board');
    const statusElement = document.getElementById('status');
    const messageElement = document.getElementById('message');
    const resetButton = document.getElementById('reset-btn');
    
    // Game state
    let boardState = null;
    let selectedSquare = null;
    let currentPlayer = 'white';
    
    // Piece images mapping
    const pieceImages = {
        'white': {
            'pawn': '♙',
            'rook': '♖',
            'knight': '♘',
            'bishop': '♗',
            'queen': '♕',
            'king': '♔'
        },
        'black': {
            'pawn': '♟',
            'rook': '♜',
            'knight': '♞',
            'bishop': '♝',
            'queen': '♛',
            'king': '♚'
        }
    };
    
    // Initialize the game
    initGame();
    
    // Event listeners
    resetButton.addEventListener('click', resetGame);
    
    // Functions
    function initGame() {
        fetchBoardState();
    }
    
    function fetchBoardState() {
        fetch('/api/board')
            .then(response => response.json())
            .then(data => {
                boardState = data.board;
                currentPlayer = data.current_player;
                renderBoard();
                updateStatus();
                
                if (data.game_over) {
                    handleGameOver(data.winner);
                }
            })
            .catch(error => {
                console.error('Error fetching board state:', error);
                messageElement.textContent = 'Error loading the game. Please try again.';
            });
    }
    
    function renderBoard() {
        // Clear the board
        chessBoard.innerHTML = '';
        
        // Create the squares
        for (let row = 0; row < 8; row++) {
            for (let col = 0; col < 8; col++) {
                const square = document.createElement('div');
                square.className = `square ${(row + col) % 2 === 0 ? 'white' : 'black'}`;
                square.dataset.row = row;
                square.dataset.col = col;
                
                // Add piece if there is one
                const piece = boardState[row][col];
                if (piece) {
                    const pieceElement = document.createElement('div');
                    pieceElement.className = 'piece';
                    pieceElement.textContent = pieceImages[piece.color][piece.type];
                    pieceElement.style.fontSize = '40px';
                    pieceElement.style.color = piece.color;
                    square.appendChild(pieceElement);
                }
                
                // Add click event
                square.addEventListener('click', handleSquareClick);
                
                // Highlight selected square
                if (selectedSquare && selectedSquare.row === row && selectedSquare.col === col) {
                    square.classList.add('selected');
                }
                
                chessBoard.appendChild(square);
            }
        }
    }
    
    function handleSquareClick(event) {
        const square = event.currentTarget;
        const row = parseInt(square.dataset.row);
        const col = parseInt(square.dataset.col);
        const piece = boardState[row][col];
        
        // If no piece is selected and the clicked square has a piece of the current player
        if (!selectedSquare && piece && piece.color === currentPlayer) {
            selectedSquare = { row, col };
            renderBoard();
            return;
        }
        
        // If a piece is already selected
        if (selectedSquare) {
            // If clicking on the same square, deselect it
            if (selectedSquare.row === row && selectedSquare.col === col) {
                selectedSquare = null;
                renderBoard();
                return;
            }
            
            // If clicking on another piece of the same color, select that piece instead
            if (piece && piece.color === currentPlayer) {
                selectedSquare = { row, col };
                renderBoard();
                return;
            }
            
            // Attempt to make the move - let the backend validate it
            makeMove(selectedSquare.row, selectedSquare.col, row, col);
            return;
        }
        
        // If none of the above conditions are met, deselect
        selectedSquare = null;
        renderBoard();
    }
    
    function makeMove(fromRow, fromCol, toRow, toCol) {
        // Clear any previous messages
        messageElement.textContent = '';
        
        const moveData = {
            from: [fromRow, fromCol],
            to: [toRow, toCol]
        };
        
        fetch('/api/move', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(moveData)
        })
        .then(response => response.json())
        .then(data => {
            if (!data.success) {
                // Display error message on invalid move
                messageElement.textContent = data.message || 'Invalid move';
                return;
            }
            
            // Update the board state
            boardState = data.board;
            currentPlayer = data.current_player;
            
            // Reset selection
            selectedSquare = null;
            
            // Update UI
            renderBoard();
            updateStatus();
            
            // Check for check or checkmate
            if (data.check) {
                messageElement.textContent = `${currentPlayer.charAt(0).toUpperCase() + currentPlayer.slice(1)} is in check!`;
            }
            
            if (data.checkmate) {
                handleGameOver(data.current_player === 'white' ? 'black' : 'white');
            }
        })
        .catch(error => {
            console.error('Error making move:', error);
            messageElement.textContent = 'Error making move. Please try again.';
        });
    }
    
    function updateStatus() {
        statusElement.textContent = `${currentPlayer.charAt(0).toUpperCase() + currentPlayer.slice(1)}'s turn`;
    }
    
    function handleGameOver(winner) {
        statusElement.textContent = `Game Over! ${winner.charAt(0).toUpperCase() + winner.slice(1)} wins!`;
        // Disable further moves
        const squares = document.querySelectorAll('.square');
        squares.forEach(square => {
            square.removeEventListener('click', handleSquareClick);
        });
    }
    
    function resetGame() {
        fetch('/api/reset', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Update the board state
                boardState = data.board;
                currentPlayer = data.current_player;
                
                // Reset selection and messages
                selectedSquare = null;
                messageElement.textContent = '';
                
                // Update UI
                renderBoard();
                updateStatus();
            } else {
                messageElement.textContent = 'Error resetting the game. Please try again.';
            }
        })
        .catch(error => {
            console.error('Error resetting game:', error);
            messageElement.textContent = 'Error resetting the game. Please try again.';
        });
    }
});