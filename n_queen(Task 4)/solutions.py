def is_safe(queens, row, col):
    for qr, qc in enumerate(queens):
        if qc == col or abs(qr - row) == abs(qc - col):
            return False
    return True

def solve(n, row, queens, solutions):
    if row == n:
        solutions.append(queens[:])
        return
    for col in range(n):
        if is_safe(queens, row, col):
            queens.append(col)
            solve(n, row + 1, queens, solutions)
            queens.pop()

def print_board(solution, n):
    print("  +" + "---+" * n)
    for row, col in enumerate(solution):
        line = f"{row+1} |"
        for c in range(n):
            line += " Q |" if c == col else " . |"
        print(line)
        print("  +" + "---+" * n)
    print()

n = int(input("Enter board size N: "))

solutions = []
solve(n, 0, [], solutions)

print(f"\nFound {len(solutions)} solution(s) for {n}x{n} board:\n")

for i, sol in enumerate(solutions, 1):
    print(f"Solution {i}:")
    print_board(sol, n)