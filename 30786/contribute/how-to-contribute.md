---
title: "How to contribute"
aliases: ["/contribute", "/en/contribute"]
bookToC: false
weight: 1
---

# How to Contribute

## Cloning the Project

To contribute to the website content, you need to **fork** the project and open a [**pull request**](https://github.com/sapienzastudentsnetwork/sapienzastudentsnetwork.github.io/pulls) with the proposed changes. The changes will be reviewed by the [project curators](/en/contribute/project-curators) before being integrated into the site. If you are not familiar with **git** and **GitHub**, you can follow the [GitHub guide](https://docs.github.com/en/get-started/quickstart/contributing-to-projects) on how to contribute to projects, or ask for help from one of the [project curators](/en/contribute/project-curators) or in one of the available [groups](/en/channels/telegram).

## Running the Site Locally

To run the site locally and test the code, follow the commands listed below, and open [localhost:4000](http://localhost:4000/) in your browser. You need to have [**Docker**](https://www.docker.com/) installed.

```bash
docker build -t hugo-site . # Only the first time
sudo docker run --rm -p 1313:1313 -v $(pwd):/app hugo-site # Every time you work on the project
```

You can stop the execution at any time by pressing `Ctrl+C` in the terminal.

## Suggestions / Bugs

If you have suggestions to improve the site or want to report a bug or issue with the site, you can open an [ISSUE](https://github.com/sapienzastudentsnetwork/sapienzastudentsnetwork.github.io/issues) on the GitHub repository. Thank you very much in advance for your contribution :-)
