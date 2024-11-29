# LLMonopoly

This project implements a Monopoly simulation designed for Large Language Models (LLMs) to interact with and utilize.

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
ollama pull llama3.2
ollama pull phi3:medium
ollama pull qwen2.5:7b
```

## Running the simulation

Start ollama server:
```bash 
ollama serve
```
In seperate terminal:
```bash 
python game.py
```

---
