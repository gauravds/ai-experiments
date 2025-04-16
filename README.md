# AI EXPERIMENTS

```.zshrc
#python
alias py="python"

# create-activate & exit venv
alias venv="python -m venv venv && source venv/bin/activate"
alias venva="source venv/bin/activate"
alias exitvenv="deactivate"
alias pipf="pip freeze > requirements.txt"
alias pipr="pip install -r requirements.txt"

pipi() {
    pip install "$@" && pip freeze > requirements.txt
}

pipui() {
    # Use '-y' to automatically confirm uninstall; remove it if you prefer manual confirmation
    pip uninstall -y "$@" && pip freeze > requirements.txt
}



# ollama
alias od1="ollama run deepseek-r1:1.5b"
alias od14="ollama run deepseek-r1:14b"
```

## Features

- [x] Tokenizer (Encoder & Decoder)
  ```sh
  cd tokenizer
  python tokenizer/tokenizer.py
  ```
