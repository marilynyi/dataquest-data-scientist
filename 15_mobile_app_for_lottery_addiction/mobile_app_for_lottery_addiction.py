import random
import pandas as pd

# == Total number of combinations for a six-number lottery ticket ==
# ==================================================================

def combinations(n, k):
    def factorial(x):
        n_fact = 1
        for i in range(1, x+1):
            n_fact *= i
        return n_fact
    return factorial(n)/(factorial(k)*factorial(n-k))

num_combos = combinations(49,6)
print(f"{num_combos:,.0f}")

print(f"{1/num_combos*100:.10f}")

# =============== Quick Pick numbers ==============
# =================================================

def quick_pick():
    quick_pick_numbers = []
    rand_num = random.randint(1,50)
    while len(quick_pick_numbers)<6:
        rand_num = random.randint(1,50)
        if rand_num not in quick_pick_numbers:
            quick_pick_numbers.append(rand_num)
    return sorted(quick_pick_numbers)

quick_pick_nums = quick_pick()
print(quick_pick_nums)

# == Odds of winning with Quick Pick versus selecting numbers ==
# ==============================================================

def one_ticket_probability(player_numbers):
    combos = combinations(49, len(player_numbers))
    proportion = 1/combos
    print(f"Your chance to win the jackpot with {player_numbers} is {proportion*100:.10f}%, or 1 in {int(combos):,}.")
    
quick_pick = one_ticket_probability(quick_pick_nums)

selection_slip = one_ticket_probability([2, 5, 7, 8, 32, 41])

# ====== Historical Data Check for Canada Lottery ======
# ======================================================

dataset = pd.read_csv("649.csv")

print(dataset.head(3))
print(dataset.tail(3))

def extract_numbers(index):
    index = index[4:10]
    index = set(index.values)
    return index   

winning_numbers = dataset.apply(extract_numbers, axis=1)
winning_numbers.head()

def check_historical_occurrence(player_numbers, winning_numbers):
    player_numbers_set = set(player_numbers)
    check_occurrence = player_numbers_set == winning_numbers
    n_occurrences = check_occurrence.sum()
    string_time = "time" if n_occurrences == 1 else "times"
    
    if n_occurrences == 0:
        print(f"Your numbers {player_numbers} have never won the lottery in the past.")
    else:
        print(f"Your numbers {player_numbers} have won {n_occurrences} {string_time} in the past.")
        
player_test1_numbers = [3, 6, 19, 24, 46, 48]
check_historical_occurrence(player_test1_numbers, winning_numbers)

player_test2_numbers = [2, 3, 15, 23, 41, 46]
check_historical_occurrence(player_test2_numbers, winning_numbers)

one_ticket_probability(player_test1_numbers)
one_ticket_probability(player_test2_numbers)

# ============= Multi-ticket Probability =============
# ====================================================

def multi_ticket_probability(number_of_tickets):
    combos = combinations(49, 6)
    proportion = number_of_tickets/combos
    string_ticket = "ticket" if number_of_tickets == 1 else "tickets"
    print(f"Your chance to win the jackpot with {number_of_tickets:,} {string_ticket} is {proportion*100:.10f}%, or 1 in {int(combos/number_of_tickets):,}.")
    
test_ticket_counts = [1, 2, 3, 4, 5, 10, 40, 100, 10_000, 1_000_000, 6_991_908, 13_983_816]

for test_ticket_count in test_ticket_counts:
    multi_ticket_probability(test_ticket_count)
    
# ================ Cost to Win ================
# =============================================

def profit(desired_net_amount):
    ticket_cost = 3
    prize_amount = 5000000
    net_cost = prize_amount-desired_net_amount
    if net_cost <= 0:
        print("Your desired profit is not achievable.")
    else:
        number_of_tickets = net_cost // ticket_cost
        string_ticket = "ticket" if number_of_tickets == 1 else "tickets"
        print(f"The cost to win the jackpot with a net profit of ${desired_net_amount:,} is ${(ticket_cost * number_of_tickets):,} ({number_of_tickets:,} {string_ticket}).")
        multi_ticket_probability(number_of_tickets)

test_desired_profit_amounts = [1, 500_000, 1_000_000, 2_000_000, 3_000_000, 4_000_000, 4_500_000, 4_999_997]

for test_desired_profit in test_desired_profit_amounts:
    profit(test_desired_profit)
    print(f"{'-'*100}")
    
# =============== Less Winning Numbers ===============
# ====================================================

def probability_less_6(count_winning_numbers):
    successful_outcomes = combinations(6, count_winning_numbers) * combinations(43, 6 - count_winning_numbers)
    combos = combinations(49, 6)
    proportion = successful_outcomes/combos
    print(f"The chance of your ticket having {count_winning_numbers} winning numbers is {proportion*100:.5f}%, or 1 in {int(combos/successful_outcomes):,}.")
    
test_count_winning_numbers = [2, 3, 4, 5]
for test_count in test_count_winning_numbers:
    probability_less_6(test_count)
    


    
    

