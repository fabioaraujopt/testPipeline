CWUsers API Idempotence

-POST   cwuser --> create user - 
					if iam role do not exists create
					if create policy
				 	if not exists create user normally
				 	if exists reset password and return as created (201)

-POST (accountId) update role_policie -> 

-PATCH  cwuser --> update user pw
					if exists and belongs to group update pw normally			
				    if not exists (404)

-DELETE cwuser --> delete user 
				   if exists delete normally
 			       if not exists return as deleted (200)


If Entity "EntityTemporarilyUnmodifiable" -> wait(x ms) and retry request

Error Codes:
401 - Unauthorized (api gateway validation failed) 
403 - Account denied action
500 - x

Error template: 
{
    Errors: ["Author with id 31 not found."],
    StatusCode: "404",
    ErrorCode: "authorNotFound"
}

-Se Username existir no cliente mas noutro contexto?

apply versioned? 
/v1/cwusers/
