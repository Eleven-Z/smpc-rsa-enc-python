from Functions_helper import *
from sympy import *
from Controller import *
class Party:
    def __init__(self, id, x, private_key, public_key):
        self.x = {}
        self.others_public_keys = {}
        self.others_shared_x = {}
        self.my_shared_x = {}
        self.my_poly = {}
        self.symbol = None
        self.id = None
        self.private_key = None
        self.public_key = None
        self.initial_values(id, x, private_key, public_key)
        self.share_from_mul_gate = None
        self.my_shares_of_mul_gate_from_others = {}

    def initial_values(self, id, x, private_key, public_key):
        self.symbol = Symbol("x" + str(id))
        self.x[self.symbol] = x
        self.id = id
        self.private_key = private_key
        self.public_key = public_key

    def get_my_symbol(self):
        return self.symbol

    def set_share_received_from_mul_gate(self, value):
        self.share_from_mul_gate = value

    def get_share_received_from_mul_gate(self):
        return self.share_from_mul_gate

    def add_my_share_of_mul_gate(self, sender, value):
        self.my_shares_of_mul_gate_from_others[sender] = value


    def send_my_share_for_given_term(self, term):
        if term in self.my_shared_x.keys():
            return self.my_shared_x[term]
        else:
            for key, value in self.others_shared_x.iteritems():
                if term in value.keys():
                    return value[term]
    #EDITED
    def share_given_x_among_all(self, all_parties, polynomial_degree,  x):
        poly = Functions_helper.poly_generator_without_random_constant(polynomial_degree,x)
        # poly = None
        # if self == all_parties[0]:
        #     poly = Poly.from_list([4, x], gens = (Symbol("x")))
        # elif self == all_parties[1]:
        #     poly = Poly.from_list([3, x], gens = (Symbol("x")))
        #
        # elif self == all_parties[2]:
        #     poly = Poly.from_list([2, x], gens = (Symbol("x")))
        #
        # elif self == all_parties[3]:
        #     poly = Poly.from_list([1, x], gens = (Symbol("x")))

        for p in all_parties:
            p.add_my_share_of_mul_gate(self, self.calculate_x_with_poly(poly, p.get_initial_x()))


    def generate_my_poly(self,term, degree):
        self.my_poly[term] = Functions_helper.poly_generator_without_random_constant(degree, self.x[term])

    def share_my_x_with_myself(self, term):
        self.my_shared_x[term] = self.calculate_x_with_poly(self.my_poly[term], self.get_initial_x())

    def get_my_x_for_term(self, term):
        return self.x[term]

    def share_my_x_with_all(self, all, term):
        self.share_my_x_with_myself(term)
        for p in all :
            if p == self:
                continue
            p.receive_someones_shared_x(self.calculate_x_with_poly(self.my_poly[term], p.x[p.get_my_symbol()]), term, self)

    def receive_someones_shared_x(self,x, term, p):
        if self.others_shared_x.has_key(p) :
            self.others_shared_x[p][term] = x
        else:
            self.others_shared_x[p] = {term: x}

    def get_x_for_term(self, term):
        return self.x[term]

    def get_initial_x(self):
        return self.get_x_for_term(Symbol("x" + str(self.id)))

    def calculate_x_with_poly(self, poly, x):
        return poly.subs(Symbol("x"), x)

    def send_received_share_of_party(self, p):
        return self.others_shared_x.get(p)

    def send_received_share_of_party_for_given_term(self, p, term):
        return self.others_shared_x[p][term]

    def add_new_x(self, term, x):
        self.x[term] = x

    def send_my_share_of_my_term(self, term):
        return self.my_shared_x[term]

    def has_x_for_term(self, term):
        if self.x[term]:
            return True
        else:
            return False

    '''needs to be edited for better support for all forms of terms '''
    def recalculate_x_for_new_term(self, parties, term, polynomial_degree):
        variables = Functions_helper.get_symbols_as_list(term)
        coeffs = Functions_helper.get_variable_coeff_as_dic(term)
        powers = Functions_helper.get_variable_power_pair_as_dic(term)
        for v in variables:
            if v in self.x.keys():
                power = 1 if not powers[v] else powers[v]
                coeff = 1 if not coeffs else coeffs[v]
                new_x = coeff * self.get_x_for_term(v) ** power
                self.add_new_x(term, new_x)         # add new x
                self.generate_my_poly(term, polynomial_degree)       #create polynomial to share new value of x
                self.share_my_x_with_myself(term)       #share x with (4,2) method with himself
                self.share_my_x_with_all(parties, term)     #shared x with (4,2) method with other parties

    @staticmethod
    def whose_this_term(parties, term):
        symbols = Functions_helper.get_symbols_as_list(term)
        all = []
        for p in parties:
            for symbol in symbols:
                if symbol in p.x.keys():
                    all.append(p)
        return all

