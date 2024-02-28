# Real-time retrieval system for social media data

In this article, you will learn how to build a real-time retrieval system for social media data. In our particular scenario, we will use only my LinkedIn posts, which can easily be extended to other platforms supporting written content, such as X, Instagram, or Medium.

Social media data platforms produce data at high frequencies, so the vector DB can easily remain behind relative to the other data sources from your system. Thus, we will show you how to build a streaming engine to constantly move data from a raw data source to a vector DB in real-time.

In this article, we will explain only the retrieval part of an RAG system. Still, you can quickly hook the retrieved LinkedIn posts to an LLM for post analysis or personalized content generation.

![Architecture](./media/social_media_retrieval_system_architecture.png)

**That being said, in this article, you will learn:**

- to build a streaming pipeline to ingest LinkedIn posts into a vector DB in real-time
- to clean, chunk, and embed LinkedIn posts
- build a retrieval client to query your LinkedIn posts
- use the rerank pattern to improve the retrieval accuracy
- visualize the retrieval for a given query in a 2D plot using UMAP

## Table of Contents

- [Articles](#articles)
- [Dependencies](#dependencies)
- [Install](#install)
- [Usage](#usage)
- [License](#license)
- [Contributors](#contributors)

------

## Articles

To fully grasp the code, check out our articles ↓

1. [Summary]()
2. [Full Article]()

## Dependencies

- [Python (version 3.11)](https://www.python.org/downloads/)
- [Poetry (version 1.6.1)](https://python-poetry.org/)
- [GNU Make (version 3.81)](https://www.gnu.org/software/make/)
- [Docker (version 24.0.7)](https://www.docker.com/) or [Qdrant](https://qdrant.tech/)

> [!IMPORTANT] 
> We also support running Qdrant locally within a Docker container, so you don't have to make an account on Qdrant. But they offer a free plan that is enough to run the code within this article. In case you want to run Qdrant locally, you need Docker. If you use Qdrant's serverless version, you don't need Docker.

## Install

As we use Make and Poetry to manage the project, to install the project, you have to run the following:
```shell
make install
```

In case you use Qdrant's serverless option, you have to add its authentication credentials in a `.env` file, as follows:
```shell
cp .env.example .env
```
...and fill in the `QDRANT_URL` and `QDRANT_API_KEY` environment variables.

## Usage

In case you run Qdrant locally, spin it up using the following command:
```shell
make run_qdrant_as_docker
```

Ingest the LinkedIn posts into Qdrant (make sure your Qdrant instance is running before triggering this command):
```shell
make run
```

You can run the retrieval client and visualizations within the following Jupyter Notebook:
`-> retrieve.ipynb`

## License

This article is an open-source project released under the MIT license. Thus, as long you distribute our LICENSE and acknowledge our work, you can safely clone or fork this project and use it as a source of inspiration for whatever you want (e.g., work, university projects, college degree projects, etc.).

## Contributors

<table>
  <tr>
    <td><a href="https://github.com/iusztinpaul" target="_blank"><img src="https://github.com/iusztinpaul.png" width="100" style="border-radius:50%;"/></a></td>
    <td>
      <strong>Paul Iusztin</strong><br />
      <i>Senior ML & MLOps Engineer</i>
    </td>
  </tr>
</table>
