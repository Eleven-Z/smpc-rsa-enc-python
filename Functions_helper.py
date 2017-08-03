from __builtin__ import staticmethod
import sympy
from sympy import *
import random
import re


class Functions_helper:


    '''
        fill it with desired function
    '''
    @staticmethod
    def get_initial_function():
        x1, x2, x3, x4 = symbols("x1 x2 x3 x4")
        return x1*x2 + x2**3 + x3 + 2*x4**5


    '''
        make it more general without hard coding anything
    '''
    @staticmethod
    def eval_function(parties):
        x1, x2, x3, x4 = symbols("x1 x2 x3 x4")
        f = Poly(x1*x2 + x2**3 + x3 + 2*x4**5)
        all_x = []
        for p in parties:
            all_x.append(p.get_initial_x())
        return f.subs([(x1, all_x[0]), (x2, all_x[1]), (x3, all_x[2]), (x4, all_x[3])])

    @staticmethod
    def poly_generator_with_random_constant(degree):
        return sympy.Poly.from_list([random.randint(1, 20) for t in range(degree + 1)], gen=sympy.Symbol("x"))

    @staticmethod
    def poly_generator_without_random_constant(degree, constant):
        coeff = [random.randint(1, 20) for t in range(degree)]
        coeff.append(constant)
        return sympy.Poly.from_list(coeff, gens=sympy.Symbol("x"))

    @staticmethod
    def get_terms_as_list(function):
        return function.as_ordered_terms()


    ''' check if there is only one symbol and one coefficient. in other word it does not need to use a mul gate '''
    @staticmethod
    def has_only_coeff_to_multiply(term):
        if "*" in str(term).replace("**", "^"):
            if str(term).split("*")[0].isdigit():
                return True
            else:
                return False
        return False

    @staticmethod
    def is_multiply(term):
        if "*" in str(term).replace("**", "^"):
            if Functions_helper.has_only_coeff_to_multiply(term):       #if this, then we should calculate it locally
                return False
            return True
        else:
            return False

    @staticmethod
    def has_coeff(term):
        for t in str(term).replace("**", "^").split("*"):
            if t.isdigit():
                return True
            else:
                return False

    @staticmethod
    def get_variable_coeff_as_dic(term):
        pair = {}
        iterator = str(term).replace("**", "^").split("*")
        for i, t in enumerate(iterator):
            if (t.isdigit()):
                symbol = Symbol(re.sub("\*\*[0-9]+", "", iterator[i+1].replace("^", "**")))
                pair[symbol] = int(t)
        return pair

    @staticmethod
    def seperate_term_by_symbol(term, symbol):
        ts = str(term).replace("**", "^").split("*")
        for t in ts:
            if str(symbol) in t:
                return t


    '''
        devide the symbols with all its power and coefficients like : 2*x1**6*x**2 => [2*x1**6 , x**2]
    '''
    @staticmethod
    def separate_multiplication_terms_as_list(term):
        ts = str(term).replace("**", "^").split("*")
        coeff = ""
        result = []
        for t in ts:
            if t.isdigit():
                coeff = t
            elif t.isalnum():
                result.append(Symbol(t.replace("^", "**")+coeff))
                coeff = ""
        return result


    @staticmethod
    def get_variable_power_pair_as_dic(term):
        pair = {}
        iterator = str(term).replace("**", "^").split("*")
        for i, t in enumerate(iterator):
            if "^" in t:
                symbol, power = Symbol(t.split("^")[0]), int(t.split("^")[1])
                pair[symbol] = power
        return pair

    @staticmethod
    def get_symbols_as_list(term):
        st = re.sub("(\*\*[0-9]+)", "", str(term)).split("*")
        return [Symbol(x) for x in st if x.isalnum() and not x.isdigit()]

    @staticmethod
    def modinv(a, m):
        def egcd(a, b):
            if a == 0:
                return (b, 0, 1)
            else:
                g, y, x = egcd(b % a, a)
                return (g, x - (b // a) * y, y)

        g, x, y = egcd(a, m)
        if g != 1:
            raise Exception('modular inverse does not exist')
        else:
            return x % m



    '''
        this is for multiply gate interpolation
    '''
    @staticmethod
    def interpolation(p):
        q = 6703903964971298549787012499102923063739682910296196688861780721860882015036773488400937149083451713845015929093243025426876941405973284973216824503042159
        new_p_s = []
        for k in range(len(p)):
            acc = 0
            for i in range(1, len(p) + 1):
                tmp = 1
                for j in range(1, len(p) + 1):
                    if (i != j):
                        # check = tmp * float(p[k][j - 1][0] / (p[k][j - 1][0] - p[k][i - 1][0]))
                        # if (int(check) != check):
                        #     tmp *= Functions_helper.modinv(p[k][j - 1][0] / (p[k][j - 1][0] - p[k][i - 1][0]), q)
                        # else:
                            tmp *= p[k][j - 1][0] / (p[k][j - 1][0] - p[k][i - 1][0])
                acc += (tmp % q) * p[i - 1][k][1]
            # p[k][k] = (p[k][k][0], acc)
            new_p_s.append((p[k][k][0], acc % q))
        return new_p_s

    @staticmethod
    def output(points):
        result = 0
        q = 6703903964971298549787012499102923063739682910296196688861780721860882015036773488400937149083451713845015929093243025426876941405973284973216824503042159
        x1, y1 = points[0]
        x2, y2 = points[1]
        result = y1 * x2 * (Functions_helper.modinv((x2 - x1) % q, q)) + y2 * x1 * (Functions_helper.modinv((x1 - x2) % q, q))
        result = result % q
        return result

    '''
        this is for output gate interpolation
    '''
    @staticmethod
    def lagrange_interpolation(points):
        q = 6703903964971298549787012499102923063739682910296196688861780721860882015036773488400937149083451713845015929093243025426876941405973284973216824503042159
        def P(x):
            total = 0
            n = len(points)
            for i in xrange(n):
                xi, yi = points[i]
                def g(i, n):
                    tot_mul = 1
                    for j in xrange(n):
                        if i == j:
                            continue
                        xj, yj = points[j]
                        tmp = tot_mul * float((x - xj) / (xi - xj))
                        if (int(tmp) != tmp):
                            tot_mul *= (Functions_helper.modinv((x - xj) / (xi - xj), q))
                        else:
                            tot_mul *= (x - xj) / (xi - xj)

                    return tot_mul

                total += yi * (g(i, n) % q)
            return total % q
        return P

