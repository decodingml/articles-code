#  The ABCs of Diffusion Models


This tutorial dives into the basics of Diffusion Models—how they work, how to train them, and how to run inference. 
<b>What you’ll Learn:</b>
- How the Diffusion Process works
- How to do Training and Inference for Diffusion Models
- Practical Use Cases and Most Recent Advances in the field

## Table of Contents

- [Articles](#article)
- [Dependencies](#dependencies)
- [Install](#install)
- [Usage](#usage)
- [License](#license)

## Articles

[Full Article](https://medium.com/decodingml/the-abcs-of-diffusion-models-51902a331068)

## Dependencies

- [Python (version 3.10)](https://www.python.org/downloads/)
- [Poetry (version 1.8.3)](https://python-poetry.org/)
- [GNU Make (version 3.81)](https://www.gnu.org/software/make/)

## Install

As we use Make and Poetry to manage the project, in order to install it you have to run the following:
```shell
make setup
```

And then run:
```shell
cp .env.example .env
```
To copy the values from the example .env file and fill them in.

## Usage

To start the training process locally you have to run the following: 

```shell
make train
```

To start the inference process locally you have to run the following: 

```shell
make inference
```

In case you don't want to run the training or inference locally, you can upload the Jupyter Notebooks and run them in Google Collab:
 - Diffusion_Inference.ipynb
 - Diffusion_Training.ipynb

## License

This article is an open-source project released under the MIT license. Thus, as long you distribute our LICENSE and acknowledge our work, you can safely clone or fork this project and use it as a source of inspiration for whatever you want (e.g., work, university projects, college degree projects, etc.).


## Author

<table>
  <tr>
    <td><a href="https://github.com/915-Muscalagiu-AncaIoana" target="_blank"><img src="https://github.com/915-Muscalagiu-AncaIoana.png" width="100" style="border-radius:50%;"/></a></td>
    <td>
      <strong>Anca Ioana Muscalagiu</strong><br />
      <i>Software Engineer</i>
    </td>
  </tr>
</table>

