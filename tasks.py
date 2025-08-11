from invoke import task
import os


@task
def tests(c, env='ci', tags='smoke', rerun=2):
    """
    Task to run tests
    """
    
    c.run(f'python3 -m pytest ./tests/*_test.py --env={env} -m {tags} --reruns {rerun}')
