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

cleanup() {
    cd "${ROOTDIR}"
    echo Removing old build directory

    if [ -d ./build ]; then
        rm -rf ./build
    fi
}

update() {
    cd "${ROOTDIR}"
    echo Updating version to ${NEWVERSION}

    sed -i "s#\"${PYVERSION}\"#\"${NEWVERSION}\"#" "gallery_dl/version.py"
    sed -i "s#v[0-9]\.[0-9]\+\.[0-9]\+#v${NEWVERSION}#" "${README}"
    make man
}

update-dev() {
    cd "${ROOTDIR}"

    IFS="." read MAJOR MINOR BUILD <<< "${NEWVERSION}"
    BUILD=$((BUILD+1))
    # update version to -dev
    sed -i "s#\"${NEWVERSION}\"#\"${MAJOR}.${MINOR}.${BUILD}-dev\"#" "gallery_dl/version.py"
    # add 'unreleased' line to changelog
    sed -i "2i\\\n## Unreleased" "${CHANGELOG}"

    git add "gallery_dl/version.py" "${CHANGELOG}"
}

build-python() {
    cd "${ROOTDIR}"
    echo Building bdist_wheel and sdist

    python setup.py bdist_wheel sdist
}

build-linux() {
    cd "${ROOTDIR}"
    echo Building Linux executable

    make executable
}

build-windows() {
    cd "${ROOTDIR}/dist"
    echo Building Windows executable

    # remove old executable
    rm -f "gallery-dl.exe"

    # build windows exe in vm
    ln -fs "${ROOTDIR}" /tmp/
    vmstart "Windows 7" &
    disown
    while [ ! -e "gallery-dl.exe" ] ; do
        sleep 5
    done
    sleep 2
}

sign() {
    cd "${ROOTDIR}/dist"
    echo Signing files

    gpg --detach-sign --armor gallery_dl-${NEWVERSION}-py3-none-any.whl
    gpg --detach-sign --armor gallery_dl-${NEWVERSION}.tar.gz
    gpg --detach-sign --yes gallery-dl.exe
    gpg --detach-sign --yes gallery-dl.bin
}

changelog() {
    cd "${ROOTDIR}"
    echo Updating "${CHANGELOG}"

    # - replace "#NN" with link to actual issue
    # - insert new version and date
    sed -i \
        -e "s*\([( ]\)#\([0-9]\+\)*\1[#\2](https://github.com/mikf/gallery-dl/issues/\2)*g" \
        -e "s*^## [Uu]nreleased*## ${NEWVERSION} - $(date +%Y-%m-%d)*" \
        "${CHANGELOG}"
}

supportedsites() {
    cd "${ROOTDIR}"
    echo Checking if "${SUPPORTEDSITES}" is up to date

    ./scripts/supportedsites.py
    if ! git diff --quiet "${SUPPORTEDSITES}"; then
        echo "updated ${SUPPORTEDSITES} contains changes"
        exit 4
    fi
}

git-upload() {
    cd "${ROOTDIR}"
    echo Pushing changes to github

    git add "gallery_dl/version.py" "${README}" "${CHANGELOG}"
    git commit -S -m "release version ${NEWVERSION}"
    git tag -s -m "version ${NEWVERSION}" "v${NEWVERSION}"
    git push
    git push origin "v${NEWVERSION}"
}

pypi-upload() {
    cd "${ROOTDIR}/dist"
    echo Uploading to PyPI

    twine upload gallery_dl-${NEWVERSION}*
}


ROOTDIR="$(realpath "$(dirname "$0")/..")/"
README="README.rst"
CHANGELOG="CHANGELOG.md"
SUPPORTEDSITES="./docs/supportedsites.rst"

LASTTAG="$(git describe --abbrev=0 --tags)"
OLDVERSION="${LASTTAG#v}"
PYVERSION="$(python -c "import gallery_dl as g; print(g.__version__)")"

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
supportedsites
cleanup
update
changelog
build-python
build-linux
build-windows
sign
git-upload
pypi-upload
update-dev
