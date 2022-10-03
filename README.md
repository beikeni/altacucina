# Altacucina Backend Test
`altacucina.spookykiwi.com/api/v1/`

Instead of providing a project to spin up locally I opted for deploying the app so that you could use it directly. Spookykiwi.com is a domain that I own and that I use for testing and learning purposes. 

For this particular excercise I created a new subdomain and secured it with SSL. 

The GitHub repo has a simple pipeline that **deploys automatically on commit** to the main branch, if you wish to test it you can simply download the repo and push a change to trigger the pipeline.

### If you really prefer to test the project locally 
- Download the repo 
- Add .env file to root level 
```
DEVELOPMENT=true
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=postgres
```
- Run `docker compose up`. The dev server will run on the usual `127.0.0.1:8000`=

## DB Schema
![db_updated](https://user-images.githubusercontent.com/64857643/193601339-b4b8a435-14fe-4a36-b0ac-6fde50bfa1d8.png)
- **User** and **Movie** have a **many-to-many** relationship with Watched as a through table. This way it's possible to record the timestamp of the row being created (movie being watched), this could come in useful for all sorts of queries later on.
- The existence of a **Watched** row between a user and a movie indicates that a certain user watched a certain movie. If a user marks a movie unwatched, then the corresponding row on the Watched table is deleted.
- Both **User** and **Movie** have a **one-to-many** relationship to **Review**. A user can review a movie even if the movie is not marked as watched, but when the reviews for a certain movie are listed, there will be a flag `is_watched_by_reviewer` indicating whether the user has watched that movie. 


## User Registration
For registration and authentication i decided to use the DRF **TokenAuthentication** since I've never used it before and this seemed like a good opportunity to learn it.

```console
curl -X POST https://altacucina.spookykiwi.com/users/register/ -H 'Content-Type: application/json' -d { "username": "altacucina", "password": "testpass123", "password2": "testpass123", "email": "test@test.com"}
```

### Get Token
```console
curl -X POST https://altacucina.spookykiwi.com/api-token-auth/ -H 'Content-Type: application/json' -d { "username": "altacucina", "password": "testpass123"}
```
*response*
```json
{
    "token": "2812b81cbbcb4cef2d82051e1251503ffa05ba0c"
}
```

## Movies 
### Create Movie
Movies are defined by their **title and year**. Duplicated movie titles are fine as long as the year is different. 
```console
curl -X POST https://altacucina.spookykiwi.com/api/v1/movies/ -H 'Content-Type: application/json' -H 'Authorization: Token 2812b81cbbcb4cef2d82051e1251503ffa05ba0c"  -d {"name": "Bear Attack 6", "platform": "prime_video", "year": "1997"}
```

### Marking a movie as watched
This single endpoint flips the watched status on and off in an alternated manner.
```console
curl https://altacucina.spookykiwi.com/api/v1/movies/1/mark-watched/ -H 'Content-Type: application/json' -H 'Authorization: Token 2812b81cbbcb4cef2d82051e1251503ffa05ba0c'
```
*responses*
```json

{
    "response": "Bear Attack 6(1997) has been removed from Altacucina's list!"
},
{
    "response": "Bear Attack 6(1997) has been added to Altacucina's list!"
}
```

### Movie List
As requested in the briefing, if the request contains a valid token header the list will have an extra field name `is_watched` with a boolean value indicating if the user has already watched that movie.
#### Authenticated
```console
curl https://altacucina.spookykiwi.com/api/v1/movies/ -H 'Content-Type: application/json' -H 'Authorization: Token 2812b81cbbcb4cef2d82051e1251503ffa05ba0c'
```
*response*
```json
[
...
    {
        "id": 1,
        "name": "Bear Attack 6",
        "year": 1997,
        "platform": "prime_video"
    },
...
]
```
#### Not Authenticated
```console
curl https://altacucina.spookykiwi.com/api/v1/movies/ -H 'Content-Type: application/json' -H 'Authorization: Token 2812b81cbbcb4cef2d82051e1251503ffa05ba0c'
```
*response*
```json
[
...
    {
        "id": 1,
        "name": "Bear Attack 6",
        "year": 1997,
        "platform": "prime_video",
        "is_watched": true 
    },
...
]
```

### Watched Movie List
```console
curl https://altacucina.spookykiwi.com/api/v1/movies/watched/ -H 'Content-Type: application/json' -H 'Authorization: Token 2812b81cbbcb4cef2d82051e1251503ffa05ba0c'
```
*response*
```json
[
    {
        "id": 1,
        "name": "Bear Attack 6",
        "year": 1997,
        "platform": "prime_video"
    }
]
```

### Movie List filtered by platform
```console
curl https://altacucina.spookykiwi.com/api/v1/movies/platform/prime_video/ -H 'Content-Type: application/json'
```
*response*
```json
[
    {
        "id": 1,
        "name": "Bear Attack 6",
        "year": 1997,
        "platform": "prime_video"
    },
    {
        "id": 3,
        "name": "Bear Attack 8",
        "year": 1999,
        "platform": "prime_video"
    }
]
```

## Reviews

### Create Review
Each user can place one review per movie. 
```console
curl -X POST https://altacucina.spookykiwi.com/api/v1/reviews/ -H 'Content-Type: application/json' -H 'Authorization: Token 2812b81cbbcb4cef2d82051e1251503ffa05ba0c' -d {"movie": "1", "body": "This movie was alright, I just wish there were more bears..", "score": 8}

```
*response*
```json
{
  "body": "This movie was alright, I just wish there were more bears..",
  "score": 8,
  "movie": 1
}
```
### List Movie Reviews with ordering
Returns a list of reviews for the movie id supplied. Additionally, the custom field `is_watched_by_reviewer` **indicates whether the user who left the review has watched the movie**, helping the reader evaluating the trustworthiness of the information received! 

This endpoints takes a url param called `ordering` that can be **set to any field's name**. To reverse the ordering add `-` in front of the field name.
```console
curl https://altacucina.spookykiwi.com/api/v1/reviews/movie/1/?ordering=-score -H 'Content-Type: application/json' -H 'Authorization: Token 2812b81cbbcb4cef2d82051e1251503ffa05ba0c'
```
*response*
```json
[
    {
        "body": "This movie was alright, I just wish there were more bears..",
        "score": 8,
        "movie": 1,
        "is_watched_by_reviewer": true
    }
]
```

### List User Reviews with ordering
This endpoints takes a url param called `ordering` that can be **set to any field's name**. To reverse the ordering add `-` in front of the field name.
```console
curl https://altacucina.spookykiwi.com/api/v1/reviews/user/3/?ordering=-score -H 'Content-Type: application/json' -H 'Authorization: Token 2812b81cbbcb4cef2d82051e1251503ffa05ba0c'
```
*response*
```json
[
    {
        "body": "Finally a decent amount of bears, I also appreciated the raccoons",
        "score": 10,
        "movie": 4
    },
    {
        "body": "This movie was alright, I just wish there were more bears..",
        "score": 8,
        "movie": 1
    },
    {
        "body": "Many more bears, just not quite enough yet",
        "score": 7,
        "movie": 2
    }
]
```

### List unwatched movies
Returns all movies that have not been watched by the authenticated user that have at least one review. 
An extra field is added with the **average score from the existing reviews**.
```console
curl https://altacucina.spookykiwi.com/api/v1/movies/unwatched-with-review  -H 'Content-Type: application/json' -H 'Authorization: Token 2812b81cbbcb4cef2d82051e1251503ffa05ba0c'
```
*response*
```json
[
  {
    "id": 1,
    "name": "Bear Attack 5",
    "year": 1996,
    "platform": "prime_video",
    "average_score": 7.5
  }
]
```
