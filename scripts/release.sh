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
    sed -i "s#\"${PYVERSION}\"#\"${NEWVERSION}\"#" "gallery_dl/version.py"
    sed -i "s#/v${OLDVERSION}/#/v${NEWVERSION}/#" "README.rst"
}

update-dev() {
    cd "${ROOTDIR}"
    sed -i "s#\"${NEWVERSION}\"#\"${NEWVERSION}-dev\"#" "gallery_dl/version.py"
}

build() {
    cd "${ROOTDIR}"

    # build wheel and source distributions
    python setup.py bdist_wheel sdist

    # build windows exe in vm
    ln -fs "${ROOTDIR}" /tmp/
    vmstart "Windows 7" &
    disown
    while [[ ! -e "gallery-dl.exe" ]] ; do
        sleep 5
    done

    # check exe version
    OUTPUT="$(wine gallery-dl.exe --version)"
    if [[ ! "${OUTPUT%?}" == "${NEWVERSION}" ]]; then
        echo "exe version mismatch: ${OUTPUT} != ${NEWVERSION}"
        exit 3
    fi
    [ -e "dist/gallery-dl.exe" ] && mv -f "dist/gallery-dl.exe" "dist/gallery-v${OLDVERSION}-dl.exe"
    mv "gallery-dl.exe" "./dist/"
}

sign() {
    cd "${ROOTDIR}/dist"
    gpg --detach-sign --armor gallery_dl-${NEWVERSION}-py3-none-any.whl
    gpg --detach-sign --armor gallery_dl-${NEWVERSION}.tar.gz
    gpg --detach-sign gallery-dl.exe
}

git-upload() {
    cd "${ROOTDIR}"
    git add "gallery_dl/version.py" "README.rst"
    git commit -S -m "release version ${NEWVERSION}"
    git tag -s -m "version ${NEWVERSION}" "v${NEWVERSION}"
    # git push origin "v${NEWVERSION}"
}

pypi-upload() {
    cd "${ROOTDIR}/dist"
    twine upload
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
update
build
sign
git-upload
pypi-upload
update-dev
