import math

## Goal: To model a prediction market comprised of two candidates ("A" and "B"). 

## Step 1. Create the Binary Market for Candidates A and B

class Market: 
    ## A market comprised of two candidates (q_A for A and q_B for B) and the sensitivity of the market (b)
    def __init__(self, b):
        self.b = b
        self.q_A = 0.0
        self.q_B= 0.0

    ## The price of Candidate A at the given point in time
    def price_A(self):
        ## Returns the current price of Candidate A based on the number of shares and market sensitivity.
        e_A = math.exp(self.q_A / self.b)
        e_B = math.exp(self.q_B / self.b)
        return e_A / (e_A + e_B)

    ## The price of Candidate B at the given point in time
    def price_B(self):
        ## Returns the current price of Candidate B based on the number of shares and market sensitivity.
        return 1 - self.price_A()

    ## The total amount of money in the market based on the trades made at a given point in time
    def cost_function(self, q_A, q_B):
      ## Formula 2: C(q) = b * ln(e^(q_A/b) + e^(q_B/b))
        return self.b * math.log(math.exp(q_A / self.b) + math.exp(q_B / self.b))

    def quote(self, candidate, shares):
    ## How much a trade would cost without making it. Positive shares = buy, negative shares = sell.
        new_A = self.q_A
        new_B = self.q_B
        if candidate == "A":
            new_A = new_A + shares
        else:
            new_B = new_B + shares
        return self.cost_function(new_A, new_B) - self.cost_function(self.q_A, self.q_B)

    def trade(self, candidate, shares):
    ## Based on what we know the trade to be, make the trade and return what it cost.
        cost = self.quote(candidate, shares)
        if candidate == "A":
            self.q_A = self.q_A + shares
        else:
            self.q_B = self.q_B + shares
        return cost
    
