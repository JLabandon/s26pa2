Assignment 2: 2048
=========
Implement a game AI for the 2048 game based on expectimax search. The base game engine uses code from [here](https://gist.github.com/lewisjdeane/752eeba4635b479f8bb2). 

Task
-----
Model the AI player as a max player, and the computer as a chance player (picking a random open spot to place a 2-tile). Implement a depth-3 game tree and the expectimax algorithm to compute decisions for the AI player. Use the score returned by the game engine as the evaluation function value at the leaf nodes of the depth-3 game trees. 

You can play the game manually using the arrow keys. Pressing 'Enter' will let the AI play, and pressing 'Enter' again will stop the AI player. Read the game engine code from `game.py` and see how it returns the game state, and evaluate its score from an arbitrary game state after an arbitrary player move. 

A depth-3 game tree means the tree should have the following levels: 

- root: player
- level 1: computer 
- level 2: player
- level 3: terminal with payoff (note that we say "terminal" to mean the leaf nodes in the shallow game tree, not the termination of the game itself)

This tree represents all the game states of a player-computer-player sequence (the player makes a move, the computer places a tile, and then the player makes another move, and then evaluate the score) from the current state. Compute the expectimax values of all the nodes in the game tree, and return the optimal move for the player. In the starter code, the AI just returns a random move.

If you have implemented the AI correctly, your depth-3 search should almost always reach 512 tiles and a score over 5000 quite often, as shown in the movie file. 

Setting up
-----
We'll use [uv](https://github.com/astral-sh/uv) again.
```
uv sync
source .venv/bin/activate
```

Usage
-----
To run the program
```
    uv run main.py
```

The file 'test.py' contains code for testing that with the depth-3 tree and the expectimax algorithm, your AI returns the right directions and values on the given test states. Run the tests using:
```
    uv run main.py -t 1
```

Once your program is running, here are a few keyboard options available in-game:
- 'r': restart the game
- 'u': undo a move
- '3'-'7': change board size
- 'g': toggle grayscale
- 'e': switch to extension mode

Extension (Optional)
------
We challenge you to optimize your algorithm!
This part is optional and gives no extra points, so only do if you are interested and have time.
Any cool results, feel free to share on slack #pa2 channel with an explanation of your approach.

While depth-3 search gives okay performance, it can apparently be improved by searching more depth or improving the evaluation function, or both. For improving the evaluation function, you can implement a heuristic value that takes into account of the difference between a "good" and "bad" game state. You can feel free to use online resources to see what strategies people have been using to reach higher scores in 2048. 

If you want to try this extension, implement a stronger AI in the `compute_decision_extension` function at the bottom of the `ai.py` file. When running the game, pressing `e` will activate/deactivate the decisions made by the `compute_decision_extension` function. 

You can engineer the AI to reach 2048 often (achieving a score of more than 20,000 on at least 6/10 runs), while each step does not take too long when running on a laptop. Note that if you implement a large tree, the search may make each decision so slow that you do not want to watch it play. In that case you want to think about how to improve the implementation, or think about improving the design of the evaluation function instead. 

To test your implementation, run:

```
    uv run main.py -t 2
```

Again, this part is optional, so have fun.

Submission
-----
Only submit `ai.py` onto Gradescope. Don't touch the `compute_decision` function in `ai.py`.

Due date
-----
Apr-26 11:59pm. 

Grading
-----
All test cases are given in `test_states` and `test_sols`. 

- Full (5 points): Passes all given tests.
- Almost (3 points): Fails some given tests.
- Nothing (0 point): No attempt or fails almost all given tests.

Late Policy: -1 point every late day (0 is floor)
