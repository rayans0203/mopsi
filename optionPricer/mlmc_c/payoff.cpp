#include "payoff.h"

Payoff::Payoff(){}

Payoff::~Payoff(){}

PayoffCall::PayoffCall(const double &K_): Payoff() {
    K=K_;
}

PayoffCall::~PayoffCall(){}

double PayoffCall::operator()(const double&S) const{
    return std::max(S-K,0.);
}

PayoffPut::PayoffPut(const double &K_): Payoff() {
    K=K_;
}

PayoffPut::~PayoffPut(){}

double PayoffPut::operator()(const double&S) const{
    return std::max(K-S,0.);
}
