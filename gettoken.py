import twoauth

def token(ckey, csecret):
    print "[Twittext OAuth Setup]"
    oa = twoauth.oauth(ckey, csecret)
    req_token = oa.request_token()
    auth_url = oa.authorize_url(req_token)
    
    print "Authorize URL (Please Allow):"
    print auth_url
    pin = raw_input("PIN: ")
    
    acc_token = oa.access_token(req_token, int(pin))
    
    atoken = acc_token["oauth_token"]
    asecret = acc_token["oauth_token_secret"]
    screen_name = acc_token["screen_name"]
    
    print "screen_name: %s" % screen_name
    
    return (atoken, asecret, screen_name)
