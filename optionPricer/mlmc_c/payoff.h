#ifndef PAYOFF_H
#define PAYOFF_H

#include <string>
#include <cstdlib>
using namespace std;
#include <algorithm>


class Payoff {
public:
    Payoff();
    virtual ~Payoff();

    virtual double operator()(const double& S) const=0;
};

class PayoffCall: public Payoff{
    double K;
public:
    PayoffCall(const double & K_);
    virtual ~PayoffCall();

    virtual double operator()(const double& S) const;
};

class PayoffPut: public Payoff{
    double K;
public:
    PayoffPut(const double & K_);
    virtual ~PayoffPut();

    virtual double operator()(const double & S)const;
};

#endif // PAYOFF_H
