# learning-pt-routing
This is an environment to learn and implement the Connection Scan Algorithm [[1]](#1) in Python.

The project is prepared in such a way that the implementation of the core algorithm, 
which is only a few lines long, can be started directly.
In particular, you do not have to do time-consuming preparatory work such 
as implementing a timetable data parser or creating suitable data structures, 
but you can start implementing the core algorithm immediately.

## Tasks

The goal is that you implement the following three variants of the 
Connection Scan Algorithm in the class ```scripts.connectionscan_router.ConnectionScanCore```.

#### Task 1: Unoptimized earliest arrival
Implement the following algorithm (figure 3 on page 7 of [[1]](#1)) in the function ```route_earliest_arrival```:

![image](docs/pseudocode_unoptimized_earliest_arrival.PNG)

#### Task 2: Unoptimized earliest arrival with reconstruction
Implement the following algorithm (figure 6 on page 10 of [[1]](#1)) in the function ```route_earliest_arrival_with_reconstruction```:

![image](docs/pseudocode_unoptimized_earliest_arrival_with_reconstruction.PNG)

#### Task 3: Optimized earliest arrival with reconstruction
Implement the following algorithm (figure 4 on page 8 of [[1]](#1)) in the function ```route_optimized_earliest_arrival_with_reconstruction```:

![image](docs/pseudocode_optimized_earliest_arrival_with_reconstruction.PNG)


## How to proceed
The following software should be installed on your computer:
- [Python 3.8 (64-bit)](https://www.python.org/downloads/release/python-381/.)
- [git](https://git-scm.com/downloads)
- A powerful text editor (i.e. [Sublime Text](https://www.sublimetext.com/])) or 
IDE (i.e. [Visual Studio Code](https://code.visualstudio.com/) or 
[PyCharm](https://www.jetbrains.com/de-de/pycharm/)) to develop the code.

### Installation
* Choose a folder for development and a folder for the virtual environment 
* Create the virtual environment:
   - Open a command line, navigate to the folder for the virtual environment
   - Create the virtual environment with ```py -m venv YOUR_NAME_OF_THE_VENV```
   - Activate the virtual environment with ```YOUR_NAME_OF_THE_VENV/Scripts/activate``` 
(depending on the platform this might be slightly different)
   - Assure that the virtual environment is running with the correct Python interpreter
* Install the project:
   - Navigate to the folder for development
   - Clone the project with ```git clone https://github.com/jlieberherr/learning-pt-routing.git```
   - Install the necessary python packages 
(the virtual environment must be activated) with ```pip install -r requirements.txt```
   - Run the default tests in the ```master``` branch: ```pytest tests/a_default```. 
   If you run all tests (with ```pytest```) all tests in ```tests/b_router``` will fail. Your task is to make them green.
* Create your branch and start coding:
   - If the default tests are green create your new branch: ```git branch NAME_OF_YOUR_NEW_BRANCH```
   - Checkout your new branch ```git checkout NAME_OF_YOUR_NEW_BRANCH```
   - Implement the three tasks in ```scripts.connectionscan_router.ConnectionScanCore```. 
   You can test your implementation per task with ```pytest tests/task_1```, ```pytest tests/task_2``` and
    ```pytest tests/task_3``` or all tests together with ```pytest```.
* Apply your implementation of the Connection Scan Algorithm on real world public transport networks:
   - Choose a [gtfs](https://developers.google.com/transit/gtfs/reference) feed from your preferred country or city, 
   for example from [transitfeeds.com](https://transitfeeds.com/)
   - Start Jupyter Lab from the development folder (the virtual environment must be activated) with ```jupyter lab```
   - Make a copy of the Jupyter notebook ```notebooks/route_on_real_world_gtfs.ipynb```
   - Link the chosen gtfs-feed in the notebook, parse it into a ```ConnectionScanCore``` object
   and run your implementation of the Connection Scan Algorithm on your preferred source-target-stop-relations. Are
   the results as expected? Does the optimization in task 3 improve the runtime?

## Prerequisites
To successfully complete the tasks you need some experience with algorithms and a solid 
understanding of Python. Especially you should be familiar with loops, 
if-else-statements and the typical data structures in Python (such as ```list```, ```dict```, ```tuple```, 
```class```, ...).

You should also have a basic understanding of the source control system [git](https://git-scm.com/), 
unit tests with [pytest](https://docs.pytest.org/en/latest/index.html), [Jupyter notebooks](https://jupyter.org/) 
, [virtual environments](https://docs.python.org/3/tutorial/venv.html) in Python and command line interaction.


## References
<a id="1">[1]</a> 
Julian Dibbelt, Thomas Pajor, Ben Strasser, Dorothea Wagner (2017). 
Connection Scan Algorithm. Available at https://arxiv.org/pdf/1703.05997.pdf
