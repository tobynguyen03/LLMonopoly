# LLMonopoly

This project implements a Monopoly simulation designed for Large Language Models (LLMs) to interact with and utilize. We host and download our models using Ollama (https://ollama.com)

## Setup

### Cloning the Repository
Before logging into PACE, make sure to join Georgia Tech's VPN first

Login to PACE:
```bash
ssh <GT_USERNAME>@login-ice.pace.gatech.edu
salloc --gres=gpu:H100:1 --ntasks-per-node=1 --time=1:00:00
```

Setup SSH keys:
```bash
ssh-keygen -t ed25519 -C "<your_email@example.com>"
```
Click enter twice to accept default file location
```bash
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519
cat ~/.ssh/id_ed25519.pub
```
- Copy the output (it should start with "ssh-ed25519" and end with your email) and go to your Github.com -> Settings -> SSH and GPG Keys
- Click "New SSH key"
- Paste your key into the "Key" field
- Click "Add SSH key"

Test your connection
```bash
ssh -T git@github.com
```
It should say something like ""Hi username! You've successfully authenticated..."

Clone the repo:
```bash
git clone git@github.com:tobynguyen03/LLMonopoly.git
```

### Install environment and dependencies:
```bash
cd LLMonopoly
module load anaconda3
conda env create -f environment.yml
conda activate llmonopoly
```


### Install ollama manually
Download binaries:
```bash
curl -L https://github.com/ollama/ollama/releases/download/v0.4.1/ollama-linux-amd64.tgz -o ollama-linux-amd64.tgz
mkdir -p ~/.local
tar -C ~/.local -xzf ollama-linux-amd64.tgz
```

Open `~/.bashrc`:

```bash
nano ~/.bashrc
```

Add the following:

```bash 
export PATH=$HOME/.local/bin:$PATH
export LD_LIBRARY_PATH=$HOME/.local/lib/ollama:$LD_LIBRARY_PATH
export OLLAMA_MODELS=/home/hice1/<GT_USERNAME>/scratch/ollama_models/
```

Run the following to update changes:

```bash
source ~/.bashrc
```

Verify
```bash 
ollama serve # run this one terminal
ollama -v # run this in another
```

Note: Make sure that you are running ollama on a terminal that you requested GPU access for. When you open a new terminal, SSH into the one ollama is running on before you run the game simulation. For example:

```bash 
ssh atl1-1-03-012-13-0
```

Dowload ollama models:
```bash
ollama pull llama3.1:8b-instruct-q5_K_M
ollama pull phi3:medium-128k
ollama pull qwen2.5:7b
ollama pull mistral:7b-instruct
ollama pull gemma2:9b
```

Model details can be found here
https://ollama.com/library/llama3.1:8b-instruct-q5_K_M
https://ollama.com/library/phi3:medium-128k
https://ollama.com/library/qwen2.5:7b
https://ollama.com/library/mistral:7b-instruct
https://ollama.com/library/gemma2:9b

## Running the simulation

Start ollama server:
```bash 
ollama serve
```
In seperate terminal:
```bash 
python game.py
```

## Performance Evaluation
Since our project is creating a custom Monopoly agent, we do not utilize any existing dataset. We evaluate the performance of our agents by having them play many simulations against a default heuristic bot (created by ourselves). 20 games (capped at 100 rounds) are ran for each LLM. Various metrics are tracked, such as win rate, number of actions (and sub-actions) made each game, inference time, game duration, etc. Win rate is used as the main statistic for determining agent ability, with our ensemble agent having the highest winrate at 60% against the benchmark agent. We were limited to 20 trials due to the long inference time of trials (12-15 minutes per game), so the variance of Monopoly as a heavily luck-based game could not be completely eliminated.

---
