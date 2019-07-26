from invoke import task


@task
def lint(c):
    c.run("echo Linting files...")
    c.run("autopep8 -i -r .")
