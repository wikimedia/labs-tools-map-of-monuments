#map-of-momuments

Map of Monuments with no article.

# Run development environment

(all paths are from repository's root)

1. Clone the repository (preferably from [Gerrit](https://gerrit.wikimedia.org/r/admin/projects/labs/tools/map-of-monuments)
2. Setup the repository for use with git review. You can use [this tutorial](https://www.mediawiki.org/wiki/Gerrit/Tutorial)
3. Create Python3 virtual environment by running `virtualenv -p python3 venv`
4. Activate the venv by running `source venv/bin/activate`
5. Install required packages by running `pip install -r support/requirements.txt`
6. Cd to src and copy config.example.yaml to config.yaml
7. Add your MySQL db credentials to config.yaml file
8. Run `python app.py` to run the development server
