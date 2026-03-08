def print_board(board, n):
    print("\n  " + "  ".join(str(c+1) for c in range(n)))
    print("  +" + "---+" * n)
    for r in range(n):
        row = f"{r+1} |"
        for c in range(n):
            row += f" {board[r][c]} |"
        print(row)
        print("  +" + "---+" * n)
    print()

def is_safe(queens, row, col):
    for qr, qc in queens:
        if qr == row or qc == col or abs(qr - row) == abs(qc - col):
            return False
    return True

def build_board(queens, n):
    board = [['.' for _ in range(n)] for _ in range(n)]
    for qr, qc in queens:
        board[qr][qc] = 'Q'
    return board

print("=== N-Queens Game ===")
n = int(input("Enter board size N: "))
queens = []

while len(queens) < n:
    print_board(build_board(queens, n), n)
    print(f"Queens placed: {len(queens)}/{n}")

    row = int(input(f"Enter row (1-{n}): ")) - 1
    col = int(input(f"Enter col (1-{n}): ")) - 1

    if not is_safe(queens, row, col):
        queens.append((row, col))
        board = build_board(queens, n)
        board[row][col] = 'X'
        print_board(board, n)
        print(f" GAME OVER! Queen at ({row+1},{col+1}) is under attack!")
        print(f"You placed {len(queens)-1} queen(s) correctly.")
        exit()

    queens.append((row, col))
    print(f"✔ Queen placed at ({row+1},{col+1})!")

print_board(build_board(queens, n), n)
print(f"🎉 YOU WIN! All {n} queens placed safely!")