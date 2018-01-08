#!/bin/bash

set -e

if   [ "$#" -eq 1 ]; then

  ODIR="$1"
  IDIR="${TTHBB_ANALYSIS}"/"${ODIR}"/mvaInput_mvaEvent_mvaEventP_boostedHbb_cp/Nominal/combined

elif [ "$#" -eq 2 ]; then

  ODIR="$1"
  IDIR="$2"

else

  printf "\n>>> ERROR -- invalid list of command-line argument(s):\n"
  printf   "             [1] path to output directory\n"
  printf   "             [2] path to input directory (optional)\n\n"
  exit

fi

if [ -d "${ODIR}" ]; then

  printf "\n>>> ERROR -- target output directory already exists: ${ODIR}\n\n"
  exit

fi

if [ ! -d "${IDIR}" ]; then

  printf "\n>>> ERROR -- target input directory not found: ${IDIR}\n\n"
  exit

fi

mkdir -p "${ODIR}"

for i_sample in signal background; do

  i_trai="${IDIR}"/"${i_sample}"Training.root
  i_test="${IDIR}"/"${i_sample}"Testing.root

  if [ ! -f "${i_trai}" ]; then printf "\n>>> ERROR -- target input file not found: ${i_trai}\n\n"; break; fi;
  if [ ! -f "${i_test}" ]; then printf "\n>>> ERROR -- target input file not found: ${i_test}\n\n"; break; fi;

  hadd "${ODIR}"/"${i_sample}"_TrainingPlusTesting.root "${i_trai}" "${i_test}"

  printf ">>> created PSO input file: ${ODIR}/${i_sample}_TrainingPlusTesting.root\n"

  unset -v i_trai i_test

done
unset -v i_sample

unset -v ODIR IDIR