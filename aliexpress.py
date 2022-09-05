MIN_REPUTATION = 20
MAX_REPUTATION = 25

def followersScore(followers):
    if followers < 100:
        return 1
    elif followers < 1000:
        return 2
    elif followers < 5000:
        return 3
    elif followers < 10000:
        return 4
    elif followers >= 10000:
        return 5
    else:
        return 0

def productScore(orders, ratings, reputation=0):
    orderscore = 0

    # if ratings is up to 5 or less than 1
    if (ratings > 5) or (ratings < 1):
        orderscore = 0
    if (orders < 100) and (ratings >= 4.5):
        # reputation is king
        if (reputation >= MIN_REPUTATION) :
            orderscore = 5
        else:
            orderscore = 2.5
    elif (orders < 1000) and (ratings >= 4.7):
        orderscore = 5
    elif (orders < 5000) and (ratings >= 4.6):
        orderscore = 5
    elif (orders < 10000) and (ratings >= 4.5):
        orderscore = 5
    elif (orders < 25000) and (ratings >= 4.4):
        orderscore = 5
    elif (orders >= 25000) and (ratings >= 4.3):
        orderscore = 5
    else:
        # if the reputation is the high and 
        # ratings above= 4.1
        if reputation >= MIN_REPUTATION and ratings >= 4.1:
            orderscore = 5
        # if reputation is high and ratings
        # above= 3.0 assign 1 as orderscore
        elif reputation >= MIN_REPUTATION and ratings >= 3.0:
            orderscore = 1
        else:
            orderscore = 0

    # multiply orderscore by product ratings
    # product with order score will get a zero
    # final score
    finalscore = orderscore * ratings

    return finalscore

def orderScore(orders, ratings, follower_score, reputation=0):
    score = 0

    # if the product has no rating
    # or strange rating
    if (ratings > 5) or (ratings == 0):
        score = 0
    # if order is less than 100
    elif (orders < 100):
        # if the seller has a reputation
        # and have atleast 5 product orders
        if reputation >= MIN_REPUTATION and orders >= 5:
            score = 4
        else:
            score = 0
    elif (orders < 1000) and ratings >= 4.8:
        score = 5
    elif (orders < 5000) and ratings >= 4.7:
        score = 5
    elif (orders < 10000) and ratings >= 4.5:
        score = 5
    elif (orders < 25000) and ratings >= 4.3:
        score = 5
    elif (orders < 1000) and ratings >= 4.1:
        score = 5
    else:
        score = ratings

    score = score * follower_score

    return score;

# calculate the store reputation
def reputationScore(follower_score, store_ratings):
    store_ratings = store_ratings / 20

    if store_ratings > 5:
        return 0

    return follower_score * store_ratings

def priceReputation(base_price, avg_price, reputation=0):
    # calculate the ration
    ratio_price = base_price / avg_price

    # if there is 75% discount
    if ratio_price <= 0.25:
        # consider reputation
        if (reputation >= MIN_REPUTATION):
            return 15
        else:
            return 0
    elif ratio_price <= 0.50:
        # consider reputation
        if (reputation >= MIN_REPUTATION):
            return 20
        else:
            return 0
    elif ratio_price >= 3.0:
        # reputation is king
        if (reputation >= MIN_REPUTATION):
            return 20
        else:
            return 10
    else:
        return 25

def getNumbers(value):
    return float("".join(c for c in value if c.isdigit() or c == ".").strip())
    #return re.sub("[^0-9.%]", "", value)

# get the followers count from the html text   
def getFollowersCount(text):
    count = "".join(c for c in text if c.isdigit() or c == "." or c == "k" or c == "m").strip()
    
    #print(count)

    if "k" in count:
        count = "".join(c for c in count if c.isdigit() or c == ".").strip()
        count = float(count) * 1000
    elif "m" in count:
        count = "".join(c for c in count if c.isdigit() or c == ".").strip()
        count = float(count) * 1000000
    else:
        count = "".join(c for c in count if c.isdigit() or c == ".").strip()

    return float(count)
