import random
from collections import Counter
import requests
import time
import tkinter as tk
from tkinter import messagebox


class ScrabbleGame:
    def __init__(self):
        self.tile_bag = {
            'A': 9, 'B': 2, 'C': 2, 'D': 4, 'E': 12,
            'F': 2, 'G': 3, 'H': 2, 'I': 9, 'J': 1,
            'K': 1, 'L': 4, 'M': 2, 'N': 6, 'O': 8,
            'P': 2, 'Q': 1, 'R': 6, 'S': 4, 'T': 6,
            'U': 4, 'V': 2, 'W': 2, 'X': 1, 'Y': 2, 'Z': 1
        }
        self.letter_scores = {
            'A': 1, 'B': 3, 'C': 3, 'D': 2, 'E': 1,
            'F': 4, 'G': 2, 'H': 4, 'I': 1, 'J': 8,
            'K': 5, 'L': 1, 'M': 3, 'N': 1, 'O': 1,
            'P': 3, 'Q': 10, 'R': 1, 'S': 1, 'T': 1,
            'U': 1, 'V': 4, 'W': 4, 'X': 8, 'Y': 4, 'Z': 10
        }
        self.remaining_tiles = sum(self.tile_bag.values())
        self.word_cache = {}

    def is_valid_dictionary_word(self, word):
        """Check if the word exists in the dictionary using an API."""
        if word in self.word_cache:
            return self.word_cache[word]

        try:
            url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word.lower()}"
            response = requests.get(url)
            is_valid = response.status_code == 200
            self.word_cache[word] = is_valid
            time.sleep(0.5)
            return is_valid
        except requests.RequestException as e:
            print(f"API Error: {e}")
            return True

    def draw_tiles(self, count):
        """Draw random tiles from the bag."""
        if count > self.remaining_tiles:
            raise ValueError("Not enough tiles left.")
        
        tiles = []
        while len(tiles) < count:
            available_letters = [
                letter for letter, freq in self.tile_bag.items() if freq > 0
            ]
            letter = random.choice(available_letters)
            tiles.append(letter)
            self.tile_bag[letter] -= 1
            self.remaining_tiles -= 1

        return tiles

    def calculate_score(self, word):
        """Calculate the score for a word."""
        return sum(self.letter_scores.get(letter.upper(), 0) for letter in word)

    def is_valid_word(self, word, player_tiles):
        """Check if a word is valid and can be formed from player's tiles."""
        player_counter = Counter(player_tiles)
        word_counter = Counter(word.upper())
        for letter, count in word_counter.items():
            if count > player_counter.get(letter, 0):
                return False, "Cannot form the word with available tiles."

        if not self.is_valid_dictionary_word(word):
            return False, "Word not found in dictionary."
        
        return True, "Valid word."

    def replenish_tiles(self, player_tiles):
        """Replenish player's tiles to maintain 7 tiles."""
        tiles_needed = min(7 - len(player_tiles), self.remaining_tiles)
        if tiles_needed > 0:
            new_tiles = self.draw_tiles(tiles_needed)
            return player_tiles + new_tiles
        return player_tiles


class ScrabbleGUI:
    def __init__(self, root):
        self.game = ScrabbleGame()
        self.players = [{"tiles": [], "score": 0}, {"tiles": [], "score": 0}]
        self.current_player = 0

        # Setup GUI
        self.root = root
        self.root.title("2-Player Scrabble Game")

        # Labels
        self.info_label = tk.Label(root, text="Welcome to Scrabble!")
        self.info_label.pack()

        self.player_tiles_label = tk.Label(root, text="")
        self.player_tiles_label.pack()

        self.score_label = tk.Label(root, text="")
        self.score_label.pack()

        # Word entry
        self.word_entry = tk.Entry(root)
        self.word_entry.pack()

        self.submit_button = tk.Button(root, text="Submit Word", command=self.submit_word)
        self.submit_button.pack()

        self.skip_button = tk.Button(root, text="Skip Turn", command=self.skip_turn)
        self.skip_button.pack()

        self.end_game_button = tk.Button(root, text="End Game", command=self.end_game)
        self.end_game_button.pack()

        self.start_game()

    def start_game(self):
        for player in self.players:
            player["tiles"] = self.game.draw_tiles(7)
        self.update_display()

    def update_display(self):
        player = self.players[self.current_player]
        self.player_tiles_label.config(
            text=f"Player {self.current_player + 1}'s Tiles: {' '.join(player['tiles'])}"
        )
        self.score_label.config(
            text=f"Player 1: {self.players[0]['score']} | Player 2: {self.players[1]['score']}"
        )

    def submit_word(self):
        word = self.word_entry.get().strip().upper()
        if not word:
            messagebox.showerror("Error", "Enter a valid word!")
            return

        player = self.players[self.current_player]
        is_valid, message = self.game.is_valid_word(word, player["tiles"])
        if not is_valid:
            messagebox.showerror("Error", message)
            return

        # Calculate score
        score = self.game.calculate_score(word)
        player["score"] += score

        # Remove used tiles and replenish
        for letter in word:
            player["tiles"].remove(letter)
        player["tiles"] = self.game.replenish_tiles(player["tiles"])

        messagebox.showinfo("Success", f"Word accepted! You scored {score} points.")
        self.next_turn()

    def skip_turn(self):
        self.next_turn()

    def next_turn(self):
        self.current_player = 1 - self.current_player
        self.word_entry.delete(0, tk.END)
        self.update_display()

    def end_game(self):
        player1_score = self.players[0]["score"]
        player2_score = self.players[1]["score"]
        winner = (
            "Player 1" if player1_score > player2_score else
            "Player 2" if player2_score > player1_score else
            "No one (tie)"
        )
        messagebox.showinfo("Game Over", f"Final Scores:\nPlayer 1: {player1_score}\nPlayer 2: {player2_score}\nWinner: {winner}")
        self.root.quit()


if __name__ == "__main__":
    root = tk.Tk()
    gui = ScrabbleGUI(root)
    root.mainloop()