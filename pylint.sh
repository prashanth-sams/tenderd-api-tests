set -x
PROJECT=pytest_raises
if [ -z "$1" ]; then
    FILES="$(find $PROJECT -maxdepth 3 -name "*.py" -print) $(find tests -maxdepth 3 -name "*.py" -print)"
else
    FILES="$1"
    echo "linting $FILES"
fi
pylint $FILES --reports=yes --rcfile=.pylintrc