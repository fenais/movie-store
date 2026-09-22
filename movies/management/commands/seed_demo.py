"""Populate the database with demo movies, users, reviews and orders.

Usage: python manage.py seed_demo
Creates an admin account (admin / admin12345) and a demo user (demo / demo12345).
"""
import random
from io import BytesIO

from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from PIL import Image, ImageDraw, ImageFont

from cart.models import Item, Order
from movies.models import Movie, Review

MOVIES = [
    ("The Last Orbit", 14, "A stranded astronaut races against a failing oxygen supply to fix her capsule and make it home.", ("#0f2027", "#2c5364")),
    ("Midnight in Savannah", 12, "A jazz pianist uncovers a decades-old family secret hidden in an abandoned Georgia mansion.", ("#42275a", "#734b6d")),
    ("Iron Harvest", 15, "Two rival farming families must work together when a drought threatens their whole valley.", ("#603813", "#b29f94")),
    ("Signal Lost", 11, "A small-town radio host starts receiving broadcasts from exactly one week in the future.", ("#141e30", "#243b55")),
    ("Paper Lanterns", 10, "A heartfelt coming-of-age story about three friends spending one last summer together.", ("#e65c00", "#f9d423")),
    ("The Cartographer", 13, "An explorer maps an uncharted island, only to find the island keeps changing shape.", ("#134e5e", "#71b280")),
    ("Neon Drift", 16, "An underground street racer takes one final job through the rain-soaked streets of Neo-Tokyo.", ("#fc466b", "#3f5efb")),
    ("Quiet Hours", 9, "A night-shift nurse forms an unlikely bond with a patient who hasn't spoken in years.", ("#2c3e50", "#4ca1af")),
]

REVIEWS = [
    (5, "Absolutely loved it, watched it twice this week."),
    (4, "Great story and visuals. The ending was a little rushed."),
    (5, "One of the best movies I've seen this year."),
    (3, "Solid, but the middle act dragged a bit."),
    (4, "Surprisingly emotional. Great performances all around."),
    (2, "Not really my kind of movie, but I can see the appeal."),
]

USERNAMES = ["alex", "jordan", "sam", "taylor", "morgan", "casey"]
STATES = ["GA", "GA", "GA", "CA", "CA", "NY", "NY", "TX", "FL", "WA", "IL"]


def make_poster(title, colors):
    """Render a simple gradient poster so the demo needs no copyrighted artwork."""
    w, h = 400, 600
    img = Image.new("RGB", (w, h))
    top = Image.new("RGB", (1, 1), colors[0]).getpixel((0, 0))
    bottom = Image.new("RGB", (1, 1), colors[1]).getpixel((0, 0))
    draw = ImageDraw.Draw(img)
    for y in range(h):
        t = y / h
        draw.line([(0, y), (w, y)], fill=tuple(int(top[i] + (bottom[i] - top[i]) * t) for i in range(3)))
    font = ImageFont.load_default(size=40)
    words, lines, line = title.upper().split(), [], ""
    for word in words:
        trial = f"{line} {word}".strip()
        if draw.textlength(trial, font=font) > w - 60 and line:
            lines.append(line)
            line = word
        else:
            line = trial
    lines.append(line)
    y = h - 60 - 50 * len(lines)
    for text in lines:
        draw.text((30, y), text, font=font, fill="white")
        y += 50
    draw.rectangle([30, y + 10, 110, y + 16], fill="white")
    buf = BytesIO()
    img.save(buf, format="JPEG", quality=90)
    return ContentFile(buf.getvalue())


class Command(BaseCommand):
    help = "Seed the database with demo movies, users, reviews and orders."

    def handle(self, *args, **options):
        random.seed(2340)

        if not User.objects.filter(username="admin").exists():
            User.objects.create_superuser("admin", "admin@example.com", "admin12345")
        if not User.objects.filter(username="demo").exists():
            User.objects.create_user("demo", "demo@example.com", "demo12345")
        users = []
        for name in USERNAMES:
            user, created = User.objects.get_or_create(username=name)
            if created:
                user.set_password("demo12345")
                user.save()
            users.append(user)

        movies = []
        for name, price, description, colors in MOVIES:
            movie = Movie.objects.filter(name=name).first()
            if movie is None:
                movie = Movie(name=name, price=price, description=description)
                slug = name.lower().replace(" ", "_")
                movie.image.save(f"{slug}.jpg", make_poster(name, colors), save=False)
                movie.save()
            movies.append(movie)

        for movie in movies:
            for user in random.sample(users, k=random.randint(2, 4)):
                rating, comment = random.choice(REVIEWS)
                Review.objects.get_or_create(user=user, movie=movie, defaults={"rating": rating, "comment": comment})

        if not Order.objects.exists():
            for _ in range(30):
                picks = random.sample(movies, k=random.randint(1, 3))
                weights = {m.id: 3 if m.name in ("Neon Drift", "The Last Orbit") else 1 for m in picks}
                order = Order.objects.create(user=random.choice(users), total=0, state=random.choice(STATES))
                total = 0
                for movie in picks:
                    qty = random.randint(1, 2) * weights[movie.id]
                    Item.objects.create(movie=movie, price=movie.price, quantity=qty, order=order)
                    total += movie.price * qty
                order.total = total
                order.save()

        self.stdout.write(self.style.SUCCESS(
            f"Seeded {Movie.objects.count()} movies, {Review.objects.count()} reviews, {Order.objects.count()} orders. "
            "Log in as demo / demo12345 or admin / admin12345."
        ))
