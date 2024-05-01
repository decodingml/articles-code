# A Kickstart to Real Time Deep Learning Video Streaming

Throughout the article, we’ll cover the basics of video data, what libraries you could use, understand video formats, and set up a basic app to stream media between two entities (API, Client).

<b>We're going to learn about the following: </b>

- video format components
- video re-encoding process
- tools to work with video in Python
- streaming video using HTTP
- streaming video using WebSockets
- streaming video using WebRTC

## Table of Contents

- [Articles](#articles)
- [Dependencies](#dependencies)
- [Install](#install)
- [Usage](#usage)
- [Notes](#notes)
- [License](#license)
- [Author](#contributors)

## Articles

This is a code-first summary version, make sure to read the article in full ↓

1. [Summary]()
2. [Full]()

## Dependencies

- [Python (version 3.19)](https://www.python.org/downloads/)
- [Miniconda (version 24.1.2)](https://docs.anaconda.com/free/miniconda/index.html)
- [Poetry (version 1.7.1)](https://python-poetry.org/)
- [GNU Make (version 3.81)](https://www.gnu.org/software/make/)
- [NPM](https://docs.npmjs.com/downloading-and-installing-node-js-and-npm)

## Install

We're using Poetry to manage the env and dependencies of this project.
<b> You don't need a GPU to run this </b>

To install, run this following command:

```shell
make install_env
```

This will create a new conda environment called `py39video`, activate it and install dependencies defined in `pyproject.toml`.

## Usage

The `Makefile` found at the root of this project, contains 5 commands:

- `install_env` : installs all the required packages
- `run_api` : will start the FastAPI backend
- `run_ui` : will start the React Web app

Here's the full command-set to start the solution:

1. Start Backend : `make run_api`
2. Start Frontend : `make run_ai`

## License

This article is an open-source project released under the MIT license. Thus, as long you distribute our LICENSE and acknowledge our work, you can safely clone or fork this project and use it as a source of inspiration for whatever you want (e.g., work, university projects, college degree projects, etc.).

## Author

<table>
  <tr>
    <td><a href="https://github.com/Joywalker" target="_blank"><img src="https://github.com/Joywalker.png" width="100" style="border-radius:50%;"/></a></td>
    <td>
      <strong>Razvant Alex</strong><br />
      <i>Senior ML Engineer</i>
    </td>
  </tr>
</table>
