import requests

import config

def generatePassword(password):
    response = requests.post(
        "{}/generatePassword".format(config.HARAMBE_IDENTITY_SERVICE_ENDPOINT),
        json={"plaintext": password}
    )

    assert(response.status_code == 200), "Error generating password"

    data = response.json()
    return data.get("hash")

def getToken(username, password):
    # get user by username from data service
    userResponse = requests.get(
        "{}/users?email_address__$eq={}".format(config.HARAMBE_DATA_SERVICE_ENDPOINT, username)
    )

    assert(userResponse.status_code == 200), "Error retrieving user"
    userData = userResponse.json()
    assert(len(userData) > 0), "No user found"
    user = userData[0]

    # login with the username and password plaintext provided
    tokenResponse = requests.post(
        "{}/generateToken".format(config.HARAMBE_IDENTITY_SERVICE_ENDPOINT),
        json={"plaintext": password, "hash": user.get("password"), "user_id": user.get("_id")}
    )

    assert(tokenResponse.status_code == 200), "Could not log in user"
    token = tokenResponse.json()

    # return the token string
    return token.get("token")



def decodeToken(token):
    # validate with identity service
    response = requests.post(
        "{}/validateToken".format(config.HARAMBE_IDENTITY_SERVICE_ENDPOINT),
        json={"token": token})

    assert(response.status_code == 200), "Provided token is invalid"

    data = response.json()
    return data