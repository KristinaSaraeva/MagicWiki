# MAGIC WIKI

## Description

A Python3 project to find where Wikipedia(en) links may lead inside. 

## Cache and cache async

Start your journey with:

`python3 cache.py -p 'cat'` (if you want to know about cats, or you can choose anything else from wiki)

The script will parse up to thousand links for you and store it in a json. But rather slowly. If you wnat it faster try:

`python3 cache_async.py -p 'cat'`

(If you don't provide an argument it will start with 'python language' )

The script is going at least three pages deep down every link. This parameter is
configurable using `-d` (3 by default).


# Graph

Now you can see all the realtions between the parsed links.

Run `python3 graph.py --render` and look at the png file in the directory.

If you want to see the path between two pages run `python3 graph.py --from page1 --to page2`

### Dependencies

- Python3
- Pycairo for visualization

### Installing

1. Clone this repository to your local machine.
2. Create the environment, activate it and install the requirements.
3. If you use Mac you may need to `brew install cairo` and  `brew install pkg-config` first.
4. Travel around wiki.


## Author

[Kristina Saraeva](https://github.com/KristinaSaraeva)


© 2024 KristinaSaraeva
