
1. Environment Configuration

-Create a virtual environment with following command
>conda env create -f environment.yml

-Activate virtual environment
>conda activate gbaenv

* The Other Way
	-Create a virtual environment
	gba>conda create -n gbaenv pip

	-Activate virtual environment
	gba>conda activate gbaenv

	-Install pip
	(gbaenv)..gba> pip install -r req.txt

2. Run

Check if virtual environment is activated
If it's not activated please activate with following command
conda activate gbaenv

- Create mode
>scrapy crawl gba -a mode=create

-Update mode
>scrapy crawl gba -a mode=update

* You can run it with batch file
- Create mode
>gba-start.bat

-Update mode

>gba-update.bat