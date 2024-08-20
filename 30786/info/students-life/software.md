---
title: Software needed
weight: 3
bookHidden: true
---

# Software needed for the course

Throughout the course, it will be common to use some software for teaching and interactive purpouses (after all, it's a computer science course). If you are not very used to tweaking your computer, then it might be hard sometimes to understand what to do. This page tries to make a comprehensive list of all the needed software for following easily the course.

{{< hint info >}}
<i class="fa-solid fa-circle-info" style="color: #74C0FC;"></i> **Different OSs**

This guide will differ in some points depending on the operating system that you might have. When that will be the case, you'll see different tabs depending on the OS that you use. Rest assured that each software treated here will be compatible with your OS
{{< /hint >}}

---

## Python (for Programming)

Used for some of the courses in ACSAI, Python will be a very handful software, so it's important to set it up properly. You'll mainly need it in the following courses:
 - Programming (first year, first semester);
 - AI Lab (second year, second semester);
 - Machine Learning (second year, second semester).

During the Programming course, you'll be given [some instructions](https://q2a.di.uniroma1.it/getting-started-with-python) on what packages you need to use and what to install. Here, we'll break it down a bit and better explain what does what.

For the Programming course you'll mainly need 2 things:
 - a **fresh installation** of **Python**, whose version must be ≥ 3.7;
 - a **text editor** (for coding, not like Word, LibreOffice or Google Docs) of your choice;

In this guide we won't focus on the text editors, but only on how to install Python and the necessary stuff. The professors will suggest you to download Python through [**Anaconda**](https://www.anaconda.com/), which offers in a single installation a GUI application for managing Python and its packages, Conda's virtual environments (which will be useful later), the [Spyder](https://www.spyder-ide.org/) text editor and a lot of other tools.

{{< hint info >}}
<i class="fa-solid fa-circle-info" style="color: #74C0FC;"></i> **Difference between Anaconda and Conda**

In this guide, you'll often find the terms of "Anaconda" and "Conda", which represent two different things:
 - "Anaconda" represents the full package provided by [anaconda.org](https://www.anaconda.com), which comprehends the Conda package manager and other programs;
 - "Conda" is the package manager, which will be, in some cases throughout this guide, an alternative to the package managers of some programming languages (in most of the cases, it will replace Python's PyPi package manager, also known as `pip`).
{{< /hint >}}

Now, before installing Conda, you have different roads ahead: since the whole package provided from Conda contains a lot of softwares, you may not want to install all of it (for example if you have an old computer or not a lot of space on your hardisk); perhaps you already have installed Python for other projects, and you don't want to redo everything just for Conda. By itself, Conda is necessary for some packages, so here we'll explain how to install Python in 2 different ways:
 1. **with the full version of Anaconda**<br>If you have enough space on your computer, and you don't mind downloading some extra stuff, opt for this option;<br><br>
 2. **with the minimal version of Anaconda (called Miniconda)**<br>If you don't want to download the full package of Conda, and you feel a bit confident with the terminal, then this might be a good option for you.

---

### 1) Install through Anaconda

1. Head over to the [Anaconda download page](https://www.anaconda.com/download/success) and, depending on your operating system, **download the install file**. If you are on macOS, then you'll have two download options depending on your CPU (if you are not sure, check the CPU model by going on <i class="fa-brands fa-apple"></i> <i class="fa-solid fa-greater-than fa-xs"></i> About this Mac):
    - if you have a Macbook that came out after 2020 with an **M*** CPU (like M1, M2, etc...), then download the "64-Bit (**Apple silicon**) Graphical Installer";
    - if you have a Macbook that came with an **Intel CPU**, then download the "64-Bit (**Intel chip**) Graphical Installer";
2. **Execute the installer** (as an administrator on Windows and as super user through `sudo` on Linux) and follow the procedures. If everything went smoothly, Anaconda will be installed on your computer;

{{< hint warning >}}
<i class="fa-solid fa-triangle-exclamation" style="color: #FFD43B;"></i> **Windows: Add to `PATH` variable**

On Windows, the installer will ask you, before the end of the installation, if you want to add Conda to the `PATH` environment variable.

What does it mean and what does it do? The `PATH` environment variable is a Windows variable which stores some locations on your disk where the applications are usually saved. This helps the OS to know where to find the binaries of each application. This is not only used on Windows, but also on UNIX systems (so macOS and Linux). Anaconda by default recommends you to not add it to the path.

This is done in order to have a separate console just for Conda, in order not to mix it with the standard terminal. However, this might create more confusion, as you would always need to open the Conda console each time that you'll need it. By adding Conda to the `PATH` variable, Windows will be able to use Conda also from the Command Prompt and from the Powershell.

TLDR: if you want to be able to use Conda from anywhere in your PC, add it to the `PATH` variable.

{{< /hint >}}

3. Check that Conda is installed:

{{< tabs "uniqueid" >}}
{{< tab "Windows" >}}

Open the menu, and scroll down on the installed applications until you find a folder called "Anaconda3 (`XX`-bit)" (where `XX` stands for either 32 or 64, depending if your operating system is a 32 or 64 bit one): open the folder and click on the `Anaconda Prompt` application. After it opens, execute the following command to test that everything is working fine:

```bash
conda --version
```

If everything goes well, you should see the following output, so the name `conda` and the currently installed version (in this case, `conda 24.1.2`)

TODO: insert screen of Anaconda prompt

{{< /tab >}}
{{< tab "Linux / macOS" >}}

Open the terminal, and type the following command to test that everything is working fine:

```bash
conda --version
```

You should see the following output, so the name `conda` and the currently installed version (in this case, `conda 24.1.2`);

<img width="90%" style="margin-left: 5%; box-shadow: 5px 5px 30px rgba(0, 0, 0, 0.75)" src="https://i.imgur.com/6afvZ7w.png">

{{< /tab >}}
{{< /tabs >}}

4. And that's it! If you managed to arrive this far, this means that you installed without problems Anaconda and Conda. You can proceed to the [next section](#installing-the-required-packages).

---

### 2) Install through Miniconda

1. Head over to the [Miniconda download page](https://docs.anaconda.com/miniconda/#latest-miniconda-installer-links)

{{< tabs "uniqueid" >}}
{{< tab "Windows" >}}

to-do

{{< /tab >}}
{{< tab "macOS" >}}

to-do

{{< /tab >}}
{{< tab "Linux" >}}

2. Open a terminal, and `cd` to the Downloads folder (or where you downlaoded the install script). In our case, it will be under `~/Download`:

```bash
cd Download
```

3. Execute the script with `sh`:

```bash
sh ./Miniconda3-latest-Linux-x86_64.sh
```

4. Once the script launches, press <kbd>ENTER</kbd> and scroll through the license (if you want to skip it, press <kbd>Q</kbd>) and accept it by typing `yes`;
5. If you want to install Miniconda under your home folder press <kbd>ENTER</kbd>, otherwise specify a new folder;
6. After pressing <kbd>ENTER</kbd>, Miniconda will unpack its resources in the folder specified above. After it, it will ask whether you want Conda to start each time you open the shell. If you want it to be always available once your shell starts, then type `yes`.

{{< /tab >}}
{{< /tabs >}}

---

### Installing the required packages

---

## Java

---

## RARS

---

## Python (for AI Lab)

---

## R

---

<kbd>⌘</kbd> + <kbd>R</kbd>


<!--
(to that extent, we highly suggest the Windows users to download their new official [Terminal app](https://apps.microsoft.com/detail/9n0dx20hk701), which supports various useful features)

---

If you want to create a new conda environment just for this subject, you can do the following steps:

Open a terminal (on Windows, if you don’t use the new Terminal app with PowerShell, open the conda shell by typing “conda“ on the search bar of the menu);

In order to create a new environment, type the following:

conda create --name ailab -y

Clearly the ailab name can be whatever you want. From now on, replace ailab with the name of your environment;

Once the environment is created, access it with the following:

conda activate ailab

Now, install Python and pip:

conda install python pip -y

After this, you’re good to go! You can install all the other packages that you may need with pip, by using the pip install <packages> formula;

OPTIONAL: if you want to install everything in one go, this command should be enough:

pip install numpy matplotlib scikit-learn opencv-contrib-python seaborn nltk

For PyTorch, follow the instructions on their website, since each installation command depends on your platform.
-->
