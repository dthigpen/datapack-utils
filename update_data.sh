#!/usr/bin/env bash
set -x
set -euo pipefail
IFS=$'\n\t'

MCMETA_GIT_TAG='1.19.1-data'
MINECRAFT_ASSETS_VER='1.19.1'
pushd datapack_utils/data

rm -rf  mcmeta
git clone --depth 1 --branch "${MCMETA_GIT_TAG}" git@github.com:misode/mcmeta.git
rm -rf mcmeta/{.git,.gitignore,.gitattributes,.github}


rm -rf minecraft-assets minecraft_assets 
git clone --depth 1 git@github.com:PrismarineJS/minecraft-assets.git minecraft_assets
pushd minecraft_assets
rm -rf {.git,.gitignore,.gitattributes,.github}
rm -rf *.md
for d in data/*
do
    name=$(basename "${d}")
    if [[ "${name}" != "${MINECRAFT_ASSETS_VER}" && "${name}" != 'common' ]]
    then
        rm -rf "${d}"
    fi
done
popd

popd
