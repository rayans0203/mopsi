#ifndef OPTION_H
#define OPTION_H

#include <vector>
#include <iostream>
#include <cmath>
#include "payoff.h"
#include "model.h"

class Option{
protected:
    Payoff* payoff;
    double K;
    double T;
    double S0;
    Model* model;
public:
    Option(const double& K_,const double& T_,
           const double& S0_, Model* model_,
           Payoff* payoff);
    virtual ~Option();

    virtual double MC(const int& N_samples, const int& n_euler) const=0;

    virtual double MLMC(const int& n_euler, const int& m_levels) const=0;
};

class EuropeanOption: public Option{
public:
    EuropeanOption(const double& K_,const double& T_,
                   const double& S0_, Model* model_,
                   Payoff* payoff);
    ~EuropeanOption();

    double BlackScholes(const string& order) const;

    double MC_explicit(const int& N_samples) const;

    double MC(const int& N_samples, const int& n_euler) const;

    double MLMC(const int& n_euler, const int& m_levels) const;
};

class AsianOption: public Option{
public:
    AsianOption(const double& K_,const double& T_,
                const double& S0_, Model* model_,
                Payoff* payoff);
    ~AsianOption();

    double MC(const int& N_samples, const int& n_euler) const;

    double MLMC(const int& n_euler, const int& m_levels) const;
};


#endif // OPTION_H
