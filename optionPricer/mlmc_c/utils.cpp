#include "utils.h"

double normalCFD(double value){
   return 0.5 * erfc(-value * M_SQRT1_2);
}

vector<double> build_BM(const int& n_euler,const double& sqrt_dt){
    vector<double> W;
    std::random_device rd;
    std::mt19937 gen(rd());
    std::normal_distribution<double> distribution(0.0,sqrt_dt);
    W.push_back(0);
    for (int k = 0; k < n_euler; k ++)W.push_back(W.at(W.size()-1)+distribution(gen));
    return W;
}

vector<double> build_BM_corr(const vector<double>& W, const double& sqrt_dt, const double& rho){
    std::random_device rd;
    std::mt19937 gen(rd());
    std::normal_distribution<double> distribution(0.0,sqrt_dt);

    int n_euler=W.size()-1;
    vector<double> W_corr;
    W_corr.push_back(0.0);
    for (int k=0; k < n_euler; k++){
        double w_old=W_corr.at(W_corr.size()-1);
        W_corr.push_back(w_old+rho*(W.at(k+1)-W.at(k))+sqrt(1-rho*rho)*(distribution(gen)));
    }
    return W_corr;
}

