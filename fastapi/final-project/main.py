from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Optional
from datetime import date

app = FastAPI(
    title="🎬 Movie Ticket Booking System",
    description="A complete FastAPI backend for booking movie tickets.",
    version="1.0.0"
)

# ─────────────────────────────────────────────
# DATA STORE (in-memory, no database needed)
# ─────────────────────────────────────────────

movies = [
    {"id": 1, "title": "Interstellar", "genre": "Sci-Fi", "language": "English", "rating": 8.6, "duration_min": 169, "price": 250.0, "available_seats": 50},
    {"id": 2, "title": "KGF Chapter 2", "genre": "Action", "language": "Kannada", "rating": 8.2, "duration_min": 168, "price": 200.0, "available_seats": 80},
    {"id": 3, "title": "Pushpa 2", "genre": "Action", "language": "Telugu", "rating": 7.9, "duration_min": 190, "price": 180.0, "available_seats": 120},
    {"id": 4, "title": "Oppenheimer", "genre": "Biography", "language": "English", "rating": 8.5, "duration_min": 180, "price": 300.0, "available_seats": 40},
    {"id": 5, "title": "Leo", "genre": "Thriller", "language": "Tamil", "rating": 7.5, "duration_min": 164, "price": 160.0, "available_seats": 0},
]

bookings = []
booking_counter = {"id": 1}

cart = {}       # user_id -> list of movie_ids
orders = []
deliveries = []


# ─────────────────────────────────────────────
# PYDANTIC MODELS
# ─────────────────────────────────────────────

class Movie(BaseModel):
    title: str = Field(..., min_length=2, max_length=100)
    genre: str = Field(..., min_length=2)
    language: str = Field(..., min_length=2)
    rating: float = Field(..., ge=0.0, le=10.0)
    duration_min: int = Field(..., gt=0)
    price: float = Field(..., gt=0)
    available_seats: int = Field(..., ge=0)

class MovieUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=2, max_length=100)
    genre: Optional[str] = None
    language: Optional[str] = None
    rating: Optional[float] = Field(None, ge=0.0, le=10.0)
    duration_min: Optional[int] = Field(None, gt=0)
    price: Optional[float] = Field(None, gt=0)
    available_seats: Optional[int] = Field(None, ge=0)

class BookingRequest(BaseModel):
    user_name: str = Field(..., min_length=2)
    movie_id: int
    seats: int = Field(..., ge=1, le=10)
    show_date: date

class CartRequest(BaseModel):
    user_id: str
    movie_id: int

class OrderRequest(BaseModel):
    user_id: str
    show_date: date

class CheckInRequest(BaseModel):
    booking_id: int
    user_name: str


# ─────────────────────────────────────────────
# HELPER FUNCTIONS
# ─────────────────────────────────────────────

def find_movie(movie_id: int):
    return next((m for m in movies if m["id"] == movie_id), None)

def find_booking(booking_id: int):
    return next((b for b in bookings if b["id"] == booking_id), None)

def calculate_total(price: float, seats: int) -> float:
    return round(price * seats, 2)

def filter_movies(genre=None, language=None, min_rating=None):
    result = movies
    if genre is not None:
        result = [m for m in result if m["genre"].lower() == genre.lower()]
    if language is not None:
        result = [m for m in result if m["language"].lower() == language.lower()]
    if min_rating is not None:
        result = [m for m in result if m["rating"] >= min_rating]
    return result


# ─────────────────────────────────────────────
# DAY 1 — GET APIs
# ─────────────────────────────────────────────

# Q1 - Home Route
@app.get("/", tags=["General"])
def home():
    return {
        "message": "🎬 Welcome to the Movie Ticket Booking System!",
        "docs": "/docs",
        "total_movies": len(movies)
    }

# Q2 - List All Movies
@app.get("/movies", tags=["Movies"])
def get_all_movies():
    return {"total": len(movies), "movies": movies}

# Q3 - Get Movie by ID
@app.get("/movies/{movie_id}", tags=["Movies"])
def get_movie_by_id(movie_id: int):
    movie = find_movie(movie_id)
    if not movie:
        raise HTTPException(status_code=404, detail=f"Movie with ID {movie_id} not found.")
    return movie

# Q4 - Summary / Count Endpoint
@app.get("/movies/summary/stats", tags=["Movies"])
def movie_summary():
    available = [m for m in movies if m["available_seats"] > 0]
    avg_rating = round(sum(m["rating"] for m in movies) / len(movies), 2) if movies else 0
    return {
        "total_movies": len(movies),
        "available_movies": len(available),
        "housefull_movies": len(movies) - len(available),
        "average_rating": avg_rating,
        "total_bookings": len(bookings)
    }


# ─────────────────────────────────────────────
# DAY 2 — POST + PYDANTIC VALIDATION
# ─────────────────────────────────────────────

# Q5 - Add a New Movie
@app.post("/movies", status_code=201, tags=["Movies"])
def add_movie(movie: Movie):
    new_id = max((m["id"] for m in movies), default=0) + 1
    new_movie = {"id": new_id, **movie.dict()}
    movies.append(new_movie)
    return {"message": "Movie added successfully.", "movie": new_movie}

# Q6 - Book Tickets (POST with validation)
@app.post("/bookings", status_code=201, tags=["Bookings"])
def book_tickets(request: BookingRequest):
    movie = find_movie(request.movie_id)
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found.")
    if movie["available_seats"] < request.seats:
        raise HTTPException(status_code=400, detail=f"Only {movie['available_seats']} seats available.")

    total = calculate_total(movie["price"], request.seats)
    booking = {
        "id": booking_counter["id"],
        "user_name": request.user_name,
        "movie_id": request.movie_id,
        "movie_title": movie["title"],
        "seats": request.seats,
        "show_date": str(request.show_date),
        "total_amount": total,
        "status": "confirmed"
    }
    bookings.append(booking)
    movie["available_seats"] -= request.seats
    booking_counter["id"] += 1
    return {"message": "🎟️ Booking confirmed!", "booking": booking}


# ─────────────────────────────────────────────
# DAY 3 — HELPER FUNCTIONS + QUERY PARAMS
# ─────────────────────────────────────────────

# Q7 - Filter Movies by Genre / Language / Rating
@app.get("/movies/filter/options", tags=["Movies"])
def filter_movies_endpoint(
    genre: Optional[str] = Query(None),
    language: Optional[str] = Query(None),
    min_rating: Optional[float] = Query(None, ge=0, le=10)
):
    result = filter_movies(genre, language, min_rating)
    if not result:
        raise HTTPException(status_code=404, detail="No movies match the given filters.")
    return {"total": len(result), "movies": result}

# Q8 - Get All Bookings
@app.get("/bookings", tags=["Bookings"])
def get_all_bookings():
    return {"total": len(bookings), "bookings": bookings}

# Q9 - Get Booking by ID
@app.get("/bookings/{booking_id}", tags=["Bookings"])
def get_booking_by_id(booking_id: int):
    booking = find_booking(booking_id)
    if not booking:
        raise HTTPException(status_code=404, detail=f"Booking ID {booking_id} not found.")
    return booking


# ─────────────────────────────────────────────
# DAY 4 — CRUD OPERATIONS
# ─────────────────────────────────────────────

# Q10 - Update Movie (PUT)
@app.put("/movies/{movie_id}", tags=["Movies"])
def update_movie(movie_id: int, updates: MovieUpdate):
    movie = find_movie(movie_id)
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found.")
    update_data = updates.dict(exclude_none=True)
    movie.update(update_data)
    return {"message": "Movie updated successfully.", "movie": movie}

# Q11 - Delete Movie (DELETE)
@app.delete("/movies/{movie_id}", tags=["Movies"])
def delete_movie(movie_id: int):
    movie = find_movie(movie_id)
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found.")
    movies.remove(movie)
    return {"message": f"Movie '{movie['title']}' deleted successfully."}

# Q12 - Cancel Booking (DELETE)
@app.delete("/bookings/{booking_id}", tags=["Bookings"])
def cancel_booking(booking_id: int):
    booking = find_booking(booking_id)
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found.")
    # Restore seats
    movie = find_movie(booking["movie_id"])
    if movie:
        movie["available_seats"] += booking["seats"]
    booking["status"] = "cancelled"
    bookings.remove(booking)
    return {"message": f"Booking #{booking_id} cancelled. Seats restored."}


# ─────────────────────────────────────────────
# DAY 5 — MULTI-STEP WORKFLOW: Cart → Order → Check-in
# ─────────────────────────────────────────────

# Q13 - Add to Cart
@app.post("/cart/add", status_code=201, tags=["Workflow"])
def add_to_cart(request: CartRequest):
    movie = find_movie(request.movie_id)
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found.")
    if movie["available_seats"] == 0:
        raise HTTPException(status_code=400, detail="No seats available for this movie.")
    if request.user_id not in cart:
        cart[request.user_id] = []
    if request.movie_id in cart[request.user_id]:
        raise HTTPException(status_code=400, detail="Movie already in cart.")
    cart[request.user_id].append(request.movie_id)
    return {"message": f"🛒 '{movie['title']}' added to cart.", "cart": cart[request.user_id]}

# Q14 - View Cart
@app.get("/cart/{user_id}", tags=["Workflow"])
def view_cart(user_id: str):
    user_cart = cart.get(user_id, [])
    cart_movies = [find_movie(mid) for mid in user_cart if find_movie(mid)]
    total = sum(m["price"] for m in cart_movies)
    return {"user_id": user_id, "items": cart_movies, "estimated_total": round(total, 2)}

# Q15 - Place Order from Cart
@app.post("/orders", status_code=201, tags=["Workflow"])
def place_order(request: OrderRequest):
    user_cart = cart.get(request.user_id, [])
    if not user_cart:
        raise HTTPException(status_code=400, detail="Cart is empty. Add movies before placing an order.")
    order_items = []
    total = 0
    for mid in user_cart:
        movie = find_movie(mid)
        if movie and movie["available_seats"] > 0:
            movie["available_seats"] -= 1
            total += movie["price"]
            order_items.append({"movie_id": mid, "title": movie["title"], "price": movie["price"]})
    order = {
        "order_id": len(orders) + 1,
        "user_id": request.user_id,
        "show_date": str(request.show_date),
        "items": order_items,
        "total_amount": round(total, 2),
        "status": "booked"
    }
    orders.append(order)
    cart[request.user_id] = []  # Clear cart
    return {"message": "🎉 Order placed successfully!", "order": order}

# Q16 - Check-in at Theatre
@app.post("/checkin", tags=["Workflow"])
def check_in(request: CheckInRequest):
    booking = find_booking(request.booking_id)
    # Also check orders
    order = next((o for o in orders if o["order_id"] == request.booking_id), None)
    if not booking and not order:
        raise HTTPException(status_code=404, detail="No booking/order found with that ID.")
    delivery = {
        "checkin_id": len(deliveries) + 1,
        "booking_id": request.booking_id,
        "user_name": request.user_name,
        "status": "checked-in ✅",
        "message": "Enjoy your movie! 🍿"
    }
    deliveries.append(delivery)
    return delivery


# ─────────────────────────────────────────────
# DAY 6 — ADVANCED: Search, Sort, Pagination, Browse
# ─────────────────────────────────────────────

# Q17 - Search Movies by Keyword
@app.get("/movies/search/keyword", tags=["Advanced"])
def search_movies(q: str = Query(..., min_length=1, description="Search keyword")):
    q_lower = q.lower()
    results = [
        m for m in movies
        if q_lower in m["title"].lower()
        or q_lower in m["genre"].lower()
        or q_lower in m["language"].lower()
    ]
    if not results:
        raise HTTPException(status_code=404, detail=f"No movies found for keyword '{q}'.")
    return {"query": q, "total": len(results), "movies": results}

# Q18 - Sort Movies
@app.get("/movies/sort/results", tags=["Advanced"])
def sort_movies(
    sort_by: str = Query("rating", description="Sort by: rating, price, duration_min, title"),
    order: str = Query("desc", description="Order: asc or desc")
):
    valid_fields = ["rating", "price", "duration_min", "title"]
    if sort_by not in valid_fields:
        raise HTTPException(status_code=400, detail=f"sort_by must be one of {valid_fields}")
    reverse = order.lower() == "desc"
    sorted_movies = sorted(movies, key=lambda m: m[sort_by], reverse=reverse)
    return {"sort_by": sort_by, "order": order, "movies": sorted_movies}

# Q19 - Paginate Movies
@app.get("/movies/paginate/list", tags=["Advanced"])
def paginate_movies(
    page: int = Query(1, ge=1),
    page_size: int = Query(3, ge=1, le=10)
):
    start = (page - 1) * page_size
    end = start + page_size
    paginated = movies[start:end]
    return {
        "page": page,
        "page_size": page_size,
        "total_movies": len(movies),
        "total_pages": -(-len(movies) // page_size),  # ceiling division
        "movies": paginated
    }

# Q20 - Combined Browse (Search + Filter + Sort + Paginate)
@app.get("/movies/browse/all", tags=["Advanced"])
def browse_movies(
    q: Optional[str] = Query(None, description="Keyword search"),
    genre: Optional[str] = Query(None),
    language: Optional[str] = Query(None),
    min_rating: Optional[float] = Query(None, ge=0, le=10),
    sort_by: str = Query("rating", description="rating | price | title | duration_min"),
    order: str = Query("desc", description="asc | desc"),
    page: int = Query(1, ge=1),
    page_size: int = Query(3, ge=1, le=10)
):
    result = list(movies)

    # Step 1: Keyword filter
    if q is not None:
        q_lower = q.lower()
        result = [m for m in result if q_lower in m["title"].lower() or q_lower in m["genre"].lower()]

    # Step 2: Attribute filters
    if genre is not None:
        result = [m for m in result if m["genre"].lower() == genre.lower()]
    if language is not None:
        result = [m for m in result if m["language"].lower() == language.lower()]
    if min_rating is not None:
        result = [m for m in result if m["rating"] >= min_rating]

    # Step 3: Sort
    valid_fields = ["rating", "price", "duration_min", "title"]
    if sort_by in valid_fields:
        result = sorted(result, key=lambda m: m[sort_by], reverse=(order == "desc"))

    # Step 4: Paginate
    total = len(result)
    start = (page - 1) * page_size
    paginated = result[start:start + page_size]

    return {
        "filters_applied": {"q": q, "genre": genre, "language": language, "min_rating": min_rating},
        "sort": {"sort_by": sort_by, "order": order},
        "pagination": {"page": page, "page_size": page_size, "total_results": total, "total_pages": -(-total // page_size)},
        "movies": paginated
    }
