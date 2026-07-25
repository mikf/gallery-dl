#!/bin/bash
set -e

prompt() {
    echo "root: ${ROOTDIR} old: ${OLDVERSION} - new: ${NEWVERSION}"
    read -n 1 -r -p "Proceed? [Y/n] " P
    echo
    if [ "$P" == y -o "$P" == Y -o -z "$P" ]; then
        return 0
    else
        exit 1
    fi
}

update() {
    cd "${ROOTDIR}"
    echo Updating version to ${NEWVERSION}

    sed -i "s#\"${OLDVERSION}\"#\"${NEWVERSION}\"#" "gallery_dl/version.py"
    sed -i "s#v[0-9]\.[0-9]\+\.[0-9]\+#v${NEWVERSION}#" "${README}"
}

changelog() {
    cd "${ROOTDIR}"
    echo Updating "${CHANGELOG}"

    cp -a -- "../gallery-dl/${CHANGELOG}" "${CHANGELOG}"
}

upload-git() {
    cd "${ROOTDIR}"
    echo Pushing changes to repository

    git add "gallery_dl/version.py" "${README}" "${CHANGELOG}"
    git commit -S -m "release version ${NEWVERSION}"
    git tag -s -m "version ${NEWVERSION}" "v${NEWVERSION}"
    git push --atomic origin "$(git rev-parse --abbrev-ref HEAD)" "v${NEWVERSION}"
}


ROOTDIR="$(realpath "$(dirname "$0")/..")/"
README="README.rst"
CHANGELOG="CHANGELOG.md"
SUPPORTEDSITES="./docs/supportedsites.md"

LASTTAG="$(git describe --abbrev=0 --tags)"
OLDVERSION="${LASTTAG#v}"
PYVERSION="$(python -c "import gallery_dl as g; v = g.__version__.split('.'); v[-1] = str(int(v[-1].partition('-')[0])+1); print('.'.join(v))")"

if [[ "$1" ]]; then
    NEWVERSION="$1"
else
    NEWVERSION="${PYVERSION%-dev}"
fi

if [[ ! $NEWVERSION =~ [0-9]+\.[0-9]+\.[0-9]+(-[a-z]+(\.[0-9]+)?)?$ ]]; then
    echo "invalid version: $NEWVERSION"
    exit 2
fi


prompt
update
changelog
upload-git
