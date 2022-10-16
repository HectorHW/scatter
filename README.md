# word game

This repository contains client and backend for simple word game I written for playing at english club of our dormitory.

The rules are simple: there are number of cards with categories and letters. The goal is to be the first to name the word starting with displayed letter that corresponds to current category. The players are expected to use their phones to connect to game server and to see current card and letter on their screen. The game admin logs with preconfigured password to control game state.

## running

You may run it using docker-compose by simply typing `docker-compose up` inside repo directory. This will setup game server, mount `questions.txt` file and expose 8080 through nginx. Game will be available at default address of [http://localhost:8080/game](http://localhost:8080/game).

Alternatively, you may build game container and run it separately like so:

```bash
docker build . -t scatter
docker run -e PASS='password' -v $(pwd)/questions.txt:/opt/scatter/questions.txt -it -p8720:8720 scatter
```

*Note*: you might want to tweak `homepage` parameter in [front/package.json](front/package.json) if you intend to use something different from `http(s)://your_address/game`.

## config

Sample file with themes is supplied in this repo ([questions.txt](questions.txt)), but you can provide your own. File is expected to have following structure: each line contains single theme in form of a word or short sentence; at the end of each line you may add optional `*` sign followed by number to indicate how many times this theme will appear. For example, `fruit` and `international brand * 4` are valid entries.

The distribution of letters is controlled by `get_letter` function in [freq.py](freq.py). By default, frequencies of first letters taken from Wikipedia are used, but you may switch to even distribution or supply your own function.
