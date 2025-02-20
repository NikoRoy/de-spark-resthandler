# Intro:
A library intended to make spark dataframes distribute rest api calls

# Notes about spark environment and testing:
* TL;DR
    - Make sure that your local environment is configure with the databricks-cli, databricks-connect, etc so that you can turn on a cluster in the dev workspace in azure to run the spark code on. 

* Given the complexities of munging the Java Runtime Environments' Pyspark gateway, to side step Group Policy, Pyspark is not a direct dependency for the project. How then do we test
with the project?
* Well the first thing is that most of this project, in its current state, does not have any spark dependencies. So testing can be done without a SparkContext. Regular old unittest works. 
* For the limit classes that are dependent on Spark libraries, the context may be provided through a few mechanisms:
    - databricks-connect, databricks-cli +/- vscode extensions and the remote workspace clusters in the cloud. aka we're run tests against a live cluster with a .databrickcfg and databricks.yml pointing at dev (remote) (Recommended for now)
     
    - docker is another option to run a spark env. This would be a reliable way to control which spark version we can expect to work with when configuring the workspace clusters. However, manually changing or upgrading the spark versions may become a pain given all the permutations of workspace clusters. (local) (Not available until the docker licensing is settled and i actually produce a Dockerfile)

    - ideally, and most localized option, pyspark could be unit tested locally by just installing the pyspark library with tox managing a test matrix for a variety of environments and dependency versions. This circles back to the first note and secondly, tox isnt part of the project yet. Should development continue, I intend to add tox. 

* a Make file may also be produced but is not yet available.  


# Build + Test
## clean before build
- rm -rf dist/ 
- rm -rf build/
- rm -rf *.egg-info/

- python -m build

- python -m pip install -e . (where local directory will have the toml file for the package) -e is editable so build changes will be applied by pip automatically, omit the tack e for regular install
- python -m -unittest or python run_tests.py