"""Jogo da cobrinha por turnos para o README do perfil.

Uso: python game/snake.py <comando> <usuario>
Comandos: up, down, left, right, new
Imprime uma mensagem de resultado (usada no comentário da issue).
"""
import json
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STATE = ROOT / "game" / "state.json"
README = ROOT / "README.md"
REPO = "jrcn1991/jrcn1991"
SIZE = 10
START, END = "<!-- SNAKE:START -->", "<!-- SNAKE:END -->"

DIRS = {"up": (0, -1), "down": (0, 1), "left": (-1, 0), "right": (1, 0)}
OPPOSITE = {"up": "down", "down": "up", "left": "right", "right": "left"}


def new_game(best=0, players=None):
    mid = SIZE // 2
    state = {
        "snake": [[mid, mid], [mid - 1, mid], [mid - 2, mid]],  # cabeça primeiro
        "dir": "right",
        "food": None,
        "score": 0,
        "best": best,
        "moves": 0,
        "over": False,
        "players": players or [],
    }
    state["food"] = place_food(state["snake"])
    return state


def place_food(snake):
    free = [[x, y] for x in range(SIZE) for y in range(SIZE) if [x, y] not in snake]
    return random.choice(free) if free else None


def load():
    if STATE.exists():
        return json.loads(STATE.read_text())
    return new_game()


def save(state):
    STATE.write_text(json.dumps(state, indent=2) + "\n")


def step(state, cmd):
    if cmd == "new":
        return new_game(state["best"], state["players"]), "Novo jogo iniciado! 🐍"
    if state["over"]:
        return state, "O jogo acabou. Clique em **Novo jogo** para recomeçar."
    if cmd == OPPOSITE[state["dir"]]:
        return state, "A cobrinha não pode voltar para trás. Jogada ignorada."

    dx, dy = DIRS[cmd]
    hx, hy = state["snake"][0]
    head = [hx + dx, hy + dy]
    state["dir"] = cmd
    state["moves"] += 1

    eating = head == state["food"]
    body = state["snake"] if eating else state["snake"][:-1]
    if not (0 <= head[0] < SIZE and 0 <= head[1] < SIZE) or head in body:
        state["over"] = True
        return state, f"💥 Bateu! Fim de jogo com {state['score']} ponto(s)."

    state["snake"] = [head] + body
    if eating:
        state["score"] += 1
        state["best"] = max(state["best"], state["score"])
        state["food"] = place_food(state["snake"])
        if state["food"] is None:
            state["over"] = True
            return state, "🏆 A cobrinha ocupou o tabuleiro inteiro. Você venceu!"
        return state, f"🍎 Nhac! Agora são {state['score']} ponto(s)."
    return state, "Jogada feita."


def link(cmd, label):
    title = f"snake%7C{cmd}"
    body = "Clique+em+%22Create%22+para+enviar+a+jogada.+N%C3%A3o+precisa+escrever+nada."
    return f'<a href="https://github.com/{REPO}/issues/new?title={title}&body={body}">{label}</a>'


def render(state):
    snake = state["snake"]
    rows = []
    for y in range(SIZE):
        row = ""
        for x in range(SIZE):
            if [x, y] == snake[0]:
                row += "💀" if state["over"] else "🐍"
            elif [x, y] in snake:
                row += "🟩"
            elif [x, y] == state["food"]:
                row += "🍎"
            else:
                row += "⬛"
        rows.append(row)
    board = "<br>\n".join(rows)

    if state["over"]:
        controls = f"<b>Fim de jogo!</b><br><br>{link('new', '🔄 Novo jogo')}"
    else:
        controls = (
            f"{link('up', '⬆️')}<br>\n"
            f"{link('left', '⬅️')}&nbsp;&nbsp;&nbsp;&nbsp;{link('right', '➡️')}<br>\n"
            f"{link('down', '⬇️')}"
        )

    players = ", ".join(f"@{p}" for p in state["players"][:5]) or "ninguém ainda"
    return f"""{START}
<p align="center">
{board}
</p>

<p align="center">
<b>Pontos:</b> {state['score']} &nbsp;|&nbsp; <b>Recorde:</b> {state['best']} &nbsp;|&nbsp; <b>Jogadas:</b> {state['moves']}
</p>

<p align="center">
{controls}
</p>

<p align="center"><sub>Últimos jogadores: {players}</sub></p>
{END}"""


def update_readme(state):
    text = README.read_text()
    before, rest = text.split(START, 1)
    _, after = rest.split(END, 1)
    README.write_text(before + render(state) + after)


def main():
    cmd = sys.argv[1].strip().lower() if len(sys.argv) > 1 else ""
    user = sys.argv[2] if len(sys.argv) > 2 else ""
    if cmd not in DIRS and cmd != "new":
        print(f"Comando desconhecido: `{cmd}`. Use up, down, left, right ou new.")
        return
    state, msg = step(load(), cmd)
    if user:
        state["players"] = [user] + [p for p in state["players"] if p != user]
        state["players"] = state["players"][:20]
    save(state)
    update_readme(state)
    print(msg)


if __name__ == "__main__":
    main()
