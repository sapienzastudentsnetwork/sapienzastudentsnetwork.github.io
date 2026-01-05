---
title: Software needed
aliases: ["/30786/info/student-life/software"]
weight: 3
bgimg: https://i.imgur.com/aJ9NVsb.png
---

# Software needed for the course

Throughout the course, it will be common to use some software for teaching and interactive purpouses (after all, it's a computer science course). If you are not very used to tweaking your computer, then it might be hard sometimes to understand what to do. This page tries to make a comprehensive list of all the needed software for following easily the course.

{{% hint info %}}
<i class="fa-solid fa-circle-info" style="color: #74C0FC;"></i> **Different OSs and Software Versions**

This guide will differ in some points depending on the operating system that you might have. When that will be the case, you'll see different tabs depending on the OS that you use. Rest assured that each software treated here will be compatible with your OS.

Since this guide can't be updated every time a new version of a particular piece of software comes out (unless a major release with ground-breaking features gets published), we are trying to provide a version-agnostic guide that should work for every version. If you notice some mismatches between the screenshots, that is because this guide was written in more than one day, so some programs got updated in the meanwhile, but you don't have to worry about that
{{% /hint %}}

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

{{% hint info %}}
<i class="fa-solid fa-circle-info" style="color: #74C0FC;"></i> **Difference between Anaconda and Conda**

In this guide, you'll often find the terms of "Anaconda" and "Conda", which represent two different things:
 - "Anaconda" represents the full package provided by [anaconda.org](https://www.anaconda.com), which comprehends the Conda package manager and other programs;
 - "Conda" is the package manager, which will be, in some cases throughout this guide, an alternative to the package managers of some programming languages (in most of the cases, it will replace Python's PyPi package manager, also known as `pip`).
{{% /hint %}}

Now, before installing Conda, you have different roads ahead: since the whole package provided from Conda contains a lot of softwares, you may not want to install all of it (for example if you have an old computer or not a lot of space on your hardisk); perhaps you already have installed Python for other projects, and you don't want to redo everything just for Conda. By itself, Conda is necessary for some packages, so here we'll explain how to install Python in 2 different ways:
 1. **with the full version of Anaconda**<br>If you have enough space on your computer, and you don't mind downloading some extra stuff, opt for this option;<br><br>
 2. **with the minimal version of Anaconda (called Miniconda)**<br>If you don't want to download the full package of Conda, and you feel a bit confident with the terminal, then this might be a good option for you.

---

### 1) Install through Anaconda

1. Head over to the [Anaconda download page](https://www.anaconda.com/download/success) and, depending on your operating system, **download the install file**. If you are on macOS, then you'll have two download options depending on your CPU (if you are not sure, check the CPU model by going on <i class="fa-brands fa-apple"></i> <i class="fa-solid fa-greater-than fa-xs"></i> About this Mac):
    - if you have a Macbook that came out after 2020 with an **M*** CPU (like M1, M2, etc...), then download the "64-Bit (**Apple silicon**) Graphical Installer";
    - if you have a Macbook that came with an **Intel CPU**, then download the "64-Bit (**Intel chip**) Graphical Installer";
2. **Execute the installer** (as an administrator on Windows and as super user through `sudo` on Linux) and follow the procedures. If everything went smoothly, Anaconda will be installed on your computer;

{{% hint warning %}}
<i class="fa-solid fa-triangle-exclamation" style="color: #FFD43B;"></i> **Windows: Add to `PATH` variable**

On Windows, the installer will ask you, before the end of the installation, if you want to add Conda to the `PATH` environment variable.

<img src="/imgs/anaconda_win_PATH.png" style="width: 70%; margin: 0 5% 0 5%; box-shadow: 5px 5px 30px rgba(0, 0, 0, 0.55); border-radius: 8px;">

What does it mean and what does it do? The `PATH` environment variable is a Windows variable which stores some locations on your disk where the applications are usually saved. This helps the OS to know where to find the binaries of each application. This is not only used on Windows, but also on UNIX systems (so macOS and Linux). Anaconda by default recommends you to not add it to the path.

This is done in order to have a separate console just for Conda, in order not to mix it with the standard terminal. However, this might create more confusion, as you would always need to open the Conda console each time that you'll need it. By adding Conda to the `PATH` variable, Windows will be able to use Conda also from the Command Prompt and from the Powershell.

TLDR: if you want to be able to use Conda from anywhere in your PC, add it to the `PATH` variable.

{{% /hint %}}

3. Check that Conda is installed:

{{% tabs "condacheck" %}}
{{% tab "Windows" %}}

Open the menu, and scroll down on the installed applications until you find a folder called "Anaconda3 (`XX`-bit)" (where `XX` stands for either 32 or 64, depending if your operating system is a 32 or 64 bit one): open the folder and click on the `Anaconda Prompt` application. After it opens, execute the following command to test that everything is working fine:

```bash
conda --version
```

If everything goes well, you should see the following output, so the name `conda` and the currently installed version (in this case, `conda 25.11.1`)

<img src="/imgs/anaconda_check_version.png" style="width: 70%; margin: 0 5% 0 5%; box-shadow: 5px 5px 30px rgba(0, 0, 0, 0.55); border-radius: 8px;">


{{% /tab %}}
{{% tab "Linux / macOS" %}}

Open the terminal, and type the following command to test that everything is working fine:

```bash
conda --version
```

You should see the following output, so the name `conda` and the currently installed version (in this case, `conda 25.11.1`);

<img width="90%" style="margin-left: 5%; box-shadow: 5px 5px 30px rgba(0, 0, 0, 0.75)" src="https://i.imgur.com/6afvZ7w.png">

{{% /tab %}}
{{% /tabs %}}

4. And that's it! If you managed to arrive this far, this means that you installed without problems Anaconda and Conda. You can proceed to the [next section](#installing-the-required-packages).

---

### 2) Install through Miniconda

1. Head over to the [Miniconda download page](https://docs.anaconda.com/miniconda/#latest-miniconda-installer-links) and download the installation file;

{{% tabs "minicondainstall" %}}
{{% tab "Windows" %}}

2. Once you downloaded the installer, start it and go through the first welcoming steps. Accept the license and chhose whether you want to install Conda just for you or all the users in the PC. The choice here is not relevant, so pick what suits you best;

<img src="/imgs/anaconda_win_1.png" style="width: 70%; margin: 0 5% 0 5%; box-shadow: 5px 5px 30px rgba(0, 0, 0, 0.55); border-radius: 8px;">

3. Choose a path for installing Conda. You can also leave the standard path;

<img src="/imgs/anaconda_win_2.png" style="width: 70%; margin: 0 5% 0 5%; box-shadow: 5px 5px 30px rgba(0, 0, 0, 0.55); border-radius: 8px;">

4. Here you will have the possibility of adding Conda to the `PATH` system variable. Although the installer does not recommend doing it, **we strongly recommend doing so**. If you want more info about what the `PATH` variable is and how it works, refer to the callout we made [at the beginning of the section](#1-install-through-anaconda). After deciding whether you want to add Conda to `PATH` or not, click on Next and install Conda;

<img src="/imgs/anaconda_win_PATH.png" style="width: 70%; margin: 0 5% 0 5%; box-shadow: 5px 5px 30px rgba(0, 0, 0, 0.55); border-radius: 8px;">

5. Wait for the installer to finish;

<img src="/imgs/anaconda_win_3.png" style="width: 70%; margin: 0 5% 0 5%; box-shadow: 5px 5px 30px rgba(0, 0, 0, 0.55); border-radius: 8px;">

6. Once the installer ends, click on `Finish`. You've now installed Conda!

<img src="/imgs/anaconda_win_4.png" style="width: 70%; margin: 0 5% 0 5%; box-shadow: 5px 5px 30px rgba(0, 0, 0, 0.55); border-radius: 8px;">

7. You can try that everything got installed by typing `conda --version` in the Terminal (either PowerShell or Command Prompt will do). You should see an output like the following:

<img src="/imgs/anaconda_check_version.png" style="width: 70%; margin: 0 5% 0 5%; box-shadow: 5px 5px 30px rgba(0, 0, 0, 0.55); border-radius: 8px;">

{{% /tab %}}
{{% tab "macOS" %}}

2. Depending on your CPU, choose your installer (either in the `.pkg` or `.sh` format):
    - if you have a Macbook that came out after 2020 with an **M*** CPU (like M1, M2, etc...), then download the "Miniconda3 macOS Apple M1 64-Bit pkg/bash";
    - if you have a Macbook that came with an **Intel CPU**, then download the "Miniconda3 macOS Intel x86 64-Bit pkg/bash";

    In this section, we'll use the `.pkg` file, which is the graphical installer. If you prefer to use the `.sh` file, then follow the **Linux** instructions (since they are both UNIX based OSs, the terminal instructions are equivalent);

3. Once you downloaded the installer, run it and go through it:

<small>1) First page of the installer</small>
<img src="https://i.imgur.com/vk6OmK6.png">

<small>2) Choose where to install Miniconda</small>
<img src="https://i.imgur.com/1Amx3ni.png">

<small>3) Wait until it finishes installing</small>
<img src="https://i.imgur.com/29RpAdO.png">

<small>4) You're done! Go forth to the next step</small>
<img src="https://i.imgur.com/GW9Oelq.png">

4. Open the terminal, and type the following command to test that everything is working fine:

```bash
conda --version
```

You should see the following output, so the name `conda` and the currently installed version (in this case, `conda 24.1.2`);

<img width="90%" style="margin-left: 5%; box-shadow: 5px 5px 30px rgba(0, 0, 0, 0.75)" src="https://i.imgur.com/6afvZ7w.png">

{{% /tab %}}
{{% tab "Linux" %}}

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
7. Open the terminal, and type the following command to test that everything is working fine:

```bash
conda --version
```

You should see the following output, so the name `conda` and the currently installed version (in this case, `conda 24.1.2`);

<img width="90%" style="margin-left: 5%; box-shadow: 5px 5px 30px rgba(0, 0, 0, 0.75)" src="https://i.imgur.com/6afvZ7w.png">

{{% /tab %}}
{{% /tabs %}}

---

### Installing the required packages

While in the Programming course you'll only need the standard library, for running and testing the homework you'll need some extra packages. This is where Conda comes into play: it's needed to download all the necessary stuff for running the tests on the homeworks. We'll here provide a list of all the packages needed, alongside what they do and how to install them. The original list is available on the <a href="https://q2a.di.uniroma1.it/25026/news-software-and-required-libraries?show=25026#q25026&course=advices/programming-ay22-23" target="_blank">Q2A site</a>.

|Package|Description|
|---|---|
|`ddt`|Allows to run tests described on a JSON file|
|`pytest-timeout`|Allows to apply a timeout for each test execution|
|`stopit`|Allows to apply a timeout for the execution of just a function|
|`pytest-profiling`|Allows to compute the time needed to execute each function|
|`radon`|Allows to compute the [intricacy](https://radon.readthedocs.io/en/latest/intro.html#cyclomatic-complexity) of the code|
|`typeguard`|Allows to check that the parameter and return types of a function are respected|
|`pandas`|A Python library used for managing and manipulate data|

All these packages can be installed in one go with the following command. This comman must be run either in the Conda Prompt (if you are on Windows and **did not** integrate Conda with your main shell) or in the shell/Terminal (on macOS or Linux):

```bash
conda install -c conda-forge \
    ddt pytest-timeout stopit pytest-profiling radon typeguard pandas
```

You can update all the packages installed with Conda in one go by executing the following command:

```bash
conda update --all
```

{{% hint info %}}
<i class="fa-solid fa-circle-info" style="color: #74C0FC;"></i> **Regarding Spyder**

While we said that we won't cover a section over which coding editor is preferrable for the Programming course, we will go over how to install the Spyder IDE (Integrated Development Environment) because it will be the editor used by the professors during the lectures and it will also be the editor that **you'll have to use at the exam**!

Spyder and all its dependencies can be installed with
```bash
conda install -c conda-forge spyder
```

In order to update it, you can use the same command for updating all the packages installed through Conda
{{% /hint %}}

---

## Java

Used in the Programming 2 course, Java is a fundamental part when it comes down to learning Object-Oriented Programming (OOP). Unlike for Python and all its dependencies, Java is pretty straightforward to install:

1. Head to the [Java download page](https://www.java.com/en/download/) and download the installer (it will automatically detect the right installer for your OS);
2. Execute the installer and go through the installation process;
3. That's it! You installed Java!

You can check that you installed Java without issues by opening a terminal and typing

```bash
java --version
```

You should see a similar output:

<img src="https://i.imgur.com/xAwvYHp.png" width="90%" style="margin-left: 5%; box-shadow: 5px 5px 30px rgba(0, 0, 0, 0.75)">

The professor will suggest you to also download [IntelliJ IDEA](https://www.jetbrains.com/idea/), JetBrains' Java IDE, which is one of the most advanced Java IDEs. There are two editions of IntelliJ IDEA: the **community** edition and the **ultimate** edition. The **community** edition is free for everyone for personal use only (academic use is fine), while the **ultimate** edition requires you to pay a license for it. Luckily, it's possible to get a [free license](https://www.jetbrains.com/community/education/#students) for all the JetBrains products while you are a student.

---

## RARS

Used in the Computer Architecture Unit 2 course, RARS is a RISC-V processor emulator, which allows you to write and run Assembly code for the RISC architecture. It's possible to download the program at [this link](https://github.com/TheThirdOne/rars?tab=readme-ov-file#download). Since it's a Java application, you'll need Java installed on your computer.

{{% hint warning %}}
<i class="fa-solid fa-triangle-exclamation" style="color: #FFD43B;"></i> **Warning**

On RARS, whenever you want to save or open a file, the program will always open the file explorer on the location where RARS is saved. So for instance, if I saved RARS under `~/Applications/RARS.jar` and my file is at `~/Documents/RISCV/my-file.asm`, then when I open RARS and try to open `my-file.asm`, the explorer pop-up will be on `~/Applications`.

In order to avoid this, the best strategy is to put RARS in a parent folder of the folder where you keep your Assembly files. So for instance, it could be put inside `~/Documents/RISCV`
{{% /hint %}}

There are two available versions of RARS, a light themed one and a dark themed one. They are both working fine, and have the same capabilities. If you want to download the dark themed RARS, remember to **download also the `theme.properties` file and place it in the same folder where you will place RARS** (this is not required for the normal version of RARS). Here are the download links for both versions:

|<img src="https://i.imgur.com/Q2ECXhe.png"><br>[Download link for RARS](https://github.com/TheThirdOne/rars)|<img src="https://i.imgur.com/oz4vfe5.png"><br>[Download link for dark RARS](https://github.com/antis0007/m-rars)|
|---|---|

---

## Python (for AI Lab)

For the AI Lab: Computer Vision and NLP course our beloved Python will be needed again, only that this time we will need to install some new packages. Chances are that, after the Programming course, Conda and Python are still there on your computer. If that is not the case don't worry, you don't need to install them again. If they still are there on your computer, then you might want to take advantage of Conda's virtual environment.

A virtual environment is a Conda feature that allows you to install Python's packages and libraries in a separate and protected enviroment. This is so that you can have different configurations of packages that won't clash between each other. Conda is one of the systems, alongside `pyvenv`, that allows users to make virtual environments.

If you don't want to take advantage of Conda's virtual environments, just go to the end of the section, where you'll be able to copy a command for installing all of the needed packages for the course.

### Creating a Conda environment

1. In order to create a Conda environment, you'll need to have installed either Anaconda or Miniconda. If you haven't installed them, you can follow either the guide for [installing Anaconda](#1-install-through-anaconda) or the one for [Miniconda](#2-install-through-miniconda);
2. Open either a Conda shell (on Windows) or a Terminal (or macOS or Linux) and type the following command:

    ```bash
    conda create --name <env_name> -y
    ```

    where `<env_name>` is a name that you will give to your environment. A good name could be `ailab` for instance, but it's up to you to what suits you best;
3. Now, in order to use the environment, type the following command in the terminal:

    ```bash
    conda activate <env_name>
    ```
4. When a new environment gets created, it contains nothing. We must then install Python and `pip`, a package manager for Python's libraries. We can install Python and `pip` with the following command:
    ```bash
    conda install python pip -y
    ```

{{% hint info %}}
<i class="fa-solid fa-circle-info" style="color: #74C0FC;"></i> **Selecting the environment and default environment**

The above command must be executed each time that you open up a terminal (if you run your scripts on the Terminal). By itself, Conda will start on the `base` environment, hence why you have to change it everytime. If you want to change it by default everytime, then you will need ot [tweak up a bit with your terminal](https://stackoverflow.com/questions/28436769/how-to-change-default-anaconda-python-environment).

On code editors like Visual Studio Code, you can easily select via a menu which environment you want to use, and it will be remembered after closing the application. Even better, if you use Jupyter notebooks, they will ask you at the very beginning which kernel (or environment) you want to use, and also in that case your choice will be remembered by the editor.

{{% /hint %}}

{{% details title="**Select the environment on Visual Studio Code**" open=false %}}

On single **Python scripts**, you can select your environment by doing the following:
1. Open a Python file, and go on the bottom right corner. There, you'll find next to the `Python` button another button with a version of Python. Click that button;

<img src="https://i.imgur.com/meQfljn.png">

2. A pop-up will open, asking you which environment you want to use. Select the environment that you prefer most.

<img src="https://i.imgur.com/kMpRLZF.png">

---

On **Jupyter notebooks**, you can select your environment by doing the following:
1. Open a Jupyter notebook, and look for the top right corner. You'll find a button that says "Detecting Kernels": click on that button;

<img src="https://i.imgur.com/sYkFz3F.png">

2. A pop-up will open, asking you which kind of kernel you want to load. Click on `Python Environments`;

<img src="https://i.imgur.com/SEEl5tQ.png">

3. Here, you'll find a list of all your Conda environments. Select the environment that you want to use with the notebook;

<img src="https://i.imgur.com/7POcDpt.png">

4. And voilà, you are there! You can check that your kernel got loaded successfully by looking at the button of Step 1: if it now displays the name of your Conda environment, then you're set!

<img src="https://i.imgur.com/LTrAVDg.png">

{{% /details %}}


### Installing the required packages

In order to install all the needed packages, you can use the `pip` package manager with the following command (if you haven't installed `pip`, run on your terminal `conda install -c conda-forge pip -y`), which will install everything in one go:

```bash
pip install numpy matplotlib scikit-learn opencv-contrib-python seaborn nltk
```

Later on in the course you will also need to use Pytorch. In order to install it, then you must refer to [Pytorch's download page](https://pytorch.org/get-started/locally/), since it will auto detect your system hardware and will thus indicate what's the best setup for you.

<!--
---

## R

---

<kbd>⌘</kbd> + <kbd>R</kbd>
-->
