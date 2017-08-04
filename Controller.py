from scipy import interpolate
from Party import *
from RSA import *
class Controller:
    t = 0
    number_of_p = 0
    parties = []
    def __init__(self, t, np):
        Controller.t = t
        Controller.number_of_p = np

    def initial_parties(self):
        for i in range(1, self.number_of_p + 1):
            public, private = RSA.generate_keypair(RSA.get_random_prime(), RSA.get_random_prime())
            # p = Party(i, random.randint(1, 50), public, private)        #EDITED
            p = Party(i,i, public, private)         #REMOVE
            p.generate_my_poly(p.get_my_symbol(), self.t)
            self.parties.append(p)

    def tell_every_one_to_share_initial_x(self):
        for p in Controller.parties:
            p.share_my_x_with_all(Controller.parties, p.get_my_symbol())

    '''
        check all terms to see if there is any term needs to be calculated locally and be shared
        note: this only supports power and coeff in add gate
        solution: edit this functions to support power, coeffs in multiply gate
    '''
    def check_for_local_calculation(self):
        terms = Functions_helper.get_terms_as_list(Functions_helper.get_initial_function())
        for term in terms:
            if not Functions_helper.is_multiply(term):
                p = Party.whose_this_term(Controller.parties, term)
                if p[0].get_my_symbol() == term:
                    continue
                p[0].recalculate_x_for_new_term(Controller.parties, term, Controller.t)


    def create_table(self, symbols):
        table = {}
        for s in symbols:
            party = Party.whose_this_term(Controller.parties, s)
            tmp = []
            for p in Controller.parties:
                if party[0] == p:
                    tmp.append(party[0].send_my_share_of_my_term(s))
                else:
                    tmp.append(p.send_received_share_of_party_for_given_term(party[0], s))
            table[party[0]] = tmp
        return table

    def multiply_table_one_by_one(self, table):
        result = []
        for i in range(Controller.number_of_p):
            tmp = 1
            for tab in table.values():
                tmp *= tab[i]
            result.append(tmp)
        return result


    def tell_each_party_to_share_its_mul_value(self, lst):
        for i, party in enumerate(Controller.parties):
            party.share_given_x_among_all(self.parties, self.t, lst[i])


    def construct_table_for_mul_gate_interpolation(self):
        table = []
        for party in Controller.parties:
            tmp = []
            for p in Controller.parties:
                tmp += [p.my_shares_of_mul_gate_from_others[party]]
            table.append(tmp)
        new_table = []
        for i in range(Controller.number_of_p):
            new_table.append(self.create_pairs_from_result(table[i]))
        return new_table

    '''
        revisit to fix
        problem: does not support coeff and power in terms like : 2*x1**6*4*x2 only suppoers x1*x2 or x1*x3*x2
        solution: needs a function to divide the terms by "*"
    '''
    def perform_multiply_gate(self):
        terms = Functions_helper.get_terms_as_list(Functions_helper.get_initial_function())
        symbols = []
        for term in terms:
            if Functions_helper.is_multiply(term):
                symbols = Functions_helper.separate_multiplication_terms_as_list(term)
        table = self.create_table(symbols)
        mul_result = self.multiply_table_one_by_one(table)

        #give each party its share of mul gate
        for i, p in enumerate(Controller.parties):
            p.set_share_received_from_mul_gate(mul_result[i])

        self.tell_each_party_to_share_its_mul_value(mul_result)
        table = self.construct_table_for_mul_gate_interpolation()
        # print "table : "
        # for f in table:
        #     print f

        interpolate = Functions_helper.interpolation(table)
        print interpolate
        for i, p in enumerate(Controller.parties):
            p.set_share_received_from_mul_gate(interpolate[i][1])


    def get_shares_of_mul_gate_as_table(self):
        table = []
        for p in Controller.parties:
            table.append(p.get_share_received_from_mul_gate())
        return table

    def get_share_for_each_term(self):
        table = []
        for term in Functions_helper.get_terms_as_list(Functions_helper.get_initial_function()):
            if not Functions_helper.is_multiply(term):
                tmp = []
                for party in Controller.parties:
                    tmp.append(party.send_my_share_for_given_term(term))
                table.append(tmp)
        return table

    def add_table_elements_one_by_one(self, table):
        final_values = []
        for i in range(Controller.number_of_p):
            tmp = 0
            for t in table:
                tmp += t[i]
            final_values.append(tmp)
        return final_values


    def create_pairs_from_result(self, result):
        res = []
        for i, p in enumerate(Controller.parties):
            res.append((p.get_initial_x(), result[i]))
        return res

    '''
        perform the add gate
    '''
    def perform_add_gate(self):
        mul_table = self.get_shares_of_mul_gate_as_table()
        initial_shares_table = self.get_share_for_each_term()
        table = initial_shares_table + [mul_table]
        result = self.add_table_elements_one_by_one(table)
        return self.create_pairs_from_result(result)


if __name__ == "__main__":
    controller = Controller(1, 4)
    controller.initial_parties()
    controller.tell_every_one_to_share_initial_x()
    controller.check_for_local_calculation()
    print "multiply gate result: "
    controller.perform_multiply_gate()

    output = controller.perform_add_gate()
    print "results from the final gate (before interpolation) : "
    print output

    print "function reuslt: "
    print Functions_helper.eval_function(Controller.parties)
    print "output from interpolation with two points"
    print Functions_helper.output(output[:2])
    print "output from interpolation with 4 points"
    print Functions_helper.output(output)
    # print Functions_helper.lagrange_interpolation([output[1]] + [output[3]] )(0)
    print Functions_helper.modular_lagrange_interpolation(0, output, 6703903964971298549787012499102923063739682910296196688861780721860882015036773488400937149083451713845015929093243025426876941405973284973216824503042159)
    # print interpolate.lagrange([x for _, x in output], [y for y, _ in output])
