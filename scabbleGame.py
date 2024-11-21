import random
from collections import Counter
import requests
import time

class ScrabbleGame:
    def __init__(self):
        # Tile bag: letter frequencies and scores
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
        self.word_cache = {}  # Cache for validated words

    def is_valid_dictionary_word(self, word):
        """Check if the word exists in the dictionary using the Free Dictionary API."""
        # Check cache first
        if word in self.word_cache:
            return self.word_cache[word]

        try:
            # Free Dictionary API
            url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word.lower()}"
            response = requests.get(url)
            
            # Cache and return result
            is_valid = response.status_code == 200
            self.word_cache[word] = is_valid
            
            # Add a small delay to avoid hitting API rate limits
            time.sleep(0.5)
            
            return is_valid
        except requests.RequestException as e:
            print(f"Warning: Could not verify word due to API error: {e}")
            # If API is down, we'll accept the word but warn the user
            return True

    def draw_tiles(self, count):
        """Draw random tiles from the bag."""
        if count > self.remaining_tiles:
            raise ValueError(f"Not enough tiles in bag. Only {self.remaining_tiles} remaining.")
        
        tiles = []
        while len(tiles) < count:
            available_letters = []
            for letter, freq in self.tile_bag.items():
                if freq > 0:
                    available_letters.extend([letter] * freq)
            
            if not available_letters:
                break
                
            letter = random.choice(available_letters)
            tiles.append(letter)
            self.tile_bag[letter] -= 1
            self.remaining_tiles -= 1
            
        return tiles

    def return_tiles(self, tiles):
        """Return tiles to the bag."""
        for tile in tiles:
            if tile in self.tile_bag:
                self.tile_bag[tile] += 1
                self.remaining_tiles += 1

    def calculate_score(self, word):
        """Calculate the score for a word."""
        return sum(self.letter_scores.get(letter.upper(), 0) for letter in word)

    def is_valid_word(self, word, player_tiles):
        """Check if word can be formed from player's tiles and exists in dictionary."""
        word_upper = word.upper()
        
        # First check if the word can be formed from tiles
        player_counter = Counter(player_tiles)
        word_counter = Counter(word_upper)
        
        for letter, count in word_counter.items():
            if count > player_counter.get(letter, 0):
                return False, "Cannot form this word with your tiles!"

        # Then check if it's a valid dictionary word
        if not self.is_valid_dictionary_word(word):
            return False, "Not a valid word in the dictionary!"
            
        return True, "Valid word!"

    def replenish_tiles(self, player_tiles, used_tiles):
        """Replenish player's tiles after playing a word."""
        tiles_needed = min(7 - len(player_tiles), self.remaining_tiles)
        if tiles_needed > 0:
            new_tiles = self.draw_tiles(tiles_needed)
            return player_tiles + new_tiles
        return player_tiles

def main():
    game = ScrabbleGame()
    player_score = 0
    
    print("Welcome to Scrabble!")
    print("\nGame Rules:")
    print("1. You will receive 7 tiles")
    print("2. Form words using your tiles")
    print("3. Enter 'QUIT' to end the game")
    print("4. Enter 'SKIP' to draw new tiles (counts as a turn)")
    print("5. Words will be verified using a dictionary")
    print(f"6. Remaining tiles in bag: {game.remaining_tiles}\n")

    try:
        player_tiles = game.draw_tiles(7)
        
        while True:
            print(f"\nYour tiles: {' '.join(player_tiles)}")
            print(f"Current score: {player_score}")
            
            word = input("\nEnter a word (or QUIT/SKIP): ").upper()
            
            if word == 'QUIT':
                break
            
            if word == 'SKIP':
                game.return_tiles(player_tiles)
                player_tiles = game.draw_tiles(7)
                continue
            
            if not word.isalpha():
                print("Please enter only letters.")
                continue
                
            # Check word validity
            is_valid, message = game.is_valid_word(word, player_tiles)
            if not is_valid:
                print(message)
                continue
            
            # Calculate score and update player's tiles
            word_score = game.calculate_score(word)
            player_score += word_score
            
            # Remove used tiles and replenish
            used_tiles = list(word.upper())
            remaining_tiles = [t for t in player_tiles]
            for letter in used_tiles:
                remaining_tiles.remove(letter)
            
            player_tiles = game.replenish_tiles(remaining_tiles, used_tiles)
            
            print(f"Word '{word}' scored {word_score} points!")
            print(f"Tiles remaining in bag: {game.remaining_tiles}")
            
            if not player_tiles and game.remaining_tiles == 0:
                print("\nGame Over! No more tiles available.")
                break
                
    except KeyboardInterrupt:
        print("\nGame terminated by user.")
    except Exception as e:
        print(f"\nAn error occurred: {e}")
    
    print(f"\nFinal score: {player_score}")

if __name__ == "__main__":
    main()