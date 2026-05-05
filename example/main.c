#include <stdio.h>

// Function to integrate
double f(double x) {
    return x * x; // Example: f(x) = x^2
}

// Trapezoidal rule function
double trapezoidal_rule(double a, double b, int n) {
    double h = (b - a) / n;
    double sum = 0.5 * (f(a) + f(b));

    for (int i = 1; i < n; i++) {
        sum += f(a + i * h);
    }

    return sum * h;
}

int main() {
    double a = 0.0; // Lower limit
    double b = 2.0; // Upper limit
    int n = 1000;   // Number of subintervals

    double result = trapezoidal_rule(a, b, n);

    printf("Integral of x^2 from %f to %f is approximately: %f\n", a, b, result);

    return 0;
}
