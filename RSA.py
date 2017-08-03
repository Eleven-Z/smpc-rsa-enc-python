'''
620031587
Net-Centric Computing Assignment
Part A - RSA Encryption
'''

import random
class RSA:
    '''
    Euclid's algorithm for determining the greatest common divisor
    Use iteration to make it faster for larger integers
    '''

    @staticmethod
    def gcd(a, b):
        while b != 0:
            a, b = b, a % b
        return a
    @staticmethod
    def gen_primes():
        """ Generate an infinite sequence of prime numbers.
        """
        # Maps composites to primes witnessing their compositeness.
        # This is memory efficient, as the sieve is not "run forward"
        # indefinitely, but only as long as required by the current
        # number being tested.
        #
        D = {}

        # The running integer that's checked for primeness
        q = 2

        while True:
            if q not in D:
                # q is a new prime.
                # Yield it and mark its first multiple that isn't
                # already marked in previous iterations
                #
                yield q
                D[q * q] = [q]
            else:
                # q is composite. D[q] is the list of primes that
                # divide it. Since we've reached q, we no longer
                # need it in the map, but we'll mark the next
                # multiples of its witnesses to prepare for larger
                # numbers
                #
                for p in D[q]:
                    D.setdefault(p + q, []).append(p)
                del D[q]

            q += 1

    @staticmethod
    def get_random_prime():
        rand = random.randint(1, 10000)
        primes = gen_primes()
        for prime in primes:
            if rand == 0:
                return prime
            rand -= 1

    '''
    Euclid's extended algorithm for finding the multiplicative inverse of two numbers
    '''

    @staticmethod
    def multiplicative_inverse(e, phi):
        d = 0
        x1 = 0
        x2 = 1
        y1 = 1
        temp_phi = phi

        while e > 0:
            temp1 = temp_phi / e
            temp2 = temp_phi - temp1 * e
            temp_phi = e
            e = temp2

            x = x2 - temp1 * x1
            y = d - temp1 * y1

            x2 = x1
            x1 = x
            d = y1
            y1 = y

        if temp_phi == 1:
            return d + phi


    '''
    Tests to see if a number is prime.
    '''

    @staticmethod
    def is_prime(num):
        if num == 2:
            return True
        if num < 2 or num % 2 == 0:
            return False
        for n in xrange(3, int(num ** 0.5) + 2, 2):
            if num % n == 0:
                return False
        return True

    @staticmethod
    def generate_keypair(p, q):
        if not (RSA.is_prime(p) and RSA.is_prime(q)):
            raise ValueError('Both numbers must be prime.')
        elif p == q:
            raise ValueError('p and q cannot be equal')
        # n = pq
        n = p * q

        # Phi is the totient of n
        phi = (p - 1) * (q - 1)

        # Choose an integer e such that e and phi(n) are coprime
        e = random.randrange(1, phi)

        # Use Euclid's Algorithm to verify that e and phi(n) are comprime
        g = RSA.gcd(e, phi)
        while g != 1:
            e = random.randrange(1, phi)
            g = RSA.gcd(e, phi)

        # Use Extended Euclid's Algorithm to generate the private key
        d = RSA.multiplicative_inverse(e, phi)

        # Return public and private keypair
        # Public key is (e, n) and private key is (d, n)
        return ((e, n), (d, n))

    @staticmethod
    def encrypt(pk, plaintext):
        # Unpack the key into it's components
        key, n = pk
        # Convert each letter in the plaintext to numbers based on the character using a^b mod m
        cipher = [(ord(char) ** key) % n for char in plaintext]
        # Return the array of bytes
        return cipher

    @staticmethod
    def decrypt(pk, ciphertext):
        # Unpack the key into its components
        key, n = pk
        # Generate the plaintext based on the ciphertext and key using a^b mod m
        plain = [chr((char ** key) % n) for char in ciphertext]
        # Return the array of bytes as a string
        return ''.join(plain)


def gen_primes():
    """ Generate an infinite sequence of prime numbers.
    """
    # Maps composites to primes witnessing their compositeness.
    # This is memory efficient, as the sieve is not "run forward"
    # indefinitely, but only as long as required by the current
    # number being tested.
    #
    D = {}

    # The running integer that's checked for primeness
    q = 2

    while True:
        if q not in D:
            # q is a new prime.
            # Yield it and mark its first multiple that isn't
            # already marked in previous iterations
            #
            yield q
            D[q * q] = [q]
        else:
            # q is composite. D[q] is the list of primes that
            # divide it. Since we've reached q, we no longer
            # need it in the map, but we'll mark the next
            # multiples of its witnesses to prepare for larger
            # numbers
            #
            for p in D[q]:
                D.setdefault(p + q, []).append(p)
            del D[q]

        q += 1

