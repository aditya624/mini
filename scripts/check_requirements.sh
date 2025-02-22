### check_requirements.txt

NEW_REQUIREMENTS=$(poetry export --without-hashes)

if [ -f requirements.txt ]; then
    echo "requirements.txt exists!"
else
    echo "FAILURE: requirements.txt does not exist!"
    poetry export -o requirements.txt --without-hashes
    exit 1
fi

REQUIREMENTS=$(cat requirements.txt)

if [ "$NEW_REQUIREMENTS" = "$REQUIREMENTS" ]; then
    echo "requirements.txt is up to date!"
    exit 0
else
    echo "FAILURE: requirements.txt is not up to date!"
    poetry export -o requirements.txt --without-hashes
    echo "requirements.txt is now up to date!"
    exit 1
fi
