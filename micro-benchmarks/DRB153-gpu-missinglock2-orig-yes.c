/*
!!!~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~!!!
!!! Copyright (c) 2017-20, Lawrence Livermore National Security, LLC
!!! and DataRaceBench project contributors. See the DataRaceBench/COPYRIGHT file for details.
!!!
!!! SPDX-License-Identifier: (BSD-3-Clause)
!!!~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~!!!
*/

/*
Concurrent access of var@26:5 in an intra region. Missing Lock leads to intra region data race.
Data Race pairs, var@26:5 and var@26:5.
*/

#include <stdio.h>
#include <omp.h>
#define N 100

int main(){
  int var = 0;

  #pragma omp target map(tofrom:var) device(0)
  #pragma omp teams num_teams(1)
  #pragma omp distribute parallel for
  for (int i=0; i<N; i++){
    var++;
  }

  printf("%d\n ",var);
  return 0;
}
