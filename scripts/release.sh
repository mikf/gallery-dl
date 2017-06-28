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
    sed -i "s#v${OLDVERSION}#v${NEWVERSION}#" "README.rst"
}

update-dev() {
    cd "${ROOTDIR}"
    IFS="." read MAJOR MINOR BUILD <<< "${NEWVERSION}"
    BUILD=$((BUILD+1))
    sed -i "s#\"${NEWVERSION}\"#\"${MAJOR}.${MINOR}.${BUILD}-dev\"#" "gallery_dl/version.py"
}

build() {
    cd "${ROOTDIR}"

    # build wheel and source distributions
    echo Building bdist_wheel and sdist
    python setup.py bdist_wheel sdist
}

build_windows() {
    # build windows exe in vm
    echo Building Windows executable
    ln -fs "${ROOTDIR}" /tmp/
    vmstart "Windows 7" &
    disown
    while [ ! -e "gallery-dl.exe" ] ; do
        sleep 5
    done

    # check exe version
    OUTPUT="$(wine gallery-dl.exe --version)"
    if [[ ! "${OUTPUT%?}" == "${NEWVERSION}" ]]; then
        echo "exe version mismatch: ${OUTPUT} != ${NEWVERSION}"
        exit 3
    fi
    if [ -e "dist/gallery-dl.exe" ]; then
        mv -f "dist/gallery-dl.exe" "dist/gallery-v${OLDVERSION}-dl.exe"
    fi
    mv "gallery-dl.exe" "./dist/"
}

sign() {
    cd "${ROOTDIR}/dist"
    echo Signing files
    gpg --detach-sign --armor gallery_dl-${NEWVERSION}-py3-none-any.whl
    gpg --detach-sign --armor gallery_dl-${NEWVERSION}.tar.gz
    gpg --detach-sign gallery-dl.exe
}

git-upload() {
    cd "${ROOTDIR}"
    echo Pushing changes to github
    git add "gallery_dl/version.py" "README.rst"
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

LASTTAG="$(git describe --abbrev=0 --tags)"
OLDVERSION="${LASTTAG#v}"
PYVERSION="$(python -c "import gallery_dl as g; print(g.__version__)")"

if [[ "$1" ]]; then
    NEWVERSION="$1"
else
    NEWVERSION="${PYVERSION%-dev}"
fi

if [[ ! $NEWVERSION =~ [0-9]+\.[0-9]+\.[0-9]+$ ]]; then
    echo "invalid version: $NEWVERSION"
    exit 2
fi


prompt
cleanup
update
build
build_windows
sign
git-upload
pypi-upload
update-dev
