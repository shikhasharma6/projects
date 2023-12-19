import sys
import csv
import time
import timeit
from itertools import product

#Defining a class named SudokuCSP and initializing variables using constructor
class SudokuCSP:
    def __init__(self, grid):
        self.grid = grid
        self.constraints = []  # List to store constraints

    #maintaining list of all constraints
    def add_constraint(self, constraint):
        self.constraints.append(constraint)

    #definition to check if the move is as per Sudoku rules
    def is_valid_move(self, row, col, num):
        # Check if placing 'num' in the specified row and column is a valid move
        for constraint in self.constraints:
            if not constraint(self.grid, row, col, num):
                return False
        return True

#Defining class SudokuSolver and intializing variables using constructor
class SudokuSolver:
    def __init__(self, input_file):
        self.grid = self.load_puzzle(input_file)
        self.empty_cell = 'X'
        self.size = 9
        self.nodes_generated = 0

    #Reading the input puzzle from the testcase.csv file
    def load_puzzle(self, input_file):
        with open(input_file, 'r') as file:
            reader = csv.reader(file)
            grid = [[cell.strip() for cell in row] for row in reader]
        return grid

    #definition to print the puzzle
    def print_puzzle(self, puzzle):
        for row in puzzle:
            print(','.join(cell if cell != self.empty_cell else 'X' for cell in row))

    #definiton to save the solved sudoku in a csv file to be used in mode==4
    def save_solution(self, solution):
        if solution is not None:
            output_file = f"{sys.argv[2].split('.')[0]}_SOLUTION.csv"
            with open(output_file, 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerows(solution)
            print(f"\nSolved puzzle saved to: {output_file}")
        else:
            print("No solution found.")

    # def is_valid_solution(self, solution):
    #     for i in range(self.size):
    #         for j in range(self.size):
    #             if not self.is_valid_move(solution, i, j, solution[i][j]):
    #                 print(f"Error at position ({i + 1}, {j + 1}): {solution[i][j]} is not a valid move.")
    #                 return False
    #     return True

    #Checking if the solved puzzle is as per the Sudoku rules
    def is_valid_solution(self, solution):
        def has_duplicates(lst):
            seen = set()
            for value in lst:
                if value != self.empty_cell:
                    if value in seen:
                        return True
                    seen.add(value)
            return False

        for i in range(self.size):
            # Check each row
            if has_duplicates(solution[i]):
                print(f"Error in row {i + 1}: Duplicate values.")
                return False

            # Check each column
            if has_duplicates(solution[j][i] for j in range(self.size)):
                print(f"Error in column {i + 1}: Duplicate values.")
                return False

            # Check each 3x3 box
            box_start_row, box_start_col = 3 * (i // 3), 3 * (i % 3)
            box_values = [solution[box_start_row + k][box_start_col + l] for k, l in product(range(3), repeat=2)]
            if has_duplicates(box_values):
                print(
                    f"Error in box ({box_start_row + 1}-{box_start_row + 3}, {box_start_col + 1}-{box_start_col + 3}): Duplicate values.")
                return False

        return True

    def is_valid_move(self, puzzle, row, col, num):
        return (
            self.is_valid_row(puzzle, row, num) and
            self.is_valid_col(puzzle, col, num) and
            self.is_valid_box(puzzle, row - row % 3, col - col % 3, num)
        )

    #check if number is not already present in the row
    def is_valid_row(self, puzzle, row, num):
        return num not in puzzle[row]

    # check if number is not already present in the column
    def is_valid_col(self, puzzle, col, num):
        return num not in [puzzle[i][col] for i in range(self.size)]

    # check if number is not already present in the subgrid
    def is_valid_box(self, puzzle, start_row, start_col, num):
        return num not in [
            puzzle[start_row + i][start_col + j]
            for i, j in product(range(3), repeat=2)
        ]
    #maintaining a list of all empty cells in the puzzle
    def find_empty_cell(self, puzzle):
        for i, j in product(range(self.size), repeat=2):
            if puzzle[i][j] == self.empty_cell:
                return i, j
        return None

    #Defining brute force algorithm
    def brute_force_search(self):
        puzzle_copy = [row[:] for row in self.grid]
        start_time = timeit.default_timer()

        solution = self.brute_force_search_helper(puzzle_copy)

        end_time = timeit.default_timer()
        search_time = end_time - start_time
        print(f"Number of search tree nodes generated: {self.nodes_generated}")
        print(f"Search time: {search_time:.4f} seconds")

        if solution is not None:
            self.save_solution(solution)
            output_file = f"{sys.argv[2].split('.')[0]}_SOLUTION.csv"
            print(f"\nSolved puzzle saved to: {output_file}")
            self.print_puzzle(solution)
            return solution
        else:
            print("No solution found.")
            return None

    #defining logic for brute force algorithm
    def brute_force_search_helper(self, puzzle):
        #finding empty cells from the list maintained
        empty_cell = self.find_empty_cell(puzzle)
        #if no empty cell means the sudoku is solved and return the puzzle
        if not empty_cell:
            return puzzle
        #else set the pointer on the empty cell
        row, col = empty_cell
        #run loop and check each number in the empty cell
        for num in map(str, range(1, 10)):
            self.nodes_generated += 1
            if self.is_valid_move(puzzle, row, col, num):
                puzzle[row][col] = num
                #recursively calling brute force function
                if self.brute_force_search_helper(puzzle) is not None:
                    return puzzle
                #If the recursive call does not find a solution, the code backtracks by resetting the value of the specified cell to empty
                puzzle[row][col] = self.empty_cell

        return None
    #defining function for CSP with backtracking
    def csp_backtracking_search(self, csp, assignment=None):
        #used to represent the assignment of values to variables
        if assignment is None:
            assignment = {}
        ##finding empty cells from the list maintained
        empty_cell = self.find_empty_cell(self.grid)
        # if no empty cell means the sudoku is solved and return the puzzle
        if not empty_cell:
            return self.grid
        # else set the pointer on the empty cell
        var = empty_cell
        row, col = var
        #iterating through values in domain
        for value in self.get_domain(row, col):
            #incrementing number of search nodes
            self.nodes_generated += 1
            #checking if placing the value is valid and assigning
            if self.is_valid_move(self.grid, row, col, value):
                self.grid[row][col] = value
                #self.nodes_generated += 1

                assignment[(row, col)] = value
                #recursive call is attempting to solve the CSP with the updated assignment
                if self.csp_backtracking_search(csp, assignment):
                    return self.grid
                #If the recursive call does not find a solution, the code backtracks. It resets the value of the specified cell in self.grid to self.empty_cell to explore other possibilities.
                self.grid[row][col] = self.empty_cell
                #the assignment for the cell is removed from the assignment dictionary
                assignment.pop((row, col), None)

        return None

    #initializes a SudokuCSP definition
    def solve_csp_puzzle(self):
        csp = SudokuCSP(self.grid)
    #Three constraint functions are defined using lambda functions which check whether placing a number in a specific cell violates the constraints of Sudoku
        row_constraint = lambda grid, r, c, num: num not in grid[r]
        col_constraint = lambda grid, r, c, num: num not in [grid[i][c] for i in range(self.size)]
        box_constraint = lambda grid, r, c, num: num not in [
            grid[i][j] for i in range(r - r % 3, r - r % 3 + 3) for j in range(c - c % 3, c - c % 3 + 3)
        ]
        #These constraint functions are then added to the SudokuCSP object using its add_constraint method.
        csp.add_constraint(row_constraint)
        csp.add_constraint(col_constraint)
        csp.add_constraint(box_constraint)

        return self.csp_backtracking_search(csp)

    #Defining forward checking function
    def forward_checking_mrv_search(self):
        #finding an empty cell in the Sudoku grid
        empty_cell = self.find_empty_cell(self.grid)
        start_time = timeit.default_timer()

        if not empty_cell:
            end_time = timeit.default_timer()
            search_time = end_time - start_time
            print(f"Number of search tree nodes generated: {self.nodes_generated}")
            print(f"Search time: {search_time:.4f} seconds")
            return self.grid
        #If there are still empty cells in the grid, the method continues by selecting an empty cell (row, col) to fill
        row, col = empty_cell
        #The domain of this cell is obtained using the get_domain method
        domain = self.get_domain(row, col)
        #it is sorted based on the number of remaining valid values for that cell
        domain.sort(key=lambda x: len(self.get_valid_values(row, col, x)))
        #iterates through the sorted domain of values for the selected cell
        for value in domain:
            #checks if placing that value in the cell is a valid move using the is_valid_move method
            if self.is_valid_move(self.grid, row, col, value):
                self.grid[row][col] = value
                #If the move is valid, the code updates the grid, increments the nodes_generated
                self.nodes_generated += 1
                #recursively calls itself to continue the search with the updated grid
                if self.forward_checking(row, col, value) and self.forward_checking_mrv_search():
                    return self.grid
                #if no solution found, resets vale to empty cell
                self.grid[row][col] = self.empty_cell

        return None

    def forward_checking(self, row, col, value):
        #collecting the original domains of cells in the same row, column, and 3x3 box as the specified cell.
        original_domains = []

        #collecting domains of cells in the same column as the specified cell.
        for i in range(self.size):
            original_domains.append(list(self.get_domain(i, col)))

        #colecting domains of cells in the same row as the specified cell.
        for j in range(self.size):
            original_domains.append(list(self.get_domain(row, j)))

        #collecting domains of cells in the same 3x3 box as the specified cell.
        box_start_row, box_start_col = 3 * (row // 3), 3 * (col // 3)
        for i, j in product(range(3), repeat=2):
            box_row, box_col = box_start_row + i, box_start_col + j
            original_domains.append(list(self.get_domain(box_row, box_col)))

        #Updating domains based on the forward checking algorithm.

        # update domains for cells in the same row as the specified cell.
        for i in range(self.size):
            if i != col and self.grid[row][i] == self.empty_cell:
                if value in self.get_domain(row, i):
                    self.remove_from_domain(row, i, value)

        # update domains for cells in the same column as the specified cell.
        for j in range(self.size):
            if j != row and self.grid[j][col] == self.empty_cell:
                if value in self.get_domain(j, col):
                    self.remove_from_domain(j, col, value)

        # update domains for cells in the same 3x3 box as the specified cell.
        for i, j in product(range(3), repeat=2):
            box_row, box_col = box_start_row + i, box_start_col + j
            if box_row != row and box_col != col and self.grid[box_row][box_col] == self.empty_cell:
                if value in self.get_domain(box_row, box_col):
                    self.remove_from_domain(box_row, box_col, value)

        return True

    def get_domain(self, row, col):
        #checking if the cell is empty
        if self.grid[row][col] == self.empty_cell:
            # If empty, return a list of strings representing the possible values (1 to 9)
            return [str(i) for i in range(1, 10)]
        else:
            # If not empty, return a list containing the current value as the only option
            return [self.grid[row][col]]

    def get_valid_values(self, row, col, value):
        # Initialize a list to store valid values
        valid_values = []

        # Iterate through each cell in the grid
        for i in range(self.size):
            # Check if the specified move (placing 'value' in the cell) is valid
            if self.is_valid_move(self.grid, row, col, value):
                # If valid, add 'value' to the list of valid values
                valid_values.append(value)

        # Return the list of valid values
        return valid_values

    # def remove_from_domain(self, row, col, value):
    #     if self.grid[row][col] == self.empty_cell:
    #         if value in self.get_domain(row, col):
    #             self.get_domain(row, col).remove(value)

    def remove_from_domain(self, row, col, value):
        # Check if the cell is empty
        if self.grid[row][col] == self.empty_cell:
            # Check if the value is in the domain of the cell
            if value in self.get_domain(row, col):
                # Remove the value from the domain of the cell
                self.get_domain(row, col).remove(value)
    def solve_puzzle(self, mode):
        start_time = timeit.default_timer()
        #defining different function execution on different modes
        if mode == 1:
            solution = self.brute_force_search()
        elif mode == 2:
            solution = self.solve_csp_puzzle()
        elif mode == 3:
            solution = self.forward_checking_mrv_search()
        elif mode == 4:
            #solution_file = f"{sys.argv[2].split('.')[0]}_SOLUTION.csv"
            # loading a solution from a file for validation
            solution_file = sys.argv[2]
            solution = self.load_puzzle(solution_file)
            print("\nLoaded solution from", solution_file)
            self.print_puzzle(solution)
            is_valid = self.is_valid_solution(solution)
            if is_valid:
                print("This is a valid, solved, Sudoku puzzle.")
            else:
                print("ERROR: This is NOT a solved Sudoku puzzle.")
            return
        else:
            print("ERROR: Invalid mode.")
            return
        # If a solution is found, display information and performance metrics
        if solution is not None:
            print(f"\nSharma, Shikha, A20543467 solution:")
            print(f"Input file: {sys.argv[2]}")
            print(
                f"Algorithm: {'Brute Force' if mode == 1 else 'Backtracking' if mode == 2 else 'CSP with Forward-Checking and MRV' if mode == 3 else 'Test'}")
            print("\nInput puzzle:")
            self.print_puzzle(self.grid)
            print(f"\nNumber of search tree nodes generated: {self.nodes_generated}")
            # Calculate and display search time
            end_time = timeit.default_timer()
            search_time = end_time - start_time
            print(f"Search time: {search_time:.4f} seconds")

            # If not in validation mode, save the solution to a file and display the solution
            if mode != 4:
                self.save_solution(solution)
                output_file = f"{sys.argv[2].split('.')[0]}_SOLUTION.csv"
                print(f"\nSolved puzzle saved to: {output_file}")
                self.print_puzzle(solution)
        else:
            print("No solution found.")


if __name__ == "__main__":
    #checking for the correct number and format of command-line arguments
    if len(sys.argv) != 3 or not sys.argv[1].isdigit() or not sys.argv[1] in {'1', '2', '3', '4'}:
        print("ERROR: Not enough/too many/illegal input arguments.")
        sys.exit(1)
    #Convert mode to integer and get the input file from command-line arguments
    mode = int(sys.argv[1])
    input_file = sys.argv[2]
    # Create a SudokuSolver object and solve the puzzle based on the specified mode
    solver = SudokuSolver(input_file)
    solver.solve_puzzle(mode)
