CWUsers API Idempotence

-POST   cwuser --> create user - if group/iam role do not exists create
				 if not exists create user normally
				 if exists reset password and return as created (201)

-PATCH  cwuser --> update user pw - if exists update pw normally
				  - if not exists create user and return as updated (200)

-DELETE cwuser --> delete user - if exists delete normally
 			       - if not exists return as deleted (200)


If Entity "EntityTemporarilyUnmodifiable" -> wait(x ms) and retry request

Error Codes:
401 - Unauthorized (api gateway validation failed) 
403 - Account denied action



