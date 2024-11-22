import torch
import multiprocessing as mp
from dataclasses import dataclass, asdict
from typing import List, Dict
from torch.cuda import amp
from queue import Queue
import time
from game.game import MonopolyGame, GameResult
from datetime import datetime
from pathlib import Path
import fcntl
import json

class BatchManager:
    def __init__(self, model, batch_size=8, max_queue_size=16):
        self.model = model
        self.batch_size = batch_size
        self.queue = Queue(maxsize=max_queue_size)
        self.results = {}
    
    @torch.cuda.amp.autocast()
    def process_batch(self, prompts):
        with torch.no_grad():
            return self.model.generate(prompts)
    
    def batch_worker(self):
        while True:
            batch = []
            batch_ids = []
            
            while len(batch) < self.batch_size:
                if not self.queue.empty():
                    game_id, prompt = self.queue.get()
                    batch.append(prompt)
                    batch_ids.append(game_id)
                else:
                    if batch:
                        break
                    time.sleep(0.001)
                    continue
            
            outputs = self.process_batch(batch)
            
            for game_id, output in zip(batch_ids, outputs):
                self.results[game_id] = output

class FileLogger:
    def __init__(self, log_dir: str = "simulation_logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        self.log_file = self.log_dir / f"monopoly_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        
        # Create file with headers
        with open(self.log_file, 'w') as f:
            f.write("# Monopoly Simulation Results\n")
            f.write("# Started at: " + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + "\n\n")
    
    def write_result(self, result: GameResult):
        """
        Thread-safe method to write a game result to the log file.
        Uses file locking to prevent concurrent writes from multiple processes.
        """
        result_dict = asdict(result)
        formatted_result = json.dumps(result_dict)
        
        with open(self.log_file, 'a') as f:
            # Acquire an exclusive lock
            fcntl.flock(f.fileno(), fcntl.LOCK_EX)
            try:
                f.write(formatted_result + '\n')
                f.flush()  # Ensure the write is committed to disk
            finally:
                # Release the lock
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
    
    def write_summary(self, total_games: int, total_time: float):
        """Write summary statistics at the end of all games"""
        with open(self.log_file, 'a') as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_EX)
            try:
                f.write("\n# Summary Statistics\n")
                f.write(f"Total Games: {total_games}\n")
                f.write(f"Total Execution Time: {total_time:.2f} seconds\n")
                f.write(f"Average Time per Game: {total_time/total_games:.2f} seconds\n")
                
                # Read all results and calculate statistics
                results = self.read_results()
                llm_wins = sum(1 for r in results if r['winner'] == 'LLM')
                default_wins = sum(1 for r in results if r['winner'] == 'Baseline')
                
                f.write(f"LLM Wins: {llm_wins}\n")
                f.write(f"Default Strategy Wins: {default_wins}\n")
                f.write(f"LLM Win Rate: {llm_wins/total_games:.2%}\n")
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
    
    def read_results(self) -> List[Dict]:
        """Read all results from the log file"""
        results = []
        with open(self.log_file, 'r') as f:
            for line in f:
                if line.startswith('{'):  # Only parse JSON lines
                    results.append(json.loads(line))
        return results

class MonopolyGameRunner:
    def __init__(self, llm_player_id: int, llm, num_games: int, num_turns: int, batch_size: int = 8):
        self.llm_player_id = llm_player_id
        self.llm = llm
        self.num_games = num_games
        self.num_turns = num_turns
        self.batch_manager = BatchManager(llm, batch_size=batch_size)
        self.game = MonopolyGame(2, llm_player_id, llm, batch_manager=self.batch_manager)

    def run_parallel_simulation(self, num_processes: int = 4):
        """Run multiple games in parallel with GPU batch processing"""
        # Start batch processing worker in a separate process
        batch_process = mp.Process(target=self.batch_manager.batch_worker)
        batch_process.start()
        
        # Run games in parallel
        with mp.Pool(num_processes) as pool:
            game_ids = range(self.num_games)
            results = pool.map(self.run_game, game_ids)
        
        # Clean up batch worker
        batch_process.terminate()
        batch_process.join()
        
        return results

    # Placeholder methods - replace with your actual implementation
    def initialize_game(self):
        return {}
    
    def needs_llm_decision(self, game_state):
        return True
    
    def create_prompt(self, game_state):
        return "Sample prompt"
    
    def apply_action(self, game_state, action):
        pass
    
    def apply_default_strategy(self, game_state):
        pass
    
    def determine_winner(self, game_state):
        return "LLM"
    
    def get_final_money(self, game_state):
        return {"LLM": 1000, "Default": 800}

def main():
    # Initialize your Llama 3 model
    llm = "phi3"  # Replace with your Llama 3 model initialization
    
    # Configuration
    NUM_GAMES = 100
    NUM_TURNS = 200
    BATCH_SIZE = 8  # Adjust based on your H100 memory
    NUM_PROCESSES = 4  # Adjust based on your CPU cores
    
    # Run simulation
    first_simulator = MonopolyGameRunner(
        llm_player_id=0
        llm=llm,
        num_games=NUM_GAMES,
        num_turns=NUM_TURNS,
        batch_size=BATCH_SIZE
    )

    second_simulator = MonopolyGameRunner(
        llm_player_id=1
        llm=llm,
        num_games=NUM_GAMES,
        num_turns=NUM_TURNS,
        batch_size=BATCH_SIZE
    )
    
    start_time = time.time()
    results = first_simulator.run_parallel_simulation(num_processes=NUM_PROCESSES)
    execution_time = time.time() - start_time
    
    print(f"\nSimulation completed in {execution_time:.2f} seconds")
    print(f"Average time per game: {execution_time/NUM_GAMES:.2f} seconds")

if __name__ == "__main__":
    main()