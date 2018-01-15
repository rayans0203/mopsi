#ifndef UTILS_H
#define UTILS_H

#include <vector>
#include <random>
#include <iostream>
#include <cstdlib>
using namespace std;

double normalCFD(double value);

vector<double> build_BM(const int& n_euler,const double& sqrt_dt);

vector<double> build_BM_corr(const vector<double>& W, const double& sqrt_dt, const double& rho);

#endif // UTILS_H
