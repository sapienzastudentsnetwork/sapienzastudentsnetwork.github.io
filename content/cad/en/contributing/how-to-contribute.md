# Contributing

SapienzaStudents.net is built **by students, for students**. It brings together practical information that is often scattered across many sources and turns it into guides, tools and shared resources that thousands of students can use. Keeping a project of this size accurate and useful takes a community: **even a small correction can save many people time and confusion**.
{{% hint info %}}
<i class="fa-solid fa-circle-info" style="color: #74C0FC;"></i> **Project contributors**

Visit the [contributors](../contributors/) page to see the people who have helped the wiki and the wider website grow. Every accepted contribution, large or small, becomes part of a resource the student community can keep improving together.
{{% /hint %}}

You do not need to be a developer, install anything or run the website locally to contribute. Fixing a typo, updating a deadline, clarifying a confusing paragraph, replacing a broken link or suggesting a missing guide are all valuable contributions.

{{% hint tip %}}
<i class="fa-solid fa-lightbulb" style="color: #238636;"></i> **Choose the simplest route**

- **Small content change:** use the edit button on the page and GitHub's web editor;
- **Suggestion, outdated information or bug:** open an issue. You do not need to know which file to change;
- **Larger content or code change:** use a fork and, when useful, run the site locally

A local development environment is an option, not an entry requirement.
{{% /hint %}}

## Quick contribution: edit a page in your browser

For most corrections to text and links, this is the recommended route. You only need a free GitHub account.

1. Open the page you want to improve on SapienzaStudents.net;
2. Use the **edit page** link or pencil button shown on the page. If the page is assembled from shared content, the site may offer more than one source file: choose the one containing the text you want to change;
3. GitHub will open the correct Markdown file. Click **Fork this repository** if GitHub asks you to create a fork;
4. Click the pencil icon, make the change and use the **Preview** tab to check the result;
5. Select **Propose changes**, briefly explain what you changed and open the pull request

That is all. GitHub handles the fork, branch and pull request for you, and the maintainers can review the change before it is published. You do **not** need to clone the repository, use the command line, install Hugo or build the site for a small content edit.

{{% hint info %}}
<i class="fa-solid fa-circle-info" style="color: #74C0FC;"></i> **A page may come from another repository**

Some guides are shared through Git submodules. The page's edit link points to the actual source repository, so follow that link rather than trying to locate the text manually in the main repository.
{{% /hint %}}

## Report a problem or propose an idea

If you are unsure how to correct something, or if your contribution is a proposal rather than a ready-made edit, [open an issue](https://github.com/sapienzastudentsnetwork/sapienzastudentsnetwork.github.io/issues) in the main repository.

Please include:

- the URL of the affected page;
- what is missing, incorrect or unclear;
- the corrected information and an authoritative source, when relevant;
- screenshots or steps to reproduce the problem, for bugs

You can also ask the [project staff](https://sapienzastudents.net/sapienza-students-network/?lang=en#sapienzastudentsnet) for help or join the [chat dedicated to the development of the website](https://t.me/addlist/8jXnS8NuTsxkMDlk). A precise report is already a useful contribution.

## What you can contribute

Contributions are not limited to code. For example, you can:

- correct typos, grammar, formatting and broken links;
- update dates, procedures, contacts and course information;
- make an explanation clearer or improve the English or Italian version;
- add a useful resource, FAQ, internship report or missing guide;
- improve accessibility, design, templates, automations or data;
- report a problem and help verify information

When a page exists in both languages, update both versions when possible and keep their meaning aligned. Prefer natural, locally appropriate wording over a literal translation. If you can update only one language, say so in the pull request: someone else can help complete the localization.

## Before you submit

A good contribution is focused and easy to verify:

- keep unrelated changes in separate pull requests;
- explain **what** changed and **why**;
- preserve front matter, shortcodes and the surrounding Markdown structure;
- check links and preview the formatted text;
- do not add personal, confidential or copyrighted material without permission;
- cite an official or reliable source for time-sensitive or administrative information;
- use clear, welcoming and inclusive language

You can browse [open pull requests](https://github.com/sapienzastudentsnetwork/sapienzastudentsnetwork.github.io/pulls) for examples. If maintainers request changes, that is a normal part of collaborative review.

## Full local workflow

Use this workflow for larger edits, code changes, structural work or anything you want to test locally. Basic familiarity with Git, forks, commits and pull requests is useful, but you can learn as you go.

### 1. Fork and clone the repository

1. Open the [website repository](https://github.com/sapienzastudentsnetwork/sapienzastudentsnetwork.github.io) and select **Fork**;
2. Clone your fork, including its submodules:

```bash
git clone --recurse-submodules https://github.com/<your-username>/sapienzastudentsnetwork.github.io.git
cd sapienzastudentsnetwork.github.io
```

If you already cloned without submodules, initialize them with:

```bash
git submodule update --init --recursive
```

3. Create a descriptive branch:

```bash
git switch -c improve-contribution-guide
```

4. Make your changes, then review them before committing:

```bash
git status
git diff
```

### 2. Run the site locally, if needed

Local preview is strongly recommended for templates, styles, scripts, navigation and substantial formatting changes. It is usually unnecessary for a small text correction made through GitHub.

### Docker Compose

Install [Docker](https://www.docker.com/) with Docker Compose, then run:

```bash
docker compose up --build
```

Open [`localhost:1313`](http://localhost:1313/) in your browser. Stop the site with `Ctrl+C`; if you started it in detached mode, use `docker compose down`.

Docker generates source-aware page metadata automatically. To skip that step for one run:

```bash
GENERATE_SOURCE_METADATA=false docker compose up --build
```
### Hugo

Install the Hugo version compatible with the repository, together with the project's front-end dependencies. From the repository root, run:

```bash
npm install
npm run build
hugo server
```

Open [`localhost:1313`](http://localhost:1313/). Hugo reloads the page when files change; press `Ctrl+C` to stop it.

The site works with Hugo's native Git metadata. To also verify edit links and last-change information for content included from other files or submodules, generate the optional local data file first:

```bash
python3 _scripts/generate-page-source-metadata.py
hugo server
```

The generated `data/page_source_metadata.json` file is ignored by Git.

### 3. Commit and open a pull request

```bash
git add <changed-files>
git commit -m "docs: improve contribution guide"
git push -u origin improve-contribution-guide
```

Open the link shown by Git, or visit your fork on GitHub, and create a pull request against the main repository's `main` branch. In the description, summarize the change, explain how you checked it and link any related issue.

## Need help?

Do not let an unfamiliar tool stop you from improving the project. [Open an issue](https://github.com/sapienzastudentsnetwork/sapienzastudentsnetwork.github.io/issues), send the proposed wording, or ask the community for guidance. Maintainers can help turn a good observation into a complete contribution.
